import pygame, math, random, sys

pygame.init()

# Ambil resolusi layar untuk fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("🌞 Simulasi Tata Surya - Pameran SMK Muhammadiyah 1 Mojokerto")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 48)

# Warna dasar
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Pusat layar (supaya di tengah monitor)
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

# Data planet: (nama, warna, jarak orbit dasar, radius, kecepatan orbit, fakta)
PLANETS = [
    ("Merkurius", (200, 200, 200), 70, 5, 0.05, "Planet terkecil dan terdekat dari Matahari."),
    ("Venus", (255, 180, 0), 110, 8, 0.035, "Planet terpanas dengan atmosfer tebal."),
    ("Bumi", (100, 149, 237), 150, 9, 0.03, "Planet kehidupan dengan air dan oksigen."),
    ("Mars", (188, 39, 50), 190, 7, 0.025, "Planet merah yang dingin dan berbatu."),
    ("Jupiter", (255, 140, 0), 260, 18, 0.02, "Planet terbesar di tata surya."),
    ("Saturnus", (210, 180, 140), 330, 15, 0.015, "Terkenal dengan cincin spektakulernya."),
    ("Uranus", (65, 105, 225), 400, 12, 0.01, "Planet es raksasa yang miring orbitnya."),
    ("Neptunus", (0, 0, 205), 460, 11, 0.008, "Planet terjauh dengan angin super cepat."),
]

# Variabel simulasi
angle = 0
zoom = 1.0
paused = False
selected_planet = None
vote_count = {p[0]: 0 for p in PLANETS}

# Bintang latar
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(300)]

# Suara klik (opsional)
try:
    click_sound = pygame.mixer.Sound("click.wav")
except Exception:
    click_sound = None

# Skalakan orbit agar sesuai resolusi tinggi
orbit_scale = (min(WIDTH, HEIGHT) / 1000)

def draw_background():
    for (x, y) in stars:
        pygame.draw.circle(screen, WHITE, (x, y), random.choice([1, 2]))

def draw_planet(planet, angle):
    name, color, orbit_radius, radius, speed, fact = planet
    scaled_orbit = orbit_radius * orbit_scale
    x = CENTER_X + scaled_orbit * math.cos(angle * speed) * zoom
    y = CENTER_Y + scaled_orbit * math.sin(angle * speed) * zoom
    pygame.draw.circle(screen, (70, 70, 70), (CENTER_X, CENTER_Y), int(scaled_orbit * zoom), 1)
    pygame.draw.circle(screen, color, (int(x), int(y)), int(radius * zoom))
    label = font.render(name, True, WHITE)
    screen.blit(label, (x + 10, y - 10))
    return x, y, radius * zoom

def draw_sun():
    pygame.draw.circle(screen, YELLOW, (CENTER_X, CENTER_Y), int(30 * zoom))
    sun_label = font.render("Matahari", True, WHITE)
    screen.blit(sun_label, (CENTER_X + 40, CENTER_Y - 10))

def draw_ui():
    info = font.render("Zoom: ↑↓ | Pause: Spasi | Klik Planet: Info + Vote | ESC: Keluar", True, (200, 200, 200))
    screen.blit(info, (40, 30))
    title = title_font.render("🌞 Simulasi Tata Surya - SMK Muhammadiyah 1 Mojokerto", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

def show_planet_info(planet):
    panel = pygame.Surface((480, 130))
    panel.fill((20, 20, 20))
    pygame.draw.rect(panel, WHITE, panel.get_rect(), 2)
    name_text = font.render(f"Nama: {planet[0]}", True, WHITE)
    fact_text = font.render(f"Fakta: {planet[5]}", True, WHITE)
    vote_text = font.render(f"Vote: {vote_count[planet[0]]}", True, (255, 215, 0))
    panel.blit(name_text, (20, 20))
    panel.blit(fact_text, (20, 55))
    panel.blit(vote_text, (20, 90))
    screen.blit(panel, (50, HEIGHT - 180))

running = True
while running:
    screen.fill(BLACK)
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_UP:
                zoom = min(zoom + 0.1, 2.5)
            if event.key == pygame.K_DOWN:
                zoom = max(zoom - 0.1, 0.5)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for planet in PLANETS:
                name, color, orbit_radius, radius, speed, fact = planet
                scaled_orbit = orbit_radius * orbit_scale
                x = CENTER_X + scaled_orbit * math.cos(angle * speed) * zoom
                y = CENTER_Y + scaled_orbit * math.sin(angle * speed) * zoom
                if math.hypot(x - mx, y - my) < radius * 2 * zoom:
                    selected_planet = planet
                    vote_count[name] += 1
                    if click_sound:
                        click_sound.play()

    draw_sun()

    for planet in PLANETS:
        draw_planet(planet, angle)

    if selected_planet:
        show_planet_info(selected_planet)

    draw_ui()

    if not paused:
        angle += 1

    pygame.display.flip()
    clock.tick(60)
