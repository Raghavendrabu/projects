# Heuristic cost for each node
H = {'A': 11, 'B': 6, 'C': 99, 'D': 1, 'E': 7, 'G': 0}

# Graph representation with edge weights
G = {
    'A': [('B', 2), ('E', 3)], 'B': [('A', 2), ('C', 1), ('G', 9)], 'C': [('B', 1)],
    'D': [('E', 6), ('G', 1)], 'E': [('A', 3), ('D', 6)], 'G': [('B', 9), ('D', 1)]
}

# A* search algorithm
def aStar(s, e):
    op, cl = {s}, set() # open and closed sets
    g, par = {s: 0}, {s: s} # cost values and parent tracking
    while op:
        n = min(op, key=lambda x: g[x] + H[x]) # choose node with lowest f(n)
        if n == e: # if target reached, reconstruct path
            p = []
            while par[n] != n:
                p.append(n)
                n = par[n]
            print(f"Path found: {[s] + p[::-1]}")
            return
        op.remove(n)
        cl.add(n)
        for m, w in G.get(n, []): # process neighborsa
            if m not in op and m not in cl:
                op.add(m)
                par[m], g[m] = n, g[n] + w
            elif g[n] + w < g.get(m, 999): # update if shorter path found
                par[m], g[m] = n, g[n] + w
                if m in cl:
                    cl.remove(m)
                    op.add(m)

aStar('A', 'G')