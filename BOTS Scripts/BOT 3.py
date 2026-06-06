# pip install playwright
# python -m playwright install

from playwright.sync_api import sync_playwright
import math, random, time

# ---------- Helpers "human-like" ----------
def wait_and_center(loc):
    loc.wait_for(state="visible")
    loc.scroll_into_view_if_needed()
    box = loc.bounding_box()
    if not box:
        raise RuntimeError("No pude obtener bounding_box")
    cx = box["x"] + box["width"] / 2
    cy = box["y"] + box["height"] / 2
    return cx, cy

def minimum_jerk(t):
    return 10*t**3 - 15*t**4 + 6*t**5

def catmull_rom(path, samples=80):
    if len(path) < 2: return path
    P = [path[0]] + path + [path[-1]]
    pts = []
    segs = len(P) - 3
    per = max(2, samples // max(1, segs))
    for i in range(segs):
        p0, p1, p2, p3 = P[i], P[i+1], P[i+2], P[i+3]
        for j in range(per):
            t = j/(per-1)
            t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            pts.append((x, y))
    return pts

def random_waypoints(start, goal):
    x0,y0 = start; x1,y1 = goal
    dx,dy = (x1-x0),(y1-y0)
    dist = math.hypot(dx,dy) or 1.0
    n_mid = random.randint(2,3)
    wps = [start]
    for i in range(1, n_mid+1):
        frac = i/(n_mid+1)
        nx, ny = (-dy/dist, dx/dist)  # perpendicular
        off = random.uniform(-0.08, 0.10) * dist
        wps.append((x0 + dx*frac + nx*off, y0 + dy*frac + ny*off))
    # overshoot
    overs = 0.02 * dist
    wps.append((x1 + (dx/dist)*overs, y1 + (dy/dist)*overs))
    wps.append((x1 + random.uniform(-1.0,1.0), y1 + random.uniform(-1.0,1.0)))
    wps.append(goal)
    return wps

def move_mouse_smooth(page, goal, prev_end=None, total_ms=(800,1200)):
    # elegir inicio: del final previo o un punto aleatorio en pantalla
    if prev_end:
        sx, sy = prev_end
        sx += random.uniform(-40, 40)
        sy += random.uniform(-40, 40)
    else:
        box = page.viewport_size
        sx = random.uniform(50, box["width"]-50)
        sy = random.uniform(20, box["height"]//3)
    start = (sx, sy)

    path = catmull_rom(random_waypoints(start, goal), samples=random.randint(70,95))
    n = len(path)
    T = [minimum_jerk(i/(n-1)) for i in range(n)]
    weights = [1] + [max(1e-4, T[i]-T[i-1]) for i in range(1,n)]
    dur = random.uniform(*total_ms)
    s = sum(weights)
    delays = [max(1, int(dur*w/s)) for w in weights]

    jitter = random.uniform(0.05, 0.2)
    last = None
    for (x,y), d in zip(path, delays):
        page.mouse.move(x+random.uniform(-jitter,jitter),
                        y+random.uniform(-jitter,jitter), steps=1)
        page.wait_for_timeout(d)
        last = (x,y)
    return last

def click_press(page, hold=(85,130)):
    h = random.randint(*hold)
    page.mouse.down()
    page.wait_for_timeout(h)
    page.mouse.up()

def type_text(page, text, total_ms=(900,1500)):
    tot = random.uniform(*total_ms)
    base = tot / max(1,len(text))
    for ch in text:
        delay = max(15, base + random.uniform(-0.3*base, 0.3*base))
        page.keyboard.type(ch, delay=delay)

# ---------- Flujo principal ----------
def run_once():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, viewport={"width":1280,"height":800})
        page = context.new_page()

        page.goto("https://localhost:7080/", wait_until="domcontentloaded")

        # Esperas
        page.wait_for_selector("#username", state="visible")
        page.wait_for_selector("#password", state="visible")
        page.wait_for_selector("#submit-button", state="visible")

        ux, uy = wait_and_center(page.locator("#username"))
        px, py = wait_and_center(page.locator("#password"))
        sx, sy = wait_and_center(page.locator("#submit-button"))

        # USERNAME
        end1 = move_mouse_smooth(page, (ux, uy))
        click_press(page)
        type_text(page, "usuarioEjemplo")

        # PASSWORD
        end2 = move_mouse_smooth(page, (px, py), prev_end=end1)
        click_press(page)
        type_text(page, "contraseñaEjemplo")

        # SUBMIT
        move_mouse_smooth(page, (sx, sy), prev_end=end2)
        click_press(page)

        page.wait_for_timeout(1000)
        browser.close()

if __name__ == "__main__":
    for i in range(10):
        run_once()
        time.sleep(random.uniform(0.5, 1.2))
