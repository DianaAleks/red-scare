
from collections import deque
from pathlib import Path
import sys
from graph_loader import load_graph
from collections import deque

def few(graph, s, t, red):

    weighted_graph = {}


    # This will build a weighted graph for every instance of a graph (weight from 0 to 1)
    for u in graph:
        weighted_graph[u] = []

        for v in graph[u]:
            weight = 1 if v in red else 0
            weighted_graph[u].append((v, weight))

    # 0-1 BFS
    dist = {v: float('inf') for v in graph}
    dist[s] = 1 if s in red else 0

    queue = deque([s])

    while queue:
        u = queue.popleft()

        for v, w in weighted_graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

                if w == 0:
                    queue.appendleft(v)
                else:
                    queue.append(v)

    if dist[t] == float('inf'):
        return -1

    return dist[t]
def main():
    if len(sys.argv) != 2:
        print("How to use: python3 alternate.py red-scare_documents/data/<input_file_name>")
        return

    filename = Path(sys.argv[1])

    graph, s, t, red = load_graph(filename)
    min_red_path = few(graph, s, t, red)
    print(min_red_path)
if __name__ == "__main__":
    main()