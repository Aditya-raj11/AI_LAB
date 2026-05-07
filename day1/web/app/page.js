import Link from "next/link";
import styles from "./page.module.css";

const days = [
  {
    day: 1,
    title: "Search Algorithm Visualizers",
    desc: "Interactive maze solving with BFS & DFS, and graph route finding using Bidirectional Search. Click, draw, and watch algorithms explore in real-time.",
    topics: ["BFS", "DFS", "Bidirectional Search", "Maze Generation"],
    icon: "🔍",
    gradient: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
    iconBg: "rgba(59, 130, 246, 0.15)",
    href: "/day1",
  },
  // Future days go here — just copy the object above and change the values!
  // {
  //   day: 2,
  //   title: "Heuristic Search",
  //   desc: "Best-First Search, A*, and UCS on grid environments.",
  //   topics: ["A*", "UCS", "Best-First", "Heuristics"],
  //   icon: "🧭",
  //   gradient: "linear-gradient(135deg, #22c55e, #06b6d4)",
  //   iconBg: "rgba(34, 197, 94, 0.15)",
  //   href: "/day2",
  // },
];

export default function Home() {
  return (
    <div className={styles.hero}>
      {/* ─── Navbar ─── */}
      <nav className={styles.navbar}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>AI</span>
          <span className={styles.logoText}>
            Lab <span className={styles.logoTextAccent}>Portfolio</span>
          </span>
        </Link>
        <ul className={styles.navLinks}>
          <li>
            <Link
              href="/"
              className={`${styles.navLink} ${styles.navLinkActive}`}
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link href="/day1" className={styles.navLink}>
              Day 1
            </Link>
          </li>
        </ul>
      </nav>

      {/* ─── Hero ─── */}
      <div className={styles.heroContent}>
        <div className={styles.badge}>
          <span className={styles.badgeDot}></span>
          AI Lab Assignments
        </div>
        <h1 className={styles.heroTitle}>
          Algorithm{" "}
          <span className={styles.heroTitleGradient}>Visualizers</span>
        </h1>
        <p className={styles.heroSubtitle}>
          Explore search algorithms through beautiful, interactive
          visualizations. Click into any day below to see the algorithms in
          action.
        </p>
      </div>

      {/* ─── Day Cards ─── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Lab Sessions</h2>
        <div className={styles.cardGrid}>
          {days.map((d, i) => (
            <Link
              key={d.day}
              href={d.href}
              className={styles.dayCard}
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div
                className={styles.dayCardGlow}
                style={{ background: d.gradient }}
              />
              <div className={styles.dayCardHeader}>
                <div
                  className={styles.dayCardIcon}
                  style={{ background: d.iconBg }}
                >
                  {d.icon}
                </div>
                <div>
                  <div className={styles.dayCardNumber}>Day {d.day}</div>
                  <div className={styles.dayCardTitle}>{d.title}</div>
                </div>
              </div>
              <p className={styles.dayCardDesc}>{d.desc}</p>
              <div className={styles.dayCardTopics}>
                {d.topics.map((t) => (
                  <span key={t} className={styles.topic}>
                    {t}
                  </span>
                ))}
              </div>
              <span className={styles.dayCardArrow}>→</span>
            </Link>
          ))}
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className={styles.footer}>
        AI Lab Portfolio · Built with Next.js
      </footer>
    </div>
  );
}
