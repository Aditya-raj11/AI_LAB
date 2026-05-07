import "./globals.css";

export const metadata = {
  title: "AI Lab Portfolio — Search Algorithm Visualizers",
  description:
    "Interactive visualizations of BFS, DFS, and Bidirectional Search algorithms built for AI Lab coursework.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
