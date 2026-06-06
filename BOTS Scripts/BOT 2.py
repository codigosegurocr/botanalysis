from playwright.sync_api import sync_playwright
import math, random, time

# ----------------- Utilidades -----------------
def center_of(page, selector):
    loc = page.locator(selector)
    loc.wait_for(state="visible")
    box = loc.bounding_box()
    return (box["x"] + box["width"]/2.0, box["y"] + box["height"]/2.0)

def perp_unit(dx, dy):
    d = math.hypot(dx, dy) or 1.0
    return (-dy/d, dx/d)

def minimum_jerk(t):
    return 10*t**3 - 15*t**4 + 6*t**5

def catmull_rom(points, samples):
    if len(points) < 2: return points
    P = [points[0]] + points + [points[-1]]
    curves = []
    segs = len(P) - 3
    samples_per = max(2, samples // max(1, segs))
    for i in range(segs):
        p0, p1, p2, p3 = P[i], P[i+1], P[i+2], P[i+3]
        for j in range(samples_per):
            t = j / (samples_per - 1)
            t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t +
                     (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 +
                     (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t +
                     (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 +
                     (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            curves.append((x, y))
    return curves

# --------------- Trayectoria variable ---------------
def make_random_path(start, goal):
    x0, y0 = start; x1, y1 = goal
    dx, dy = x1-x0, y1-y0
    dist = math.hypot(dx, dy) or 1.0
    nx, ny = perp_unit(dx, dy)

    waypoints = [start]

    # 2–4 puntos intermedios con offsets aleatorios
    n_mid = random.randint(2, 4)
    for i in range(1, n_mid+1):
        frac = i/(n_mid+1)
        px = x0 + dx*frac + nx*random.uniform(-0.12, 0.12)*dist
        py = y0 + dy*frac + ny*random.uniform(-0.12, 0.12)*dist
        waypoints.append((px, py))

    # Overshoot con magnitud aleatoria
    overshoot_mag = random.uniform(0.01, 0.05)*dist
    waypoints.append((x1 + (dx/dist)*overshoot_mag,
                      y1 + (dy/dist)*overshoot_mag))

    # Micro-corrección
    waypoints.append((x1 + random.uniform(-1.5, 1.5),
                      y1 + random.uniform(-1.5, 1.5)))

    waypoints.append(goal)

    samples = random.randint(60, 110)
    path = catmull_rom(waypoints, samples=samples)

    # jitter dinámico
    jitter = random.uniform(0.05, 0.3)
    path = [(x+random.uniform(-jitter,jitter),
             y+random.uniform(-jitter,jitter)) for x,y in path]

    return path

def move_mouse(page, selector, total_ms_range=(650, 1500)):
    target = center_of(page, selector)
    # inicio aleatorio relativo
    start = (target[0]-random.uniform(80,140),
             target[1]-random.uniform(50,90))
    path = make_random_path(start, target)

    n = len(path)
    T = [minimum_jerk(i/(n-1)) for i in range(n)]
    weights = [1] + [max(1e-3,T[i]-T[i-1]) for i in range(1,n)]
    total_ms = random.uniform(*total_ms_range)
    s = sum(weights)
    delays = [max(1,int(total_ms*w/s)) for w in weights]

    for (x,y),d in zip(path,delays):
        page.mouse.move(x,y,steps=1)
        page.wait_for_timeout(d)

def click_press(page):
    hold = random.randint(80,150)
    page.mouse.down()
    page.wait_for_timeout(hold)
    page.mouse.up()

def type_text(page, text):
    total = random.uniform(900,1600)
    base = total/max(1,len(text))
    for ch in text:
        delay = max(15, base+random.uniform(-0.3*base,0.3*base))
        page.keyboard.type(ch, delay=delay)

def micro_pause(page):
    page.wait_for_timeout(random.randint(90,300))

# ---------------- Flujo principal ----------------
def run_once():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://localhost:7080/", wait_until="domcontentloaded")

        move_mouse(page,"#username")
        click_press(page)
        micro_pause(page)
        type_text(page,"usuarioEjemplo")

        move_mouse(page,"#password")
        click_press(page)
        micro_pause(page)
        type_text(page,"contraseñaEjemplo")

        move_mouse(page,"#submit-button")
        click_press(page)

        page.wait_for_timeout(random.randint(400,800))
        browser.close()

if __name__=="__main__":
    for _ in range(5):  # pon más si quieres repetir
        run_once()
        time.sleep(random.uniform(0.5,1.2))
