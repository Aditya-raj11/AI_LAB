import Link from "next/link";
import styles from "./day1.module.css";

export const metadata = {
  title: "Day 1 — Search Algorithms | AI Lab",
  description: "Maze Solver and Route Finder visualizers using BFS, DFS, and Bidirectional Search.",
};

export default function Day1Page() {
  return (
    <div className={styles.container}>
      <nav className={styles.navbar}>
        <Link href="/" className={styles.backLink}>
          ← Back to Dashboard
        </Link>
        <span className={styles.dayTitle}>
          Day 1 — <span className={styles.dayTitleAccent}>Search Algorithms</span>
        </span>
        <div />
      </nav>

      <main className={styles.content}>
        <div className={styles.header}>
          <div className={styles.headerBadge}>📅 Day 1</div>
          <h1 className={styles.headerTitle}>Search Algorithm Visualizers</h1>
          <p className={styles.headerDesc}>
            Explore how search algorithms navigate through mazes and graphs.
            Choose a visualizer below to start experimenting.
          </p>
        </div>

        <div className={styles.toolGrid}>
          {/* Maze Solver Card */}
          <Link href="/day1/maze" className={styles.toolCard}>
            <div className={styles.toolCardGlow} style={{ background: "var(--gradient-accent)" }} />
            <div className={styles.toolCardIcon} style={{ background: "rgba(59, 130, 246, 0.12)" }}>
              🧩
            </div>
            <h2 className={styles.toolCardTitle}>Maze Solver</h2>
            <p className={styles.toolCardDesc}>
              Watch BFS and DFS algorithms explore a maze cell-by-cell. Click to
              toggle walls, generate random mazes, and compare search strategies.
            </p>
            <div className={styles.toolCardFeatures}>
              {["BFS", "DFS", "Maze Generation", "Step-by-Step Animation", "Interactive Grid"].map((f) => (
                <span key={f} className={styles.feature}>{f}</span>
              ))}
            </div>
            <span className={styles.toolCardBtn} style={{ background: "var(--accent-glow)" }}>
              Open Visualizer →
            </span>
          </Link>

          {/* Route Finder Card */}
          <Link href="/day1/route" className={styles.toolCard} style={{ animationDelay: "0.1s" }}>
            <div className={styles.toolCardGlow} style={{ background: "var(--gradient-success)" }} />
            <div className={styles.toolCardIcon} style={{ background: "rgba(34, 197, 94, 0.12)" }}>
              🗺️
            </div>
            <h2 className={styles.toolCardTitle}>Route Finder</h2>
            <p className={styles.toolCardDesc}>
              Visualize Bidirectional Search finding routes on a graph. Create
              nodes, draw connections, and see two search waves meet in the middle.
            </p>
            <div className={styles.toolCardFeatures}>
              {["Bidirectional BFS", "Interactive Graph", "Add/Remove Nodes", "Drag Connections", "Random Graphs"].map((f) => (
                <span key={f} className={styles.feature}>{f}</span>
              ))}
            </div>
            <span className={styles.toolCardBtn} style={{ background: "var(--success-glow)" }}>
              Open Visualizer →
            </span>
          </Link>
        </div>
      </main>
    </div>
  );
}
