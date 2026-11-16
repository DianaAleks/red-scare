from collections import deque
import sys
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

    from_s = set()
    queue = deque([s])
    from_s.add(s)

    while queue:
        u = queue.popleft()

        for v in graph[u]:
            if v not in from_s:
                from_s.add(v)
                queue.append(v)

    to_t = set()
    queue = deque([t])
    to_t.add(t)

    while queue:
        u = queue.popleft()

        for v in reverse[u]:
            if v not in to_t:
                to_t.add(v)
                queue.append(v)

    return len(red & from_s & to_t) > 0


def undirected_some(graph, s, t, red):
    disc = {}
    low = {}
    parent = {}
    edge_stack = []
    blocks = []
    time = 0

    # Iterative DFS to find biconnected components
    for root in graph:
        if root in disc:
            continue

        if not graph[root]:
            disc[root] = time
            low[root] = time
            time += 1
            blocks.append({root})
            continue

        disc[root] = time
        low[root] = time
        time += 1
        parent[root] = None

        stack = [(root, iter(graph[root]))]

        while stack:
            u, neighbours = stack[-1]

            try:
                v = next(neighbours)

                if v not in disc:
                    parent[v] = u
                    edge_stack.append((u, v))

                    disc[v] = time
                    low[v] = time
                    time += 1

                    stack.append((v, iter(graph[v])))

                elif v != parent[u] and disc[v] < disc[u]:
                    low[u] = min(low[u], disc[v])
                    edge_stack.append((u, v))

            except StopIteration:
                stack.pop()

                p = parent[u]

                if p is not None:
                    low[p] = min(low[p], low[u])

                    if low[u] >= disc[p]:
                        block = set()

                        while edge_stack:
                            a, b = edge_stack.pop()
                            block.add(a)
                            block.add(b)

                            if (a == p and b == u) or (a == u and b == p):
                                break

                        if block:
                            blocks.append(block)

    # Find which blocks contain each vertex
    belongs = {v: [] for v in graph}

    for i, block in enumerate(blocks):
        for v in block:
            belongs[v].append(i)

    # Articulation vertices belong to more than one block
    articulation = set()
    for v in graph:
        if len(belongs[v]) > 1:
            articulation.add(v)

    # Build the block-cut tree
    tree = {}
    block_nodes = []

    for i in range(len(blocks)):
        node = ("B", i)
        tree[node] = []
        block_nodes.append(node)

    for v in articulation:
        tree[("A", v)] = []

    for i, block in enumerate(blocks):
        block_node = ("B", i)

        for v in block:
            if v in articulation:
                art_node = ("A", v)
                tree[block_node].append(art_node)
                tree[art_node].append(block_node)

    # Find the tree node for the start and end vertices
    def find_node(v):
        if v in articulation:
            return ("A", v)
        if belongs[v]:
            return ("B", belongs[v][0])
        return None

    start = find_node(s)
    end = find_node(t)

    if start is None or end is None:
        return False

    # Find the unique route in the block-cut tree
    queue = deque([start])
    previous = {start: None}

    while queue:
        u = queue.popleft()

        if u == end:
            break

        for v in tree[u]:
            if v not in previous:
                previous[v] = u
                queue.append(v)

    if end not in previous:
        return False

    route = []
    current = end

    while current is not None:
        route.append(current)
        current = previous[current]

    # Check red vertices on the route
    for node in route:
        if node[0] == "A":
            if node[1] in red:
                return True
        else:
            block = blocks[node[1]]
            if block & red:
                return True

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

    graph, s, t, red = load_graph(sys.argv[1])
    print(some(graph, s, t, red))


if __name__ == "__main__":
    main()


   
    
