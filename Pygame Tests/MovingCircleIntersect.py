import pygame
import sys
import math
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720

class Line(pygame.sprite.Sprite):
    def __init__(self, length, center, thickness):
        super().__init__()
        self.length = length
        self.center = center
        self.thickness = max(1, thickness)
        self.angle = 0  # degrees

        self.image = pygame.Surface((length, self.thickness), pygame.SRCALPHA)
        pygame.draw.line(
            self.image, (255, 255, 255),
            (0, self.thickness // 2), (length, self.thickness // 2),
            self.thickness
        )
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, angle_delta=0):
        self.angle = (self.angle + angle_delta) % 360
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

    def get_endpoints(self):
        rad = math.radians(-self.angle)
        dx = math.cos(rad) * self.length / 2
        dy = math.sin(rad) * self.length / 2
        x, y = self.center
        return ((x - dx, y - dy), (x + dx, y + dy))

class Circle(pygame.sprite.Sprite):
    def __init__(self, radius, center, thickness):
        super().__init__()
        self.radius = radius
        self.center = list(center)
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

        # Random direction, normalized
        angle = random.uniform(0, 2 * math.pi)
        self.pixels_per_second = 400
        self.velocity = [math.cos(angle) * self.pixels_per_second, math.sin(angle) * self.pixels_per_second]  # 30 px/sec

    def update(self, dt):
        self.center[0] += self.velocity[0] * dt
        self.center[1] += self.velocity[1] * dt
        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))
        self.mask = pygame.mask.from_surface(self.image)

        # Bounce off boundaries
        if self.rect.left < 0:
            self.center[0] = self.radius
            self.velocity[0] *= -1
        if self.rect.right > WINDOW_WIDTH:
            self.center[0] = WINDOW_WIDTH - self.radius
            self.velocity[0] *= -1
        if self.rect.top < 0:
            self.center[1] = self.radius
            self.velocity[1] *= -1
        if self.rect.bottom > WINDOW_HEIGHT:
            self.center[1] = WINDOW_HEIGHT - self.radius
            self.velocity[1] *= -1

        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))

    def bounce_off_line(self, line):
        # Find the closest point on the line to the circle center
        (x1, y1), (x2, y2) = line.get_endpoints()
        cx, cy = self.center

        # Line segment vector
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            return

        # Project point onto the line segment
        t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Distance from circle center to closest point
        dist = math.hypot(cx - closest_x, cy - closest_y)
        if dist == 0:
            return

        # If touching or overlapping, bounce
        if dist <= self.radius:
            # Normal vector
            nx = (cx - closest_x) / dist
            ny = (cy - closest_y) / dist
            # Reflect velocity
            v_dot_n = self.velocity[0] * nx + self.velocity[1] * ny
            self.velocity[0] -= 2 * v_dot_n * nx
            self.velocity[1] -= 2 * v_dot_n * ny
            # Move circle out so it only touches at one point
            self.center[0] = closest_x + nx * self.radius
            self.center[1] = closest_y + ny * self.radius
            self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))

def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Line & Circle Bounce")

    clock = pygame.time.Clock()

    line = Line(400, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), 1)
    # Place circle away from the line
    circle = Circle(30, (WINDOW_WIDTH // 2 + 200, WINDOW_HEIGHT // 2 - 200), 1)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds

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
        circle.update(dt)

        # Bounce off the line
        offset = (circle.rect.left - line.rect.left, circle.rect.top - line.rect.top)
        overlap = line.mask.overlap(circle.mask, offset)
        if overlap:
            circle.bounce_off_line(line)

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

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()