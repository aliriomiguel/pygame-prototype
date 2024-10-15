import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1920, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Prototype")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load images (replace with your own image paths)
player_img = pygame.image.load("player.png").convert_alpha()
tiger_img = pygame.image.load("tiger.png").convert_alpha()
background_img = pygame.image.load("jungle_background.jpg").convert()

def scale_image(img, max_width, max_height):
    ratio = min(max_width / img.get_width(), max_height / img.get_height())
    new_width = int(img.get_width() * ratio)
    new_height = int(img.get_height() * ratio)
    return pygame.transform.scale(img, (new_width, new_height))

# Resize images
player_img = scale_image(player_img, 70, 80)
tiger_img = scale_image(tiger_img, 150, 60)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Player settings
player_x = 50
player_y = HEIGHT - 150
player_speed = 7
player_jump_power = 20
player_y_velocity = 0
player_lives = 5

# Tiger settings
tiger_x = WIDTH - 100
tiger_y = HEIGHT - 150
tiger_speed = 5
tiger_jump_power = 18
tiger_y_velocity = 0
tiger_last_jump_time = 0
TIGER_JUMP_COOLDOWN = 1.5

# Stone settings
stone_speed = 10
stones = []

# Physics
GRAVITY = 1
GROUND_HEIGHT = HEIGHT - 100

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def draw_button(text, font, color, button_color, x, y, width, height):
    pygame.draw.rect(screen, button_color, (x, y, width, height))
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x + width // 2, y + height // 2)
    screen.blit(text_surface, text_rect)
    return pygame.Rect(x, y, width, height)

def apply_gravity(y, y_velocity, img_height):
    y_velocity += GRAVITY
    y += y_velocity
    if y > GROUND_HEIGHT - img_height:
        y = GROUND_HEIGHT - img_height
        y_velocity = 0
    return y, y_velocity

def game_loop():
    global player_x, player_y, player_y_velocity, tiger_x, tiger_y, tiger_y_velocity, player_lives, tiger_last_jump_time

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_y == GROUND_HEIGHT - player_img.get_height():
                    player_y_velocity = -player_jump_power
                elif event.key == pygame.K_e:
                    # Throw a stone
                    stones.append([player_x + player_img.get_width(), player_y + player_img.get_height() // 2])

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_img.get_width():
            player_x += player_speed

        # Apply gravity to player
        player_y, player_y_velocity = apply_gravity(player_y, player_y_velocity, player_img.get_height())

        # Tiger AI and movement
        dx = player_x - tiger_x
        dy = player_y - tiger_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            tiger_x += (dx / distance) * tiger_speed
            
            # Make tiger jump if player is higher, tiger is on the ground, and cooldown has passed
            current_time = time.time()
            if (player_y < tiger_y - 50 and 
                tiger_y == GROUND_HEIGHT - tiger_img.get_height() and 
                current_time - tiger_last_jump_time > TIGER_JUMP_COOLDOWN):
                tiger_y_velocity = -tiger_jump_power
                tiger_last_jump_time = current_time

        # Apply gravity to tiger
        tiger_y, tiger_y_velocity = apply_gravity(tiger_y, tiger_y_velocity, tiger_img.get_height())

        # Update stone positions and check for collisions
        for stone in stones[:]:
            stone[0] += stone_speed
            if stone[0] > WIDTH:
                stones.remove(stone)
            else:
                stone_rect = pygame.Rect(stone[0], stone[1], 10, 10)
                tiger_rect = pygame.Rect(tiger_x, tiger_y, tiger_img.get_width(), tiger_img.get_height())
                if stone_rect.colliderect(tiger_rect):
                    return "win"

        # Collision detection
        player_rect = pygame.Rect(player_x, player_y, player_img.get_width(), player_img.get_height())
        tiger_rect = pygame.Rect(tiger_x, tiger_y, tiger_img.get_width(), tiger_img.get_height())

        if player_rect.colliderect(tiger_rect):
            player_lives -= 1
            if player_lives <= 0:
                return "game_over"
            # Reset positions after collision
            player_x = 50
            tiger_x = WIDTH - 100
            tiger_last_jump_time = 0  # Reset tiger's jump cooldown

        # Draw everything
        screen.blit(background_img, (0, 0))
        screen.blit(player_img, (player_x, player_y))
        screen.blit(tiger_img, (tiger_x, tiger_y))

        # Draw stones
        for stone in stones:
            pygame.draw.circle(screen, (100, 100, 100), stone, 5)

        # Draw lives
        draw_text(f"Lives: {player_lives}", font, WHITE, 100, 50)

        pygame.display.flip()
        clock.tick(60)

    return "quit"

def main_menu():
    while True:
        screen.blit(background_img, (0, 0))
        draw_text("Game Prototype", big_font, WHITE, WIDTH // 2, HEIGHT // 3)
        play_button = draw_button("Play", font, BLACK, GREEN, WIDTH // 2 - 50, HEIGHT // 2, 100, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play"

        pygame.display.flip()

def win_screen():
    while True:
        screen.blit(background_img, (0, 0))
        draw_text("You Win!", big_font, GREEN, WIDTH // 2, HEIGHT // 3)
        retry_button = draw_button("Retry", font, BLACK, GREEN, WIDTH // 2 - 50, HEIGHT // 2, 100, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    return "play"

        pygame.display.flip()

def game_over_screen():
    while True:
        screen.blit(background_img, (0, 0))
        draw_text("Game Over", big_font, RED, WIDTH // 2, HEIGHT // 3)
        retry_button = draw_button("Retry", font, BLACK, GREEN, WIDTH // 2 - 50, HEIGHT // 2, 100, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    return "play"

        pygame.display.flip()

# Game state machine
state = "menu"
while state != "quit":
    if state == "menu":
        state = main_menu()
    elif state == "play":
        player_lives = 5  # Reset lives
        player_x, player_y = 50, HEIGHT - 150  # Reset player position
        tiger_x, tiger_y = WIDTH - 100, HEIGHT - 150  # Reset tiger position
        tiger_last_jump_time = 0
        stones = []  # Clear any existing stones
        state = game_loop()
    elif state == "game_over":
        state = game_over_screen()
    elif state == "win":
        state = win_screen()

pygame.quit()