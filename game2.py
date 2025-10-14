import pygame, math, random, sys

# Inisialisasi pygame
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulasi Tata Surya Realistis - SMK Muhammadiyah 1 Mojokerto")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# Warna dasar
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Data planet: (nama, warna, jarak orbit, radius, kecepatan orbit)
PLANETS = [
    ("Merkurius", (200, 200, 200), 70, 5, 0.05),
    ("Venus", (255, 180, 0), 110, 8, 0.035),
    ("Bumi", (100, 149, 237), 150, 9, 0.03),
    ("Mars", (188, 39, 50), 190, 7, 0.025),
    ("Jupiter", (255, 140, 0), 260, 18, 0.02),
    ("Saturnus", (210, 180, 140), 330, 15, 0.015),
    ("Uranus", (65, 105, 225), 400, 12, 0.01),
    ("Neptunus", (0, 0, 205), 460, 11, 0.008),
]

# Variabel simulasi
angle = 0
zoom = 1.0
paused = False

# Buat bintang di background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(200)]

def draw_background():
    for (x, y) in stars:
        pygame.draw.circle(screen, WHITE, (x, y), random.choice([1, 2]))

def draw_planet(name, color, orbit_radius, radius, speed, angle):
    # Hitung posisi orbit
    x = WIDTH // 2 + orbit_radius * math.cos(angle * speed) * zoom
    y = HEIGHT // 2 + orbit_radius * math.sin(angle * speed) * zoom

    # Orbit
    pygame.draw.circle(screen, (70, 70, 70), (WIDTH // 2, HEIGHT // 2), int(orbit_radius * zoom), 1)

    # Planet
    pygame.draw.circle(screen, color, (int(x), int(y)), int(radius * zoom))

    # Label nama planet
    label = font.render(name, True, WHITE)
    screen.blit(label, (x + 10, y - 10))

def draw_sun():
    pygame.draw.circle(screen, YELLOW, (WIDTH // 2, HEIGHT // 2), int(25 * zoom))
    sun_label = font.render("Matahari", True, WHITE)
    screen.blit(sun_label, (WIDTH // 2 + 30, HEIGHT // 2 - 10))

def draw_ui():
    info = font.render("Zoom: ↑↓ | Pause: Spasi | Keluar: ESC", True, (200, 200, 200))
    screen.blit(info, (20, 20))

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

    draw_sun()

    # Gambar semua planet
    for name, color, orbit_radius, radius, speed in PLANETS:
        draw_planet(name, color, orbit_radius, radius, speed, angle)

    draw_ui()

    # Update sudut orbit
    if not paused:
        angle += 1

    pygame.display.flip()
    clock.tick(60)
