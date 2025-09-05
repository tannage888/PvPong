import pygame
import random
from sys import exit

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
PADDLE_WIDTH, PADDLE_HEIGHT = 10,80


PONGBALL_SPEED = 400
PONGBALL_DAMAGE = 100
SPAWNPROB = 1
POLYGON_HEALTH = 300
PADDLE_SPEED_IDLE = 300
PADDLE_SPEED_MANUAL = 300
PADDLE_DISTANCE_FROM_EDGE = 50
PROJECTILE_COOLDOWN = 0.1
THICKNESS = 1
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20

# Define game states
STATE_TITLE, STATE_GAME_ACTIVE, STATE_GAME_OVER, STATE_ROUND_OVER = range(4)

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

    def update(self):
        pass



class PongBall(Mob):

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
        self.update_position()
        super().update()

        
    def collidemob(self, mob):
        blockplayercollide = pygame.sprite.collide_mask(mob, self)
        if blockplayercollide is not None:
            dotcoord = (mob.rect.topleft[0] + blockplayercollide[0], mob.rect.topleft[1] + blockplayercollide[1])
            clipping_projection = dotcoord - unit_vector(self.velocity) * (self.radius + 1)

            self.center = clipping_projection
            self.refresh_image()
            self.update()




# class Paddle(pygame.sprite.Sprite):

#     def __init__(self, location, paddle_height):
#         # Call the parent class (Sprite) constructor
#         super().__init__()

#         # Pass in the color of the paddle, its width and height.
#         # Set the background color and set it to be transparent
#         self.image = pygame.Surface((PADDLE_WIDTH, paddle_height))
#         self.image.fill('Black')
#         self.image.set_colorkey('Black')

#         pygame.draw.rect(self.image, 'White', [0, 0, PADDLE_WIDTH, paddle_height])
#         self.rect = self.image.get_rect()
#         self.rect.x = location[0]
#         self.rect.y = location[1]

#         self.pewstate = False

#     # def event_handler(self):
#     #     return True

#     # def apply_physics(self):
#     #     return True
#     #
#     # def animate(self):
#     #     return True
#     #

#     # def update(self):
#     #     self.event_handler()
#         # self.apply_physics()
#         # self.animate()


# class PlayerPaddle(Paddle):

#     def __init__(self, paddle_height):
#         # Call the parent class (Sprite) constructor
#         super().__init__((50, int(WINDOW_HEIGHT/2)), paddle_height)
#         self.paddlespeed = 15
#         self.lastpewtime = pygame.time.get_ticks()
#         self.pewfreq = 250

#     def event_handler(self):
#         self.rect.y += pygame.mouse.get_rel()[1]

#         keys = pygame.key.get_pressed()

#         if keys[pygame.K_w]:
#             self.rect.y -= self.paddlespeed

#         if keys[pygame.K_s]:
#             self.rect.y += self.paddlespeed

#         if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.lastpewtime > self.pewfreq:
#             self.lastpewtime = pygame.time.get_ticks()
#             projectiles.add(PewPew((self.rect.right, self.rect.centery), PewPew.pewspeed))                  

#         if self.rect.bottom > WINDOW_HEIGHT:
#             self.rect.bottom = WINDOW_HEIGHT

#         if self.rect.top < 0:
#             self.rect.top = 0

#     # def apply_physics(self):
#     #     return True
#     #
#     # def animate(self):
#     #     return True
#     #

#     def update(self):
#         self.event_handler()
#     # self.apply_physics()
#     # self.animate()

# class ComputerPaddle(Paddle):

#     def __init__(self, pongball, paddle_height):
#         # Call the parent class (Sprite) constructor
#         super().__init__((WINDOW_WIDTH - 50, int(WINDOW_HEIGHT/2)), paddle_height)
#         self.pongball = pongball
#         self.paddlespeed = 5
#         self.pewprob = 0.015


#     def event_handler(self):
#         if pongball.rect.y > self.rect.y:
#             self.rect.y += self.paddlespeed

#         if pongball.rect.y < self.rect.y:
#             self.rect.y -= self.paddlespeed

#         if self.rect.bottom > WINDOW_HEIGHT:
#             self.rect.bottom = WINDOW_HEIGHT

#         if self.rect.top < 0:
#             self.rect.top = 0

#         if random.random() < self.pewprob:
#              projectiles.add(PewPew((self.rect.left, self.rect.centery), -1 * PewPew.pewspeed))           
    
        

#     # def apply_physics(self):
#     #     return True
#     #
#     # def animate(self):
#     #     return True
#     #

#     def update(self):
#         self.event_handler()

# class PewPew(pygame.sprite.Sprite):

#     # pewpew_sound = pygame.mixer.Sound(r'.\Pong\Sounds\laser-bolt-89300.mp3')
#     pewpew_sound = pygame.mixer.Sound(r'.\Pong\Sounds\mixkit-short-laser-gun-shot-1670.wav')
#     pewspeed = 25

#     def __init__(self, location, speed):
#         super().__init__()

#         self.image = pygame.Surface((10, 1))
#         self.image.fill('Black')
#         self.image.set_colorkey('Black')

#         pygame.draw.rect(self.image, 'Red', [0, 0, 10, 1])
#         self.rect = self.image.get_rect()
#         self.rect.x = location[0]
#         self.rect.y = location[1]

#         self.direction = speed
#         PewPew.pewpew_sound.play()

#     def update(self):
#         self.rect.x += self.direction
#         if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
#             self.kill()




# Define obstacles
class Block(Mob):

    def __init__(self, center, size, color=[255, 255, 255], thickness=1):
        super().__init__(size, center)
        self.health = size[0] * size[1]
        self.maxhealth = self.health

        self.image.fill('Black')
        self.image.set_colorkey('Black')

        self.colour = list(colour)
        self.startcolour = (255,255,255)

        pygame.draw.rect(self.image, self.colour, [0, 0, self.size[0], self.size[1]])
        # pygame.draw.rect(self.image, self.colour, [0, 0, self.xsize, self.ysize], self.colour,5)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def refresh_image(self):
        super().refresh_image()

    def update(self):
        return True

    def damage(self, damage):
        self.health -= damage
        
        if self.health <= 0:
            self.kill()
        else:
            ratio = self.health / self.maxhealth
            newcolour = [255,255,255]
            for i in range(3):
                newcolour[i] = int(self.colour[i]*ratio)
                if newcolour[i] > self.startcolour[i]/10:
                    newcolour[i] = int(self.colour[i]*ratio)
            pygame.draw.rect(self.image, newcolour, [0, 0, self.xsize, self.ysize]) 
            # play collision sound

# class Circle(Obstacle):

#     minradius = 30
#     maxradius = 60

#     spawnprob = 0.25
#     maxcircles = 6

#     @classmethod
#     def spawn(cls):
#         if random.random() < Circle.spawnprob:
#             circlelist = [ x for x in players if isinstance(x, Obstacle) ]
#             if len(circlelist) < Circle.maxcircles:
#                 newcircle = Circle()
#                 while len([x for x in circlelist if x.rect.colliderect(newcircle.rect)]) > 0:
#                     newcircle = Circle()
#                 players.add(newcircle)        
        

#     def __init__(self):
#         super().__init__()

#         self.radius = random.randint(Circle.minradius,Circle.maxradius)

#         self.image = pygame.Surface((self.radius * 2, self.radius * 2))
#         self.image.fill('Black')
#         self.image.set_colorkey('Black')

#         self.colour = (255,255,255)
#         self.startcolour = (255,255,255)

#         pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
#         # pygame.draw.rect(self.image, self.colour, [0, 0, self.xsize, self.ysize], self.colour,5)
#         self.rect = self.image.get_rect()
#         self.rect.center = (random.randint(200, WINDOW_WIDTH - 200), random.randint(self.radius, WINDOW_HEIGHT - self.radius))

#         self.health = int(3.1416 * self.radius ** 2)
#         self.maxhealth = self.health

#     def update(self):
#         return True

#     def damage(self, damage):
#         self.health -= damage
        
#         if self.health <= 0:
#             self.kill()
#         else:
#             ratio = self.health / self.maxhealth
#             newcolour = [255,255,255]
#             for i in range(3):
#                 newcolour[i] = int(self.colour[i]*ratio)
#                 if newcolour[i] > self.startcolour[i]/10:
#                     newcolour[i] = int(self.colour[i]*ratio)
#             pygame.draw.circle(self.image, newcolour, (self.radius, self.radius), self.radius)
#             Obstacle.impact_sound.play()



def display_score(start_time):
    current_time = pygame.time.get_ticks()
    score_surf = test_font.render(f'Current Score: {int((current_time - start_time) / 1000)}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 80))
    display_surface.blit(score_surf, score_rect)



def main():
    display_surface  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Pong')
    display_surface.fill((0,0,0))
    clock = pygame.time.Clock()

    # test_font = pygame.font.Font(r'.\Runner\font\PixelType.ttf', 50)
    # title_surf = test_font.render('Ready to Pong?', False, (255, 255, 255))
    # title_rect = title_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)))

    # winner_surf = test_font.render('Winner is: ', False, (255, 255, 255))
    # winner_rect = winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)+50))

    # round_winner_surf = test_font.render('Round Winner is: ', False, (255, 255, 255))
    # round_winner_rect = round_winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)))

    # round_continue_surf = test_font.render('Press any key to continue', False, (255, 255, 255))
    # round_continue_rect = round_continue_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)+80))

    # player_1_score_surf = test_font.render('P1 Score: ', False, (255, 255, 255))
    # player_1_score_rect = player_1_score_surf.get_rect(midleft=(50, 80))

    # player_2_score_surf = test_font.render('P2 Score: ', False, (255, 255, 255))
    # player_2_score_rect = player_2_score_surf.get_rect(midright=(WINDOW_WIDTH-50, 80))

    # round_surf = test_font.render(f'Round:1', False, (255, 255, 255))
    # round_rect = round_surf.get_rect(center =(int(WINDOW_WIDTH/2), 80))

    game_state = STATE_GAME_ACTIVE

    block_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(block_timer, 900)

    playedgame = False

    pongball = PongBall(5, (100,100))
    ball = pygame.sprite.GroupSingle()
    ball.add(pongball)

    players = pygame.sprite.Group()
    # players.add(PlayerPaddle(100))
    # players.add(ComputerPaddle(pongball,100))
    # players.add(Goal((0,0)))
    # players.add(Goal((WINDOW_WIDTH-1,0)))
    # players.add(Block())
    # players.add(Circle())

    # projectiles = pygame.sprite.Group()

    # obstacles = pygame.sprite.Group()
    obstacles.add(Block())

    player1_score = 0
    player2_score = 0
    round_number = 1

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

            if game_state == STATE_ROUND_OVER:
                if event.type == pygame.KEYDOWN:
                    game_state = STATE_GAME_ACTIVE
                    pongball = PongBall()
                    ball = pygame.sprite.GroupSingle()
                    ball.add(pongball)

                    players = pygame.sprite.Group()
                    players.add(PlayerPaddle(100))
                    players.add(ComputerPaddle(pongball,100))
                    players.add(Goal((0,0)))
                    players.add(Goal((WINDOW_WIDTH-1,0)))
                    round_number += 1
                    round_surf = test_font.render(f'Round:{round_number}', False, (255, 255, 255))

            if event.type == block_timer:
                Block.spawn()
                Circle.spawn()

        if game_state == STATE_GAME_ACTIVE:
            display_surface.fill((0, 0, 0))

            # player_1_score_surf = test_font.render(f'P1 Score: {player1_score}', False, (255, 255, 255))
            # player_2_score_surf = test_font.render(f'P2 Score: {player2_score}', False, (255, 255, 255))
            # display_surface.blit(player_1_score_surf,player_1_score_rect)
            # display_surface.blit(player_2_score_surf,player_2_score_rect)
            # display_surface.blit(round_surf,round_rect)

            ball.update()
            ball.draw(display_surface)
            projectiles.update()
            projectiles.draw(display_surface)
            players.update()
            players.draw(display_surface)
        
            coldict =  pygame.sprite.groupcollide(players, projectiles, False, False)
            for collmob in players:
                collist = coldict.get(collmob, [])
                for mob in collist:
                    if isinstance(mob, PewPew):
                        if isinstance(collmob, Obstacle):
                            collmob.damage(1000) 
                            mob.kill()


            for collmob in pygame.sprite.spritecollide(ball.sprite, players, False):
                pongball.collide(collmob)
                
                if isinstance(collmob, Obstacle):
                    collmob.damage(5000)

                elif isinstance(collmob, Goal):
                    if collmob.rect.x == 0:
                        game_state = STATE_ROUND_OVER
                        round_winner_surf = test_font.render(f'Round {round_number} Winner is: Computer', False, (255, 255, 255))
                        round_winner_rect = round_winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)))
                        player2_score += 1
                    if collmob.rect.x == WINDOW_WIDTH - 1:
                        game_state = STATE_ROUND_OVER
                        round_winner_surf = test_font.render(f'Round {round_number} Winner is: Player', False, (255, 255, 255))
                        round_winner_rect = round_winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)))
                        player1_score += 1                    

        elif game_state == STATE_ROUND_OVER:
            display_surface.fill((0, 0, 0))
            display_surface.blit(round_winner_surf,round_winner_rect)

        elif game_state == STATE_TITLE:
            pygame.draw.rect(display_surface, 'Black', title_rect)
            display_surface.blit(title_surf, title_rect)

            if playedgame:
                display_surface.blit(winner_surf, winner_rect)
        elif game_state == STATE_GAME_OVER:    
            print('GAME OVER')

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()