# ==== Day 4D: DRONE CLASS ====
class Drone:
    def __init__(self, depot):
        self.pos = depot.pos
        self.depot = depot
        self.path = []
        self.package = None
        self.target = None
        self.battery = 100
        self.reward = 0  

    def grid(self): return self.pos
    def move_towards(self, target):
        if self.path: self.pos = self.path.pop(0)

    def assign_package(self, pkg, path):
        self.package, self.target, self.path = pkg, pkg.target, path
        pkg.assigned = True

    def step(self, blocked):
        if self.battery <= 0:
            self.reward -= 5
            self.path = a_star_grid(self.grid(), self.depot.pos, blocked)
            if not self.path: return
            self.pos = self.path.pop(0)
            if self.pos == self.depot.pos:
                self.battery = 100
            return

        if self.path:
            self.move_towards(self.path[0])
            self.reward -= 1  
        self.battery -= 0.1

        # Successful delivery
        if self.package and self.grid() == self.package.target.grid():
            self.reward += 10
            self.package.delivered = True
            self.package, self.target = None, None