from collections import deque
from graph_loader import load_graph
import sys

def reachable(graph, start):
    visited = {start}
    queue = deque([start])

    while queue:
        u = queue.popleft()

        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)

    return visited


def reverse_graph(graph):
    reverse = {v: [] for v in graph}

    for u in graph:
        for v in graph[u]:
            reverse[v].append(u)

    return reverse


def is_dag(graph):
    indegree = {v: 0 for v in graph}

    for u in graph:
        for v in graph[u]:
            indegree[v] += 1

    queue = deque(v for v in graph if indegree[v] == 0)
    count = 0

    while queue:
        u = queue.popleft()
        count += 1

        for v in graph[u]:
            indegree[v] -= 1

            if indegree[v] == 0:
                queue.append(v)

    return count == len(graph)


def solve_directed(graph, s, t, red):
    if not is_dag(graph):
        return "?!"

    if s == t:
        return s in red

    from_s = reachable(graph, s)
    to_t = reachable(reverse_graph(graph), t)

    return any(v in from_s and v in to_t for v in red)


def solve_undirected(graph, s, t, red):
    if s == t:
        return s in red

    parent = {s: None}
    queue = deque([s])
    component = {s}
    edges = 0

    while queue:
        u = queue.popleft()

        for v in graph[u]:
            edges += 1

            if v not in parent:
                parent[v] = u
                component.add(v)
                queue.append(v)

    if t not in component:
        return False

    if edges // 2 != len(component) - 1:
        return "?!"

    path = []
    current = t

    while current is not None:
        path.append(current)
        current = parent[current]

    return any(v in red for v in path)


def some(graph, s, t, red, directed):
    if directed:
        return solve_directed(graph, s, t, red)

    return solve_undirected(graph, s, t, red)


if __name__ == "__main__":
    filename = sys.argv[1]

    graph, s, t, red, directed = load_graph(filename)

    result = some(graph, s, t, red, directed)

    if isinstance(result, bool):
        print(str(result).lower())
    else:
        print(result)
