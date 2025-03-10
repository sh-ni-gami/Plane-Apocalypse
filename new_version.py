import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
PLAYER_SPEED = 8
MISSILE_SPEED = 5
MAX_MISSILES = 5

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plane Apocalypse")
clock = pygame.time.Clock()

# Load assets
font = pygame.font.Font(None, 36)
high_score_file = "highscore.txt"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.speed = PLAYER_SPEED
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250
        
        # Draw plane shape
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.circle(self.image, WHITE, (25, 20), 8)
        pygame.draw.rect(self.image, RED, (5, 35, 15, 5))
        pygame.draw.rect(self.image, RED, (30, 35, 15, 5))
        
        # Create collision mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Missile(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.image = pygame.Surface((10, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.target = target
        self.speed = MISSILE_SPEED
        
        # Draw missile
        pygame.draw.rect(self.image, RED, (0, 0, 10, 20))
        pygame.draw.polygon(self.image, YELLOW, [(0, 20), (10, 20), (5, 30)])
        
        # Create collision mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance != 0:
            self.rect.x += self.speed * dx / distance
            self.rect.y += self.speed * dy / distance

class Game:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.load_high_score()
        self.player = Player()
        self.missiles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.game_over = False
        self.difficulty = 1

    def load_high_score(self):
        if os.path.exists(high_score_file):
            with open(high_score_file, "r") as f:
                self.high_score = int(f.read())

    def save_high_score(self):
        with open(high_score_file, "w") as f:
            f.write(str(self.high_score))

    def spawn_missile(self):
        if len(self.missiles) < MAX_MISSILES * self.difficulty:
            missile = Missile(self.player)
            missile.rect.center = (random.randint(0, SCREEN_WIDTH), -20)
            self.missiles.add(missile)
            self.all_sprites.add(missile)

    def check_collisions(self):
        # Check collision between player and missiles
        if pygame.sprite.spritecollide(self.player, self.missiles, False, pygame.sprite.collide_mask):
            self.game_over = True

    def check_missile_collisions(self):
        # Check for collisions among missiles
        collided = set()
        missiles_list = self.missiles.sprites()
        for i in range(len(missiles_list)):
            for j in range(i + 1, len(missiles_list)):
                m1 = missiles_list[i]
                m2 = missiles_list[j]
                # Only process if neither missile has been marked as collided
                if m1 not in collided and m2 not in collided:
                    if pygame.sprite.collide_mask(m1, m2):
                        collided.add(m1)
                        collided.add(m2)
        # Remove collided missiles and spawn replacements
        for missile in collided:
            self.missiles.remove(missile)
            self.all_sprites.remove(missile)
            self.spawn_missile()  # Spawn a new missile for each missile destroyed

    def show_menu(self):
        menu = True
        while menu:
            screen.fill(BLACK)
            self.draw_text("Plane Apocalypse", 72, SCREEN_WIDTH/2, 100)
            self.draw_text("Press SPACE to Start", 36, SCREEN_WIDTH/2, 300)
            self.draw_text(f"High Score: {self.high_score}", 36, SCREEN_WIDTH/2, 400)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        menu = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def run(self):
        self.show_menu()
        
        while not self.game_over:
            clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
            
            # Update
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            
            # Spawn missiles over time
            if random.random() < 0.02 * self.difficulty:
                self.spawn_missile()
            
            self.missiles.update()
            
            # Check collisions among missiles and between missiles and the player
            self.check_missile_collisions()
            self.check_collisions()
            
            # Increase difficulty and score
            self.score += 1
            if self.score % 1000 == 0:
                self.difficulty += 0.2
            
            # Draw everything
            screen.fill(BLACK)
            self.all_sprites.draw(screen)
            
            # Draw HUD
            self.draw_text(f"Score: {self.score}", 36, 100, 30)
            self.draw_text(f"Difficulty: {self.difficulty:.1f}x", 36, SCREEN_WIDTH - 120, 30)
            
            pygame.display.flip()

        # Game over sequence
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        screen.fill(BLACK)
        self.draw_text("Game Over!", 72, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)
        self.draw_text(f"Final Score: {self.score}", 48, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)
        self.draw_text("Press SPACE to play again", 36, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 150)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.__init__()
                        self.run()
                    if event.key == pygame.K_ESCAPE:
                        waiting = False

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
