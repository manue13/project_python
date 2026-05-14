import pygame, heapq, math, sys, time

pygame.init()

W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("TIRANA FLY : Depot - Client - Depot")
clock = pygame.time.Clock()

BG = (10, 16, 30)
PANEL_BG = (15, 22, 42)
ROAD_COL = (70, 90, 120)
PATH_COL = (255, 220, 50)
NODE_COL = (40, 80, 140)
NODE_START = (255, 160, 30)
NODE_END = (80, 200, 100)
NODE_DONE = (200, 220, 255)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (255, 60, 60)
GREEN = (80, 200, 100)

F_BIG = pygame.font.SysFont("consolas", 22, bold=True)
F_MED = pygame.font.SysFont("consolas", 16)
F_SML = pygame.font.SysFont("consolas", 13)
F_TITLE = pygame.font.SysFont("consolas", 28, bold=True)

NODES = {
    "Magazina Perëndim": (180, 320),
    "Magazina Qendër": (430, 300),
    "Magazina Lindje": (700, 300),

    "1. Veri": (320, 120),
    "2. Lindje": (760, 150),
    "3. Lindje Jug": (720, 450),
    "4. Qendër": (430, 180),
    "5. Perëndim": (220, 420),
    "6. Jug Perëndim": (300, 580),
    "7. Jug": (480, 580),
    "8. Jug Lindje": (680, 580),
}

EDGES = [
    ("Magazina Perëndim", "1. Veri", 7),
    ("Magazina Perëndim", "5. Perëndim", 3),
    ("Magazina Perëndim", "6. Jug Perëndim", 6),

    ("Magazina Qendër", "4. Qendër", 2),
    ("Magazina Qendër", "7. Jug", 5),
    ("Magazina Qendër", "8. Jug Lindje", 8),

    ("Magazina Lindje", "2. Lindje", 4),
    ("Magazina Lindje", "3. Lindje Jug", 5),

    ("Magazina Perëndim", "Magazina Qendër", 5),
    ("Magazina Qendër", "Magazina Lindje", 5),
    ("Magazina Perëndim", "Magazina Lindje", 9),

    ("1. Veri", "4. Qendër", 6),
    ("4. Qendër", "2. Lindje", 7),
    ("4. Qendër", "5. Perëndim", 5),
    ("5. Perëndim", "6. Jug Perëndim", 4),
    ("6. Jug Perëndim", "7. Jug", 3),
    ("7. Jug", "8. Jug Lindje", 4),
    ("8. Jug Lindje", "3. Lindje Jug", 4),
    ("3. Lindje Jug", "2. Lindje", 6),
]

graph = {node: [] for node in NODES}

for u, v, w in EDGES:
    graph[u].append((v, w))
    graph[v].append((u, w))


def dijkstra_steps(start, end):
    dist = {node: float("inf") for node in NODES}
    prev = {node: None for node in NODES}
    dist[start] = 0

    pq = [(0, start)]
    visited = set()
    steps = []

    while pq:
        d, u = heapq.heappop(pq)

        if u in visited:
            continue

        visited.add(u)
        steps.append(("visit", u, dict(dist), set(visited)))

        if u == end:
            break

        for v, w in graph[u]:
            nd = d + w

            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
                steps.append(("relax", u, v, w, dict(dist), set(visited)))

    path = []
    cur = end

    while cur is not None:
        path.append(cur)
        cur = prev[cur]

    path.reverse()
    return steps, path, dist


def build_round_trip(depot, client):
    steps_1, path_1, dist_1 = dijkstra_steps(depot, client)
    steps_2, path_2, dist_2 = dijkstra_steps(client, depot)

    full_path = path_1 + path_2[1:]
    total_cost = dist_1[client] + dist_2[depot]
    full_steps = steps_1 + steps_2

    return full_steps, full_path, total_cost


def lerp(a, b, t):
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t
    )


def draw_drone(pos):
    x, y = int(pos[0]), int(pos[1])
    pygame.draw.circle(screen, RED, (x, y), 18)
    pygame.draw.circle(screen, WHITE, (x, y), 18, 3)
    pygame.draw.line(screen, WHITE, (x - 22, y), (x + 22, y), 5)
    pygame.draw.line(screen, WHITE, (x, y - 22), (x, y + 22), 5)
    pygame.draw.line(screen, WHITE, (x - 10, y + 15), (x + 10, y + 15), 4)


def is_edge_in_path(u, v, route):
    for i in range(len(route) - 1):
        a = route[i]
        b = route[i + 1]
        if (u == a and v == b) or (u == b and v == a):
            return True
    return False


def draw_scene():
    MAP_W = 900
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL_BG, (MAP_W, 0, W - MAP_W, H))
    pygame.draw.line(screen, (40, 60, 90), (MAP_W, 0), (MAP_W, H), 2)

    for u, v, w in EDGES:
        p1 = NODES[u]
        p2 = NODES[v]
        in_path = is_edge_in_path(u, v, path)
        color = PATH_COL if in_path else ROAD_COL
        width = 6 if in_path else 3
        pygame.draw.line(screen, color, p1, p2, width)

        mx = (p1[0] + p2[0]) // 2
        my = (p1[1] + p2[1]) // 2
        screen.blit(F_SML.render(str(w), True, GOLD), (mx, my))

    for name, pos in NODES.items():
        if name == depot:
            color = NODE_START
        elif name == client:
            color = NODE_END
        elif name in visited_anim:
            color = NODE_DONE
        else:
            color = NODE_COL

        pygame.draw.circle(screen, color, pos, 22)
        pygame.draw.circle(screen, WHITE, pos, 22, 2)

        label = F_SML.render(name, True, WHITE)
        screen.blit(label, (pos[0] - label.get_width() // 2, pos[1] + 28))

        if dist_anim and name in dist_anim and dist_anim[name] < float("inf"):
            d_label = F_SML.render(str(dist_anim[name]), True, GOLD)
            screen.blit(d_label, (pos[0] - d_label.get_width() // 2, pos[1] - 38))

    if drone_pos:
        draw_drone(drone_pos)

    title = F_TITLE.render("TIRANA FLY — DEPOT → CLIENT → DEPOT", True, WHITE)
    screen.blit(title, (MAP_W // 2 - title.get_width() // 2, 20))

    px = MAP_W + 20
    py = 20

    screen.blit(F_BIG.render("Controls", True, GOLD), (px, py))
    py += 40

    controls = [
        "Click depot/start node",
        "Click client node",
        "SPACE = next Dijkstra step",
        "A = auto play",
        "ENTER = move drone",
        "R = restart",
        "ESC = exit"
    ]

    for c in controls:
        screen.blit(F_SML.render(c, True, WHITE), (px, py))
        py += 22

    py += 20
    screen.blit(F_MED.render(f"Depot: {depot or '-'}", True, NODE_START), (px, py))
    py += 25
    screen.blit(F_MED.render(f"Client: {client or '-'}", True, NODE_END), (px, py))
    py += 35

    screen.blit(F_SML.render(message, True, GREEN), (px, py))
    py += 35

    if path:
        screen.blit(F_MED.render("Round trip route:", True, GOLD), (px, py))
        py += 25

        for node in path[:12]:
            screen.blit(F_SML.render("→ " + node, True, WHITE), (px, py))
            py += 19

        if len(path) > 12:
            screen.blit(F_SML.render("...", True, WHITE), (px, py))
            py += 19

        py += 10
        screen.blit(F_MED.render(f"Total cost: {total_cost}", True, GOLD), (px, py))

    pygame.display.flip()


def reset():
    global depot, client, phase, all_steps, step_idx
    global path, total_cost, visited_anim, dist_anim
    global auto_play, drone_pos, drone_seg, drone_t, message

    depot = None
    client = None
    phase = "pick_depot"

    all_steps = []
    step_idx = 0

    path = []
    total_cost = 0
    visited_anim = set()
    dist_anim = {}

    auto_play = False

    drone_pos = None
    drone_seg = 0
    drone_t = 0

    message = "Click the depot/start node."


reset()
last_auto = 0
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                reset()

            elif event.key == pygame.K_SPACE and path:
                if step_idx < len(all_steps):
                    s = all_steps[step_idx]

                    if s[0] == "visit":
                        _, u, d, vis = s
                        dist_anim = d
                        visited_anim = vis
                        message = f"Visit: {u}"
                    else:
                        _, u, v, w, d, vis = s
                        dist_anim = d
                        visited_anim = vis
                        message = f"Relax: {u} → {v}"

                    step_idx += 1
                else:
                    message = "Dijkstra steps finished. Press ENTER."

            elif event.key == pygame.K_a and path:
                auto_play = not auto_play
                message = "Auto play ON" if auto_play else "Auto play OFF"

            elif event.key == pygame.K_RETURN and path:
                phase = "moving"
                drone_pos = NODES[path[0]]
                drone_seg = 0
                drone_t = 0
                message = "Drone moving..."

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if mx < 900:
                for name, pos in NODES.items():
                    if math.hypot(mx - pos[0], my - pos[1]) < 25:
                        if phase == "pick_depot":
                            depot = name
                            phase = "pick_client"
                            message = "Now click the client node."

                        elif phase == "pick_client" and name != depot:
                            client = name
                            all_steps, path, total_cost = build_round_trip(depot, client)
                            phase = "ready"
                            message = "Round trip ready. Press SPACE/A or ENTER."

                        break

    if auto_play and path:
        now = time.time()

        if now - last_auto > 0.35:
            last_auto = now

            if step_idx < len(all_steps):
                s = all_steps[step_idx]

                if s[0] == "visit":
                    _, u, d, vis = s
                    dist_anim = d
                    visited_anim = vis
                    message = f"Visit: {u}"
                else:
                    _, u, v, w, d, vis = s
                    dist_anim = d
                    visited_anim = vis
                    message = f"Relax: {u} → {v}"

                step_idx += 1
            else:
                auto_play = False
                message = "Steps finished. Press ENTER."

    if phase == "moving" and path and drone_seg < len(path) - 1:
        drone_t += dt * 0.8

        if drone_t >= 1:
            drone_t = 0
            drone_seg += 1

            if drone_seg >= len(path) - 1:
                phase = "done"
                drone_pos = NODES[path[-1]]
                message = "Drone arrived back at depot!"

        if drone_seg < len(path) - 1:
            p1 = NODES[path[drone_seg]]
            p2 = NODES[path[drone_seg + 1]]
            drone_pos = lerp(p1, p2, drone_t)

    draw_scene()

pygame.quit()
sys.exit()

