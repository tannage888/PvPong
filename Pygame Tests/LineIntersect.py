# create the below code using python and pygame

# create a display_surface with WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720

# create a class Line that inherits from the pygame.sprite.Sprite
# This class constructor takes three parameters:
# - length as an integer in pixels 
# - center a two element tuple that denotes the centre of the line
# - and integer that denotes the thickness of the line in pixelsn minimum 1 pixel

# This class must generate a mask for the line.  The line must be white

# using the Line class:
# - create a line of length 400 pixels with the center of the line in the centre of the screen
# the a key rotates this line anti clockwise and the d key rotates it clockwise
# - create another line of length 600 with the center where the mouse pointer is located.  This line must move to where the mouse pointer is located.  Left mouse button rotates it anti clockwise and right mouse button rotates it clockwise

# the game loop must test for the collision between the two lines, and draw a red dot where the lines intersect


import pygame
import sys
import math

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720

class Line(pygame.sprite.Sprite):
    def __init__(self, length, center, thickness):
        super().__init__()
        self.length = length
        self.center = center
        self.thickness = max(1, thickness)
        self.angle = 0  # in degrees

        # Create a surface for the line
        self.image = pygame.Surface((length, self.thickness), pygame.SRCALPHA)
        pygame.draw.line(
            self.image, (255, 255, 255),
            (0, self.thickness // 2), (length, self.thickness // 2),
            self.thickness
        )
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, center=None, angle_delta=0):
        if center:
            self.center = center
        self.angle = (self.angle + angle_delta) % 360
        # Rotate the image
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Line Collision")

    clock = pygame.time.Clock()

    center_screen = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    line1 = Line(400, center_screen, 1)
    line2 = Line(600, pygame.mouse.get_pos(), 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        angle_delta1 = 0
        angle_delta2 = 0

        if keys[pygame.K_a]:
            angle_delta1 = 2  # rotate anti-clockwise
        if keys[pygame.K_d]:
            angle_delta1 = -2  # rotate clockwise

        if mouse_buttons[0]:  # Left mouse button
            angle_delta2 = 2
        if mouse_buttons[2]:  # Right mouse button
            angle_delta2 = -2

        line1.update(angle_delta=angle_delta1)
        mouse_pos = pygame.mouse.get_pos()
        line2.update(center=mouse_pos, angle_delta=angle_delta2)

        display_surface.fill((0, 0, 0))
        display_surface.blit(line1.image, line1.rect)
        display_surface.blit(line2.image, line2.rect)

        # Collision detection
        offset = (line2.rect.left - line1.rect.left, line2.rect.top - line1.rect.top)
        overlap = line1.mask.overlap(line2.mask, offset)
        if overlap:
            collision_point = (line1.rect.left + overlap[0], line1.rect.top + overlap[1])
            pygame.draw.circle(display_surface, (255, 0, 0), collision_point, 2)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()