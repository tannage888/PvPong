




import pygame
import sys
import math
import random
import time

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

pygame.init()
collision_sound = pygame.mixer.Sound(r'.\Pong\Sounds\18782.mp3')
pewpew_sound = pygame.mixer.Sound(r'.\Pong\Sounds\mixkit-short-laser-gun-shot-1670.wav')

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.points = []
        self.center = [0, 0]
        self.color = (255, 255, 255)
        self.thickness = 1
        self.image = None
        self.rect = None
        self.mask = None

    def update(self):
        pass


        

class Line(pygame.sprite.Sprite):
    def __init__(self, length, center, orientation, thickness, color=(255,255,255)):
        super().__init__()
        self.length = length
        self.center = list(center)
        self.orientation = orientation
        self.thickness = max(1, thickness)
        self.color = color
        self.image = pygame.Surface((length, self.thickness), pygame.SRCALPHA)
        pygame.draw.line(
            self.image, self.color,
            (0, self.thickness // 2), (length, self.thickness // 2),
            self.thickness
        )
        self.orig_image = self.image.copy()
        self.image = pygame.transform.rotate(self.orig_image, -self.orientation)
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity = [0, 0]

    def update(self):
        self.image = pygame.transform.rotate(self.orig_image, -self.orientation)
        self.rect = self.image.get_rect(center=self.center)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dx):
        self.center[0] += dx
        self.update()

    def move_towards(self, x, speed, dt):
        if abs(self.center[0] - x) > 1:
            direction = 1 if x > self.center[0] else -1
            self.move(direction * speed * dt)

    def set_velocity(self, vx, vy):
        self.velocity = [vx, vy]

    def move_projectile(self, dt):
        self.center[0] += self.velocity[0] * dt
        self.center[1] += self.velocity[1] * dt
      



class Projectile(Line):
    colour_dict = {
        "standard": (255, 0, 0),  # red
        "bouncy": (0, 255, 0)     # green
    }

    def __init__(self, length, center, thickness, type_, targetcenter):
        # Calculate angle from center to targetcenter
        dx = targetcenter[0] - center[0]
        dy = targetcenter[1] - center[1]
        angle_rad = math.atan2(dy, dx)
        orientation = math.degrees(angle_rad)
        color = Projectile.colour_dict[type_]
        super().__init__(length, center, orientation, thickness, color)
        self.type = type_
        self.targetcenter = targetcenter
        self.orientation = orientation  # store for reference

        # Set velocity towards targetcenter at speed PONGBALL_SPEED*2
        speed = PONGBALL_SPEED * 2
        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed
        self.set_velocity(vx, vy)
        pewpew_sound.play()

    def update(self, polygons, pongball, projectiles, dt):
        self.move_projectile(dt)
        # Remove if off screen
        if (self.center[0] < 0 or self.center[0] > WINDOW_WIDTH or
            self.center[1] < 0 or self.center[1] > WINDOW_HEIGHT):
            projectiles.remove(self)
            return
        # Collide with polygons
        for poly in list(polygons):
            offset = (self.rect.left - poly.rect.left, self.rect.top - poly.rect.top)
            if poly.mask.overlap(self.mask, offset):
                poly.damage(PONGBALL_DAMAGE)
                poly.on_hit(pongball)
                poly.refresh_image()
                collision_sound.play()

                if self.type == "standard":
                    projectiles.remove(self)
                elif self.type == "bouncy":
                    # Bounce: reflect velocity over normal (approximate as away from center)
                    dx = self.center[0] - poly.center[0]
                    dy = self.center[1] - poly.center[1]
                    norm = math.hypot(dx, dy)
                    if norm != 0:
                        nx, ny = dx / norm, dy / norm
                        v_dot_n = self.velocity[0] * nx + self.velocity[1] * ny
                        self.velocity[0] -= 2 * v_dot_n * nx
                        self.velocity[1] -= 2 * v_dot_n * ny
                return
        # Collide with pongball
        offset = (self.rect.left - pongball.rect.left, self.rect.top - pongball.rect.top)
        if pongball.mask.overlap(self.mask, offset):
            dx = pongball.center[0] - self.center[0]
            dy = pongball.center[1] - self.center[1]
            norm = math.hypot(dx, dy)
            if norm != 0:
                nx, ny = dx / norm, dy / norm
                v_dot_n = pongball.velocity[0] * nx + pongball.velocity[1] * ny
                pongball.velocity[0] -= 2 * v_dot_n * nx
                pongball.velocity[1] -= 2 * v_dot_n * ny
                pongball.move(dt)
                collision_sound.play()
            if self.type == "standard":
                projectiles.remove(self)
            elif self.type == "bouncy":
                # Bounce: reflect velocity over normal (approximate as away from center)
                dx = self.center[0] - pongball.center[0]
                dy = self.center[1] - pongball.center[1]
                norm = math.hypot(dx, dy)
                if norm != 0:
                    nx, ny = dx / norm, dy / norm
                    v_dot_n = self.velocity[0] * nx + self.velocity[1] * ny
                    self.velocity[0] -= 2 * v_dot_n * nx
                    self.velocity[1] -= 2 * v_dot_n * ny
        super().update()

class Paddle(Line):
    def __init__(self, center):
        length = 100
        thickness = 5
        angle = 0
        super().__init__(length, center, angle, thickness)
        self.location = center

        self.last_shot_time = 0

    def get_endpoints(self):
        angle_rad = math.radians(self.orientation)
        dx = (self.length / 2) * math.cos(angle_rad)
        dy = (self.length / 2) * math.sin(angle_rad)
        x1 = int(self.center[0] - dx)
        y1 = int(self.center[1] - dy)
        x2 = int(self.center[0] + dx)
        y2 = int(self.center[1] + dy)
        return [(x1, y1), (x2, y2)]

class PlayerPaddle(Paddle):
    
    # Player padde is always at the bottom of the screen

    def __init__(self, center):
        super().__init__(center)
        self.keys = [pygame.K_a, pygame.K_d, pygame.K_w]
        self.shootbutton = 0
        self.auto = False  # If True, paddle moves automatically
        self.autocooldown = 0.01
        self.last_autotime = 0

    def handle_input(self, keys, mousebuttons, mousepos, pongball, projectiles, dt):

        if keys[self.keys[0]]:
            self.move(-PADDLE_SPEED_MANUAL * dt)
            self.auto = not self.auto           
        elif keys[self.keys[1]]:
            self.move(PADDLE_SPEED_MANUAL * dt)
            self.auto = not self.auto           
        elif keys[self.keys[2]]:
            if time.time() - self.last_autotime >= self.autocooldown:
                self.auto = not self.auto           

        # Keep paddle on screen
        self.center[0] = max(int(self.length//2), min(int(WINDOW_WIDTH-self.length//2), self.center[0]))
        if self.auto:
            self.move_towards(pongball.center[0], PADDLE_SPEED_IDLE, dt)
        # Shooting
        if mousebuttons[self.shootbutton]:
            now = time.time()
            if now - self.last_shot_time >= PROJECTILE_COOLDOWN:
                proj = Projectile(20, (self.center[0], self.center[1]), 1, 'standard', mousepos)
                projectiles.add(proj)
                self.last_shot_time = now


class ComputerPaddle(Paddle):
    
    def __init__(self, center):
        super().__init__(center)
        self.keys = []
        self.shootbutton = 0

    def handle_input(self, keys, mousebuttons, mousepos, pongball, projectiles, dt):

        if pongball.rect.center[0] < self.rect.centerx:
            self.move(-PADDLE_SPEED_MANUAL * dt)

        elif pongball.rect.center[0] > self.rect.centerx:
            self.move(PADDLE_SPEED_MANUAL * dt)

        # Keep paddle on screen
        self.center[0] = max(int(self.length//2), min(int(WINDOW_WIDTH-self.length//2), self.center[0]))

        # Shooting
        # if mousebuttons[self.shootbutton]:
        #     now = time.time()
        #     if now - self.last_shot_time >= PROJECTILE_COOLDOWN:
        #         if self.location == 'top':
        #             proj = Projectile(20, (self.center[0], self.center[1] + 10), 90, 1, 'down', 'standard')
        #         else:
        #             proj = Projectile(20, (self.center[0], self.center[1] - 10), 90, 1, 'up', 'standard')
        #         projectiles.add(proj)
        #         self.last_shot_time = now


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
            (int(size[0] // 2), int(size[1] // 2)),
            radius, 0
        )
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity = [0, 0]

    def update(self):
        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))
        self.mask = pygame.mask.from_surface(self.image)

    def set_velocity(self, vx, vy):
        self.velocity = [vx, vy]

    def move(self, dt):
        self.center[0] += self.velocity[0] * dt
        self.center[1] += self.velocity[1] * dt
        self.update()

    def bounce_boundary(self):
        bounced = False
        if self.center[0] - self.radius < 0:
            self.center[0] = self.radius
            self.velocity[0] *= -1
            bounced = True
        if self.center[0] + self.radius > WINDOW_WIDTH:
            self.center[0] = WINDOW_WIDTH - self.radius
            self.velocity[0] *= -1
            bounced = True
        if self.center[1] - self.radius < 0:
            self.center[1] = self.radius
            self.velocity[1] *= -1
            bounced = True
        if self.center[1] + self.radius > WINDOW_HEIGHT:
            self.center[1] = WINDOW_HEIGHT - self.radius
            self.velocity[1] *= -1
            bounced = True
        if bounced:
            self.update()

class Polygon(pygame.sprite.Sprite):
    def __init__(self, points, center, thickness, orientation=0, damagefactor=1.0):
        super().__init__()

        self.center = list(center)
        self.health = POLYGON_HEALTH
        self.thickness = max(1, thickness)
        self.mass = 10
        self.points = points
        self.orientation = orientation
        self.damagefactor = damagefactor  # Multiplier for damage taken on hit
        if orientation != 0:
            self.rotate(orientation)

        # Calculate offset for local coordinates
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.size = (max(xs) - self.min_x, max(ys) - self.min_y)

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.refresh_image()
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def get_local_points(self):
        # Convert global points to local surface coordinates
        return [(x - self.min_x, y - self.min_y) for (x, y) in self.points]

    def refresh_image(self):
        fill = int(255 * max(0, self.health) / POLYGON_HEALTH)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.size = (max(xs) - self.min_x, max(ys) - self.min_y)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))
        self.mask = pygame.mask.from_surface(self.image)

        local_points = self.get_local_points()
        pygame.draw.polygon(self.image, (fill, fill, fill), local_points, 0)
        pygame.draw.polygon(self.image, (255, 255, 255), local_points, self.thickness)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):        
        self.rect = self.image.get_rect(center=(int(self.center[0]), int(self.center[1])))      
        self.refresh_image()

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
        self.orientation = (self.orientation + degrees) % 360
        self.update()

    def damage(self, amount):
        self.health -= amount * self.damagefactor
        if self.health <= 0:
            self.kill()
        self.refresh_image()

    def on_hit(self, impactmob=None):
        # Default behavior: do nothing
        pass
    
class Block(Polygon):

    def __init__(self, xlength, ylength, center, thickness, orientation=0,damagefactor=1.0):
        # Calculate the four corners of the rectangle centered at 'center'
        hw = int(xlength / 2)
        hh = int(ylength / 2)
        # Start with axis-aligned rectangle points (before rotation)
        points = [
            (center[0] - hw, center[1] - hh),  # Top-left
            (center[0] + hw, center[1] - hh),  # Top-right
            (center[0] + hw, center[1] + hh),  # Bottom-right
            (center[0] - hw, center[1] + hh),  # Bottom-left
        ]

        super().__init__(points, center, thickness, orientation=orientation,damagefactor=damagefactor)


class Crosshairs(pygame.sprite.Sprite):
    def __init__(self, radius=15, line_length=10, thickness=2):
        super().__init__()
        self.radius = radius
        self.line_length = line_length
        self.thickness = thickness
        size = (radius * 2 + line_length * 2, radius * 2 + line_length * 2)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_image()
        self.update_position((0, 0))

    def update_image(self):
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


class Gravwell(Polygon):
    def __init__(self, center, radius, range_, g, thickness=2):
        # Draw a circle as the gravwell
        points = []
        num_points = 32
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        super().__init__(points, center, thickness)
        self.radius = radius
        self.range = range_
        self.g = g

    def attract(self, pongball, dt):
        # Calculate distance from pongball to gravwell center
        dx = self.center[0] - pongball.center[0]
        dy = self.center[1] - pongball.center[1]
        dist = math.hypot(dx, dy)
        if dist < self.range and dist > 1:
            # Normalize direction
            nx = dx / dist
            ny = dy / dist
            # Apply acceleration towards gravwell
            pongball.velocity[0] += int(nx * self.g * dt)
            pongball.velocity[1] += int(ny * self.g * dt)


class MovableBlock(Block):
    def __init__(self, xlength, ylength, center, thickness, orientation=0, move=10, r=10, s=100, damagefactor=0.01):
        super().__init__(xlength, ylength, center, thickness, orientation, damagefactor)
        self.move_amount = move  # pixels to move on hit
        self.rotate_amount = r   # degrees to rotate on hit
        self.slow_amount = s     # amount to slow pongball (pixels per second)

    def on_hit(self, impactmob):
        impact_dx = impactmob.velocity[0]
        impact_dy = impactmob.velocity[1]
        # Normalize impact direction
        norm = math.hypot(impact_dx, impact_dy)
        if norm == 0:
            return
        nx = impact_dx / norm
        ny = impact_dy / norm
        # Move block in direction of impact
        self.center[0] += int(nx * self.move_amount)
        self.center[1] += (ny * self.move_amount)
        # Rotate block
        self.rotate(self.rotate_amount)
        # Slow pongball if provided
        if isinstance(impactmob, Circle):
            v_norm = math.hypot(impactmob.velocity[0], impactmob.velocity[1])
            if v_norm > self.slow_amount:
                scale = (v_norm - self.slow_amount) / v_norm
                impactmob.velocity[0] *= scale
                impactmob.velocity[1] *= scale
            # else:
            #     impactmob.velocity[0] = 0
            #     impactmob.velocity[1] = 0
        # Update position and image
        self.update()



def random_center_middle_third():
    x_min = 50
    x_max = WINDOW_WIDTH - 50
    y_min = WINDOW_HEIGHT // 3
    y_max = 2 * WINDOW_HEIGHT // 3
    x = random.randint(x_min, x_max)
    y = random.randint(y_min, y_max)
    return (x, y)

def clampcenter(xlen, ylen, center):
        # Clamp center so block stays fully on screen
    hw = xlen // 2
    hh = ylen // 2
    cx = max(hw, min(WINDOW_WIDTH - hw, center[0]))
    cy = max(hh, min(WINDOW_HEIGHT - hh, center[1]))
    center = (cx, cy)
    return center

def main():
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong AI Prompt Example")

    clock = pygame.time.Clock()

    pongball = Circle(10, (int(WINDOW_WIDTH // 2), int(WINDOW_HEIGHT // 2)), THICKNESS)
    angle = random.uniform(0, 2 * math.pi)
    pongball.set_velocity(int(math.cos(angle) * PONGBALL_SPEED), int(math.sin(angle) * PONGBALL_SPEED))

    Player1 = PlayerPaddle((int(WINDOW_WIDTH // 2), WINDOW_HEIGHT - 50))
    Player2 = ComputerPaddle((int(WINDOW_WIDTH // 2), 50))

    polygons = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    polygon_spawn_timer = 0

    crosshairs = Crosshairs()

    running = True
    while running:
        dt = clock.tick(60) / 1_000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mousebuttons = pygame.mouse.get_pressed()
        mousepos = pygame.mouse.get_pos()

        Player1.handle_input(keys, mousebuttons, mousepos, pongball, projectiles, dt)
        Player2.handle_input(keys, mousebuttons, mousepos, pongball, projectiles, dt)

        pongball.move(dt)
        pongball.bounce_boundary()


  # Polygon Spawning
        polygon_spawn_timer += dt
        if polygon_spawn_timer >= 1.0:
            polygon_spawn_timer = 0
            if len(polygons) < POLYGON_MAX_NUMBER and random.random() < SPAWNPROB:
                # Try up to 10 times to find a valid spawn location
                for _ in range(10):
                    polytype = random.choice(['hblock', 'vblock', 'gravwell', 'movableblock'])
                    # polytype = random.choice(['movableblock'])
                    center = random_center_middle_third()
                    if polytype == 'gravwell':
                        radius = 20
                        range_ = radius * 4
                        g = random.randint(800, 1500)
                        
                        new_block = Gravwell(center, radius, range_, g, thickness=2)

                    elif polytype in ['hblock', 'vblock']:
                        if polytype == 'hblock':
                            xlen = random.randint(50, 300)
                            ylen = 25
                            center = clampcenter(xlen, ylen, center)
                        elif polytype == 'vblock':
                            xlen = 25
                            ylen = random.randint(50, 300)
                            center = clampcenter(xlen, ylen, center)
                        new_block = Block(xlen, ylen, center, 5, orientation=0)
                    elif polytype == 'movableblock':
                        ylen = random.randint(50, 150)
                        xlen = ylen
                        center = clampcenter(xlen, ylen, center)
                        new_block = MovableBlock(xlen, ylen, center, 5, orientation=0)
                    
                    # Check for overlap with existing blocks (distance between centers >= 50 + max half-width)
                    overlap = False
                    for other in polygons:
                        dist = math.hypot(new_block.center[0] - other.center[0], new_block.center[1] - other.center[1])
                        min_dist = 50 + max(new_block.size[0], new_block.size[1], other.size[0], other.size[1]) // 2
                        if dist < min_dist or new_block.rect.colliderect(other.rect.inflate(50, 50)):
                            overlap = True
                            break
                    pongball_offset = (new_block.rect.left - pongball.rect.left, new_block.rect.top - pongball.rect.top)
                    if new_block.rect.colliderect(pongball.rect) or pongball.mask.overlap(new_block.mask, pongball_offset):
                        overlap = True
                    if not overlap:
                        polygons.add(new_block)
                        break


        # Polygon Collisions
        for poly in list(polygons):

            if isinstance(poly, Gravwell):
                poly.attract(pongball, dt)

            offset = (pongball.rect.left - poly.rect.left, pongball.rect.top - poly.rect.top)
            if poly.mask.overlap(pongball.mask, offset):
                # --- Improved bounce for Block (axis-aligned rectangle) ---
                if isinstance(poly, Block):
                    # Find overlap direction: compare previous and current positions
                    prev_x = pongball.center[0] - pongball.velocity[0] * dt
                    prev_y = pongball.center[1] - pongball.velocity[1] * dt
                    block_left = poly.rect.left
                    block_right = poly.rect.right
                    block_top = poly.rect.top
                    block_bottom = poly.rect.bottom

                    # Check which side the ball came from
                    if prev_y + pongball.radius <= block_top:
                        # Came from above, bounce vertically
                        pongball.center[1] = block_top - pongball.radius
                        pongball.velocity[1] *= -1
                    elif prev_y - pongball.radius >= block_bottom:
                        # Came from below, bounce vertically
                        pongball.center[1] = block_bottom + pongball.radius
                        pongball.velocity[1] *= -1
                    elif prev_x + pongball.radius <= block_left:
                        # Came from left, bounce horizontally
                        pongball.center[0] = block_left - pongball.radius
                        pongball.velocity[0] *= -1
                    elif prev_x - pongball.radius >= block_right:
                        # Came from right, bounce horizontally
                        pongball.center[0] = block_right + pongball.radius
                        pongball.velocity[0] *= -1
                    else:
                        # Fallback: reflect over vector from block center
                        dx = pongball.center[0] - poly.center[0]
                        dy = pongball.center[1] - poly.center[1]
                        norm = math.hypot(dx, dy)
                        if norm != 0:
                            nx, ny = dx / norm, dy / norm
                            v_dot_n = pongball.velocity[0] * nx + pongball.velocity[1] * ny
                            pongball.velocity[0] -= 2 * v_dot_n * nx
                            pongball.velocity[1] -= 2 * v_dot_n * ny
                else:
                    # Default polygon bounce (reflect over normal)
                    dx = pongball.center[0] - poly.center[0]
                    dy = pongball.center[1] - poly.center[1]
                    norm = math.hypot(dx, dy)
                    if norm == 0:
                        continue
                    nx, ny = dx / norm, dy / norm
                    v_dot_n = pongball.velocity[0] * nx + pongball.velocity[1] * ny
                    pongball.velocity[0] -= 2 * v_dot_n * nx
                    pongball.velocity[1] -= 2 * v_dot_n * ny

                pongball.move(dt)
                poly.damage(PONGBALL_DAMAGE)
                poly.refresh_image()
                collision_sound.play()
                break

        # Paddle Collisions
        for paddle in [Player1, Player2]:
            offset = (pongball.rect.left - paddle.rect.left, pongball.rect.top - paddle.rect.top)
            overlap = paddle.mask.overlap(pongball.mask, offset)
            if overlap:
                (x1, y1), (x2, y2) = paddle.get_endpoints()
                lx, ly = x2 - x1, y2 - y1
                norm = math.hypot(lx, ly)
                if norm == 0:
                    continue
                nx, ny = -(ly / norm), (lx / norm)
                v_dot_n = pongball.velocity[0] * nx + pongball.velocity[1] * ny
                pongball.velocity[0] -= 2 * v_dot_n * nx
                pongball.velocity[1] -= 2 * v_dot_n * ny
                pongball.move(dt)
                collision_sound.play()
                break

        # Projectile Movement and Collisions
        for proj in list(projectiles):
            proj.update(polygons, pongball, projectiles, dt)

        display_surface.fill((0, 0, 0))
        display_surface.blit(Player1.image, Player1.rect)
        display_surface.blit(Player2.image, Player2.rect)
        for poly in polygons:
            display_surface.blit(poly.image, poly.rect)
        for proj in projectiles:
            display_surface.blit(proj.image, proj.rect)
        display_surface.blit(pongball.image, pongball.rect)

        # In your game loop, before drawing:
        mouse_pos = pygame.mouse.get_pos()
        crosshairs.update_position(mouse_pos)
        display_surface.blit(crosshairs.image, crosshairs.rect)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()    