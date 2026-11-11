from pathlib import Path
from collections import deque


def read_graph(filename):
    """Read one Red Scare graph file."""
    path = Path(filename)
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError(f"{path.name}: file is too short")

    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    if len(lines) < 2 + n:
        raise ValueError(f"{path.name}: expected {n} vertex lines")

    vertices = []
    red = set()
    for line in lines[2:2 + n]:
        parts = line.split()
        if len(parts) not in (1, 2):
            raise ValueError(f"{path.name}: invalid vertex line: {line!r}")
        v = parts[0]
        vertices.append(v)
        if len(parts) == 2:
            if parts[1] != "*":
                raise ValueError(f"{path.name}: invalid vertex marker: {line!r}")
            red.add(v)

    if len(vertices) != n or len(set(vertices)) != n:
        raise ValueError(f"{path.name}: vertex count or names are inconsistent")
    if len(red) != r:
        raise ValueError(f"{path.name}: header says {r} red vertices, found {len(red)}")
    vertex_set = set(vertices)
    if s not in vertex_set or t not in vertex_set:
        raise ValueError(f"{path.name}: start or end vertex is missing")

    adjacency = {v: [] for v in vertices}
    reverse = {v: [] for v in vertices}
    edge_lines = lines[2 + n:]
    if len(edge_lines) != m:
        raise ValueError(f"{path.name}: header says {m} edges, found {len(edge_lines)}")

    edge_type = None
    for line in edge_lines:
        parts = line.split()
        if len(parts) != 3 or parts[1] not in ("--", "->"):
            raise ValueError(f"{path.name}: invalid edge line: {line!r}")
        u, operator, v = parts
        if u not in vertex_set or v not in vertex_set:
            raise ValueError(f"{path.name}: edge uses an unknown vertex: {line!r}")
        if edge_type is None:
            edge_type = operator
        elif operator != edge_type:
            raise ValueError(f"{path.name}: mixed directed and undirected edges")

        adjacency[u].append(v)
        reverse[v].append(u)
        if operator == "--":
            adjacency[v].append(u)
            reverse[u].append(v)

    directed = edge_type == "->"
    return vertices, red, s, t, adjacency, reverse, directed


def reachable(start, adjacency):
    """Return all vertices reachable from start using an iterative search."""
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def is_dag(vertices, adjacency, reverse):
    """Check whether a directed graph is acyclic using Kahn's algorithm."""
    indegree = {v: len(reverse[v]) for v in vertices}
    queue = deque(v for v in vertices if indegree[v] == 0)
    visited_count = 0
    while queue:
        u = queue.popleft()
        visited_count += 1
        for v in adjacency[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return visited_count == len(vertices)


def undirected_blocks_and_articulations(vertices, adjacency):
    """Find biconnected components and articulation vertices without recursion."""
    discovery = {}
    low = {}
    parent = {}
    child_count = {}
    edge_stack = []
    blocks = []
    articulations = set()
    clock = 0

    for root in vertices:
        if root in discovery:
            continue

        parent[root] = None
        child_count[root] = 0
        clock += 1
        discovery[root] = low[root] = clock
        frames = [(root, iter(adjacency[root]))]

        while frames:
            u, neighbours = frames[-1]
            try:
                v = next(neighbours)
            except StopIteration:
                frames.pop()
                p = parent[u]
                if p is None:
                    if child_count[u] > 1:
                        articulations.add(u)
                    if not adjacency[u]:
                        blocks.append({u})
                else:
                    low[p] = min(low[p], low[u])
                    if low[u] >= discovery[p]:
                        if parent[p] is not None:
                            articulations.add(p)
                        component = set()
                        while edge_stack:
                            a, b = edge_stack.pop()
                            component.add(a)
                            component.add(b)
                            if a == p and b == u:
                                break
                        if component:
                            blocks.append(component)
                continue

            if v == parent[u]:
                continue

            if v not in discovery:
                parent[v] = u
                child_count[u] += 1
                child_count[v] = 0
                edge_stack.append((u, v))
                clock += 1
                discovery[v] = low[v] = clock
                frames.append((v, iter(adjacency[v])))
            elif discovery[v] < discovery[u]:
                low[u] = min(low[u], discovery[v])
                edge_stack.append((u, v))

    return blocks, articulations

def solve_undirected(vertices, red, s, t, adjacency):
    """Decide whether an undirected simple s-t path contains a red vertex."""
    if s == t:
        return s in red

    blocks, articulations = undirected_blocks_and_articulations(
        vertices, adjacency
    )

    block_count = len(blocks)
    articulation_list = list(articulations)

    articulation_node = {
        v: block_count + i
        for i, v in enumerate(articulation_list)
    }

    tree = [[] for _ in range(block_count + len(articulation_list))]
    vertex_block = {}
    block_has_red_vertex = [False] * block_count

    # Build the block-cut forest.
    for block_id, block in enumerate(blocks):
        for v in block:
            if v in articulations:
                a_node = articulation_node[v]
                tree[block_id].append(a_node)
                tree[a_node].append(block_id)
            else:
                vertex_block[v] = block_id

            if v in red:
                block_has_red_vertex[block_id] = True

    # Find the block-cut-tree node representing a vertex.
    def anchor(v):
        if v in articulations:
            return articulation_node[v]
        return vertex_block.get(v)

    start_node = anchor(s)
    end_node = anchor(t)

    if start_node is None or end_node is None:
        return False

    # Find the unique route between s and t.
    parent_node = {start_node: -1}
    stack = [start_node]

    while stack and end_node not in parent_node:
        u = stack.pop()

        for v in tree[u]:
            if v not in parent_node:
                parent_node[v] = u
                stack.append(v)

    if end_node not in parent_node:
        return False

    # Check whether the route contains a red vertex.
    node = end_node

    while node != -1:
        if node < block_count:
            if block_has_red_vertex[node]:
                return True
        else:
            original_vertex = articulation_list[node - block_count]
            if original_vertex in red:
                return True

        node = parent_node[node]

    return False

    def anchor(v):
        if v in articulations:
            return articulation_node[v]
        return vertex_block.get(v)

    start_node = anchor(s)
    end_node = anchor(t)
    if start_node is None or end_node is None:
        return False

    parent_node = {start_node: -1}
    stack = [start_node]
    while stack and end_node not in parent_node:
        u = stack.pop()
        for v in tree[u]:
            if v not in parent_node:
                parent_node[v] = u
                stack.append(v)

    if end_node not in parent_node:
        return False

    # Only nodes on the unique block-cut-tree route from s to t can matter.
    node = end_node
    while node != -1:
        if node < block_count:
            if block_has_red_non_articulation[node]:
                return True
        else:
            original_vertex = articulation_list[node - block_count]
            if original_vertex in red:
                return True
        node = parent_node[node]

    return False


def solve_some(filename):
    vertices, red, s, t, adjacency, reverse, directed = read_graph(filename)

    if s == t:
        return s in red

    if directed:
        # For a DAG, a path s->v followed by v->t cannot repeat a vertex.
        # Every directed instance in the supplied data set is a DAG.
        if not is_dag(vertices, adjacency, reverse):
            raise ValueError("This directed graph has a cycle; the DAG method does not apply.")
        from_s = reachable(s, adjacency)
        to_t = reachable(t, reverse)
       return bool(red & from_s & to_t)

    return solve_undirected(vertices, red, s, t, adjacency)

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        graph_filename = sys.argv[1]
    else:
        # When run from IDLE, let the user choose a graph file in a window.
        try:
            import tkinter as tk
            from tkinter import filedialog

            window = tk.Tk()
            window.withdraw()
            graph_filename = filedialog.askopenfilename(
                title="Choose a Red Scare graph file",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            window.destroy()
        except Exception:
            graph_filename = input("Enter the full path to a graph file: ").strip().strip('"')

    if not graph_filename:
        print("No file selected.")
    else:
        try:
            answer = solve_some(graph_filename)
            print(f"{Path(graph_filename).name}: {str(answer).lower()}")
        except (OSError, ValueError) as error:
            print(f"Could not process this graph: {error}")
