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
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list = [start_node]
    closed_list = []

    while open_list:
        current_node = min(open_list, key=lambda o: o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if not (0 <= node_position[0] < grid_size and 0 <= node_position[1] < grid_size):
                continue
            if node_position in obstacles:
                continue

            new_node = Node(current_node, node_position)
            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            if any(open_node for open_node in open_list if child == open_node and child.g > open_node.g):
                continue

            open_list.append(child)
    return None
