# aiml/pathfinding.py

class Node:
    """A node class for A* Pathfinding"""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar_pathfinding(grid_size, start, end, obstacles):
    """Returns a list of tuples as a path from start to end avoiding obstacles."""
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list = [start_node]
    closed_list = []

    while open_list:
        # choose lowest f node
        current_node = min(open_list, key=lambda o: o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        # goal reached
        if current_node == end_node:
            path = []
            curr = current_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            return path[::-1]

        # explore neighbors
        children = []
        for move in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_pos = (current_node.position[0] + move[0],
                       current_node.position[1] + move[1])

            # valid boundaries
            if not (0 <= new_pos[0] < grid_size and 0 <= new_pos[1] < grid_size):
                continue
            # obstacle check
            if new_pos in obstacles:
                continue

            children.append(Node(current_node, new_pos))

        # process children
        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            # if already in open list with lower g, skip
            if any(open_node for open_node in open_list
                   if child == open_node and child.g > open_node.g):
                continue

            open_list.append(child)

    return None
