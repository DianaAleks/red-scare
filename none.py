from collections import deque
import os

# BFS
def read_graph(filename):
    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()

    n,m,r =map(int,lines[0].split())
    s,t = lines[1].split()

    red = set()
    neighbours = {}
    for position in range(2,n+2):
        parts = lines[position].split()
        if len(parts)>1 :
            red.add(parts[0])
        neighbours[parts[0]]= []

    for position in range (n+2,n+m+2):
        parts = lines[position].split()
        first = parts[0]
        second = parts[-1]
        neighbours[first].append(second)
        if parts[1] == '--':
            neighbours[second].append(first)
    return s,t,red,neighbours


def none(s,t,red,neighbours):
    distance = {s:0}
    queue = deque([s])

    while queue:
        u = queue.popleft()
        for w in neighbours[u]:
            if (w not in distance) and (w not in red or w==t):
                distance[w]= distance[u]+1
                queue.append(w)

    if t in distance:
        return(distance[t])
    else:
        return(-1)

def main():
    data = ('red-scare_documents/data/')
    for file in os.listdir(data):
        if file.endswith(".txt"):
            s,t,red,neighbours = read_graph(data+file)
            print(file, none(s,t,red,neighbours))

main()
