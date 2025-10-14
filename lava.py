"""
volcano_realistic_full.py
Simulasi Gunung Berapi Realistis untuk pameran
Kontrol:
  ←  : dorong lempeng (tambah tekanan)
  →  : kurangi tekanan (opsional)
  SPACE : paksa erupsi
  R  : reset
  ESC: keluar
Klik mouse di area puncak juga memicu erupsi kecil.
"""

import pygame, sys, random, math
from pygame.locals import *

# -------------------------
# Inisialisasi
# -------------------------
pygame.init()
try:
    pygame.mixer.init()
except:
    pass

# Fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

clock = pygame.time.Clock()
FPS = 60

# Font
TITLE_FONT = pygame.font.Font(None, 48)
MAIN_FONT = pygame.font.Font(None, 28)

# -------------------------
# Warna & konstanta
# -------------------------
SKY_DAY = (85, 170, 255)
SKY_WARN = (255, 140, 80)
SKY_NIGHT = (25, 25, 50)

MOUNTAIN_BASE = (70, 50, 40)
MOUNTAIN_HIGHLIGHT = (110, 90, 70)
LAVA_CORE = (255, 140, 0)
LAVA_GLOW = (255, 200, 60)
SMOKE_BASE = (120, 120, 120)
ASH = (40, 40, 40)

# Kontrol tekanan / erupsi
pressure = 0.0
PRESSURE_MAX = 160.0
eruption_active = False
eruption_timer = 0
quake = 0.0

# Partikel / lava / smoke
lava_particles = []      # eruptive projectiles
lava_flows = []          # continuous flow particles down slope
smoke_particles = []     # rising smoke puffs
ash_particles = []

# Lempeng visual (kiri-kanan)
plate_offset = 0.0

# Info teks
info_texts = [
    "Lempeng saling bertumbukan → tekanan meningkat.",
    "Magma naik ke permukaan, kawah memanas.",
    "Tekanan puncak → letusan! Lava, asap, dan abu keluar.",
]
info_idx = 0
info_counter = 0

# -------------------------
# Fungsi util
# -------------------------
def clamp(v, a, b):
    return max(a, min(b, v))

def draw_sky(surface, t):
    """Gradasi langit: t dari 0 (siang) ke 1 (letusan/merah)"""
    top = (
        int(SKY_DAY[0] * (1 - t) + SKY_NIGHT[0] * t),
        int(SKY_DAY[1] * (1 - t) + SKY_NIGHT[1] * t),
        int(SKY_DAY[2] * (1 - t) + SKY_NIGHT[2] * t),
    )
    bottom = (
        int(SKY_WARN[0] * t + SKY_DAY[0] * (1 - t)),
        int(SKY_WARN[1] * t + SKY_DAY[1] * (1 - t)),
        int(SKY_WARN[2] * t + SKY_DAY[2] * (1 - t)),
    )
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_mountain_base(surface, quake_offset=0):
    """Gambar gunung semi-3D dengan beberapa layer polygon"""
    peak_x = CENTER_X + int(math.sin(pygame.time.get_ticks() * 0.001) * 6)  # sedikit goyangan alami
    peak_y = CENTER_Y - 180
    # lapisan paling belakang (bayangan)
    left = (CENTER_X - 360 + int(quake_offset), CENTER_Y + 210)
    right = (CENTER_X + 360 + int(quake_offset), CENTER_Y + 210)
    peak = (peak_x, peak_y - int(quake_offset * 0.2))
    pygame.draw.polygon(surface, tuple(int(c*0.6) for c in MOUNTAIN_BASE), [left, right, (peak_x, peak_y - 10)])
    # lapisan utama
    main_poly = [
        (CENTER_X - 320 + int(quake_offset*0.4), CENTER_Y + 200),
        (CENTER_X - 60 + int(quake_offset*0.2), CENTER_Y + 40),
        (peak_x, peak_y),
        (CENTER_X + 60 + int(-quake_offset*0.2), CENTER_Y + 40),
        (CENTER_X + 320 + int(-quake_offset*0.4), CENTER_Y + 200)
    ]
    pygame.draw.polygon(surface, MOUNTAIN_BASE, main_poly)
    # highlight sisi kiri (memberi kesan 3D)
    highlight = [
        (CENTER_X - 320 + int(quake_offset*0.4), CENTER_Y + 200),
        (CENTER_X - 60 + int(quake_offset*0.2), CENTER_Y + 40),
        (CENTER_X, CENTER_Y + 40),
        (CENTER_X, CENTER_Y + 200)
    ]
    pygame.draw.polygon(surface, MOUNTAIN_HIGHLIGHT, highlight)
    # kawah
    pygame.draw.ellipse(surface, (25, 25, 25), (CENTER_X - 58, CENTER_Y - 210, 116, 42))

def spawn_eruption_shot(strength=1.0):
    """Proyektil lava besar (letusan)"""
    for _ in range(int(24 * strength)):
        angle = random.uniform(-math.pi/3, math.pi/3)
        speed = random.uniform(6, 14) * (0.8 + 0.8*strength)
        vx = math.cos(angle) * speed + random.uniform(-1, 1)
        vy = -abs(math.sin(angle) * speed) + random.uniform(-2, 2)
        x = CENTER_X + random.uniform(-20, 20)
        y = CENTER_Y - 200
        size = random.randint(4, 9)
        lava_particles.append([x, y, vx, vy, size, random.randint(30, 90)])  # life ticks

def spawn_lava_flow():
    """Flow lava lambat yang mengalir ke sisi (continual)"""
    side = random.choice([-1, 1])
    start_x = CENTER_X + side * random.uniform(10, 40)
    start_y = CENTER_Y - 170 + random.uniform(-6, 6)
    vx = side * random.uniform(0.6, 1.6)
    vy = random.uniform(0.4, 1.2)
    size = random.randint(6, 12)
    lava_flows.append([start_x, start_y, vx, vy, size, 200 + random.randint(0,150)])

def spawn_smoke_puff():
    x = CENTER_X + random.uniform(-40, 40)
    y = CENTER_Y - 180 + random.uniform(-8, 8)
    vx = random.uniform(-0.4, 0.4)
    vy = random.uniform(-1.2, -0.6)
    life = random.randint(80, 160)
    smoke_particles.append([x, y, vx, vy, life, random.randint(10, 26)])

def spawn_ash():
    x = random.uniform(0, WIDTH)
    y = random.uniform(-40, -10)
    vx = random.uniform(-0.6, 0.6)
    vy = random.uniform(0.3, 1.2)
    life = random.randint(120, 280)
    ash_particles.append([x, y, vx, vy, life, random.randint(2, 4)])

# -------------------------
# Load optional sounds safely
# -------------------------
try:
    rumble_snd = pygame.mixer.Sound("rumble.wav")
    eruption_snd = pygame.mixer.Sound("eruption.wav")
except Exception:
    rumble_snd = None
    eruption_snd = None

# -------------------------
# Reset fungsi
# -------------------------
def reset_all():
    global pressure, eruption_active, eruption_timer, quake
    global lava_particles, lava_flows, smoke_particles, ash_particles, plate_offset
    pressure = 0.0
    eruption_active = False
    eruption_timer = 0
    quake = 0.0
    lava_particles.clear()
    lava_flows.clear()
    smoke_particles.clear()
    ash_particles.clear()
    plate_offset = 0.0

reset_all()

# -------------------------
# Loop utama
# -------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # detik
    # event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_r:
                reset_all()
            if event.key == K_SPACE:
                # paksa erupsi
                pressure = PRESSURE_MAX
        if event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # jika klik di area puncak (kawah), memicu letusan kecil
            if (CENTER_X - 100 < mx < CENTER_X + 100) and (CENTER_Y - 250 < my < CENTER_Y - 130):
                # sedikit efek
                spawn_eruption_shot(0.8)
                for _ in range(6):
                    spawn_smoke_puff()
                pressure += 25
                if eruption_snd:
                    eruption_snd.play()

    # tombol ditekan (kontrol interaktif)
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        pressure += 80.0 * dt   # cepat naik dengan hold tombol
        plate_offset = clamp(plate_offset + 80.0 * dt, -200, 200)
        if rumble_snd and not eruption_active:
            rumble_snd.play(maxtime=200)
    if keys[K_RIGHT]:
        pressure -= 100.0 * dt
        plate_offset = clamp(plate_offset - 60.0 * dt, -200, 200)

    pressure = clamp(pressure, 0.0, PRESSURE_MAX * 1.5)

    # visual parameter berdasarkan pressure
    t = clamp(pressure / (PRESSURE_MAX), 0.0, 1.0)  # 0..1 : pengaruh warna langit
    # draw background sky gradient (lebih oranye jika t tinggi)
    draw_sky(screen, min(1.0, t * 0.9))

    # ground (simple)
    pygame.draw.rect(screen, (35, 30, 28), (0, CENTER_Y + 200, WIDTH, HEIGHT - (CENTER_Y + 200)))

    # gambar gunung semi-3D
    draw_mountain_base(screen, quake_offset=plate_offset * 0.02)

    # update erupsi state
    if not eruption_active and pressure >= PRESSURE_MAX:
        eruption_active = True
        eruption_timer = 4.0  # erupsi aktif minimal 4 detik
        if eruption_snd:
            eruption_snd.play()
    if eruption_active:
        eruption_timer -= dt
        quake = clamp(quake + 20.0 * dt, 0, 8)
        # spawn projectiles dan lava flow lebih intens saat erupsi
        if random.random() < 0.25:
            spawn_eruption_shot(1.0)
        if random.random() < 0.8:
            spawn_lava_flow()
        if random.random() < 0.6:
            spawn_smoke_puff()
        if random.random() < 0.7:
            spawn_ash()
        if eruption_timer <= 0:
            eruption_active = False
            quake = 0.0
            pressure *= 0.35  # tekanan turun setelah letusan

    else:
        # non-eruption gentle flows & smoke
        if pressure > 0 and random.random() < 0.04:
            spawn_lava_flow()
        if random.random() < 0.02:
            spawn_smoke_puff()

    # update lava projectiles
    for p in lava_particles[:]:
        p[0] += p[2]  # x
        p[1] += p[3]  # y
        p[3] += 12.0 * dt  # gravity accel scaled by dt
        p[5] -= 1
        # draw glow + core
        glow_surf = pygame.Surface((p[4]*4, p[4]*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 150, 0, 140), (p[4]*2, p[4]*2), int(p[4]*2))
        screen.blit(glow_surf, (p[0]-p[4]*2, p[1]-p[4]*2), special_flags=BLEND_RGBA_ADD)
        pygame.draw.circle(screen, LAVA_CORE, (int(p[0]), int(p[1])), max(1, int(p[4])))
        if p[5] <= 0 or p[1] > HEIGHT + 50:
            lava_particles.remove(p)
            # saat jatuh, timbul asap/abu
            for _ in range(3):
                ash_particles.append([p[0] + random.uniform(-6,6), p[1] + random.uniform(-6,6),
                                      random.uniform(-0.4,0.4), random.uniform(0.2,1.0), random.randint(30,120), random.uniform(2,4)])

    # update lava flows (mengalir di sisi)
    for f in lava_flows[:]:
        f[0] += f[2]
        f[1] += f[3]
        f[5] -= 1
        # draw elongated glowing blob (flow)
        pygame.draw.ellipse(screen, LAVA_GLOW, (f[0]-f[4], f[1]-f[4]//2, f[4]*2, f[4]))
        pygame.draw.ellipse(screen, LAVA_CORE, (f[0]-f[4]//2, f[1]-f[4]//4, f[4], f[4]//2))
        if f[5] <= 0:
            lava_flows.remove(f)

    # update smoke
    for s in smoke_particles[:]:
        s[0] += s[2]
        s[1] += s[3]
        s[4] -= 1
        s[3] -= 0.02  # smoke naik perlahan (vy negatif)
        if s[4] > 0:
            alpha = clamp(int(200 * (s[4] / 140.0)), 10, 220)
            surf = pygame.Surface((int(s[4]*1.2), int(s[4]*1.2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (SMOKE_BASE[0], SMOKE_BASE[1], SMOKE_BASE[2], alpha), (surf.get_width()//2, surf.get_height()//2), int(s[4]*0.35))
            screen.blit(surf, (s[0]-surf.get_width()//2, s[1]-surf.get_height()//2))
        else:
            smoke_particles.remove(s)

    # update ash
    for a in ash_particles[:]:
        a[0] += a[2]
        a[1] += a[3]
        a[4] -= 1
        if a[4] > 0:
            pygame.draw.circle(screen, ASH, (int(a[0]), int(a[1])), int(a[5]))
        else:
            ash_particles.remove(a)

    # overlay cahaya lava di sekitar kawah ketika erupsi (penerangan)
    if eruption_active or pressure > PRESSURE_MAX*0.6:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = clamp(int(120 * (pressure / PRESSURE_MAX)), 0, 200)
        glow.fill((255, 90, 30, alpha))
        screen.blit(glow, (0,0), special_flags=BLEND_RGBA_ADD)

    # teks & UI
    title = TITLE_FONT.render("Simulasi Gunung Berapi & Lempeng Tektonik SMK MUSA", True, (240,240,240))
    screen.blit(title, (CENTER_X - title.get_width()//2, 18))
    hint = MAIN_FONT.render("← dorong lempeng  •  SPACE paksa erupsi  •  R reset  •  ESC keluar", True, (230,230,230))
    screen.blit(hint, (CENTER_X - hint.get_width()//2, HEIGHT - 36))

    # info berganti
    info_counter += 1
    if info_counter % (FPS * 6) == 0:
        info_idx = (info_idx + 1) % len(info_texts)
    info = MAIN_FONT.render(info_texts[info_idx], True, (240,240,240))
    screen.blit(info, (CENTER_X - info.get_width()//2, HEIGHT - 72))

    # indikator pressure bar
    bar_w = 360
    bar_h = 14
    bx = 40
    by = 80
    pygame.draw.rect(screen, (50,50,50), (bx, by, bar_w, bar_h))
    pygame.draw.rect(screen, (200,60,60), (bx, by, int(bar_w * clamp(pressure / PRESSURE_MAX, 0, 1.0)), bar_h))
    ptext = MAIN_FONT.render(f"Pressure: {int(pressure)}", True, (240,240,240))
    screen.blit(ptext, (bx, by+bar_h+6))

    # flip screen
    pygame.display.flip()

# cleanup
pygame.quit()
sys.exit()
