
from collections import deque
from pathlib import Path
import sys
from graph_loader import load_graph

# BFS used
def alternate(graph, s, t, red):
    queue = deque([s])
    visited = set()
    visited.add(s)

    while queue:
        current = queue.popleft()

        if current == t:
            return True

        for neighbor in graph[current]:
            different_colors = (current in red) != (neighbor in red)
            if different_colors and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False


def main():
    if len(sys.argv) != 2:
        print("How to use: python3 alternate.py red-scare_documents/data/<input_file_name>")
        return

    filename = Path(sys.argv[1])

    graph, s, t, red = load_graph(filename)
    print(alternate(graph, s, t, red))

if __name__ == "__main__":
    main()