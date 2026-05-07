from collections import deque
import tkinter as tk
from tkinter import ttk


class BiDirectionalSearch:
    def __init__(self, graph):
        self.graph = graph

    def bidirectional_trace(self, start, goal):
        if start == goal:
            yield {
                "event": "solution",
                "step": 0,
                "current": start,
                "front_visited": {start},
                "back_visited": {goal},
                "frontier_front": [],
                "frontier_back": [],
                "path": [start],
                "meeting": start,
                "message": "Start and goal are the same node.",
            }
            return

        front_queue = deque([start])
        back_queue = deque([goal])
        front_parent = {start: None}
        back_parent = {goal: None}
        front_visited = {start}
        back_visited = {goal}
        step = 0

        yield {
            "event": "start",
            "step": step,
            "current": start,
            "front_visited": set(front_visited),
            "back_visited": set(back_visited),
            "frontier_front": list(front_queue),
            "frontier_back": list(back_queue),
            "path": [start],
            "meeting": None,
            "message": f"Starting bidirectional search from {start} to {goal}.",
        }

        while front_queue and back_queue:
            step += 1
            front_node, front_message, meet = self.expand(front_queue, front_parent, front_visited, back_visited, "forward")

            yield {
                "event": "front_expand",
                "step": step,
                "current": front_node,
                "front_visited": set(front_visited),
                "back_visited": set(back_visited),
                "frontier_front": list(front_queue),
                "frontier_back": list(back_queue),
                "path": self.build_path(front_parent, back_parent, meet) if meet else [],
                "meeting": meet,
                "message": front_message,
            }

            if meet:
                path = self.build_path(front_parent, back_parent, meet)
                yield {
                    "event": "solution",
                    "step": step,
                    "current": meet,
                    "front_visited": set(front_visited),
                    "back_visited": set(back_visited),
                    "frontier_front": list(front_queue),
                    "frontier_back": list(back_queue),
                    "path": path,
                    "meeting": meet,
                    "message": f"Searches met at {meet}.",
                }
                return

            step += 1
            back_node, back_message, meet = self.expand(back_queue, back_parent, back_visited, front_visited, "backward")

            yield {
                "event": "back_expand",
                "step": step,
                "current": back_node,
                "front_visited": set(front_visited),
                "back_visited": set(back_visited),
                "frontier_front": list(front_queue),
                "frontier_back": list(back_queue),
                "path": self.build_path(front_parent, back_parent, meet) if meet else [],
                "meeting": meet,
                "message": back_message,
            }

            if meet:
                path = self.build_path(front_parent, back_parent, meet)
                yield {
                    "event": "solution",
                    "step": step,
                    "current": meet,
                    "front_visited": set(front_visited),
                    "back_visited": set(back_visited),
                    "frontier_front": list(front_queue),
                    "frontier_back": list(back_queue),
                    "path": path,
                    "meeting": meet,
                    "message": f"Searches met at {meet}.",
                }
                return

        yield {
            "event": "no_path",
            "step": step,
            "current": None,
            "front_visited": set(front_visited),
            "back_visited": set(back_visited),
            "frontier_front": list(front_queue),
            "frontier_back": list(back_queue),
            "path": [],
            "meeting": None,
            "message": "No route found between the selected nodes.",
        }

    def expand(self, queue, this_side, this_visited, other_visited, label):
        if not queue:
            return None, f"{label.title()} frontier is empty.", None

        node = queue.popleft()
        for neigh in self.graph[node]:
            if neigh not in this_visited:
                this_visited.add(neigh)
                this_side[neigh] = node
                queue.append(neigh)

                if neigh in other_visited:
                    return node, f"{label.title()} side reached meeting node {neigh}.", neigh

        return node, f"{label.title()} side expanded {node}.", None

    def build_path(self, front, back, meet):
        if meet is None:
            return []

        path = []
        node = meet
        while node is not None:
            path.append(node)
            node = front[node]
        path.reverse()

        node = back[meet]
        while node is not None:
            path.append(node)
            node = back[node]

        return path


class RouteFinderApp:
    NODE_RADIUS = 28
    CONNECT_THRESHOLD = 120

    def __init__(self, root):
        self.root = root
        self.root.title("Route Finder Visualizer")
        self.root.geometry("1180x760")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0b1020")

        self.graph = self.default_graph()
        self.positions = self.default_positions()
        self.searcher = BiDirectionalSearch(self.graph)
        self.nodes = sorted(self.graph)
        self.start_var = tk.StringVar(value="A")
        self.goal_var = tk.StringVar(value="F")
        self.status_var = tk.StringVar(value="Ready to run bidirectional search.")
        self.step_var = tk.StringVar(value="0")
        self.current_var = tk.StringVar(value="-")
        self.meeting_var = tk.StringVar(value="-")
        self.path_var = tk.StringVar(value="-")
        self.running = False
        self.trace = None
        self.front_visited = set()
        self.back_visited = set()
        self.frontier_front = []
        self.frontier_back = []
        self.final_path = []
        self.meeting_node = None
        self.dragging_node = None
        self.dragging_new_node = False
        self.canvas_drag_offset = (0, 0)
        self.edge_start_node = None
        self.current_edge_line = None

        self._configure_styles()
        self._build_ui()
        self._draw_graph()

    def default_graph(self):
        return {
            "A": ["B", "C"],
            "B": ["A", "D", "E"],
            "C": ["A", "F"],
            "D": ["B"],
            "E": ["B", "F"],
            "F": ["C", "E"],
        }

    def default_positions(self):
        return {
            "A": (160, 120),
            "B": (320, 90),
            "C": (320, 210),
            "D": (500, 90),
            "E": (500, 210),
            "F": (670, 150),
        }

    def _index_to_name(self, index):
        letters = []
        index += 1
        while index:
            index, remainder = divmod(index - 1, 26)
            letters.append(chr(65 + remainder))
        return "".join(reversed(letters))

    def _next_node_name(self):
        existing = set(self.graph)
        index = 0
        while True:
            name = self._index_to_name(index)
            if name not in existing:
                return name
            index += 1

    def _node_at_point(self, x, y):
        for node, (nx, ny) in self.positions.items():
            if (nx - x) ** 2 + (ny - y) ** 2 <= self.NODE_RADIUS ** 2:
                return node
        return None

    def _nearest_node(self, x, y):
        nearest_node = None
        nearest_distance = None
        for node, (nx, ny) in self.positions.items():
            distance = ((nx - x) ** 2 + (ny - y) ** 2) ** 0.5
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_node = node
        return nearest_node, nearest_distance

    def _connect_nodes(self, a, b):
        if b not in self.graph[a]:
            self.graph[a].append(b)
        if a not in self.graph[b]:
            self.graph[b].append(a)

    def _add_node(self, x, y):
        node = self._next_node_name()
        self.graph[node] = []
        self.positions[node] = (x, y)

        nearest_node, distance = self._nearest_node(x, y)
        if nearest_node is not None and nearest_node != node and distance is not None and distance <= self.CONNECT_THRESHOLD:
            self._connect_nodes(node, nearest_node)

        self.nodes = sorted(self.graph)
        self.start_box["values"] = self.nodes
        self.goal_box["values"] = self.nodes
        self._reset_state(f"Added node {node}.")
        self._draw_graph()

    def _point_within_canvas(self, x, y):
        return 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#0b1020")
        style.configure("Header.TFrame", background="#111827")
        style.configure("Panel.TFrame", background="#111827")
        style.configure("Card.TFrame", background="#182235")
        style.configure("Title.TLabel", background="#111827", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#111827", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#111827", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        style.configure("Info.TLabel", background="#111827", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        style.configure("TCombobox", padding=6)

    def _build_ui(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(24, 18))
        header.pack(fill="x")

        ttk.Label(header, text="Route Finder Visualizer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Question: How do two search waves meet in the middle to find a route faster?",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        body = ttk.Frame(self.root, style="Root.TFrame", padding=18)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, style="Root.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right_wrapper = ttk.Frame(body, style="Panel.TFrame")
        right_wrapper.pack(side="right", fill="y")

        canvas_wrap = ttk.Frame(left, style="Card.TFrame", padding=12)
        canvas_wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_wrap, bg="#0b1020", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.canvas.bind("<Button-3>", self._on_canvas_right_press)
        self.canvas.bind("<B3-Motion>", self._on_canvas_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_canvas_right_release)

        right_canvas = tk.Canvas(right_wrapper, bg="#111827", highlightthickness=0, width=320)
        right_scrollbar = ttk.Scrollbar(right_wrapper, orient="vertical", command=right_canvas.yview)
        
        controls = ttk.Frame(right_canvas, style="Panel.TFrame", padding=18)
        
        controls.bind(
            "<Configure>",
            lambda e: right_canvas.configure(
                scrollregion=right_canvas.bbox("all")
            )
        )
        
        right_canvas_window = right_canvas.create_window((0, 0), window=controls, anchor="nw")
        right_canvas.bind("<Configure>", lambda e: right_canvas.itemconfig(right_canvas_window, width=e.width))
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if right_canvas.yview() != (0.0, 1.0):
                right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        right_wrapper.bind("<Enter>", lambda e: right_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        right_wrapper.bind("<Leave>", lambda e: right_canvas.unbind_all("<MouseWheel>"))

        ttk.Label(controls, text="Controls", style="PanelTitle.TLabel").pack(anchor="w")

        ttk.Label(controls, text="Start node", style="Info.TLabel").pack(anchor="w", pady=(16, 4))
        self.start_box = ttk.Combobox(controls, textvariable=self.start_var, values=self.nodes, state="readonly")
        self.start_box.pack(fill="x")

        ttk.Label(controls, text="Goal node", style="Info.TLabel").pack(anchor="w", pady=(12, 4))
        self.goal_box = ttk.Combobox(controls, textvariable=self.goal_var, values=self.nodes, state="readonly")
        self.goal_box.pack(fill="x")

        ttk.Label(controls, text="Drag to add", style="Info.TLabel").pack(anchor="w", pady=(16, 4))
        drag_card = ttk.Frame(controls, style="Card.TFrame", padding=10)
        drag_card.pack(fill="x")
        self.new_node_label = ttk.Label(drag_card, text="New Node", style="Info.TLabel")
        self.new_node_label.pack(fill="x")
        self.new_node_label.bind("<Button-1>", self._start_new_node_drag)
        self.new_node_label.bind("<B1-Motion>", self._drag_new_node_preview)
        self.new_node_label.bind("<ButtonRelease-1>", self._drop_new_node)
        ttk.Label(drag_card, text="Drag onto canvas to create.\nRight-click drag to add/remove connections.\nDouble-click a node to delete it.", style="Subtitle.TLabel").pack(anchor="w", pady=(6, 0))

        ttk.Button(controls, text="Run Search", style="Accent.TButton", command=self.start_search).pack(fill="x", pady=(16, 0))
        
        btn_row = ttk.Frame(controls, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Sample", command=self.load_sample_graph).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(btn_row, text="Random", command=self.generate_random_graph).pack(side="left", fill="x", expand=True, padx=(2, 2))
        ttk.Button(btn_row, text="Clear", command=self.clear_graph).pack(side="left", fill="x", expand=True, padx=(2, 0))

        stats = ttk.Frame(controls, style="Card.TFrame", padding=12)
        stats.pack(fill="x", pady=(18, 0))

        self._stat_row(stats, "Status", self.status_var)
        self._stat_row(stats, "Step", self.step_var)
        self._stat_row(stats, "Current", self.current_var)
        self._stat_row(stats, "Meeting", self.meeting_var)
        self._stat_row(stats, "Path length", self.path_var)

        log_frame = ttk.Frame(controls, style="Card.TFrame", padding=12)
        log_frame.pack(fill="both", expand=True, pady=(18, 0))

        ttk.Label(log_frame, text="Search Log", style="PanelTitle.TLabel").pack(anchor="w")
        self.log_text = tk.Text(
            log_frame,
            height=12,
            wrap="word",
            bg="#0b1020",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.log_text.pack(fill="both", expand=True, pady=(12, 0))
        self.log_text.configure(state="disabled")

    def _stat_row(self, parent, label, variable):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, style="Info.TLabel").pack(side="left")
        ttk.Label(row, textvariable=variable, style="Info.TLabel").pack(side="right")

    def _node_fill(self, node):
        if node == self.meeting_node and self.final_path:
            return "#86efac"
        if node in self.final_path:
            return "#fde68a"
        if node == self._selected_start():
            return "#fbbf24"
        if node == self._selected_goal():
            return "#fca5a5"
        if node in self.front_visited and node in self.back_visited:
            return "#c084fc"
        if node in self.front_visited:
            return "#7dd3fc"
        if node in self.back_visited:
            return "#f9a8d4"
        if node in self.frontier_front or node in self.frontier_back:
            return "#a7f3d0"
        return "#e2e8f0"

    def _selected_start(self):
        return self.start_var.get()

    def _selected_goal(self):
        return self.goal_var.get()

    def _draw_graph(self):
        self.canvas.delete("all")

        drawn_edges = set()
        for node, neighbors in self.graph.items():
            x1, y1 = self.positions[node]
            for neighbor in neighbors:
                edge = tuple(sorted((node, neighbor)))
                if edge in drawn_edges:
                    continue
                drawn_edges.add(edge)
                x2, y2 = self.positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill="#334155", width=4)

        for node, (x, y) in self.positions.items():
            fill = self._node_fill(node)
            outline = "#111827"
            if node in self.final_path:
                outline = "#f59e0b"
            elif node == self.meeting_node:
                outline = "#22c55e"

            self.canvas.create_oval(x - self.NODE_RADIUS, y - self.NODE_RADIUS, x + self.NODE_RADIUS, y + self.NODE_RADIUS, fill=fill, outline=outline, width=3)
            self.canvas.create_text(x, y, text=node, fill="#0f172a", font=("Segoe UI", 15, "bold"))

        self.canvas.create_text(150, 30, text="Front search: blue | Back search: pink | Meeting: green | Final route: gold", fill="#cbd5e1", font=("Segoe UI", 10))

    def _start_new_node_drag(self, event):
        if self.running:
            return
        self.dragging_new_node = True

    def _drag_new_node_preview(self, event):
        if not self.dragging_new_node:
            return
        self.status_var.set("Drop the new node onto the canvas to create it.")

    def _drop_new_node(self, event):
        if not self.dragging_new_node:
            return

        self.dragging_new_node = False
        canvas_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        if self._point_within_canvas(canvas_x, canvas_y):
            self._add_node(canvas_x, canvas_y)
        else:
            self.status_var.set("Drop the new node on the canvas area.")

    def _on_canvas_press(self, event):
        if self.running:
            return

        node = self._node_at_point(event.x, event.y)
        if node is None:
            return

        self.dragging_node = node
        node_x, node_y = self.positions[node]
        self.canvas_drag_offset = (node_x - event.x, node_y - event.y)

    def _on_canvas_drag(self, event):
        if self.running or self.dragging_node is None:
            return

        x = max(self.NODE_RADIUS, min(self.canvas.winfo_width() - self.NODE_RADIUS, event.x + self.canvas_drag_offset[0]))
        y = max(self.NODE_RADIUS, min(self.canvas.winfo_height() - self.NODE_RADIUS, event.y + self.canvas_drag_offset[1]))
        self.positions[self.dragging_node] = (x, y)
        self._draw_graph()

    def _on_canvas_release(self, event):
        if self.running or self.dragging_node is None:
            return

        moved_node = self.dragging_node
        self.dragging_node = None
        x, y = self.positions[moved_node]
        nearest_node, distance = self._nearest_node(x, y)
        if nearest_node is not None and nearest_node != moved_node and distance is not None and distance <= self.CONNECT_THRESHOLD:
            self._connect_nodes(moved_node, nearest_node)
            self.status_var.set(f"Moved {moved_node} and connected it to {nearest_node}.")
        else:
            self.status_var.set(f"Moved {moved_node}.")
        self._draw_graph()

    def _on_canvas_right_press(self, event):
        if self.running: return
        node = self._node_at_point(event.x, event.y)
        if node:
            self.edge_start_node = node
            x, y = self.positions[node]
            self.current_edge_line = self.canvas.create_line(x, y, event.x, event.y, fill="#94a3b8", width=3, dash=(4, 4))

    def _on_canvas_right_drag(self, event):
        if self.running or not self.edge_start_node or not self.current_edge_line: return
        x, y = self.positions[self.edge_start_node]
        self.canvas.coords(self.current_edge_line, x, y, event.x, event.y)

    def _on_canvas_right_release(self, event):
        if self.running or not self.edge_start_node: return
        
        if self.current_edge_line:
            self.canvas.delete(self.current_edge_line)
            self.current_edge_line = None
            
        node = self._node_at_point(event.x, event.y)
        if node and node != self.edge_start_node:
            if node in self.graph[self.edge_start_node]:
                self.graph[self.edge_start_node].remove(node)
                self.graph[node].remove(self.edge_start_node)
                self.status_var.set(f"Disconnected {self.edge_start_node} and {node}.")
            else:
                self._connect_nodes(self.edge_start_node, node)
                self.status_var.set(f"Connected {self.edge_start_node} and {node}.")
            self._draw_graph()
        self.edge_start_node = None

    def _on_canvas_double_click(self, event):
        if self.running: return
        node = self._node_at_point(event.x, event.y)
        if node:
            self.dragging_node = None
            for neighbor in list(self.graph[node]):
                self.graph[neighbor].remove(node)
            del self.graph[node]
            del self.positions[node]
            
            self.nodes = sorted(self.graph)
            self.start_box["values"] = self.nodes
            self.goal_box["values"] = self.nodes
            
            if self.start_var.get() == node:
                self.start_var.set(self.nodes[0] if self.nodes else "")
            if self.goal_var.get() == node:
                self.goal_var.set(self.nodes[-1] if self.nodes else "")
                
            self._reset_state(f"Removed node {node}.")
            self._draw_graph()

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _refresh_status(self, state):
        self.step_var.set(str(state.get("step", 0)))
        current = state.get("current")
        self.current_var.set(str(current) if current is not None else "-")
        meeting = state.get("meeting")
        self.meeting_var.set(str(meeting) if meeting is not None else "-")
        self.path_var.set(str(len(state.get("path", []))))
        self.status_var.set(state.get("message", ""))

    def _apply_state(self, state):
        self.front_visited = set(state.get("front_visited", set()))
        self.back_visited = set(state.get("back_visited", set()))
        self.frontier_front = list(state.get("frontier_front", []))
        self.frontier_back = list(state.get("frontier_back", []))
        self.meeting_node = state.get("meeting")

        if state.get("event") == "solution":
            self.final_path = list(state.get("path", []))

        self._refresh_status(state)
        self._draw_graph()
        self._log(state.get("message", ""))

    def load_sample_graph(self):
        if self.running:
            return

        self.graph = self.default_graph()
        self.positions = self.default_positions()
        self.searcher = BiDirectionalSearch(self.graph)
        self.nodes = sorted(self.graph)
        self.start_box["values"] = self.nodes
        self.goal_box["values"] = self.nodes
        self.start_var.set("A")
        self.goal_var.set("F")
        self._reset_state("Sample graph loaded.")
        self._draw_graph()

    def generate_random_graph(self):
        if self.running:
            return
        import random
        self.graph = {}
        self.positions = {}
        num_nodes = random.randint(6, 12)
        width = self.canvas.winfo_width() or 600
        height = self.canvas.winfo_height() or 600
        
        for i in range(num_nodes):
            name = self._index_to_name(i)
            self.graph[name] = []
            x = random.randint(self.NODE_RADIUS + 20, max(self.NODE_RADIUS + 21, width - self.NODE_RADIUS - 20))
            y = random.randint(self.NODE_RADIUS + 20, max(self.NODE_RADIUS + 21, height - self.NODE_RADIUS - 20))
            self.positions[name] = (x, y)
            
        nodes = list(self.graph.keys())
        for i, node in enumerate(nodes):
            if i > 0:
                target = nodes[random.randint(0, i-1)]
                self._connect_nodes(node, target)
            for _ in range(random.randint(0, 2)):
                target = random.choice(nodes)
                if target != node:
                    self._connect_nodes(node, target)

        self.nodes = sorted(self.graph)
        self.start_box["values"] = self.nodes
        self.goal_box["values"] = self.nodes
        if self.nodes:
            self.start_var.set(self.nodes[0])
            self.goal_var.set(self.nodes[-1])
        self.searcher = BiDirectionalSearch(self.graph)
        self._reset_state("Random graph generated.")
        self._draw_graph()

    def clear_graph(self):
        if self.running:
            return
        self.graph = {}
        self.positions = {}
        self.nodes = []
        self.start_box["values"] = []
        self.goal_box["values"] = []
        self.start_var.set("")
        self.goal_var.set("")
        self.searcher = BiDirectionalSearch(self.graph)
        self._reset_state("Graph cleared. Drag new nodes onto the canvas.")
        self._draw_graph()

    def _reset_state(self, message):
        self.front_visited = set()
        self.back_visited = set()
        self.frontier_front = []
        self.frontier_back = []
        self.final_path = []
        self.meeting_node = None
        self.status_var.set(message)
        self.step_var.set("0")
        self.current_var.set("-")
        self.meeting_var.set("-")
        self.path_var.set("-")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def start_search(self):
        if self.running:
            return

        start = self._selected_start()
        goal = self._selected_goal()
        if start == goal:
            self._reset_state("Start and goal are the same. The route is already complete.")
            self.trace = self.searcher.bidirectional_trace(start, goal)
            self.running = True
            self._advance_trace()
            return

        self._reset_state("Search started.")
        self.trace = self.searcher.bidirectional_trace(start, goal)
        self.running = True
        self._advance_trace()

    def _advance_trace(self):
        if not self.running or self.trace is None:
            return

        try:
            state = next(self.trace)
        except StopIteration:
            self.running = False
            self.trace = None
            return

        self._apply_state(state)

        if state.get("event") in {"solution", "no_path"}:
            self.running = False
            self.trace = None
            if state.get("event") == "solution":
                self.status_var.set("Route found successfully.")
            else:
                self.status_var.set("No route found.")
            return

        self.root.after(280, self._advance_trace)


def main():
    root = tk.Tk()
    RouteFinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()