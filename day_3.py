# ==== Day 3D: WORLD ELEMENTS ====
class Building:
    def __init__(self, pos, size):
        self.pos, self.size = pos, size
    def cells(self):
        return [(self.pos[0]+dx, self.pos[1]+dy)
                for dx in range(self.size[0])
                for dy in range(self.size[1])]

class Depot:
    def __init__(self, pos): self.pos = pos

class Package:
    def __init__(self, source, target):
        self.source, self.target = source, target
        self.assigned = False
        self.delivered = False