import sys
import random
import pygame
from pygame.locals import *

pygame.init()  # 🔹 Inisialisasi semua modul pygame

''' IMAGES '''
# 🔹 File gambar yang digunakan dalam game
player_ship = 'plyship.png'
enemy_ship = 'enemyship.png'
ufo_ship = 'ufo.png'
player_bullet = 'pbullet.png'
enemy_bullet = 'enemybullet.png'
ufo_bullet = 'enemybullet.png'

# 🔹 Membuat jendela fullscreen dan mendapatkan ukuran layar
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
s_width, s_height = screen.get_size()

# 🔹 Mengatur FPS dan clock untuk kontrol kecepatan frame
clock = pygame.time.Clock()
FPS = 60

# 🔹 Kelompok sprite (objek di layar)
Background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
ufobullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

sprite_group = pygame.sprite.Group()  # 🔹 Kumpulan semua sprite agar mudah di-draw dan di-update

pygame.mouse.set_visible(False)
# =====================================================
# 🔸 KELAS BACKGROUND (bintang atau latar belakang)
# =====================================================
class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):  
        super().__init__()
        # Membuat permukaan kecil berwarna putih (bintang)
        self.image = pygame.Surface([x, y])
        self.image.fill('white')
        self.image.set_colorkey('black')  # Hitam dianggap transparan
        self.rect = self.image.get_rect()  

    def update(self):
        # Menggerakkan latar belakang perlahan ke bawah
        self.rect.y += 1
        self.rect.x += 1
        # Jika keluar dari layar, kembalikan ke atas secara acak
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)
            

# =====================================================
# 🔸 KELAS PLAYER (pesawat pemain)
# =====================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')  # Hitam transparan
        self.alive = True
        self.count_to_live = 0
        self.activate_bullet = True
        self.alpha_duration = 0
        
    def update(self):
        if self.alive:
            self.image.set_alpha(80)
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.image.set_alpha(255)
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0] - 20
            self.rect.y = mouse[1] + 40
        else:
            self.alpha_duration = 0
            expl_x = self.rect.x + 20
            expl_y = self.rect.y + 40
            explosion = Explosion(expl_x, expl_y)
            explosion_group.add(explosion)
            sprite_group.add(explosion)
            self.rect.y = s_height + 200
            self.count_to_live += 1
            if self.count_to_live > 100:
                self.alive = True
                self.count_to_live = 0
                self.activate_bullet = True
        
    def shoot(self):
        if self.activate_bullet:
            bullet = PlayerBullet(player_bullet)
            mouse = pygame.mouse.get_pos()
            bullet.rect.x = mouse[0]
            bullet.rect.y = mouse[1]
            playerbullet_group.add(bullet)
            sprite_group.add(bullet) 
        
    def dead(self):
        self.alive = False
        self.activate_bullet = False
        
        

# =====================================================
# 🔸 KELAS ENEMY (musuh biasa)
# =====================================================
class Enemy(Player):
     def __init__(self, img):
          super().__init__(img)
          # Menentukan posisi acak di atas layar
          self.rect.x = random.randrange(80, s_width-80)
          self.rect.y = random.randrange(-500, 0)
          screen.blit(self.image, (self.rect.x, self.rect.y))
          
     def update(self):
        # Musuh bergerak turun
        self.rect.y += 1
        # Jika keluar layar, reset ke posisi acak di atas
        if self.rect.y > s_height:
            self.rect.x = random.randrange(80, s_width-80)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()
            
     def shoot(self):
        # Musuh menembak di posisi tertentu
        if self.rect.y in (0, 30, 70, 300, 700):
            enemybullet = EnemyBullet(enemy_bullet)
            enemybullet.rect.x = self.rect.x + 20
            enemybullet.rect.y = self.rect.y + 50
            enemybullet_group.add(enemybullet)
            sprite_group.add(enemybullet)
        

# =====================================================
# 🔸 KELAS UFO (musuh khusus yang bergerak horizontal)
# =====================================================
class Ufo(Enemy):
     def __init__(self, img):
         super().__init__(img) 
         self.rect.x = -200  # Mulai dari luar kiri layar
         self.rect.y = 200
         self.move = 1  # Kecepatan arah kanan
         
     def update(self):
         # Bergerak kiri-kanan bolak-balik
         self.rect.x += self.move
         if self.rect.x > s_width + 200:
             self.move *= -1
         elif self.rect.x < -200:
             self.move *= -1
         self.shoot()
         
     def shoot(self):
          # UFO menembak setiap kelipatan 50 posisi
          if self.rect.x % 50 == 0:
            ufobullet = EnemyBullet(ufo_bullet)
            ufobullet.rect.x = self.rect.x + 50
            ufobullet.rect.y = self.rect.y + 70
            ufobullet_group.add(ufobullet)
            sprite_group.add(ufobullet)
            

# =====================================================
# 🔸 KELAS PELURU PEMAIN
# =====================================================
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        
    def update(self):
        # Bergerak ke atas
        self.rect.y -= 18
        # Hapus peluru jika keluar layar
        if self.rect.y < 0:
            self.kill()
            

# =====================================================
# 🔸 KELAS PELURU MUSUH
# =====================================================
class EnemyBullet(PlayerBullet):
     def __init__(self, img):
           super().__init__(img)
           self.image.set_colorkey('white')  # Putih transparan
           
     def update(self):
         # Bergerak ke bawah
         self.rect.y += 3
         if self.rect.y > s_height:
             self.kill()
        
class Explosion(pygame.sprite.Sprite):
     def __init__(self, x, y):
         super().__init__()
         self.img_list = []
         for i in range(1, 6):
             img = pygame.image.load(f'exp{i}.png').convert()
             img.set_colorkey('black')
             img = pygame.transform.scale(img, (120, 120))
             self.img_list.append(img)
         self.index = 0
         self.image = self.img_list[self.index]
         self.rect = self.image.get_rect()
         self.rect.center = [x, y]
         self.count_delay = 0
         
     def update(self):
         self.count_delay += 1
         if self.count_delay >= 12:
             if self.index < len(self.img_list) -1:
                 self.count_delay = 0
                 self.index += 1
                 self.image = self.img_list[self.index]
         if self.index >= len(self.img_list) -1:
             if self.count_delay >= 12:
                 self.kill() 

# =====================================================
# 🔸 KELAS GAME UTAMA
# =====================================================
class Game:
    def __init__(self):
        self.count_hit = 0
        self.count_hit2 = 0
        self.lives = 3 
        self.score = 0
        self.paused = False
        self.run_game()  # Jalankan game langsung saat dibuat

    # Membuat bintang background
    def create_background(self):
        for i in range(20):
            x = random.randint(1, 5)
            Background_image = Background(x, x)
            Background_image.rect.x = random.randrange(0, s_width)
            Background_image.rect.y = random.randrange(0, s_height)
            Background_group.add(Background_image)
            sprite_group.add(Background_image)

    # Membuat pemain
    def create_player(self):
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player)
        
    # Membuat musuh
    def create_enemy(self):
        for i in range(10):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)
            
    # Membuat UFO
    def create_ufo(self):
        for i in range(1):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)
            
    def playerbullet_hits_enemy(self):
        hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
        for i in hits:
            self.count_hit += 1
            self.score += 10
            if self.count_hit == 3:
                expl_x = i.rect.x + 20
                expl_y = i.rect.y + 40
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = random.randrange(0, s_width)
                i.rect.y = random.randrange(-3000, -100)
                self.count_hit = 0
                
    def playerbullet_hits_ufo(self):
        hits = pygame.sprite.groupcollide(ufo_group, playerbullet_group, False, True)
        for i in hits:
            self.count_hit2 += 1
            self.score += 50
            if self.count_hit2 == 40:
                expl_x = i.rect.x + 50
                expl_y = i.rect.y + 60
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = -199
                self.count_hit2 = 0
    def enemybullet_hits_player(self):
        hits = []
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
        if hits:
            self.lives -= 1
            self.player.dead()
        if self.lives < 0:
            pygame.quit()
            sys.exit()
    def ufobullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufobullet_group, True)
            if hits:
                self.lives -= 1
                self.player.dead
                if self.lives < 0:
                    pygame.quit()
                    sys.exit()
                
    def player_enemy_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
            if hits:
                for i in hits:
                    i.rect.x = random.randrange(0, s_width)
                    i.rect.y = random.randrange(-3000, -100)
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        pygame.quit()
                        sys.exit()
            
    def player_ufo_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufo_group, False)
            if hits:
                for i in hits:
                    i.rect.x = -199
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        pygame.quit()
                        sys.exit()
            
    def create_lives(self):
        self.live_img = pygame.image.load(player_ship)
        self.live_img = pygame.transform.scale(self.live_img, (30, 30))
        n = 0
        for i in range(self.lives):
            screen.blit(self.live_img, (10 + n, 5))
            n += 40
            
    def create_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, 'black')
        screen.blit(score_text, (200, 10))

    def create_paused(self):
        font = pygame.font.Font(None, 72)
        paused_text = font.render("PAUSED", True, 'red')
        rect = paused_text.get_rect(center=(s_width//2, s_height//2))
        screen.blit(paused_text, rect)
        
    def create_game_over(self):
        # Latar belakang gelap
        overlay = pygame.Surface((s_width, s_height))
        overlay.set_alpha(180)  # transparansi
        overlay.fill('black')
        screen.blit(overlay, (0, 0))
        
        # Tulisan Game Over
        font = pygame.font.Font(None, 100)
        text = font.render("GAME OVER", True, 'red')
        text_rect = text.get_rect(center=(s_width//2, s_height//2 - 50))
        screen.blit(text, text_rect)
        
        # Instruksi restart
        font2 = pygame.font.Font(None, 50)
        restart_text = font2.render("Press R to Restart", True, 'white')
        restart_rect = restart_text.get_rect(center=(s_width//2, s_height//2 + 50))
        screen.blit(restart_text, restart_rect)
        
        pygame.display.update()  # Refresh layar

    
    # Update semua sprite di layar
    def run_update(self):
        sprite_group.draw(screen)
        sprite_group.update()

    # 🔹 Loop utama game
    def run_game(self):
        self.create_background()
        self.create_player()
        self.create_enemy()
        self.create_ufo()
        while True:
            screen.fill('black')  # Bersihkan layar setiap frame
            if self.lives <= 0:
                self.create_game_over()
            else:
                self.playerbullet_hits_enemy()
                self.playerbullet_hits_ufo()
                self.enemybullet_hits_player()
                self.ufobullet_hits_player()
                self.player_enemy_crash()
                self.player_ufo_crash()     
                pygame.draw.rect(screen, 'white', (0,0,s_width,40))
                self.create_lives()
                self.create_score()
                self.run_update() 
          
            # Cek event keyboard / mouse
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_p and self.lives > 0:
                        self.paused = not self.paused
                        
                    if event.key == K_r and self.lives <= 0:
           
                        self.__init__()  # ini akan jalankan run_game lagi
                    # Pemain menembak
                    if event.key == K_SPACE and not self.paused and self.lives > 0:
                        self.player.shoot()
                    if not self.paused and self.lives >= 0:
                        self.player.shoot()
                    
            if self.paused and self.lives >= 0:
                self.create_paused()

            pygame.display.update()  # Refresh layar
            clock.tick(FPS)          # Jaga frame rate tetap 60 FPS


# =====================================================
# 🔸 JALANKAN GAME
# =====================================================
def main():
    game = Game()

if __name__ == "__main__":
    main()
