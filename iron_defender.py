import os
import pygame
from pygame import mixer

class Settings():
    WINDOW = pygame.rect.Rect((0, 0, 1400, 800))
    FPS = 60
    DELTATIME = 1.0 / FPS
    DIRECTIONS = {"right": pygame.math.Vector2(5, 0), 
                  "left": pygame.math.Vector2(-5, 0), 
                  "up": pygame.math.Vector2(0, -5), 
                  "down": pygame.math.Vector2(0, 5)}
    TITLE = "Iron Defender"
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.join(FILE_PATH, "images")
    SOUND_PATH = os.path.join(FILE_PATH, "sounds")
    start_pos = pygame.math.Vector2(0, WINDOW.height // 2)


class Iron_Man(pygame.sprite.Sprite):
    def __init__(self, size, pos, screen):
        super().__init__()
        
        self.normal_image_unscaled = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "normal.png")).convert_alpha()
        self.shoot_image_unscaled = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "shoot.png")).convert_alpha()
        self.normal_image = pygame.transform.scale(self.normal_image_unscaled, (size))

        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 250
        self.screen = screen
        self.is_shooting = False
        self.health = 3
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 500

    def get_hand_position(self):
        hand_x = self.rect.right - 5
        hand_y = self.rect.top + 55
        return hand_x, hand_y

    def move(self):
        #Iron Man Bewegung
        self.pos.x += self.direction.x * self.speed * Settings.DELTATIME
        self.pos.y += self.direction.y * self.speed * Settings.DELTATIME
        #Begrenzung links
        if self.pos.x < 0:
            self.pos.x = 0
        #Begrenzung rechts nur bis zum viertel
        max_x = self.screen.get_width() // 4 - self.rect.width
        if self.pos.x > max_x:
            self.pos.x = max_x
        #begrenzung oben
        if self.pos.y < 0:
            self.pos.y = 0
        #begrenzung unten
        if self.pos.y + self.rect.height > self.screen.get_height():
            self.pos.y = self.screen.get_height() - self.rect.height
            
        self.rect.topleft = self.pos

    def update(self):
        if self.is_shooting:
            self.image = self.shoot_image_unscaled
            self.rect = self.image.get_rect(topleft=self.pos)
        else:
            self.image = self.normal_image
            self.rect = self.image.get_rect(topleft=self.pos)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, size, screen):
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Enemy", "enemy1.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)

        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.right = screen.get_width()
        self.screen = screen
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.health = 1

    def got_hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction=1, is_enemy = False):
        super().__init__()
        if is_enemy:
            self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Enemy", "ebullet.png")).convert_alpha()
        else:
            self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "bullet.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 40))
        self.rect = self.image.get_rect(midleft=pos)
        self.direction = direction
        self.is_enemy = is_enemy

    def update(self):
        self.rect.x += 8 * self.direction

class Game():
    def __init__(self):
        #Quelle für Bildschirmanzeige:
        #https://www.youtube.com/watch?v=GX_fsDz4j8A 
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((screen_width - 10, screen_height - 50), pygame.RESIZABLE)
        pygame.display.set_caption("Iron Defender")
        self.clock = pygame.time.Clock()
        self.score = 0

        self.iron_man = pygame.sprite.GroupSingle(Iron_Man((150, 240),(Settings.start_pos), self.screen))

        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn_enemies()

        self.background_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Hintergrund", "hintergrund.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())

        #Anfangsbegrüßung
        mixer.music.load(os.path.join(Settings.SOUND_PATH, "jarvis.mp3"))
        mixer.music.set_volume(0.3)
        mixer.music.play()

        #Sound beim Schießen
        self.shoot_sound = mixer.Sound(os.path.join(Settings.SOUND_PATH, "ironman_blaster.mp3"))
        self.shoot_sound.set_volume(0.3)

        self.running = True
        self.show_title = True
        self.show_instruction = False

        self.lives = 3
        self.heart_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "leben.png")).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (50, 50))
        self.font = pygame.font.Font(None, 36)
    
    def spawn_enemies(self):
        enemy_size = (120, 180)
        for row in range(4):
            for col in range(4):
                enemy = Enemy(enemy_size, self.screen)
                enemy.rect.x = self.screen.get_width() - enemy.rect.width - col * (enemy.rect.width + 30)
                enemy.rect.y = 80 + row * (enemy.rect.height + 30)
                self.enemies.add(enemy)

    def handle_hit(self):
        if self.lives > 0:
            self.lives -= 1
            if self.lives == 0:
                self.show_title_screen()

    def check_collisions(self):
        #bullet und enemy
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                enemy_killed = enemy.got_hit()
                if enemy_killed:
                    self.score += 1

        #iron man trifft enemy
        if pygame.sprite.spritecollideany(self.iron_man.sprite, self.enemies):
            self.handle_hit()

        #enemy trifft iron man
        for bullet in self.bullets:
            if bullet.is_enemy and bullet.rect.colliderect(self.iron_man.sprite.rect):
                bullet.kill()
                self.handle_hit()


    def run(self):
        while self.running:
            if self.show_title:
                self.show_title_screen()
            elif self.show_instruction:
                self.show_instruction_screen()
            else:
                self.watch_for_events()
                self.update()
                self.draw()
            self.clock.tick(Settings.FPS)
        pygame.quit()

    def draw(self):
        self.screen.blit(self.background_image, (0,0))
        self.iron_man.draw(self.screen)
        self.enemies.draw(self.screen)
        self.bullets.draw(self.screen)
        #transparente bar oben
        bar_height = 65
        screen_width = self.screen.get_width()
        transparent_bar = pygame.Surface((screen_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bar, (102, 102, 102, 102), transparent_bar.get_rect())
        self.screen.blit(transparent_bar, (0, 0))
        #lebensanzeige
        icon_spacing = 10
        start_x = self.screen.get_width() - 10
        heart_rect = self.heart_image.get_rect(topright=(start_x, 10))
        current_x = heart_rect.left
        for i in range(self.lives):
            self.screen.blit(self.heart_image, (current_x, heart_rect.top))
            current_x -= (heart_rect.width + icon_spacing)
        #punktestand
        score_text = self.font.render("Score: " + str(self.score), True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()

    def watch_for_events(self):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0,0)

        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        
        if direction.length() > 0:
            self.iron_man.sprite.direction = direction.normalize()
        else:
            self.iron_man.sprite.direction = direction

        self.iron_man.sprite.move()

        for event in pygame.event.get():
            time_now = pygame.time.get_ticks()
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:          
                if event.key == pygame.K_ESCAPE:  
                    self.running = False
                elif event.key == pygame.K_SPACE and time_now - self.iron_man.sprite.last_shot > self.iron_man.sprite.cooldown:
                    self.iron_man.sprite.is_shooting = True
                    hand_pos = self.iron_man.sprite.get_hand_position()
                    bullet = Bullet(hand_pos)
                    self.bullets.add(bullet)
                    self.shoot_sound.play()
                    self.iron_man.sprite.last_shot = time_now

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.iron_man.sprite.is_shooting = False

    def show_title_screen(self):
        self.title_screen = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Hintergrund", "splash_screen.jpg")).convert()
        self.title_screen = pygame.transform.scale(self.title_screen, self.screen.get_size())
        self.screen.blit(self.title_screen, (0,0))
        #Quelle für Fonts benutzt:
        #https://medium.com/@amit25173/pygame-fonts-guide-for-beginners-e2ec8bf7671c
        font = pygame.font.SysFont("Aharoni", 60, bold=True)
        text = font.render("Press SPACE to start", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 100))

        font2 = pygame.font.SysFont("Aharoni", 120, bold=True)
        text2 = font2.render("Iron Defender", True, (255, 255, 255))
        text2_rect = text2.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))

        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text2_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_title = False
                self.show_instruction = True

    def show_instruction_screen(self):
        self.screen.fill("black")
        image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "instruction.png")).convert()
        pos = (10, 500)
        
        font = pygame.font.SysFont("Arial", 60, bold=True)
        text = font.render("How to play", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, 50))
        #Quelle für schreiben in mehrere Zeilen benutzt:
        #https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame/42015712#42015712
        font2 = pygame.font.SysFont("Comic Sans MS", 25)
        text2 = font2.render(
            "You're Iron Man and need to protect the city from the enemies. \n"
            "The other Avengers are not here so it's on you alone to rescue \n"
            "the people from the threat. Shoot them and be the hero! ",
            True,
            "white",
            None
        )
        
        text2_rect = text2.get_rect(center=(400, 250))

        font3 = pygame.font.SysFont("Comic Sans MS", 25)
        text3 = font3.render(
            "Move up with 'w' \n"
            "Move left with 'a' \n"
            "Move down with 's' \n"
            "Move right with 'd' \n"
            "Shoot with 'Space' ",
            True,
            "white",
            None
        )

        text3_rect = text3.get_rect(center=(1150, 270))

        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text2_rect)
        self.screen.blit(text3, text3_rect)
        self.screen.blit(image, pos)
        pygame.display.flip()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_instruction = False
    
    def show_end_screen(self):
        #Hintergrundmusik
        mixer.music.load(os.path.join(Settings.SOUND_PATH, "The Avengers.mp3"))
        mixer.music.set_volume(0.1)
        mixer.music.play(-1)
        
        font = pygame.font.SysFont("Aharoni", 80)
        text = font.render("You defeated every enemy and saved the city!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))

        font2 = pygame.font.SysFont("Aharoni", 50)
        text2 = font2.render("Press ESC to close the game", True, (200, 200, 200))
        text2_rect = text2.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))

        while True:
            self.end_screen = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Hintergrund", "iron_man.jpg")).convert()
            self.end_screen = pygame.transform.scale(self.end_screen, self.screen.get_size())
            self.screen.blit(self.end_screen, (0,0))
            self.screen.blit(text, text_rect)
            self.screen.blit(text2, text2_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    
    def update(self):
        self.iron_man.update()
        self.bullets.update()
        self.enemies.update()
        self.check_collisions()
        if not self.enemies:
            self.show_end_screen()



def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()



