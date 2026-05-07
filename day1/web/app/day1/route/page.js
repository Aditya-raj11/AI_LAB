"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import styles from "./route.module.css";

/* ═══════════════════════════════════════════
   BIDIRECTIONAL SEARCH (ported from Python)
   ═══════════════════════════════════════════ */
function* bidirectionalTrace(graph, start, goal) {
  if (start === goal) {
    yield { event:"solution", step:0, current:start, frontVisited:new Set([start]),
            backVisited:new Set([goal]), path:[start], meeting:start,
            message:"Start and goal are the same node." };
    return;
  }

  const frontQueue = [start], backQueue = [goal];
  const frontParent = { [start]: null }, backParent = { [goal]: null };
  const frontVisited = new Set([start]), backVisited = new Set([goal]);
  let step = 0;

  yield { event:"start", step, current:start, frontVisited:new Set(frontVisited),
          backVisited:new Set(backVisited), path:[start], meeting:null,
          message:`Starting bidirectional search from ${start} to ${goal}.` };

  function buildPath(meet) {
    const path = [];
    let node = meet;
    while (node !== null) { path.push(node); node = frontParent[node]; }
    path.reverse();
    node = backParent[meet];
    while (node !== null) { path.push(node); node = backParent[node]; }
    return path;
  }

  function expand(queue, parent, thisVisited, otherVisited, label) {
    if (!queue.length) return [null, `${label} frontier is empty.`, null];
    const node = queue.shift();
    for (const neigh of (graph[node] || [])) {
      if (!thisVisited.has(neigh)) {
        thisVisited.add(neigh);
        parent[neigh] = node;
        queue.push(neigh);
        if (otherVisited.has(neigh))
          return [node, `${label} side reached meeting node ${neigh}.`, neigh];
      }
    }
    return [node, `${label} side expanded ${node}.`, null];
  }

  while (frontQueue.length && backQueue.length) {
    step++;
    const [fNode, fMsg, fMeet] = expand(frontQueue, frontParent, frontVisited, backVisited, "Forward");
    yield { event:"front_expand", step, current:fNode, frontVisited:new Set(frontVisited),
            backVisited:new Set(backVisited), path:fMeet?buildPath(fMeet):[], meeting:fMeet, message:fMsg };
    if (fMeet) {
      yield { event:"solution", step, current:fMeet, frontVisited:new Set(frontVisited),
              backVisited:new Set(backVisited), path:buildPath(fMeet), meeting:fMeet,
              message:`Searches met at ${fMeet}.` };
      return;
    }

    step++;
    const [bNode, bMsg, bMeet] = expand(backQueue, backParent, backVisited, frontVisited, "Backward");
    yield { event:"back_expand", step, current:bNode, frontVisited:new Set(frontVisited),
            backVisited:new Set(backVisited), path:bMeet?buildPath(bMeet):[], meeting:bMeet, message:bMsg };
    if (bMeet) {
      yield { event:"solution", step, current:bNode, frontVisited:new Set(frontVisited),
              backVisited:new Set(backVisited), path:buildPath(bMeet), meeting:bMeet,
              message:`Searches met at ${bMeet}.` };
      return;
    }
  }

  yield { event:"no_path", step, current:null, frontVisited:new Set(frontVisited),
          backVisited:new Set(backVisited), path:[], meeting:null,
          message:"No route found between the selected nodes." };
}

/* ═══════════════════════════════════════════
   DEFAULT GRAPH
   ═══════════════════════════════════════════ */
const DEFAULT_GRAPH = { A:["B","C"], B:["A","D","E"], C:["A","F"], D:["B"], E:["B","F"], F:["C","E"] };
const DEFAULT_POS = { A:[160,140], B:[340,100], C:[340,230], D:[520,100], E:[520,230], F:[690,165] };

const NODE_R = 28;

/* ═══════════════════════════════════════════
   COMPONENT
   ═══════════════════════════════════════════ */
export default function RoutePage() {
  const [graph, setGraph] = useState(() => JSON.parse(JSON.stringify(DEFAULT_GRAPH)));
  const [positions, setPositions] = useState(() => JSON.parse(JSON.stringify(DEFAULT_POS)));
  const [startNode, setStartNode] = useState("A");
  const [goalNode, setGoalNode] = useState("F");
  const [running, setRunning] = useState(false);
  const [frontVisited, setFrontVisited] = useState(new Set());
  const [backVisited, setBackVisited] = useState(new Set());
  const [finalPath, setFinalPath] = useState([]);
  const [meetingNode, setMeetingNode] = useState(null);
  const [stepCount, setStepCount] = useState(0);
  const [statusMsg, setStatusMsg] = useState("Ready");
  const [statusColor, setStatusColor] = useState("#22c55e");
  const [logs, setLogs] = useState([]);

  const canvasRef = useRef(null);
  const traceRef = useRef(null);
  const timerRef = useRef(null);
  const dragRef = useRef(null);
  const edgeRef = useRef(null);
  const logBoxRef = useRef(null);

  const nodes = Object.keys(graph).sort();

  // ─── Drawing ───
  const drawGraph = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    const drawn = new Set();
    for (const [node, neighbors] of Object.entries(graph)) {
      const [x1, y1] = positions[node] || [0, 0];
      for (const neigh of neighbors) {
        const edge = [node, neigh].sort().join("-");
        if (drawn.has(edge)) continue;
        drawn.add(edge);
        const [x2, y2] = positions[neigh] || [0, 0];

        const inPath = finalPath.length > 1 &&
          finalPath.some((n, i) => i < finalPath.length - 1 &&
            ((n === node && finalPath[i+1] === neigh) || (n === neigh && finalPath[i+1] === node)));

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = inPath ? "#f59e0b" : "#334155";
        ctx.lineWidth = inPath ? 4 : 3;
        ctx.stroke();
      }
    }

    // Draw edge preview
    if (edgeRef.current?.line) {
      ctx.beginPath();
      ctx.setLineDash([6, 4]);
      ctx.moveTo(edgeRef.current.startX, edgeRef.current.startY);
      ctx.lineTo(edgeRef.current.endX, edgeRef.current.endY);
      ctx.strokeStyle = "#94a3b8";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw nodes
    for (const [node, [x, y]] of Object.entries(positions)) {
      let fill = "#e2e8f0";
      let outline = "#111827";

      if (node === meetingNode && finalPath.length) { fill = "#86efac"; outline = "#22c55e"; }
      else if (finalPath.includes(node)) { fill = "#fde68a"; outline = "#f59e0b"; }
      else if (node === startNode) { fill = "#fbbf24"; }
      else if (node === goalNode) { fill = "#fca5a5"; }
      else if (frontVisited.has(node) && backVisited.has(node)) { fill = "#c084fc"; }
      else if (frontVisited.has(node)) { fill = "#7dd3fc"; }
      else if (backVisited.has(node)) { fill = "#f9a8d4"; }

      ctx.beginPath();
      ctx.arc(x, y, NODE_R, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.strokeStyle = outline;
      ctx.lineWidth = 3;
      ctx.stroke();

      ctx.fillStyle = "#0f172a";
      ctx.font = "bold 15px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(node, x, y);
    }
  }, [graph, positions, startNode, goalNode, frontVisited, backVisited, finalPath, meetingNode]);

  useEffect(() => { drawGraph(); }, [drawGraph]);

  // Resize
  useEffect(() => {
    const resize = () => drawGraph();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [drawGraph]);

  // ─── Mouse ───
  const nodeAtPoint = (x, y) => {
    for (const [node, [nx, ny]] of Object.entries(positions)) {
      if ((nx-x)**2 + (ny-y)**2 <= NODE_R**2) return node;
    }
    return null;
  };

  const nextNodeName = () => {
    const existing = new Set(Object.keys(graph));
    let i = 0;
    while (true) {
      let idx = i + 1, letters = [];
      while (idx) { const r = (idx - 1) % 26; letters.push(String.fromCharCode(65 + r)); idx = Math.floor((idx - 1) / 26); }
      const name = letters.reverse().join("");
      if (!existing.has(name)) return name;
      i++;
    }
  };

  const handleMouseDown = (e) => {
    if (running) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;

    if (e.button === 2) { // Right click — edge draw
      const node = nodeAtPoint(x, y);
      if (node) {
        edgeRef.current = { node, startX: positions[node][0], startY: positions[node][1], endX: x, endY: y, line: true };
      }
      return;
    }

    const node = nodeAtPoint(x, y);
    if (node) {
      dragRef.current = { node, offsetX: positions[node][0] - x, offsetY: positions[node][1] - y };
    }
  };

  const handleMouseMove = (e) => {
    if (running) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;

    if (edgeRef.current?.line) {
      edgeRef.current.endX = x;
      edgeRef.current.endY = y;
      drawGraph();
      return;
    }

    if (dragRef.current) {
      const newX = Math.max(NODE_R, Math.min(rect.width - NODE_R, x + dragRef.current.offsetX));
      const newY = Math.max(NODE_R, Math.min(rect.height - NODE_R, y + dragRef.current.offsetY));
      setPositions(prev => ({ ...prev, [dragRef.current.node]: [newX, newY] }));
    }
  };

  const handleMouseUp = (e) => {
    if (running) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;

    if (edgeRef.current?.line) {
      const target = nodeAtPoint(x, y);
      const edgeStartNode = edgeRef.current.node;
      if (target && target !== edgeStartNode) {
        setGraph(prev => {
          const g = JSON.parse(JSON.stringify(prev));
          const a = edgeStartNode, b = target;
          if (g[a].includes(b)) {
            g[a] = g[a].filter(n => n !== b);
            g[b] = g[b].filter(n => n !== a);
            setStatusMsg(`Disconnected ${a} and ${b}.`);
          } else {
            if (!g[a].includes(b)) g[a].push(b);
            if (!g[b].includes(a)) g[b].push(a);
            setStatusMsg(`Connected ${a} and ${b}.`);
          }
          return g;
        });
      }
      edgeRef.current = null;
      drawGraph();
      return;
    }

    if (dragRef.current) {
      dragRef.current = null;
    }
  };

  const handleDblClick = (e) => {
    if (running) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;
    const node = nodeAtPoint(x, y);
    if (node) {
      setGraph(prev => {
        const g = JSON.parse(JSON.stringify(prev));
        for (const neigh of (g[node] || [])) { g[neigh] = g[neigh].filter(n => n !== node); }
        delete g[node];
        return g;
      });
      setPositions(prev => { const p = { ...prev }; delete p[node]; return p; });
      if (startNode === node) setStartNode(Object.keys(graph).filter(n => n !== node).sort()[0] || "");
      if (goalNode === node) setGoalNode(Object.keys(graph).filter(n => n !== node).sort().pop() || "");
      setStatusMsg(`Removed node ${node}.`);
    } else {
      // Add node on empty space
      const name = nextNodeName();
      setGraph(prev => ({ ...prev, [name]: [] }));
      setPositions(prev => ({ ...prev, [name]: [x, y] }));
      setStatusMsg(`Added node ${name}.`);
    }
  };

  const handleContextMenu = (e) => e.preventDefault();

  // ─── Search ───
  const resetState = (msg) => {
    setFrontVisited(new Set());
    setBackVisited(new Set());
    setFinalPath([]);
    setMeetingNode(null);
    setStepCount(0);
    setLogs([]);
    setStatusMsg(msg || "Ready");
    setStatusColor("#22c55e");
    if (timerRef.current) clearTimeout(timerRef.current);
    traceRef.current = null;
  };

  const advance = useCallback(() => {
    if (!traceRef.current) return;
    const result = traceRef.current.next();
    if (result.done) { setRunning(false); return; }
    const s = result.value;
    setFrontVisited(s.frontVisited);
    setBackVisited(s.backVisited);
    setMeetingNode(s.meeting);
    setStepCount(s.step);
    setStatusMsg(s.message);
    setLogs(prev => [...prev, s.message]);

    if (s.event === "solution") {
      setFinalPath(s.path);
      setStatusColor("#22c55e");
      setRunning(false);
      return;
    }
    if (s.event === "no_path") {
      setStatusColor("#ef4444");
      setRunning(false);
      return;
    }
  }, []);

  useEffect(() => {
    if (!running) return;
    const tick = () => { advance(); timerRef.current = setTimeout(tick, 280); };
    timerRef.current = setTimeout(tick, 280);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [running, advance]);

  useEffect(() => {
    if (logBoxRef.current) logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight;
  }, [logs]);

  const startSearch = () => {
    if (running || !startNode || !goalNode) return;
    resetState("Searching…");
    setStatusColor("#f59e0b");
    traceRef.current = bidirectionalTrace(graph, startNode, goalNode);
    setRunning(true);
  };

  const loadSample = () => {
    if (running) return;
    setGraph(JSON.parse(JSON.stringify(DEFAULT_GRAPH)));
    setPositions(JSON.parse(JSON.stringify(DEFAULT_POS)));
    setStartNode("A"); setGoalNode("F");
    resetState("Sample graph loaded.");
  };

  const genRandom = () => {
    if (running) return;
    const g = {}, p = {};
    const n = 6 + Math.floor(Math.random() * 7);
    const rect = canvasRef.current?.getBoundingClientRect();
    const w = rect?.width || 700, h = rect?.height || 500;
    const names = [];
    for (let i = 0; i < n; i++) {
      let idx = i + 1, letters = [];
      while (idx) { const r = (idx-1)%26; letters.push(String.fromCharCode(65+r)); idx = Math.floor((idx-1)/26); }
      const name = letters.reverse().join("");
      names.push(name);
      g[name] = [];
      p[name] = [NODE_R+20+Math.random()*(w-NODE_R*2-40), NODE_R+20+Math.random()*(h-NODE_R*2-40)];
    }
    for (let i = 1; i < names.length; i++) {
      const target = names[Math.floor(Math.random()*i)];
      if (!g[names[i]].includes(target)) { g[names[i]].push(target); g[target].push(names[i]); }
      for (let j = 0; j < Math.floor(Math.random()*2); j++) {
        const t = names[Math.floor(Math.random()*names.length)];
        if (t !== names[i] && !g[names[i]].includes(t)) { g[names[i]].push(t); g[t].push(names[i]); }
      }
    }
    setGraph(g); setPositions(p);
    setStartNode(names[0]); setGoalNode(names[names.length-1]);
    resetState("Random graph generated.");
  };

  const clearAll = () => {
    if (running) return;
    setGraph({}); setPositions({});
    setStartNode(""); setGoalNode("");
    resetState("Graph cleared. Double-click canvas to add nodes.");
  };

  return (
    <div className={styles.page}>
      <nav className={styles.navbar}>
        <Link href="/day1" className={styles.backLink}>← Day 1</Link>
        <span className={styles.pageTitle}>
          Route <span className={styles.pageTitleAccent}>Finder</span>
        </span>
        <div />
      </nav>

      <div className={styles.body}>
        <div className={styles.canvasArea}>
          <canvas
            ref={canvasRef}
            className={styles.graphCanvas}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onDoubleClick={handleDblClick}
            onContextMenu={handleContextMenu}
          />
          <div className={styles.canvasLegend}>
            Front: blue · Back: pink · Meeting: green · Route: gold<br/>
            Double-click: add/remove node · Right-drag: connect/disconnect
          </div>
        </div>

        <div className={styles.panel}>
          {/* Controls */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Controls</div>
            <div className={styles.selectRow}>
              <div className={styles.selectLabel}>Start node</div>
              <select className={styles.select} value={startNode} onChange={e => setStartNode(e.target.value)} disabled={running}>
                {nodes.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div className={styles.selectRow}>
              <div className={styles.selectLabel}>Goal node</div>
              <select className={styles.select} value={goalNode} onChange={e => setGoalNode(e.target.value)} disabled={running}>
                {nodes.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Actions</div>
            <button className={`${styles.actionBtn} ${styles.primaryBtn}`} onClick={startSearch} disabled={running}>
              {running ? "⏸ Running…" : "▶ Run Search"}
            </button>
            <div className={styles.btnRow}>
              <button className={`${styles.actionBtn} ${styles.secondaryBtn}`} onClick={loadSample} disabled={running}>Sample</button>
              <button className={`${styles.actionBtn} ${styles.secondaryBtn}`} onClick={genRandom} disabled={running}>Random</button>
              <button className={`${styles.actionBtn} ${styles.secondaryBtn}`} onClick={clearAll} disabled={running}>Clear</button>
            </div>
          </div>

          {/* Stats */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Statistics</div>
            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>Step</div>
                <div className={styles.statValue}>{stepCount}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>Meeting</div>
                <div className={styles.statValue}>{meetingNode || "—"}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>Visited</div>
                <div className={styles.statValue}>{frontVisited.size + backVisited.size}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>Path</div>
                <div className={styles.statValue}>{finalPath.length || "—"}</div>
              </div>
            </div>
          </div>

          {/* Status */}
          <div className={styles.panelSection}>
            <div className={styles.statusBar}>
              <span className={styles.statusDot} style={{ background: statusColor }} />
              <span className={styles.statusText}>{statusMsg}</span>
            </div>
          </div>

          {/* Log */}
          <div className={styles.logSection}>
            <div className={styles.sectionLabel}>Search Log</div>
            <div className={styles.logBox} ref={logBoxRef}>
              {logs.map((msg, i) => <div key={i} className={styles.logEntry}>{msg}</div>)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
