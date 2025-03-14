import os
import pygame

class Settings():
    WINDOW = pygame.rect.Rect((0, 0, 1400, 800))
    FPS = 60
    DELTATIME = 1.0 / FPS
    DIRECTIONS = {"right": pygame.math.Vector2(5, 0), 
                  "left": pygame.math.Vector2(-5, 0), 
                  "up": pygame.math.Vector2(0, -5), 
                  "down": pygame.math.Vector2(0, 5)}
    image_sprite = [pygame.image.load("normal.png"),
                    pygame.image.load("shoot.png")]
    TITLE = "Iron Defender"
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.join(FILE_PATH, "images")
    start_pos = pygame.math.Vector2(0, WINDOW.height // 2)


class Iron_Man(pygame.sprite.Sprite):
    def __init__(self, image_file, size, pos, screen):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", image_file)).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 250
        self.screen = screen
        self.is_shooting = False

    def move(self):
        self.pos.x += self.direction.x * self.speed * Settings.DELTATIME
        self.pos.y += self.direction.y * self.speed * Settings.DELTATIME

    # Begrenzungen des Fensters
        # self.pos.x = max(0, min(Settings.WINDOW.width - self.rect.width, self.pos.x))
        # self.pos.y = max(0, min(Settings.WINDOW.height - self.rect.height, self.pos.y))

        # if self.direction == "left":
        #     self.pos.x -= self.speed * Settings.DELTATIME
        # elif self.direction == "right":
        #     self.pos.x += self.speed * Settings.DELTATIME
        # elif self.direction == "up":
        #     self.pos.y -= self.speed * Settings.DELTATIME
        # elif self.direction == "down":
        #     self.pos.y += self.speed * Settings.DELTATIME

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
        if self.is_shooting:
            self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "shoot.png")).convert_alpha()
        else:
            self.image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "Iron Man", "normal.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 240))
        self.move()


class Game():
    def __init__(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.display.set_caption("Iron Defender")
        self.clock = pygame.time.Clock()

        self.iron_man = pygame.sprite.GroupSingle(Iron_Man("normal.png",(150, 240),(Settings.start_pos), self.screen))

        self.background_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "background.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())

        self.running = True

    def run(self):
        while self.running:
            self.watch_for_events()
            self.update()
            self.draw()
            self.clock.tick(Settings.FPS)
        pygame.quit()

    def draw(self):
        self.screen.blit(self.background_image)
        self.iron_man.draw(self.screen)
        pygame.display.flip()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:          
                if event.key == pygame.K_ESCAPE:  
                    self.running = False

                elif event.key == pygame.K_LEFT:
                    self.iron_man.sprite.direction = pygame.math.Vector2(-1, 0)
                
                elif event.key == pygame.K_RIGHT:
                    self.iron_man.sprite.direction = pygame.math.Vector2(1, 0)

                elif event.key == pygame.K_UP:
                    self.iron_man.sprite.direction = pygame.math.Vector2(0, -1)

                elif event.key == pygame.K_DOWN:
                    self.iron_man.sprite.direction = pygame.math.Vector2(0, 1)

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.iron_man.sprite.direction.x = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.iron_man.sprite.direction.y = 0
            if event.key == pygame.K_SPACE:
                


    def update(self):
        self.iron_man.update()



def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()



