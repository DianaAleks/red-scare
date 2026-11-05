from collections import deque
import os
from graph_loader import load_graph

# BFS

def none(neighbours,s,t,red):
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
            neighbours,s,t,red = load_graph(data+file)
            print(file, none(neighbours,s,t,red))

main()
