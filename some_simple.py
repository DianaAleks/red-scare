from collections import deque
from pathlib import Path
import sys
from graph_loader import load_graph


def is_directed_file(filename):
    lines = [
        line.split()
        for line in Path(filename).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    n, m, r = map(int, lines[0])
    edges = lines[2 + n:2 + n + m]
    types = {edge[1] for edge in edges}

    if len(types) > 1:
        raise ValueError("Mixed directed and undirected edges")

    return "->" in types


def reachable(start, graph):
    seen = {start}
    stack = [start]

    while stack:
        u = stack.pop()
        for v in graph[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)

    return seen


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


def find_blocks(graph):
    discovery = {}
    low = {}
    parent = {}
    children = {}
    edge_stack = []
    blocks = []
    articulations = set()
    time = 0

    for root in graph:
        if root in discovery:
            continue

        parent[root] = None
        children[root] = 0
        time += 1
        discovery[root] = low[root] = time

        stack = [(root, iter(graph[root]))]

        while stack:
            u, neighbours = stack[-1]

            try:
                v = next(neighbours)
            except StopIteration:
                stack.pop()
                p = parent[u]

                if p is None:
                    if children[u] > 1:
                        articulations.add(u)
                    if not graph[u]:
                        blocks.append({u})
                else:
                    low[p] = min(low[p], low[u])

                    if low[u] >= discovery[p]:
                        if parent[p] is not None:
                            articulations.add(p)

                        block = set()

                        while edge_stack:
                            a, b = edge_stack.pop()
                            block.update((a, b))

                            if a == p and b == u:
                                break

                        if block:
                            blocks.append(block)

                continue

            if v == parent[u]:
                continue

            if v not in discovery:
                parent[v] = u
                children[u] += 1
                children[v] = 0
                edge_stack.append((u, v))

                time += 1
                discovery[v] = low[v] = time
                stack.append((v, iter(graph[v])))

            elif discovery[v] < discovery[u]:
                low[u] = min(low[u], discovery[v])
                edge_stack.append((u, v))

    return blocks, articulations


def undirected_answer(graph, red, s, t):
    if s == t:
        return s in red

    blocks, arts = find_blocks(graph)
    art_list = list(arts)
    number_of_blocks = len(blocks)

    art_nodes = {
        v: number_of_blocks + i
        for i, v in enumerate(art_list)
    }

    tree = [[] for _ in range(number_of_blocks + len(arts))]
    vertex_block = {}
    red_blocks = []

    for i, block in enumerate(blocks):
        red_blocks.append(bool(block & red))

        for v in block:
            if v in arts:
                a = art_nodes[v]
                tree[i].append(a)
                tree[a].append(i)
            else:
                vertex_block[v] = i

    def get_node(v):
        if v in arts:
            return art_nodes[v]
        return vertex_block.get(v)

    start = get_node(s)
    end = get_node(t)

    if start is None or end is None:
        return False

    parents = {start: -1}
    stack = [start]

    while stack and end not in parents:
        u = stack.pop()

        for v in tree[u]:
            if v not in parents:
                parents[v] = u
                stack.append(v)

    if end not in parents:
        return False

    node = end

    while node != -1:
        if node < number_of_blocks:
            if red_blocks[node]:
                return True
        else:
            v = art_list[node - number_of_blocks]
            if v in red:
                return True

        node = parents[node]

    return False


def solve_some(filename):
    graph, s, t, red = load_graph(filename)

    if s == t:
        return s in red

    if is_directed_file(filename):
        if not is_dag(graph):
            return "?!"

        reverse = {v: [] for v in graph}

        for u in graph:
            for v in graph[u]:
                reverse[v].append(u)

        from_s = reachable(s, graph)
        to_t = reachable(t, reverse)

        return bool(red & from_s & to_t)

    return undirected_answer(graph, red, s, t)


if __name__ == "__main__":
    filename = sys.argv[1]
    answer = solve_some(filename)
    print(str(answer).lower())
