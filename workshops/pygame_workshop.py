# Pygame Workshop
# William Soylemez - Robotics 2025

# This workshop covers basic game development concepts using the Pygame library including:
# - Setting up a Pygame window
# - Handling user input
# - Drawing shapes and text
# - Basic game loop structure
# The tasks are scattered throughout teh code, find them and complete them!

import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Workshop!")

# Set up the clock for frame rate
clock = pygame.time.Clock()
FPS = 60

# Define colors (RGB format)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up font
font = pygame.font.Font(None, 48)

# ============================================
# TASK 1: Create player variables
# ============================================
# TODO: Create variables for the player rectangle:
# - player_x: starting x position (try 375)
# - player_y: starting y position (try 275)
# - player_width: width of the rectangle (try 50)
# - player_height: height of the rectangle (try 50)
# - player_speed: how fast the player moves (try 5)

# Game state
running = True

# Main game loop
while running:
    # Handle events (like closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # ============================================
    # TASK 3: Handle keyboard input
    # ============================================
    # TODO: Get which keys are currently pressed using: keys = pygame.key.get_pressed()
    # TODO: Check if arrow keys are pressed and update player_x and player_y:
    #   - Left arrow: pygame.K_LEFT (decrease player_x by player_speed)
    #   - Right arrow: pygame.K_RIGHT (increase player_x by player_speed)
    #   - Up arrow: pygame.K_UP (decrease player_y by player_speed)
    #   - Down arrow: pygame.K_DOWN (increase player_y by player_speed)
    # BONUS: Add boundary checking so the player can't go off screen!
    
    # Draw title text
    title_text = font.render("Pygame Workshop!", True, WHITE)
    text_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(title_text, text_rect)
    
    # ============================================
    # TASK 2: Draw the player
    # ============================================
    # TODO: Draw the player rectangle using pygame.draw.rect()
    # Format: pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()