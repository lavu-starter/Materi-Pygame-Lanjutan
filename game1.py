import pygame, random, sys

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Bersih Hati Banyak Amal")

# Warna
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
HIJAU = (50, 200, 50)
MERAH = (220, 20, 60)
KUNING = (255, 215, 0)
BIRU = (180, 230, 255)

# Font dan clock
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Pemain
pemain = pygame.Rect(275, 350, 50, 30)
kecepatan = 7

# Objek
amal_baik = []
amal_buruk = []
kecepatan_jatuh = 5

skor = 0
waktu = 30
running = True
game_over = False

# Timer event
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

def spawn_amal():
    if random.randint(0, 1) == 0:
        amal_baik.append(pygame.Rect(random.randint(0, 570), -30, 30, 30))
    else:
        amal_buruk.append(pygame.Rect(random.randint(0, 570), -30, 30, 30))

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == TIMER_EVENT and not game_over:
            waktu -= 1
            if waktu <= 0:
                game_over = True

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT] and pemain.left > 0:
            pemain.x -= kecepatan
        if keys[pygame.K_RIGHT] and pemain.right < 600:
            pemain.x += kecepatan

        # Buat amal tiap beberapa frame
        if random.randint(1, 20) == 1:
            spawn_amal()

        # Gerakkan amal baik/buruk
        for a in amal_baik[:]:
            a.y += kecepatan_jatuh
            if a.colliderect(pemain):
                skor += 1
                amal_baik.remove(a)
            elif a.y > 400:
                amal_baik.remove(a)

        for b in amal_buruk[:]:
            b.y += kecepatan_jatuh
            if b.colliderect(pemain):
                skor -= 1
                amal_buruk.remove(b)
            elif b.y > 400:
                amal_buruk.remove(b)

    screen.fill(BIRU)

    # Gambar pemain dan objek
    pygame.draw.rect(screen, HIJAU, pemain)
    for a in amal_baik:
        pygame.draw.rect(screen, KUNING, a)
    for b in amal_buruk:
        pygame.draw.rect(screen, MERAH, b)

    # Tampilkan skor dan waktu
    screen.blit(font.render(f"Skor: {skor}", True, HITAM), (10, 10))
    screen.blit(font.render(f"Waktu: {waktu}", True, HITAM), (10, 40))

    if game_over:
        text1 = font.render("MasyaAllah! Skor kamu:", True, HITAM)
        text2 = font.render(str(skor), True, HITAM)
        text3 = font.render("Tekan R untuk main lagi", True, HITAM)
        screen.blit(text1, (180, 150))
        screen.blit(text2, (280, 190))
        screen.blit(text3, (150, 230))
        if keys[pygame.K_r]:
            skor = 0
            waktu = 30
            amal_baik.clear()
            amal_buruk.clear()
            game_over = False

    pygame.display.flip()
    clock.tick(60)
