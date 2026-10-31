from collections import deque
from pathlib import Path
import sys
from graph_loader import load_graph


def topological_sort(graph):

    in_degree = {v: 0 for v in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque(v for v in graph if in_degree[v] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(order) < len(graph):
        return None
    return order


def many(graph, s, t, red):
    order = topological_sort(graph)
    if order is None:
        return "?!"  

   
    best = {v: -1 for v in graph}
    best[s] = 1 if s in red else 0

    for u in order:
        if best[u] == -1:
            continue 
        for v in graph[u]:
            gain = 1 if v in red else 0
            if best[u] + gain > best[v]:
                best[v] = best[u] + gain

    return best[t]


def main():
    if len(sys.argv) != 2:
        print("How to use: python many.py red-scare_documents/data/<file>")
        return

    filename = Path(sys.argv[1])

    graph, s, t, red = load_graph(filename)
    print(many(graph, s, t, red))


if __name__ == "__main__":
    main()
