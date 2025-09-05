import pygame
import sys
import math
import random
import time
import numpy as np

# --- Constants ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
PONGBALL_SPEED = 400
PONGBALL_DAMAGE = 100
SPAWNPROB = 1
POLYGON_MAXSIDES = 5
POLYGON_MINSIDES = 3
POLYGON_MAXSIZE = 100
POLYGON_MINSIZE = 50
POLYGON_MAX_NUMBER = 10
POLYGON_HEALTH = 300
PADDLE_SPEED_IDLE = 300
PADDLE_SPEED_MANUAL = 300
PADDLE_DISTANCE_FROM_EDGE = 50
PROJECTILE_COOLDOWN = 0.1
THICKNESS = 1
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20

pygame.init()
collision_sound = pygame.mixer.Sound(r'.\Sounds\18782.mp3')
pewpew_sound = pygame.mixer.Sound(r'.\Sounds\mixkit-short-laser-gun-shot-1670.wav')

class Mob(pygame.sprite.Sprite):

    def __init__(self, center, size):

        super().__init__()

        self.center = list(center)
        self.size = size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.center)
        # self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass
    
    def clamp_to_screen(self):  
        """
        If any part of the Mob's rect is off the screen, move it so its bounding rectangle is fully on screen.
        """
        Mob.refresh_image(self)

        dx, dy = 0, 0

        if self.rect.left < 0:
            dx = -self.rect.left
        elif self.rect.right > WINDOW_WIDTH:
            dx = WINDOW_WIDTH - self.rect.right

        if self.rect.top < 0:
            dy = -self.rect.top
        elif self.rect.bottom > WINDOW_HEIGHT:
            dy = WINDOW_HEIGHT - self.rect.bottom

        if dx != 0 or dy != 0:
            self.points = [(x + dx, y + dy) for (x, y) in self.points]
            self.center = [self.center[0] + dx, self.center[1] + dy]
        
        Mob.refresh_image(self)

    def refresh_image(self):
        self.rect = self.image.get_rect(center=self.center)
        # self.mask = pygame.mask.from_surface(self.image)


class Polygon(Mob):

    @classmethod
    def get_local_points(cls, points):
        # Calculate offset for local coordinates
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x = min(xs)
        min_y = min(ys)
        local_points = [(x - min_x, y - min_y) for (x, y) in points]
        return local_points, min_x, min_y
    
    @classmethod
    def get_size(cls, points):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x = min(xs)
        min_y = min(ys)
        size = (max(xs) - min_x, max(ys) - min_y)
        if size[0] <= 0 or size[1] <= 0:
            size = (1, 1)
        return size

    def __init__(self, points, center,  orientation = 0, color= [255,255,255], thickness=1):

        super().__init__(center, Polygon.get_size(points))

        self.points = points
        self.local_points = []
        self.fillcolor = color
        self.bordercolor = color
        self.thickness = max(1, thickness)
        self.rotate(orientation)
        self.set_local_coords()
        
        # Draw the filled polygon
        pygame.draw.polygon(self.image, self.fillcolor, self.local_points, 0)
        # Draw the polygon outline
        pygame.draw.polygon(self.image, self.bordercolor, self.local_points, self.thickness)

    def move(self, vector, dt):
        self.center = [self.center[0] + vector[0] * dt, self.center[1] + vector[1]* dt]
        # Move all points by the same vector
        self.points = [(x + vector[0] * dt, y + vector[1] * dt) for (x, y) in self.points]
        self.clamp_to_screen()     
        self.refresh_image()

    def rotate_degrees_per_second(self, degrees, dt):
        self.rotate(degrees * dt)

    def rotate(self, degrees):
        # Rotate self.points by 'degrees' about the center
        radians = math.radians(degrees)
        cos_theta = math.cos(radians)
        sin_theta = math.sin(radians)
        cx, cy = self.center

        new_points = []
        for x, y in self.points:
            # Translate point to origin
            tx = x - cx
            ty = y - cy
            # Rotate
            rx = tx * cos_theta - ty * sin_theta
            ry = tx * sin_theta + ty * cos_theta
            # Translate back
            new_x = rx + cx
            new_y = ry + cy
            new_points.append((new_x, new_y))

        self.points = new_points
        self.center = [cx, cy]

        self.size = Polygon.get_size(self.points)
        Polygon.refresh_image(self)

    def set_local_coords(self):
        self.local_points, self.minx, self.miny = self.get_local_points(self.points)       

    def calculate_size(self):
        self.size = self.get_size(self.points)

    def refresh_image(self):
        self.clamp_to_screen()
        self.set_local_coords()
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))
        # Draw the filled polygon
        pygame.draw.polygon(self.image, self.fillcolor, self.local_points, 0)
        # Draw the polygon outline
        pygame.draw.polygon(self.image, self.bordercolor, self.local_points, self.thickness)


class Block(Polygon):

    @classmethod
    def create_rectangle(cls, xlength, ylength, center, color, thickness, orientation=0, damagefactor=1.0):
        # Create the four corners of the rectangle centered at 'center'
        points = cls.get_points(xlength, ylength, center)
        return cls(points, center, color, thickness, orientation, damagefactor)

    @classmethod
    def get_points(cls, xlength, ylength, center):
        # Create the four corners of the rectangle centered at 'center'
        hw = int(xlength / 2)
        hh = int(ylength / 2)
        points = [
            (center[0] - hw, center[1] - hh),  # Top-left
            (center[0] + hw, center[1] - hh),  # Top-right
            (center[0] + hw, center[1] + hh),  # Bottom-right
            (center[0] - hw, center[1] + hh),  # Bottom-left
        ]
        return points

    def __init__(self, points, center, color=[255, 255, 255], thickness=1, orientation=0):
        super().__init__(points, center, orientation, color, thickness)

    def refresh_image(self):
        super().refresh_image()


class ObstacleBlock(Block):

    @classmethod
    def create_obstacleblock(cls, xlength, ylength, center, color, thickness, orientation=0, damagefactor=1.0):
        # Create the four corners of the rectangle centered at 'center'
        points = Block.get_points(xlength, ylength, center)
        return cls(points, center, color, thickness, orientation, damagefactor)

    def __init__(self, points, center, color=[255, 255, 255], thickness=1, orientation=0, damagefactor=1.0):

        super().__init__(points, center, color, thickness, orientation)

        self.health = self.size[0] * self.size[1] 
        self.max_health = self.health
        self.damagefactor = damagefactor

    def refresh_image(self):
        healthscale = max(0, self.health) / self.max_health

        self.fillcolor = (int(self.fillcolor[0] * healthscale), 
                           int(self.fillcolor[1] * healthscale), 
                           int(self.fillcolor[2] * healthscale))
        super().refresh_image()

    def take_damage(self, damage):
        self.health -= damage * self.damagefactor
        self.refresh_image()



class Crosshairs(pygame.sprite.Sprite):
    def __init__(self, radius=15, line_length=10, thickness=2):
        super().__init__()
        self.radius = radius
        self.line_length = line_length
        self.thickness = thickness
        size = (radius * 2 + line_length * 2, radius * 2 + line_length * 2)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_position((0, 0))
        self.refresh_image()
        

    def refresh_image(self):
        self.image.fill((0, 0, 0, 0))
        center = (self.image.get_width() // 2, self.image.get_height() // 2)
        # Draw circle
        pygame.draw.circle(self.image, (255, 255, 255, 180), center, self.radius, self.thickness)
        # Draw lines (N, S, E, W)
        pygame.draw.line(
            self.image, (255, 255, 255, 180),
            (center[0], center[1] - self.radius - self.line_length),
            (center[0], center[1] - self.radius), self.thickness
        )
        pygame.draw.line(
            self.image, (255, 255, 255, 180),
            (center[0], center[1] + self.radius),
            (center[0], center[1] + self.radius + self.line_length), self.thickness
        )
        pygame.draw.line(
            self.image, (255, 255, 255, 180),
            (center[0] - self.radius - self.line_length, center[1]),
            (center[0] - self.radius, center[1]), self.thickness
        )
        pygame.draw.line(
            self.image, (255, 255, 255, 180),
            (center[0] + self.radius, center[1]),
            (center[0] + self.radius + self.line_length, center[1]), self.thickness
        )

    def update_position(self, pos):
        # pos is the mouse position
        self.rect.center = pos

def unit_vector(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        raise ValueError("Zero vector has no direction")
    return v / norm

def point_to_segment_distance(p, a, b):
    """
    Compute the distance from point p to the segment ab.

    Args:
        p (tuple): (px, py)
        a (tuple): (x1, y1)
        b (tuple): (x2, y2)

    Returns:
        tuple: (distance, (proj_x, proj_y)) where (proj_x, proj_y) is the closest point on the segment.
    """
    px, py = p
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        # The segment is a point
        return math.hypot(px - x1, py - y1), (x1, y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    dist = math.hypot(px - proj_x, py - proj_y)
    return dist, (proj_x, proj_y)

def nearest_edge(p, points):
    """
    Given a point p=(px, py) and a list of (x, y) tuples for a polygon,
    find the nearest edge to p.
    Returns (i, j, proj) where points[i] and points[j] are the ends of the nearest edge,
    and proj is the (x, y) of the closest point on the edge.
    """
    px, py = p
    n = len(points)
    min_dist = None
    nearest = None
    nearest_proj = None

    for i in range(n):
        j = (i + 1) % n
        dist, proj = point_to_segment_distance((px, py), points[i], points[j])
        if min_dist is None or dist < min_dist:
            min_dist = dist
            nearest = [points[i], points[j]]
            nearest_proj = proj

    return list(nearest)


class Pongball(Mob):

    @classmethod
    def get_size(cls, radius, thickness):
        return (radius * 2 + thickness, radius * 2 + thickness)

    def __init__(self, radius, center,  color=[255,255,255], thickness=1, velocity=(10,10)):

        super().__init__(center,  Pongball.get_size(radius, thickness))
        self.radius = radius
        self.thickness = max(1, thickness)
        self.velocity = list(velocity)
        self.fillcolor  = color
        self.bordercolor = color
        self.refresh_image()

    def set_velocity(self, vx, vy):
        self.velocity = [vx, vy]

    def bounce_boundary(self):
        if self.center[0] - self.radius < 0:
            self.center[0] = self.radius
            self.velocity[0] *= -1
        if self.center[0] + self.radius > WINDOW_WIDTH:
            self.center[0] = WINDOW_WIDTH - self.radius
            self.velocity[0] *= -1
        if self.center[1] - self.radius < 0:
            self.center[1] = self.radius
            self.velocity[1] *= -1
        if self.center[1] + self.radius > WINDOW_HEIGHT:
            self.center[1] = WINDOW_HEIGHT - self.radius
            self.velocity[1] *= -1


    def refresh_image(self):
        pygame.draw.circle(self.image, self.fillcolor,
            (int(self.size[0] // 2), int(self.size[1] // 2)), self.radius, 0)
        pygame.draw.circle(self.image, self.bordercolor,
            (int(self.size[0] // 2), int(self.size[1] // 2)), self.radius, self.thickness)

        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, vector=None, dt = 0):
        if vector is None:
            vector = self.velocity
        self.center[0] += vector[0] * dt
        self.center[1] += vector[1] * dt
        self.rect.center = self.center

    def update_position(self, pos):
        # pos is the mouse position
        self.rect.center = pos

    def update(self):
        self.bounce_boundary()
        super().update()

        
    def collidemob(self, mob):
        blockplayercollide = pygame.sprite.collide_mask(mob, self)
        if blockplayercollide is not None:
            dotcoord = (mob.rect.topleft[0] + blockplayercollide[0], mob.rect.topleft[1] + blockplayercollide[1])
            clipping_projection = dotcoord - unit_vector(self.velocity) * (self.radius + 1)

            self.center = clipping_projection
            self.refresh_image()
            self.update()


class Paddle(Polygon):

        # polygon constructor def __init__(self, points, center,  orientation = 0, color= [255,255,255], thickness=1):
    def __init__(self, center, length, orientation = 0 , color = [255,255,255], thickness=25):

        super().__init__(Block.get_points(length, thickness, center), center, orientation, color, thickness)

    def get_endpoints(self):
        angle_rad = 0  # Flat (horizontal) line 
        dx = (self.length / 2) * math.cos(angle_rad)
        dy = (self.length / 2) * math.sin(angle_rad)
        x1 = int(self.center[0] - dx)
        y1 = int(self.center[1] - dy)
        x2 = int(self.center[0] + dx)
        y2 = int(self.center[1] + dy)
        return [(x1, y1), (x2, y2)]

class PlayerPaddle(Paddle):
    # Player paddle is always at the bottom of the screen

    def __init__(self, center, color = [255, 255, 255]):
        super().__init__(center, PADDLE_WIDTH, 0, color, PADDLE_HEIGHT)
        self.keys = [pygame.K_a, pygame.K_d, pygame.K_w]
        self.shootbutton = 0
        self.auto = True  # If True, paddle moves automatically
        self.autocooldown = 0.01
        self.last_autotime = 0
        self.length = PADDLE_WIDTH
        self.update()

    def move_towards(self, x, speed, dt):
        if abs(self.center[0] - x) > 1:
            direction = 1 if x > self.center[0] else -1
            self.move((direction * speed,0), dt)


    def handle_input(self, keys, mousebuttons, mousepos, pongball, projectiles, dt):

        if keys[self.keys[0]]:
            self.move((-PADDLE_SPEED_MANUAL,0), dt)
            if self.auto: self.auto = not self.auto           
        elif keys[self.keys[1]]:
            self.move((PADDLE_SPEED_MANUAL,0), dt)
            if self.auto: self.auto = not self.auto
        elif keys[self.keys[2]]:
            if time.time() - self.last_autotime >= self.autocooldown:
                self.auto = not self.auto           

        if self.auto:
            self.move_towards(pongball.center[0], PADDLE_SPEED_IDLE, dt)

        # Keep paddle on screen
        self.center[0] = max(int(self.length//2), min(int(WINDOW_WIDTH-self.length//2), self.center[0]))

        # Shooting
        # if mousebuttons[self.shootbutton]:
        #     now = time.time()
        #     if now - self.last_shot_time >= PROJECTILE_COOLDOWN:
        #         proj = Projectile(20, (self.center[0], self.center[1]), 1, 'standard', mousepos)
        #         projectiles.add(proj)
        #         self.last_shot_time = now


# returns the distance from point (px, py) to the segment (x1, y1)-(x2, y2)
# and also the unit vector of a perpendicular line from px,py to the segment (x1, y1)-(x2, y2)

def point_to_segment_distance(p, a, b):
    """
    Compute the distance from point p to the segment ab.

    Args:
        p (tuple): (px, py)
        a (tuple): (x1, y1)
        b (tuple): (x2, y2)

    Returns:
        tuple: (distance, (proj_x, proj_y)) where (proj_x, proj_y) is the closest point on the segment.
    """
    px, py = p
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        # The segment is a point
        return math.hypot(px - x1, py - y1), (x1, y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    dist = math.hypot(px - proj_x, py - proj_y)
    return dist, (proj_x, proj_y)

def main():
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PvPong")

    clock = pygame.time.Clock()

    # mobgroup = pygame.sprite.Group()
    
    # mobgroup.add(Block(200, 50, (600, 360), THICKNESS, 50))
    # mobgroup.add(Block(100, 25, (200, 400), THICKNESS, 90))
    # mobgroup.add(Block(300, 15, (800, 150), THICKNESS, 45))

    mobgroup = pygame.sprite.Group()
    # mobgroup.add(ObstacleBlock.create_rectangle(600, 50, (600, 360), [255, 255, 255], 1))

    mob = ObstacleBlock.create_rectangle(600, 50, (600, 360), [255, 255, 255], 1)
    
    player1 = PlayerPaddle((int(WINDOW_WIDTH // 2), WINDOW_HEIGHT - 50))
    # crosshairs = Crosshairs()
    
    pongball = Pongball(5, (350, 190), [255,255,255], 1, [0,0])
    
    projectiles = []

    running = True
   
    BLOCKMOVE = 100

    print("Running this code")
    while running:

        dt = clock.tick(60) / 1_000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            mob.move([-BLOCKMOVE,0], dt)
        if keys[pygame.K_RIGHT]:
            mob.move([BLOCKMOVE,0], dt)
        if keys[pygame.K_UP]:
            mob.move([0,-BLOCKMOVE], dt)
        if keys[pygame.K_DOWN]:
            mob.move([0,BLOCKMOVE], dt)
        if keys[pygame.K_n]:
            mob.rotate_degrees_per_second(BLOCKMOVE, dt)  
        if keys[pygame.K_m]:
            mob.rotate_degrees_per_second(-BLOCKMOVE, dt)
        mob.update()

        display_surface.fill((0, 0, 0))        


        mousebuttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # pongball.move(dt=dt)
        pongball.update_position(mouse_pos)
        pongball.update()
        # crosshairs.update_position(mouse_pos)

        player1.handle_input(keys, mousebuttons, mouse_pos, pongball, projectiles, dt)
        player1.update()       

        mobgroup.update()

        display_surface.blit(mob.image, mob.rect)
        display_surface.blit(pongball.image, pongball.rect)
        # display_surface.blit(crosshairs.image, crosshairs.rect)
        display_surface.blit(player1.image, player1.rect)

        pongball.collidemob(mob)
        
        mobgroup.draw(display_surface)


        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
