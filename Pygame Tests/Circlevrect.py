import pygame

# --- Setup ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mask Collision: Circle and Rectangle")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Create the Rectangle Sprite and Mask ---
# Create a surface for the rectangle. The surface size must be big enough to hold the rect.
rect_surface_size = (150, 100)
rect_surface = pygame.Surface(rect_surface_size).convert_alpha()
rect_surface.fill(BLACK) # Fill with black (or any non-transparent color)
# Create a mask from the filled surface. This mask will be a solid rectangle of '1's.
rect_mask = pygame.mask.from_surface(rect_surface)
# Get a Rect object for the rectangle to handle its position on screen.
rect_rect = rect_surface.get_rect(center=(200, SCREEN_HEIGHT // 2))

# --- Create the Circle Sprite and Mask ---
# Create a surface for the circle. IMPORTANT: Use convert_alpha() for transparency.
circle_radius = 50
circle_surface_size = (circle_radius * 2, circle_radius * 2)
circle_surface = pygame.Surface(circle_surface_size, pygame.SRCALPHA).convert_alpha()
# Draw the circle on its surface. The background of this surface is transparent.
pygame.draw.circle(circle_surface, WHITE, (circle_radius, circle_radius), circle_radius)
# Create a mask from the circle's surface. This mask will be a circle of '1's.
circle_mask = pygame.mask.from_surface(circle_surface)
# Get a Rect object for the circle to handle its position.
circle_rect = circle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))


# --- Game Loop ---
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # Get mouse position and move the circle sprite
    circle_rect.center = pygame.mouse.get_pos()

    # --- Collision Detection ---
    # Calculate the offset between the two rects. This is crucial for mask.overlap().
    # The offset is the vector from the top-left of the first mask's rect to the top-left of the second.
    offset_x = circle_rect.x - rect_rect.x
    offset_y = circle_rect.y - rect_rect.y
    
    # Check if the masks overlap using the calculated offset.
    # The overlap() method returns the coordinates of the first overlapping pixel or None.
    collision_point = rect_mask.overlap(circle_mask, (offset_x, offset_y))
    
    # Change the color of the rectangle to show a collision
    current_color = GREEN
    if collision_point:
        current_color = RED
    
    # --- Drawing ---
    screen.fill(BLACK)  # Clear screen with black
    
    # Redraw the rectangle surface with the new color
    rect_surface.fill(current_color)
    
    # Draw the surfaces to the main screen at their respective positions
    screen.blit(rect_surface, rect_rect)
    screen.blit(circle_surface, circle_rect)
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
