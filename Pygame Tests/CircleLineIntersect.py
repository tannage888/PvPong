# create the below code using python and pygame

# create a display_surface with WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720

# thickness of the circle and line must be 1

# create a class Line that inherits from the pygame.sprite.Sprite
# This class constructor takes three parameters:
# - length as an integer in pixels 
# - center a two element tuple that denotes the centre of the line
# - and integer that denotes the thickness of the line in pixels minimum 1 pixel

# This class must generate a mask for the line.  The line must be white


# create a class Circle that inherits from the pygame.sprite.Sprite
# This class constructor takes three parameters:
# - radius as an integer in pixels 
# - center a two element tuple that denotes the centre of the line
# - and integer that denotes the thickness of the line in pixelsn minimum 1 pixel

# This class must generate a mask for the line.  The line must be white

# using the Line class:
# - create a line of length 400 pixels with the center of the line in the centre of the screen
# the a key rotates this line anti clockwise and the d key rotates it clockwise

# using the Circle class:
# - create a circle of radius 100 with the center where the mouse pointer is located.  This line must move to where the mouse pointer is located.  

# the game loop must test for the collision between the line and the circle, and draw a red dot where the circle touches the line.

# the circle and line can only overlap at one point. 



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
        self.angle = 0  # degrees

        # Create a transparent surface for the line
        self.image = pygame.Surface((length, self.thickness), pygame.SRCALPHA)
        pygame.draw.line(
            self.image, (255, 255, 255),
            (0, self.thickness // 2), (length, self.thickness // 2),
            self.thickness
        )
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, angle_delta=0, center=None):
        if center:
            self.center = center
        self.angle = (self.angle + angle_delta) % 360
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

    def get_endpoints(self):
        # Returns the endpoints of the line after rotation
        rad = math.radians(-self.angle)
        dx = math.cos(rad) * self.length / 2
        dy = math.sin(rad) * self.length / 2
        x, y = self.center
        return ((x - dx, y - dy), (x + dx, y + dy))

class Circle(pygame.sprite.Sprite):
    def __init__(self, radius, center, thickness):
        super().__init__()
        self.radius = radius
        self.center = center
        self.thickness = max(1, thickness)

        size = (radius * 2 + self.thickness, radius * 2 + self.thickness)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(
            self.image, (255, 255, 255),
            (size[0] // 2, size[1] // 2),
            radius, self.thickness
        )
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, center):
        self.center = center
        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

def move_circle_to_one_point(line, circle):
    # Find the closest point on the line to the circle center
    (x1, y1), (x2, y2) = line.get_endpoints()
    cx, cy = circle.center

    # Line segment vector
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return circle.center

    # Project point onto the line segment
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    # Move circle center to be exactly radius away from the line, along the normal
    # Find the normal vector
    nx, ny = -(y2 - y1), (x2 - x1)
    norm = math.hypot(nx, ny)
    if norm == 0:
        return circle.center
    nx /= norm
    ny /= norm

    # Determine which side of the line the circle center is on
    side = (cx - x1) * ny - (cy - y1) * nx
    if side < 0:
        nx, ny = -nx, -ny

    # Place the circle so it just touches the line at one point
    new_cx = closest_x + nx * circle.radius
    new_cy = closest_y + ny * circle.radius
    return int(new_cx), int(new_cy)

def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Line & Circle One Point Touch")

    clock = pygame.time.Clock()

    line = Line(400, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), 1)
    circle = Circle(100, pygame.mouse.get_pos(), 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        angle_delta = 0
        if keys[pygame.K_a]:
            angle_delta = 2
        if keys[pygame.K_d]:
            angle_delta = -2

        line.update(angle_delta=angle_delta)
        mouse_pos = pygame.mouse.get_pos()
        circle.update(center=mouse_pos)

        # Check for overlap
        offset = (circle.rect.left - line.rect.left, circle.rect.top - line.rect.top)
        overlap = line.mask.overlap(circle.mask, offset)

        # If overlapping at more than one point, move the circle so it only touches at one point
        if overlap:
            new_center = move_circle_to_one_point(line, circle)
            circle.update(center=new_center)
            offset = (circle.rect.left - line.rect.left, circle.rect.top - line.rect.top)
            overlap = line.mask.overlap(circle.mask, offset)

        display_surface.fill((0, 0, 0))
        display_surface.blit(line.image, line.rect)
        display_surface.blit(circle.image, circle.rect)

        # Draw red dot at the point of contact if touching
        offset = (circle.rect.left - line.rect.left, circle.rect.top - line.rect.top)
        overlap = line.mask.overlap(circle.mask, offset)
        if overlap:
            collision_point = (line.rect.left + overlap[0], line.rect.top + overlap[1])
            pygame.draw.circle(display_surface, (255, 0, 0), collision_point, 5)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()