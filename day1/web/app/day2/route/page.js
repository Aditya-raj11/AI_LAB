"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import styles from "./route.module.css";

/* ═══════════════════════════════════════════
   UNIFORM COST SEARCH (ported from Python)
   ═══════════════════════════════════════════ */
function* ucsTrace(graph, positions, start, goal) {
  if (start === goal) {
    yield { event:"solution", step:0, current:start, frontVisited:new Set([start]),
            backVisited:new Set(), path:[start], meeting:null,
            message:"Start and goal are the same node." };
    return;
  }

  const distance = (n1, n2) => {
    const [x1, y1] = positions[n1] || [0,0];
    const [x2, y2] = positions[n2] || [0,0];
    return Math.sqrt((x1-x2)**2 + (y1-y2)**2);
  };

  const pq = [{ node: start, cost: 0, path: [start] }];
  const visited = new Set();
  let step = 0;

  yield { event:"start", step, current:start, frontVisited:new Set(visited),
          backVisited:new Set(), path:[start], meeting:null,
          message:`Starting Uniform Cost Search from ${start} to ${goal}.` };

  while (pq.length > 0) {
    // Extract minimum cost node
    pq.sort((a, b) => a.cost - b.cost);
    const { node, cost, path } = pq.shift();

    if (visited.has(node)) continue;
    visited.add(node);
    step++;

    yield { event:"expand", step, current:node, frontVisited:new Set(visited),
            backVisited:new Set(), path: [], meeting:null,
            message:`Expanded ${node} (Cost: ${Math.round(cost)})` };

    if (node === goal) {
      yield { event:"solution", step, current:node, frontVisited:new Set(visited),
              backVisited:new Set(), path, meeting:null,
              message:`✓ Goal reached! Total cost: ${Math.round(cost)}` };
      return;
    }

    for (const neigh of (graph[node] || [])) {
      if (!visited.has(neigh)) {
        const edgeCost = distance(node, neigh);
        pq.push({ node: neigh, cost: cost + edgeCost, path: [...path, neigh] });
      }
    }
  }

  yield { event:"no_path", step, current:null, frontVisited:new Set(visited),
          backVisited:new Set(), path:[], meeting:null,
          message:"No route found between the selected nodes." };
}

/* ═══════════════════════════════════════════
   DEFAULT GRAPH
   ═══════════════════════════════════════════ */
const DEFAULT_GRAPH = { A:["B","C"], B:["A","D","E"], C:["A","F"], D:["B"], E:["B","F"], F:["C","E"] };
const DEFAULT_POS = { A:[0.19,0.42], B:[0.40,0.30], C:[0.40,0.69], D:[0.61,0.30], E:[0.61,0.69], F:[0.81,0.50] };

const NODE_R = 28;

// Scale normalized positions (0-1) to actual canvas pixel coordinates
function scalePositions(normalizedPos, w, h) {
  const pad = NODE_R + 10;
  const result = {};
  for (const [node, [nx, ny]] of Object.entries(normalizedPos)) {
    result[node] = [
      pad + nx * (w - pad * 2),
      pad + ny * (h - pad * 2),
    ];
  }
  return result;
}

/* ═══════════════════════════════════════════
   COMPONENT
   ═══════════════════════════════════════════ */
export default function RoutePage() {
  const [graph, setGraph] = useState(() => JSON.parse(JSON.stringify(DEFAULT_GRAPH)));
  const [positions, setPositions] = useState({});
  const prevSizeRef = useRef({ w: 0, h: 0 });
  const initializedRef = useRef(false);
  const [startNode, setStartNode] = useState("A");
  const [goalNode, setGoalNode] = useState("F");
  const [running, setRunning] = useState(false);
  const [touchMode, setTouchMode] = useState("move"); // 'move' | 'connect' | 'edit'
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

  // Initialize positions once canvas is available
  useEffect(() => {
    if (initializedRef.current) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      const scaled = scalePositions(DEFAULT_POS, rect.width, rect.height);
      setPositions(scaled);
      prevSizeRef.current = { w: rect.width, h: rect.height };
      initializedRef.current = true;
    }
  });

  useEffect(() => { drawGraph(); }, [drawGraph]);

  // Resize — rescale all node positions proportionally
  useEffect(() => {
    const resize = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const newW = rect.width, newH = rect.height;
      const { w: oldW, h: oldH } = prevSizeRef.current;
      if (oldW > 0 && oldH > 0 && (Math.abs(newW - oldW) > 5 || Math.abs(newH - oldH) > 5)) {
        setPositions(prev => {
          const scaled = {};
          for (const [node, [x, y]] of Object.entries(prev)) {
            scaled[node] = [
              Math.max(NODE_R, Math.min(newW - NODE_R, (x / oldW) * newW)),
              Math.max(NODE_R, Math.min(newH - NODE_R, (y / oldH) * newH)),
            ];
          }
          return scaled;
        });
        prevSizeRef.current = { w: newW, h: newH };
      }
      drawGraph();
    };
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

  // Helper: get pointer coords from mouse or touch event
  const getPointerXY = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return [clientX - rect.left, clientY - rect.top, rect];
  };

  const getPointerXYEnd = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const clientX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX;
    const clientY = e.changedTouches ? e.changedTouches[0].clientY : e.clientY;
    return [clientX - rect.left, clientY - rect.top, rect];
  };

  // Determine effective mode: on desktop, right-click forces connect, dblclick forces edit
  const getEffectiveMode = (e) => {
    if (e.button === 2) return 'connect';
    return touchMode;
  };

  const handlePointerDown = (e) => {
    if (running) return;
    if (e.touches) e.preventDefault(); // prevent scroll on touch
    const [x, y] = getPointerXY(e);
    const mode = getEffectiveMode(e);
    const node = nodeAtPoint(x, y);

    if (mode === 'connect') {
      if (node) {
        edgeRef.current = { node, startX: positions[node][0], startY: positions[node][1], endX: x, endY: y, line: true };
      }
      return;
    }

    if (mode === 'edit') {
      // Tap on node = remove, tap on empty = add
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
        const name = nextNodeName();
        setGraph(prev => ({ ...prev, [name]: [] }));
        setPositions(prev => ({ ...prev, [name]: [x, y] }));
        setStatusMsg(`Added node ${name}.`);
      }
      return;
    }

    // mode === 'move'
    if (node) {
      dragRef.current = { node, offsetX: positions[node][0] - x, offsetY: positions[node][1] - y };
    }
  };

  const handlePointerMove = (e) => {
    if (running) return;
    if (e.touches) e.preventDefault();
    const [x, y, rect] = getPointerXY(e);

    if (edgeRef.current?.line) {
      edgeRef.current.endX = x;
      edgeRef.current.endY = y;
      drawGraph();
      return;
    }

    if (dragRef.current) {
      const newX = Math.max(NODE_R, Math.min(rect.width - NODE_R, x + dragRef.current.offsetX));
      const newY = Math.max(NODE_R, Math.min(rect.height - NODE_R, y + dragRef.current.offsetY));
      const nodeToMove = dragRef.current.node;
      setPositions(prev => ({ ...prev, [nodeToMove]: [newX, newY] }));
    }
  };

  const handlePointerUp = (e) => {
    if (running) return;
    const [x, y] = getPointerXYEnd(e);

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

  // Keep double-click for desktop convenience
  const handleDblClick = (e) => {
    if (running) return;
    const [x, y] = getPointerXY(e);
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
      const name = nextNodeName();
      setGraph(prev => ({ ...prev, [name]: [] }));
      setPositions(prev => ({ ...prev, [name]: [x, y] }));
      setStatusMsg(`Added node ${name}.`);
    }
  };

  const handleContextMenu = (e) => e.preventDefault();

  const modeHints = {
    move: '✋ Drag nodes to reposition them',
    connect: '🔗 Drag between two nodes to connect/disconnect',
    edit: '✏️ Tap empty space to add · Tap node to remove',
  };

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
    traceRef.current = ucsTrace(graph, positions, startNode, goalNode);
    setRunning(true);
  };

  const loadSample = () => {
    if (running) return;
    setGraph(JSON.parse(JSON.stringify(DEFAULT_GRAPH)));
    const rect = canvasRef.current?.getBoundingClientRect();
    const w = rect?.width || 700, h = rect?.height || 400;
    setPositions(scalePositions(DEFAULT_POS, w, h));
    prevSizeRef.current = { w, h };
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
    prevSizeRef.current = { w, h };
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
        <Link href="/day2" className={styles.backLink}>← Day 2</Link>
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
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
            onDoubleClick={handleDblClick}
            onContextMenu={handleContextMenu}
          />
          <div className={styles.canvasLegend}>
            Frontier: blue · Path: gold · Drag nodes to see edge weights dynamically update!<br/>
            {modeHints[touchMode]}
          </div>
        </div>

        <div className={styles.panel}>
          {/* Interaction Mode */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Touch Mode</div>
            <div className={styles.modeRow}>
              {[{id:'move', label:'✋ Move', icon:'✋'}, {id:'connect', label:'🔗 Connect', icon:'🔗'}, {id:'edit', label:'✏️ Edit', icon:'✏️'}].map(m => (
                <button
                  key={m.id}
                  className={`${styles.modeBtn} ${touchMode === m.id ? styles.modeBtnActive : ''}`}
                  onClick={() => setTouchMode(m.id)}
                  disabled={running}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

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
