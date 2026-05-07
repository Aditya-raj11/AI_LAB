from collections import deque

class BiDirectionalSearch:

    def __init__(self, graph):
        self.graph = graph

    def bidirectional_bfs(self, start, goal):
        if start == goal:
            return [start]

        front_queue = deque([start])
        back_queue = deque([goal])

        front_parent = {start: None}
        back_parent = {goal: None}

        while front_queue and back_queue:

            # Expand from start side
            meet = self.expand(front_queue, front_parent, back_parent)
            if meet:
                return self.build_path(front_parent, back_parent, meet)

            # Expand from goal side
            meet = self.expand(back_queue, back_parent, front_parent)
            if meet:
                return self.build_path(front_parent, back_parent, meet)

        return None

    def expand(self, queue, this_side, other_side):
        if not queue:
            return None

        node = queue.popleft()

        for neigh in self.graph[node]:
            if neigh not in this_side:
                this_side[neigh] = node
                queue.append(neigh)

                # If both searches reach same node
                if neigh in other_side:
                    return neigh
        return None

    def build_path(self, front, back, meet):
        path = []

        # start → meeting node
        node = meet
        while node is not None:
            path.append(node)
            node = front[node]
        path.reverse()

        # meeting node → goal
        node = back[meet]
        while node is not None:
            path.append(node)
            node = back[node]

        return path

if __name__ == "__main__":

    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }

    searcher = BiDirectionalSearch(graph)

    print("Bi-Directional BFS Route:", searcher.bidirectional_bfs('A', 'F'))