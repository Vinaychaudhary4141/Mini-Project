# ==== Day 5D: SIMULATOR CORE ====
class Simulator:
    def __init__(self, n_drones=3, n_packages=5):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Drone Delivery RL")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # world
        self.buildings = [Building((10,10),(5,5)), Building((30,20),(6,6))]
        self.depots = [Depot((5,5)), Depot((50,40))]
        self.packages = [Package(random.choice(self.depots),
                                 Depot((random.randint(0,GRID_W-1), random.randint(0,GRID_H-1))))
                         for _ in range(n_packages)]
        self.drones = [Drone(random.choice(self.depots)) for _ in range(n_drones)]

        # blocked grid
        self.blocked = set()
        for b in self.buildings:
            self.blocked.update(b.cells())

        self.t = 0
        self.running = True
        self.selected = 0

    def replan(self):
        for drone in self.drones:
            if not drone.package:
                unassigned = [p for p in self.packages if not p.assigned and not p.delivered]
                if unassigned:
                    pkg = random.choice(unassigned)
                    path = a_star_grid(drone.grid(), pkg.target.pos, self.blocked)
                    if path: drone.assign_package(pkg, path)

    def step(self):
        self.t += 1
        if self.t % 20 == 0: self.replan()
        for d in self.drones: d.step(self.blocked)

    def draw(self):
        self.screen.fill(WHITE)
        # grid
        for x in range(0, SCREEN_W, CELL):
            pygame.draw.line(self.screen, GRAY, (x,0), (x,SCREEN_H))
        for y in range(0, SCREEN_H, CELL):
            pygame.draw.line(self.screen, GRAY, (0,y), (SCREEN_W,y))

        # buildings
        for b in self.buildings:
            for c in b.cells():
                pygame.draw.rect(self.screen, BLACK, (c[0]*CELL, c[1]*CELL, CELL, CELL))

        # depots
        for d in self.depots:
            pygame.draw.rect(self.screen, BLUE, (d.pos[0]*CELL, d.pos[1]*CELL, CELL, CELL))

        # packages
        for p in self.packages:
            color = YELLOW if not p.delivered else GREEN
            pygame.draw.rect(self.screen, color, (p.target.pos[0]*CELL, p.target.pos[1]*CELL, CELL, CELL))

        # drones
        for i, d in enumerate(self.drones):
            color = RED if i == self.selected else GREEN
            pygame.draw.circle(self.screen, color, (d.pos[0]*CELL+CELL//2, d.pos[1]*CELL+CELL//2), CELL//2)

        # HUD info
        d = self.drones[self.selected]
        hud = f"Drone {self.selected} @ {d.grid()} | Battery: {int(d.battery)} | Package: {bool(d.package)} | Reward: {d.reward}"
        text = self.font.render(hud, True, BLACK)
        self.screen.blit(text, (10,10))

        pygame.display.flip()

    def process_input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self.running = False
                elif e.key == pygame.K_TAB: self.selected = (self.selected+1) % len(self.drones)

    def run(self):
        while self.running:
            self.process_input()
            self.step()
            self.draw()
            self.clock.tick(30)
