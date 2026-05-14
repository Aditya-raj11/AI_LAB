import Link from "next/link";
import styles from "./day1.module.css";

export const metadata = {
  title: "Day 2 — Heuristic & Cost Search | AI Lab",
  description: "Maze Solver and Route Finder visualizers using Greedy Best-First Search and Uniform Cost Search.",
};

export default function Day2Page() {
  return (
    <div className={styles.container}>
      <nav className={styles.navbar}>
        <Link href="/" className={styles.backLink}>
          ← Back to Dashboard
        </Link>
        <span className={styles.dayTitle}>
          Day 2 — <span className={styles.dayTitleAccent}>Heuristic & Cost Search</span>
        </span>
        <div />
      </nav>

      <main className={styles.content}>
        <div className={styles.header}>
          <div className={styles.headerBadge}>📅 Day 2</div>
          <h1 className={styles.headerTitle}>Advanced Search Visualizers</h1>
          <p className={styles.headerDesc}>
            Explore how search algorithms navigate through mazes and graphs.
            Choose a visualizer below to start experimenting.
          </p>
        </div>

        <div className={styles.toolGrid}>
          {/* Maze Solver Card */}
          <Link href="/day2/maze" className={styles.toolCard}>
            <div className={styles.toolCardGlow} style={{ background: "var(--gradient-accent)" }} />
            <div className={styles.toolCardIcon} style={{ background: "rgba(59, 130, 246, 0.12)" }}>
              🧩
            </div>
            <h2 className={styles.toolCardTitle}>Maze Solver (GBFS)</h2>
            <p className={styles.toolCardDesc}>
              Watch Greedy Best-First Search explore a maze cell-by-cell using the Manhattan Distance heuristic to prioritize cells closest to the goal.
            </p>
            <div className={styles.toolCardFeatures}>
              {["Greedy Best-First Search", "Manhattan Heuristic", "Maze Generation", "Interactive Grid"].map((f) => (
                <span key={f} className={styles.feature}>{f}</span>
              ))}
            </div>
            <span className={styles.toolCardBtn} style={{ background: "var(--accent-glow)" }}>
              Open Visualizer →
            </span>
          </Link>

          {/* Route Finder Card */}
          <Link href="/day2/route" className={styles.toolCard} style={{ animationDelay: "0.1s" }}>
            <div className={styles.toolCardGlow} style={{ background: "var(--gradient-success)" }} />
            <div className={styles.toolCardIcon} style={{ background: "rgba(34, 197, 94, 0.12)" }}>
              🗺️
            </div>
            <h2 className={styles.toolCardTitle}>Route Finder (UCS)</h2>
            <p className={styles.toolCardDesc}>
              Visualize Uniform Cost Search finding routes on a graph. Edge weights are dynamically calculated based on the physical distance between nodes!
            </p>
            <div className={styles.toolCardFeatures}>
              {["Uniform Cost Search", "Dynamic Edge Weights", "Interactive Graph", "Add/Remove Nodes", "Drag Connections"].map((f) => (
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
