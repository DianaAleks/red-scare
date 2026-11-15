
from collections import deque
import sys
from pathlib import Path
from graph_loader import load_graph


def is_undirected(graph):
    for u in graph:
        for v in graph[u]:
            if u not in graph[v]:
                return False
    return True


def is_dag(graph):
    indegree = {v: 0 for v in graph}

    for u in graph:
        for v in graph[u]:
            indegree[v] += 1

    queue = deque()
    for v in graph:
        if indegree[v] == 0:
            queue.append(v)

    count = 0

    while queue:
        u = queue.popleft()
        count += 1

        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    return count == len(graph)


def directed_some(graph, s, t, red):
    reverse = {v: [] for v in graph}

    for u in graph:
        for v in graph[u]:
            reverse[v].append(u)

    # Find vertices reachable from s.
    from_s = set()
    queue = deque([s])
    from_s.add(s)

    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in from_s:
                from_s.add(v)
                queue.append(v)

    # Find vertices that can reach t.
    to_t = set()
    queue = deque([t])
    to_t.add(t)

    while queue:
        u = queue.popleft()
        for v in reverse[u]:
            if v not in to_t:
                to_t.add(v)
                queue.append(v)

    # A red vertex must be reachable from s and able to reach t.
    return len(red & from_s & to_t) > 0


def undirected_some(graph, s, t, red):
    # Find the biconnected components using DFS.
    discovery = {}
    low = {}
    parent = {}
    articulation = set()
    edge_stack = []
    blocks = []
    time = 0

    def dfs(u):
        nonlocal time
        time += 1
        discovery[u] = time
        low[u] = time
        children = 0

        for v in graph[u]:
            if v not in discovery:
                parent[v] = u
                children += 1
                edge_stack.append((u, v))

                dfs(v)
                low[u] = min(low[u], low[v])

                if parent[u] is not None and low[v] >= discovery[u]:
                    articulation.add(u)

                if low[v] >= discovery[u]:
                    block = set()

                    while edge_stack:
                        edge = edge_stack.pop()
                        block.update(edge)

                        if edge == (u, v):
                            break

                    blocks.append(block)

            elif v != parent[u] and discovery[v] < discovery[u]:
                low[u] = min(low[u], discovery[v])
                edge_stack.append((u, v))

        if parent[u] is None and children > 1:
            articulation.add(u)

    # Run DFS in every connected component.
    for v in graph:
        if v not in discovery:
            parent[v] = None
            dfs(v)

    # Include isolated vertices.
    vertices_in_blocks = set()
    for block in blocks:
        vertices_in_blocks.update(block)

    for v in graph:
        if v not in vertices_in_blocks:
            blocks.append({v})

    # Build the block-cut tree.
    tree = {}
    block_of_vertex = {}

    for i, block in enumerate(blocks):
        block_node = ("B", i)
        tree[block_node] = []

        for v in block:
            if v in articulation:
                art_node = ("A", v)

                if art_node not in tree:
                    tree[art_node] = []

                tree[block_node].append(art_node)
                tree[art_node].append(block_node)
            else:
                block_of_vertex[v] = block_node

    # Find the tree node for s and t.
    if s in articulation:
        start = ("A", s)
    else:
        start = block_of_vertex[s]

    if t in articulation:
        target = ("A", t)
    else:
        target = block_of_vertex[t]

    # Find the unique path in the block-cut tree.
    previous = {start: None}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        if current == target:
            break

        for neighbour in tree[current]:
            if neighbour not in previous:
                previous[neighbour] = current
                queue.append(neighbour)

    if target not in previous:
        return False

    # Check the blocks and articulation vertices on that path.
    current = target

    while current is not None:
        if current[0] == "A":
            if current[1] in red:
                return True
        else:
            block = blocks[current[1]]
            if block & red:
                return True

        current = previous[current]

    return False


def some(graph, s, t, red):
    if s == t:
        return s in red

    if is_undirected(graph):
        return undirected_some(graph, s, t, red)

    if is_dag(graph):
        return directed_some(graph, s, t, red)

    return "?!"


def main():
    if len(sys.argv) != 2:
        print("Usage: python some_new.py <input-file>")
        return

    filename = Path(sys.argv[1])
    graph, s, t, red = load_graph(filename)

    print(some(graph, s, t, red))


if __name__ == "__main__":
    main()
