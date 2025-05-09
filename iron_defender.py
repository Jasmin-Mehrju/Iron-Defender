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
        self.last_shot = pygame.time.get_ticks()

    def get_hand_position(self):
        hand_x = self.rect.right - 5
        hand_y = self.rect.top + 55
        return hand_x, hand_y

    def move(self):
        self.pos.x += self.direction.x * self.speed * Settings.DELTATIME
        self.pos.y += self.direction.y * self.speed * Settings.DELTATIME

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x + self.rect.width > self.screen.get_width():
            self.pos.x = self.screen.get_width() - self.rect.width

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y + self.rect.height > self.screen.get_height():
            self.pos.y = self.screen.get_height() - self.rect.height
            
        self.rect.topleft = self.pos

    def update(self):
        self.cooldown = 500
        if self.is_shooting:
            self.image = self.shoot_image_unscaled
            self.rect = self.image.get_rect(topleft=self.pos)
        else:
            self.image = self.normal_image
            self.rect = self.image.get_rect(topleft=self.pos)
        #self.move()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, size, pos, screen):
        super().__init__()

        self.normal_image_unscaled = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Enemy", "enemy1.png")).convert_alpha()
        self.shoot_image_unscaled = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Enemy", "enemy2.png")).convert_alpha()
        self.normal_image = pygame.transform.scale(self.normal_image_unscaled, (size))

        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(pos)
        self.screen = screen
        self.is_shooting = False
        self.last_shot = pygame.time.get_ticks()

    def get_hand_position(self):
        hand_x = self.rect.right - 5
        hand_y = self.rect.top + 55
        return hand_x, hand_y

    def move(self):
        # self.pos.x += self.direction.x * self.speed * Settings.DELTATIME
        # self.pos.y += self.direction.y * self.speed * Settings.DELTATIME

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x + self.rect.width > self.screen.get_width():
            self.pos.x = self.screen.get_width() - self.rect.width

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y + self.rect.height > self.screen.get_height():
            self.pos.y = self.screen.get_height() - self.rect.height
            
        self.rect.topleft = self.pos

    def update(self):
        self.cooldown = 500
        if self.is_shooting:
            self.image = self.shoot_image_unscaled
            self.rect = self.image.get_rect(topleft=self.pos)
        else:
            self.image = self.normal_image
            self.rect = self.image.get_rect(topleft=self.pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "bullet.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 40))
        self.rect = self.image.get_rect(midleft=pos)

    def update(self):
        self.rect.x += 8
        if self.rect.left > Settings.WINDOW.width:
            self.kill()
  

class Game():
    def __init__(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.display.set_caption("Iron Defender")
        self.clock = pygame.time.Clock()

        self.iron_man = pygame.sprite.GroupSingle(Iron_Man((150, 240),(Settings.start_pos), self.screen))
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.background_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "background.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())

        self.title_screen = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Hintergrund", "splash_screen.jpg")).convert()
        self.title_screen = pygame.transform.scale(self.title_screen, self.screen.get_size())

        mixer.music.load("jarvis.mp3")
        mixer.music.play()

        self.running = True
        self.show_title = True
        self.lives = 3
        self.heart_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "leben.png")).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (50, 50))
        self.font = pygame.font.Font(None, 36)

    def handle_hit(self):
        if self.lives > 0:
            self.lives -= 1
            if self.lives == 0:
                self.show_title_screen()

    def run(self):
        while self.running:
            if self.show_title:
                self.show_title_screen()
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
        bar_height = 65
        screen_width = self.screen.get_width()
        transparent_bar = pygame.Surface((screen_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bar, (102, 102, 102, 102), transparent_bar.get_rect())
        self.screen.blit(transparent_bar, (0, 0))
        icon_spacing = 10
        start_x = self.screen.get_width() - 10
        heart_rect = self.heart_image.get_rect(topright=(start_x, 10))
        current_x = heart_rect.left
        for i in range(self.lives):
            self.screen.blit(self.heart_image, (current_x, heart_rect.top))
            current_x -= (heart_rect.width + icon_spacing)
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
                    self.iron_man.sprite.last_shot = time_now

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.iron_man.sprite.is_shooting = False

    def show_title_screen(self):
        self.screen.blit(self.title_screen, (0,0))
        font = pygame.font.SysFont("Comic Sans MS", 60, bold=True)
        text = font.render("Press SPACE to start", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 100))
        font2 = pygame.font.SysFont("DotumChe", 40)
        text2 = font2.render(
            "Controls:\n"
            "w: up\n"
            "a: left\n"
            "s: down\n" 
            "d: right\n",
            True,
            "white",
            None
        )
        text2_rect = text2.get_rect(topleft=(self.screen.get_width() - 1515, self.screen.get_height() - 850))

        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text2_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_title = False
    
    def update(self):
        self.iron_man.update()
        self.bullets.update()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()



