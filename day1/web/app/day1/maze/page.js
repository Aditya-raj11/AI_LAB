"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import styles from "./maze.module.css";

/* ═══════════════════════════════════════════
   MAZE SOLVER ALGORITHM (ported from Python)
   ═══════════════════════════════════════════ */
function getNeighbors(maze, r, c) {
  const rows = maze.length, cols = maze[0].length;
  const result = [];
  for (const [dr, dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && maze[nr][nc] === 0)
      result.push([nr, nc]);
  }
  return result;
}

function* searchTrace(maze, start, goal, algorithm) {
  const key = (r,c) => `${r},${c}`;
  const useQueue = algorithm === "BFS";

  if (key(...start) === key(...goal)) {
    yield { event:"solution", step:0, current:start, visited:new Set([key(...start)]),
            frontier:[], path:[start], message:"Start equals goal." };
    return;
  }

  const frontier = [[start, [start]]];
  const discovered = new Set([key(...start)]);
  const visited = new Set();
  let step = 0;

  yield { event:"start", step, current:start, visited:new Set(), frontier:[start],
          path:[start], message:`▶  ${algorithm} initialised — exploring from (${start})` };

  while (frontier.length) {
    const [node, path] = useQueue ? frontier.shift() : frontier.pop();
    const nk = key(...node);
    visited.add(nk);
    step++;

    yield { event:"visit", step, current:node, visited:new Set(visited),
            frontier:frontier.map(f=>f[0]), path, message:`Step ${step}: visiting (${node})` };

    if (key(...node) === key(...goal)) {
      yield { event:"solution", step, current:node, visited:new Set(visited),
              frontier:frontier.map(f=>f[0]), path,
              message:`✓  Goal reached in ${step} steps — path length ${path.length}` };
      return;
    }

    for (const neigh of getNeighbors(maze, ...node)) {
      const neighKey = key(...neigh);
      if (!discovered.has(neighKey)) {
        discovered.add(neighKey);
        frontier.push([neigh, [...path, neigh]]);
        yield { event:"enqueue", step, current:node, visited:new Set(visited),
                frontier:frontier.map(f=>f[0]), path:[...path, neigh],
                message:`  ↳ queued (${neigh})` };
      }
    }
  }

  yield { event:"no_path", step, current:null, visited:new Set(visited),
          frontier:[], path:[], message:"✗  No path exists between start and goal." };
}

/* ═══════════════════════════════════════════
   MAZE GENERATION (recursive backtracker)
   ═══════════════════════════════════════════ */
function generateTreeMaze(rows, cols) {
  const maze = Array.from({length: rows}, () => Array(cols).fill(1));
  const start = [0, 0];
  const goal = [rows - 1, cols - 1];

  function carve(r, c) {
    maze[r][c] = 0;
    const dirs = [[0,2],[0,-2],[2,0],[-2,0]];
    for (let i = dirs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [dirs[i], dirs[j]] = [dirs[j], dirs[i]];
    }
    for (const [dr, dc] of dirs) {
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && maze[nr][nc] === 1) {
        maze[r + dr/2][c + dc/2] = 0;
        carve(nr, nc);
      }
    }
  }

  carve(0, 0);
  maze[goal[0]][goal[1]] = 0;
  return { maze, start, goal };
}

/* ═══════════════════════════════════════════
   DEFAULT MAZE
   ═══════════════════════════════════════════ */
const DEFAULT_MAZE = [
  [0,1,0,0,0],
  [0,1,0,1,0],
  [0,0,0,1,0],
  [1,1,0,0,0],
  [0,0,0,1,0],
];

/* ═══════════════════════════════════════════
   LEGEND DATA
   ═══════════════════════════════════════════ */
const legendItems = [
  { color: "#2563eb", label: "Start" },
  { color: "#dc2626", label: "Goal" },
  { color: "#0d1117", label: "Wall" },
  { color: "#1c2d4a", label: "Visited" },
  { color: "#1e3a5f", label: "Frontier" },
  { color: "#d97706", label: "Current" },
  { color: "#16a34a", label: "Solution" },
];

/* ═══════════════════════════════════════════
   COMPONENT
   ═══════════════════════════════════════════ */
export default function MazePage() {
  const [maze, setMaze] = useState(DEFAULT_MAZE.map(r => [...r]));
  const [start, setStart] = useState([0, 0]);
  const [goal, setGoal] = useState([4, 4]);
  const [placementMode, setPlacementMode] = useState(null); // null | 'start' | 'goal'
  const [algorithm, setAlgorithm] = useState("BFS");
  const [speed, setSpeed] = useState(200);
  const [running, setRunning] = useState(false);
  const [visited, setVisited] = useState(new Set());
  const [frontier, setFrontier] = useState([]);
  const [currentCell, setCurrentCell] = useState(null);
  const [finalPath, setFinalPath] = useState([]);
  const [stepCount, setStepCount] = useState(0);
  const [statusMsg, setStatusMsg] = useState("Ready");
  const [statusColor, setStatusColor] = useState("#22c55e");
  const [logs, setLogs] = useState([]);

  const traceRef = useRef(null);
  const timerRef = useRef(null);
  const logBoxRef = useRef(null);

  const key = (r,c) => `${r},${c}`;

  const cellClass = useCallback((r, c) => {
    const k = key(r, c);
    if (r === start[0] && c === start[1]) return styles.cellStart;
    if (r === goal[0] && c === goal[1]) return styles.cellGoal;
    if (maze[r][c] === 1) return styles.cellWall;
    if (finalPath.some(([pr,pc]) => pr===r && pc===c)) return styles.cellSolution;
    if (currentCell && currentCell[0]===r && currentCell[1]===c) return styles.cellCurrent;
    if (frontier.some(([fr,fc]) => fr===r && fc===c)) return styles.cellFrontier;
    if (visited.has(k)) return styles.cellVisited;
    return styles.cellOpen;
  }, [maze, start, goal, visited, frontier, currentCell, finalPath]);

  const resetState = useCallback(() => {
    setVisited(new Set());
    setFrontier([]);
    setCurrentCell(null);
    setFinalPath([]);
    setStepCount(0);
    setLogs([]);
    setStatusMsg("Ready");
    setStatusColor("#22c55e");
    if (timerRef.current) clearTimeout(timerRef.current);
    traceRef.current = null;
  }, []);

  const toggleWall = useCallback((r, c) => {
    if (running) return;

    // Placement mode: set start or goal
    if (placementMode === 'start') {
      if (maze[r][c] === 1) return; // can't place on a wall
      setStart([r, c]);
      setPlacementMode(null);
      resetState();
      return;
    }
    if (placementMode === 'goal') {
      if (maze[r][c] === 1) return;
      setGoal([r, c]);
      setPlacementMode(null);
      resetState();
      return;
    }

    // Normal mode: toggle wall (but not on start/goal)
    if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) return;
    setMaze(prev => {
      const copy = prev.map(row => [...row]);
      copy[r][c] ^= 1;
      return copy;
    });
    resetState();
  }, [running, start, goal, maze, placementMode, resetState]);

  const advance = useCallback(() => {
    if (!traceRef.current) return;
    const result = traceRef.current.next();
    if (result.done) {
      setRunning(false);
      return;
    }
    const s = result.value;
    setCurrentCell(s.current);
    setVisited(new Set(s.visited));
    setFrontier(s.frontier || []);
    setStepCount(s.step);
    setStatusMsg(s.message);
    setLogs(prev => [...prev, { event: s.event, message: s.message }]);

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

  // Run loop
  useEffect(() => {
    if (!running) return;
    const tick = () => {
      advance();
      timerRef.current = setTimeout(tick, speed);
    };
    timerRef.current = setTimeout(tick, speed);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [running, speed, advance]);

  // Auto-scroll log
  useEffect(() => {
    if (logBoxRef.current) logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight;
  }, [logs]);

  const startSearch = () => {
    if (running) return;
    resetState();
    traceRef.current = searchTrace(maze, start, goal, algorithm);
    setRunning(true);
    setStatusMsg("Searching…");
    setStatusColor("#f59e0b");
  };

  const loadSample = () => {
    if (running) return;
    setMaze(DEFAULT_MAZE.map(r => [...r]));
    setStart([0, 0]);
    setGoal([4, 4]);
    setPlacementMode(null);
    resetState();
    setStatusMsg("Sample maze loaded");
  };

  const clearMaze = () => {
    if (running) return;
    const rows = maze.length, cols = maze[0].length;
    setMaze(maze.map(r => r.map(() => 0)));
    setStart([0, 0]);
    setGoal([rows - 1, cols - 1]);
    setPlacementMode(null);
    resetState();
    setStatusMsg("Maze cleared — click to add walls");
  };

  const genMaze = () => {
    if (running) return;
    const rows = 9, cols = 13;
    const { maze: m } = generateTreeMaze(rows, cols);
    setMaze(m);
    setStart([0, 0]);
    setGoal([rows - 1, cols - 1]);
    setPlacementMode(null);
    resetState();
    setStatusMsg("Tree maze generated!");
  };

  const logClass = (ev) => {
    if (ev === "solution") return styles.logSolution;
    if (ev === "visit") return styles.logVisit;
    if (ev === "no_path") return styles.logNoPath;
    if (ev === "enqueue") return styles.logEnqueue;
    if (ev === "start") return styles.logStart;
    return "";
  };

  const rows = maze.length;
  const cols = maze[0].length;

  return (
    <div className={styles.page}>
      {/* Navbar */}
      <nav className={styles.navbar}>
        <Link href="/day1" className={styles.backLink}>← Day 1</Link>
        <span className={styles.pageTitle}>
          Maze <span className={styles.pageTitleAccent}>Pathfinder</span>
        </span>
        <div />
      </nav>

      <div className={styles.body}>
        {/* Canvas Area */}
        <div className={styles.canvasArea}>
          <div className={styles.grid} style={{ gridTemplateColumns: `repeat(${cols}, var(--cell-size))` }}>
            {maze.map((row, r) =>
              row.map((_, c) => (
                <div
                  key={key(r, c)}
                  className={`${styles.cell} ${cellClass(r, c)}`}
                  onClick={() => toggleWall(r, c)}
                >
                  {maze[r][c] === 1 ? "w" : `${r},${c}`}
                  {finalPath.some(([pr,pc]) => pr===r && pc===c) &&
                   !(r===start[0]&&c===start[1]) && !(r===goal[0]&&c===goal[1]) &&
                    <span className={styles.cellDot} />
                  }
                </div>
              ))
            )}
          </div>

          <div className={styles.legend}>
            {legendItems.map(({ color, label }) => (
              <div key={label} className={styles.legendItem}>
                <span className={styles.legendChip} style={{ background: color }} />
                {label}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel */}
        <div className={styles.panel}>
          {/* Start / Goal Placement */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Start &amp; Goal</div>
            <div className={styles.algRow}>
              <button
                className={`${styles.algBtn} ${placementMode === 'start' ? styles.algBtnActive : ''}`}
                onClick={() => !running && setPlacementMode(placementMode === 'start' ? null : 'start')}
                disabled={running}
              >
                📍 Set Start ({start[0]},{start[1]})
              </button>
              <button
                className={`${styles.algBtn} ${placementMode === 'goal' ? styles.algBtnActive : ''}`}
                onClick={() => !running && setPlacementMode(placementMode === 'goal' ? null : 'goal')}
                disabled={running}
              >
                🎯 Set Goal ({goal[0]},{goal[1]})
              </button>
            </div>
            {placementMode && (
              <div className={styles.statusBar} style={{marginTop:'6px'}}>
                <span className={styles.statusDot} style={{ background: placementMode === 'start' ? '#2563eb' : '#dc2626' }} />
                <span className={styles.statusText}>Click a cell to place {placementMode}</span>
              </div>
            )}
          </div>

          {/* Algorithm */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Algorithm</div>
            <div className={styles.algRow}>
              {["BFS", "DFS"].map(a => (
                <button
                  key={a}
                  className={`${styles.algBtn} ${algorithm === a ? styles.algBtnActive : ""}`}
                  onClick={() => !running && setAlgorithm(a)}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          {/* Speed */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Speed</div>
            <div className={styles.speedRow}>
              <span className={styles.speedLabel}>Fast</span>
              <input
                type="range"
                min={30}
                max={600}
                value={speed}
                onChange={e => setSpeed(Number(e.target.value))}
                className={styles.speedSlider}
              />
              <span className={styles.speedLabel}>Slow</span>
            </div>
          </div>

          {/* Actions */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Actions</div>
            <button className={`${styles.actionBtn} ${styles.primaryBtn}`} onClick={startSearch} disabled={running}>
              {running ? "⏸ Running…" : "▶ Run Search"}
            </button>
            <button className={`${styles.actionBtn} ${styles.successBtn}`} onClick={genMaze} disabled={running}>
              🌲 Generate Tree Maze
            </button>
            <button className={`${styles.actionBtn} ${styles.secondaryBtn}`} onClick={loadSample} disabled={running}>
              ↺ Sample Maze
            </button>
            <button className={`${styles.actionBtn} ${styles.secondaryBtn}`} onClick={clearMaze} disabled={running}>
              ✕ Clear Maze
            </button>
          </div>

          {/* Stats */}
          <div className={styles.panelSection}>
            <div className={styles.sectionLabel}>Statistics</div>
            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>⚡ Steps</div>
                <div className={styles.statValue}>{stepCount}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>👁 Visited</div>
                <div className={styles.statValue}>{visited.size}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>🔮 Frontier</div>
                <div className={styles.statValue}>{frontier.length}</div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statLabel}>📍 Path</div>
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
              {logs.map((l, i) => (
                <div key={i} className={`${styles.logEntry} ${logClass(l.event)}`}>
                  {l.message}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
