# === DAY 2: PATHFINDING


neigh_fn = neighbors_8 if allow_diagonal else neighbors_4
diag = allow_diagonal


open_heap = []
gscore = {start: 0.0}
fscore = {start: heuristic(start, goal, diag)}
heapq.heappush(open_heap, (fscore[start], gscore[start], start))
came_from = {}


while open_heap:
_, cur_g, current = heapq.heappop(open_heap)
if cur_g != gscore.get(current, None):
continue
if current == goal:
# reconstruct
path = [current]
while current in came_from:
current = came_from[current]
path.append(current)
path.reverse()
return path
for nb in neigh_fn(current[0], current[1], max_c, max_r):
nc, nr = nb
if is_blocked(nc, nr):
continue
# corner cut prevention for diagonal
if diag and abs(nc-current[0])==1 and abs(nr-current[1])==1:
if is_blocked(current[0], nr) or is_blocked(nc, current[1]):
continue
cost = 1.41421356 if diag and abs(nc-current[0])==1 and abs(nr-current[1])==1 else 1.0
tentative_g = gscore[current] + cost
if tentative_g < gscore.get(nb, float('inf')):
came_from[nb] = current
gscore[nb] = tentative_g
f = tentative_g + heuristic(nb, goal, diag)
heapq.heappush(open_heap, (f, tentative_g, nb))
return []