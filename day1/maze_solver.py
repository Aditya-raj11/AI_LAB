from collections import deque
import tkinter as tk
from tkinter import font as tkfont
import math


# ─────────────────────────────────────────────
#  PALETTE
# ─────────────────────────────────────────────
BG          = "#0d1117"
SURFACE     = "#161b22"
SURFACE2    = "#21262d"
BORDER      = "#30363d"
TEXT        = "#f0f6fc"
TEXT_MUTED  = "#8b949e"
ACCENT      = "#58a6ff"
ACCENT_GLOW = "#1f6feb"
SUCCESS     = "#3fb950"
WARN        = "#d29922"
DANGER      = "#f85149"
PURPLE      = "#bc8cff"

CELL_WALL     = "#0d1117"
CELL_OPEN     = "#21262d"
CELL_VISITED  = "#1c2d3f"
CELL_FRONTIER = "#1a3a5c"
CELL_CURRENT  = "#d29922"
CELL_PATH     = "#0a3d1f"
CELL_SOLUTION = "#3fb950"
CELL_START    = "#1f6feb"
CELL_GOAL     = "#b91c1c"

CELL_TEXT_DARK  = "#0d1117"
CELL_TEXT_LIGHT = "#8b949e"


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    """Draw a rounded rectangle on a Canvas."""
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=38,
                 bg=ACCENT_GLOW, fg=TEXT, hover_bg=ACCENT,
                 radius=10, font_size=10, bold=True, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=SURFACE, highlightthickness=0, **kwargs)
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._text = text
        self._command = command
        self._radius = radius
        self._btn_w = width
        self._btn_h = height
        self._font = tkfont.Font(family="Segoe UI", size=font_size,
                                  weight="bold" if bold else "normal")
        self._rect = None
        self._label = None
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, bg=None):
        self.delete("all")
        color = bg or self._bg
        self._rect = rounded_rect(self, 2, 2, self._btn_w - 2, self._btn_h - 2,
                                   radius=self._radius, fill=color, outline="")
        self._label = self.create_text(
            self._btn_w // 2, self._btn_h // 2,
            text=self._text, fill=self._fg, font=self._font
        )

    def _on_enter(self, _):
        self._draw(self._hover_bg)
        self.configure(cursor="hand2")

    def _on_leave(self, _):
        self._draw(self._bg)

    def _on_click(self, _):
        self._draw(lerp_color(self._hover_bg, "#000000", 0.25))

    def _on_release(self, _):
        self._draw(self._hover_bg)
        if self._command:
            self._command()

    def set_text(self, text):
        self._text = text
        self._draw()


class StatCard(tk.Frame):
    def __init__(self, parent, label, variable, icon="", **kwargs):
        super().__init__(parent, bg=SURFACE2, **kwargs)
        self.configure(padx=14, pady=10)

        top = tk.Frame(self, bg=SURFACE2)
        top.pack(fill="x")

        tk.Label(top, text=icon + "  " + label if icon else label,
                 bg=SURFACE2, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        self._val_label = tk.Label(self, textvariable=variable,
                                   bg=SURFACE2, fg=TEXT,
                                   font=("Segoe UI", 16, "bold"))
        self._val_label.pack(anchor="w", pady=(2, 0))

    def flash(self, color=ACCENT):
        orig = self._val_label.cget("fg")
        self._val_label.configure(fg=color)
        self.after(400, lambda: self._val_label.configure(fg=orig))


class SectionHeader(tk.Frame):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        tk.Label(self, text=text, bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        sep = tk.Canvas(self, height=1, bg=BORDER, highlightthickness=0)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=(6, 0))


class SpeedSlider(tk.Frame):
    def __init__(self, parent, label="Speed", from_=50, to=800,
                 default=260, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        tk.Label(self, text=label, bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        row = tk.Frame(self, bg=SURFACE)
        row.pack(fill="x", pady=(4, 0))
        tk.Label(row, text="Fast", bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 7)).pack(side="left")
        self.var = tk.IntVar(value=default)
        self._slider = tk.Scale(
            row, from_=from_, to=to, orient="horizontal",
            variable=self.var, showvalue=False,
            bg=SURFACE, fg=TEXT_MUTED,
            troughcolor=SURFACE2, activebackground=ACCENT,
            highlightthickness=0, bd=0, sliderrelief="flat",
        )
        self._slider.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(row, text="Slow", bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 7)).pack(side="right")

    @property
    def value(self):
        return self.var.get()


# ─────────────────────────────────────────────
#  SOLVER CORE
# ─────────────────────────────────────────────
class MazeSolver:
    def __init__(self, maze, start, goal):
        self.maze = maze
        self.start = start
        self.goal = goal

    def get_neighbors(self, r, c):
        result = []
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(self.maze) and 0 <= nc < len(self.maze[0]):
                if self.maze[nr][nc] == 0:
                    result.append((nr, nc))
        return result

    def search_trace(self, algorithm):
        algorithm = algorithm.upper()
        use_queue = algorithm == "BFS"

        if self.start == self.goal:
            yield {"event": "solution", "step": 0, "current": self.start,
                   "visited": {self.start}, "frontier": [],
                   "path": [self.start], "message": "Start equals goal."}
            return

        frontier = deque([(self.start, [self.start])]) if use_queue else [(self.start, [self.start])]
        discovered = {self.start}
        visited = set()
        step = 0

        yield {"event": "start", "step": step, "current": self.start,
               "visited": set(), "frontier": [self.start],
               "path": [self.start],
               "message": f"▶  {algorithm} initialised — exploring from {self.start}"}

        while frontier:
            node, path = frontier.popleft() if use_queue else frontier.pop()
            visited.add(node)
            step += 1

            yield {"event": "visit", "step": step, "current": node,
                   "visited": set(visited), "frontier": [i[0] for i in frontier],
                   "path": path, "message": f"Step {step}: visiting {node}"}

            if node == self.goal:
                yield {"event": "solution", "step": step, "current": node,
                       "visited": set(visited), "frontier": [i[0] for i in frontier],
                       "path": path,
                       "message": f"✓  Goal reached in {step} steps — path length {len(path)}"}
                return

            for neigh in self.get_neighbors(*node):
                if neigh not in discovered:
                    discovered.add(neigh)
                    frontier.append((neigh, path + [neigh]))
                    yield {"event": "enqueue", "step": step, "current": node,
                           "visited": set(visited), "frontier": [i[0] for i in frontier],
                           "path": path + [neigh],
                           "message": f"  ↳ queued {neigh}"}

        yield {"event": "no_path", "step": step, "current": None,
               "visited": set(visited), "frontier": [], "path": [],
               "message": "✗  No path exists between start and goal."}


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class MazeSolverApp:
    CELL  = 60
    GAP   = 3
    R     = 8      # cell corner radius

    def __init__(self, root):
        self.root = root
        self.root.title("Maze Pathfinder  ·  BFS / DFS Visualizer")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 680)
        self.root.configure(bg=BG)

        self.maze = self._default_maze()
        self.start = (0, 0)
        self.goal  = (4, 4)

        self.algorithm_var = tk.StringVar(value="BFS")
        self.status_var    = tk.StringVar(value="Ready")
        self.step_var      = tk.StringVar(value="0")
        self.visited_var   = tk.StringVar(value="0")
        self.frontier_var  = tk.StringVar(value="0")
        self.path_var      = tk.StringVar(value="—")

        self.running      = False
        self.trace        = None
        self.visited      = set()
        self.frontier     = []
        self.active_path  = []
        self.final_path   = []
        self.current_cell = None
        self._pulse_step  = 0

        self._build_ui()
        self._draw_maze()
        self._start_pulse()

    # ── default maze ──────────────────────────
    def _default_maze(self):
        return [
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0],
        ]

    # ── UI BUILD ──────────────────────────────
    def _build_ui(self):
        # ── header ──────────────────────────
        header = tk.Frame(self.root, bg=SURFACE, pady=0)
        header.pack(fill="x")

        accent_bar = tk.Canvas(header, height=3, bg=ACCENT_GLOW,
                               highlightthickness=0)
        accent_bar.pack(fill="x")

        inner_h = tk.Frame(header, bg=SURFACE, padx=28, pady=18)
        inner_h.pack(fill="x")

        tk.Label(inner_h, text="MAZE  PATHFINDER", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(side="left")

        badge = tk.Frame(inner_h, bg=ACCENT_GLOW, padx=10, pady=4)
        badge.pack(side="left", padx=14)
        tk.Label(badge, text="BFS · DFS", bg=ACCENT_GLOW, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack()

        tk.Label(inner_h, text="Click cells to toggle walls  ·  Pick algorithm  ·  Run",
                 bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(side="right")

        # ── body ────────────────────────────
        body = tk.Frame(self.root, bg=BG, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # LEFT: canvas
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        canvas_card = tk.Frame(left, bg=SURFACE, padx=2, pady=2)
        canvas_card.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_card, bg=BG,
                                highlightthickness=0)
        self.canvas.pack(padx=16, pady=16)
        self.canvas.bind("<Button-1>", self._on_click)

        # legend
        self._build_legend(left)

        # RIGHT: panel
        right = tk.PanedWindow(body, orient="vertical", bg=BG, bd=0, sashwidth=8, sashcursor="sb_v_double_arrow", width=270)
        right.pack(side="right", fill="y", padx=(18, 0))

        controls_wrapper = tk.Frame(right, bg=SURFACE)
        right.add(controls_wrapper, stretch="never")

        controls_canvas = tk.Canvas(controls_wrapper, bg=SURFACE, highlightthickness=0)
        controls_scrollbar = tk.Scrollbar(controls_wrapper, orient="vertical", command=controls_canvas.yview, bg=SURFACE, troughcolor=SURFACE2, activebackground=BORDER, relief="flat", width=8)
        controls_panel = tk.Frame(controls_canvas, bg=SURFACE, padx=18, pady=10)
        
        controls_panel.bind(
            "<Configure>",
            lambda e: controls_canvas.configure(
                scrollregion=controls_canvas.bbox("all")
            )
        )
        
        controls_canvas_window = controls_canvas.create_window((0, 0), window=controls_panel, anchor="nw")
        controls_canvas.bind("<Configure>", lambda e: controls_canvas.itemconfig(controls_canvas_window, width=e.width))
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        
        controls_canvas.pack(side="left", fill="both", expand=True)
        controls_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            if controls_canvas.yview() != (0.0, 1.0):
                controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
        controls_wrapper.bind("<Enter>", lambda e: controls_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        controls_wrapper.bind("<Leave>", lambda e: controls_canvas.unbind_all("<MouseWheel>"))

        log_panel = tk.Frame(right, bg=SURFACE, padx=18, pady=10)
        right.add(log_panel, stretch="always")

        # Algorithm selector
        SectionHeader(controls_panel, "Algorithm").pack(fill="x", pady=(0, 5))

        alg_row = tk.Frame(controls_panel, bg=SURFACE)
        alg_row.pack(fill="x", pady=(0, 8))

        self._bfs_btn = self._alg_button(alg_row, "BFS", "BFS")
        self._bfs_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self._dfs_btn = self._alg_button(alg_row, "DFS", "DFS")
        self._dfs_btn.pack(side="left", fill="x", expand=True)

        self._update_alg_buttons()

        # Speed
        self.speed = SpeedSlider(controls_panel, "Animation Speed")
        self.speed.pack(fill="x", pady=(0, 10))

        # Action buttons
        SectionHeader(controls_panel, "Actions").pack(fill="x", pady=(0, 5))

        self.run_btn = RoundedButton(controls_panel, "▶  Run Search",
                                     command=self._start_search,
                                     width=234, height=38,
                                     bg=ACCENT_GLOW, hover_bg=ACCENT,
                                     font_size=11)
        self.run_btn.pack(fill="x", pady=(0, 6))

        RoundedButton(controls_panel, "🌲 Generate Tree Maze",
                      command=self._generate_maze,
                      width=234, height=32,
                      bg=SURFACE2, hover_bg=BORDER, fg=SUCCESS,
                      font_size=10).pack(fill="x", pady=(0, 4))

        RoundedButton(controls_panel, "↺  Sample Maze",
                      command=self._load_sample,
                      width=234, height=32,
                      bg=SURFACE2, hover_bg=BORDER, fg=TEXT,
                      font_size=10).pack(fill="x", pady=(0, 4))

        RoundedButton(controls_panel, "✕  Clear Maze",
                      command=self._clear_maze,
                      width=234, height=32,
                      bg=SURFACE2, hover_bg=BORDER, fg=TEXT,
                      font_size=10).pack(fill="x", pady=(0, 10))

        # Stats
        SectionHeader(controls_panel, "Statistics").pack(fill="x", pady=(0, 5))

        stats_grid = tk.Frame(controls_panel, bg=SURFACE)
        stats_grid.pack(fill="x")
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        self._step_card     = self._stat(stats_grid, "STEPS", self.step_var, "⚡", 0, 0)
        self._visited_card  = self._stat(stats_grid, "VISITED", self.visited_var, "👁", 0, 1)
        self._frontier_card = self._stat(stats_grid, "FRONTIER", self.frontier_var, "🔮", 1, 0)
        self._path_card     = self._stat(stats_grid, "PATH LEN", self.path_var, "📍", 1, 1)

        # Status bar
        status_frame = tk.Frame(controls_panel, bg=SURFACE2, padx=12, pady=8)
        status_frame.pack(fill="x", pady=(8, 0))

        self._status_dot = tk.Canvas(status_frame, width=10, height=10,
                                      bg=SURFACE2, highlightthickness=0)
        self._status_dot.pack(side="left", padx=(0, 8))
        self._dot_oval = self._status_dot.create_oval(1, 1, 9, 9,
                                                       fill=SUCCESS, outline="")

        tk.Label(status_frame, textvariable=self.status_var,
                 bg=SURFACE2, fg=TEXT_MUTED,
                 font=("Segoe UI", 9), wraplength=190,
                 justify="left").pack(side="left", fill="x", expand=True)

        # Log
        SectionHeader(log_panel, "Search Log").pack(fill="x", pady=(0, 4))

        log_frame = tk.Frame(log_panel, bg=SURFACE2)
        log_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(log_frame, bg=SURFACE2, troughcolor=SURFACE2,
                          activebackground=BORDER, relief="flat", width=8)
        sb.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_frame, wrap="word",
            bg=SURFACE2, fg=TEXT,
            insertbackground=TEXT, relief="flat",
            font=("Cascadia Code", 9) if self._font_exists("Cascadia Code")
                 else ("Courier New", 9),
            padx=10, pady=10, spacing1=2,
            yscrollcommand=sb.set
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        sb.config(command=self.log_text.yview)
        self.log_text.configure(state="disabled")

        # Tag colours for log
        self.log_text.tag_configure("solution", foreground=SUCCESS)
        self.log_text.tag_configure("visit",    foreground=ACCENT)
        self.log_text.tag_configure("no_path",  foreground=DANGER)
        self.log_text.tag_configure("enqueue",  foreground=TEXT_MUTED)
        self.log_text.tag_configure("start",    foreground=PURPLE)

    def _font_exists(self, name):
        try:
            tkfont.Font(family=name, size=9)
            return name in tkfont.families()
        except Exception:
            return False

    def _alg_button(self, parent, text, value):
        btn = tk.Label(parent, text=text, bg=SURFACE2, fg=TEXT_MUTED,
                       font=("Segoe UI", 11, "bold"),
                       padx=10, pady=8, cursor="hand2")
        btn.bind("<Button-1>", lambda _: self._set_alg(value))
        btn.bind("<Enter>",    lambda _, b=btn: b.configure(fg=TEXT) if self.algorithm_var.get() != value else None)
        btn.bind("<Leave>",    lambda _, b=btn, v=value: self._update_alg_buttons())
        return btn

    def _set_alg(self, value):
        self.algorithm_var.set(value)
        self._update_alg_buttons()

    def _update_alg_buttons(self):
        alg = self.algorithm_var.get()
        for btn, val in ((self._bfs_btn, "BFS"), (self._dfs_btn, "DFS")):
            if val == alg:
                btn.configure(bg=ACCENT_GLOW, fg=TEXT)
            else:
                btn.configure(bg=SURFACE2, fg=TEXT_MUTED)

    def _stat(self, parent, label, var, icon, row, col):
        card = StatCard(parent, label, var, icon)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
        return card

    def _build_legend(self, parent):
        leg = tk.Frame(parent, bg=BG, pady=10)
        leg.pack(fill="x")

        items = [
            (CELL_START,    "Start"),
            (CELL_GOAL,     "Goal"),
            (CELL_WALL,     "Wall"),
            (CELL_VISITED,  "Visited"),
            (CELL_FRONTIER, "Frontier"),
            (CELL_CURRENT,  "Current"),
            (CELL_SOLUTION, "Solution"),
        ]
        row = tk.Frame(leg, bg=BG)
        row.pack()
        for color, label in items:
            chip = tk.Canvas(row, width=12, height=12, bg=BG,
                             highlightthickness=0)
            chip.pack(side="left", padx=(8, 3))
            chip.create_rectangle(0, 0, 12, 12, fill=color,
                                  outline=BORDER, width=1)
            tk.Label(row, text=label, bg=BG, fg=TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))

    # ── MAZE DRAWING ─────────────────────────
    def _cell_color(self, cell):
        if cell == self.start:  return CELL_START
        if cell == self.goal:   return CELL_GOAL
        r, c = cell
        if self.maze[r][c] == 1: return CELL_WALL
        if self.final_path and cell in self.final_path: return CELL_SOLUTION
        if cell == self.current_cell: return CELL_CURRENT
        if cell in self.frontier: return CELL_FRONTIER
        if cell in self.visited:  return CELL_VISITED
        return CELL_OPEN

    def _draw_maze(self):
        rows = len(self.maze)
        cols = len(self.maze[0])
        cs   = self.CELL
        gap  = self.GAP
        step = cs + gap
        w = cols * step - gap
        h = rows * step - gap
        self.canvas.configure(width=w, height=h)
        self.canvas.delete("all")

        for r in range(rows):
            for c in range(cols):
                cell = (r, c)
                x1 = c * step
                y1 = r * step
                x2 = x1 + cs
                y2 = y1 + cs
                color = self._cell_color(cell)

                # glow effect for current cell
                if cell == self.current_cell:
                    glow_alpha = abs(math.sin(self._pulse_step * 0.15))
                    glow_color = lerp_color(CELL_CURRENT, WARN, glow_alpha * 0.4)
                    rounded_rect(self.canvas, x1 - 3, y1 - 3, x2 + 3, y2 + 3,
                                 radius=self.R + 3,
                                 fill=glow_color, outline="")

                rounded_rect(self.canvas, x1, y1, x2, y2,
                             radius=self.R, fill=color, outline="")

                # border for special cells
                if cell == self.start:
                    rounded_rect(self.canvas, x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                 radius=self.R - 2, fill="", outline=ACCENT, width=2)
                elif cell == self.goal:
                    rounded_rect(self.canvas, x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                 radius=self.R - 2, fill="", outline=DANGER, width=2)

                # solution path connector dot
                if self.final_path and cell in self.final_path and cell not in (self.start, self.goal):
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                            fill=SUCCESS, outline="")

                # label
                light_cells = {CELL_OPEN, CELL_WALL}
                txt_color = CELL_TEXT_LIGHT if color in light_cells else TEXT
                if color in (CELL_START, CELL_GOAL, CELL_CURRENT):
                    txt_color = TEXT
                
                if self.maze[r][c] == 1:
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="w",
                        fill=txt_color,
                        font=("Segoe UI", 10, "bold"),
                    )
                else:
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text=f"{r},{c}",
                        fill=txt_color,
                        font=("Segoe UI", 8, "bold"),
                    )

    # ── PULSE ANIMATION ──────────────────────
    def _start_pulse(self):
        self._pulse_step += 1
        if self.running:
            self._draw_maze()
        self.root.after(60, self._start_pulse)

    # ── STATUS DOT ───────────────────────────
    def _set_dot(self, color):
        self._status_dot.itemconfigure(self._dot_oval, fill=color)

    # ── INTERACTIONS ─────────────────────────
    def _on_click(self, event):
        if self.running: return
        cs = self.CELL + self.GAP
        r = event.y // cs
        c = event.x // cs
        if not (0 <= r < len(self.maze) and 0 <= c < len(self.maze[0])): return
        if (r, c) in (self.start, self.goal): return
        self.maze[r][c] ^= 1
        self._reset_state()
        self.status_var.set("Maze updated")
        self._draw_maze()

    def _reset_state(self):
        self.final_path = []
        self.active_path = []
        self.visited = set()
        self.frontier = []
        self.current_cell = None
        self.step_var.set("0")
        self.visited_var.set("0")
        self.frontier_var.set("0")
        self.path_var.set("—")
        self._set_dot(TEXT_MUTED)

    def _load_sample(self):
        if self.running: return
        self.maze = self._default_maze()
        self._reset_state()
        self.status_var.set("Sample maze loaded")
        self._clear_log()
        self._draw_maze()

    def _clear_maze(self):
        if self.running: return
        self.maze = [[0] * len(self.maze[0]) for _ in range(len(self.maze))]
        self._reset_state()
        self.status_var.set("Maze cleared — click to add walls")
        self._clear_log()
        self._draw_maze()

    def _generate_maze(self):
        if self.running: return
        import random
        rows, cols = 9, 13
        self.maze = [[1] * cols for _ in range(rows)]
        self.start = (0, 0)
        self.goal = (rows - 1, cols - 1)
        
        def carve(r, c):
            self.maze[r][c] = 0
            dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] == 1:
                    self.maze[r + dr//2][c + dc//2] = 0
                    carve(nr, nc)
                    
        carve(0, 0)
        self.maze[self.goal[0]][self.goal[1]] = 0
        
        self._reset_state()
        self.status_var.set("Tree maze generated!")
        self._clear_log()
        self._draw_maze()

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ── SEARCH ───────────────────────────────
    def _start_search(self):
        if self.running: return
        self._reset_state()
        self._clear_log()
        solver = MazeSolver(self.maze, self.start, self.goal)
        self.trace = solver.search_trace(self.algorithm_var.get())
        self.running = True
        self.run_btn.set_text("⏸  Running…")
        self._set_dot(WARN)
        self.status_var.set("Searching…")
        self._advance()

    def _advance(self):
        if not self.running or self.trace is None: return
        try:
            state = next(self.trace)
        except StopIteration:
            self._finish()
            return

        self._apply(state)

        if state["event"] in {"solution", "no_path"}:
            self._finish(state["event"])
            return

        self.root.after(self.speed.value, self._advance)

    def _apply(self, state):
        ev = state.get("event", "")
        self.current_cell = state.get("current")
        self.visited      = set(state.get("visited", set()))
        self.frontier     = list(state.get("frontier", []))

        if ev == "solution":
            self.final_path  = list(state.get("path", []))
            self.active_path = []
        else:
            self.active_path = list(state.get("path", []))

        self.step_var.set(str(state.get("step", 0)))
        self.visited_var.set(str(len(self.visited)))
        self.frontier_var.set(str(len(self.frontier)))
        path = state.get("path", [])
        self.path_var.set(str(len(path)) if path else "—")
        self.status_var.set(state.get("message", ""))

        self._draw_maze()
        self._log(ev, state.get("message", ""))

    def _finish(self, event=None):
        self.running = False
        self.trace = None
        self.run_btn.set_text("▶  Run Search")
        if event == "solution":
            self.status_var.set(f"✓  Path found — {len(self.final_path)} cells")
            self._set_dot(SUCCESS)
            self._step_card.flash(SUCCESS)
            self._path_card.flash(SUCCESS)
        elif event == "no_path":
            self.status_var.set("✗  No path exists")
            self._set_dot(DANGER)
        else:
            self.status_var.set("Done")
            self._set_dot(TEXT_MUTED)

    def _log(self, event, message):
        tag = event if event in {"solution", "visit", "no_path", "enqueue", "start"} else ""
        self.log_text.configure(state="normal")
        if tag:
            self.log_text.insert("end", message + "\n", (tag,))
        else:
            self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


# ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.tk.call("tk", "scaling", 1.3)       # crisp on HiDPI
    MazeSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()