

def load_graph(filename):
    with open(filename, "r") as file:
        n, m, r = map(int, file.readline().split())
        s, t = file.readline().split()

        graph = {}
        red_vertices = set()
        # Read vertices
        for line in range(n):
            parts = file.readline().split()
            vertex = parts[0]
            graph[vertex] = []
            if len(parts) > 1 and parts[1] == "*":
                red_vertices.add(vertex)

        # Read edges
        for line in range(m):
            u, direction, v = file.readline().split()
            graph[u].append(v)
            # If undirected edge, add edges both ways
            if direction == "--":
                graph[v].append(u)

    return graph, s, t, red_vertices