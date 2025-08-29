import pygame
import random
from sys import exit

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
PADDLE_WIDTH, PADDLE_HEIGHT = 10,80

# Define game states
STATE_TITLE, STATE_GAME_ACTIVE, STATE_GAME_OVER, STATE_ROUND_OVER = range(4)

pygame.init()

class PongBall(pygame.sprite.Sprite):

    pongball_radius = 5

    def __init__(self):
        super().__init__()

        self.pongball_radius = PongBall.pongball_radius
        self.image = pygame.Surface([self.pongball_radius * 2, self.pongball_radius * 2])
        self.image.fill('Black')
        self.image.set_colorkey('Black')
        pygame.draw.circle(self.image, 'White', (self.pongball_radius, self.pongball_radius), self.pongball_radius, 0)

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.rect.x = int(WINDOW_WIDTH/2)
        self.rect.y = int(WINDOW_HEIGHT/2)

        self.vectorx = random.randint(-8,8)
        self.vectory = random.randint(-8,8)
        self.vectordelta = 4

        self.collision_sound = pygame.mixer.Sound(r'.\Pong\Sounds\18782.mp3')
        # self.collision_sound.set_volume = 0.25

    def event_handler(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.vectorx += self.vectordelta

        if keys[pygame.K_LEFT]:
            self.vectorx -= self.vectordelta

        if keys[pygame.K_UP]:
            self.vectory -= self.vectordelta

        if keys[pygame.K_DOWN]:
            self.vectory += self.vectordelta

    def apply_physics(self):
        playsound = False
        self.rect.x += self.vectorx

        if self.rect.left < 0:
            self.rect.left = 0
            self.vectorx *= -1
            playsound = True

        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.vectorx *= -1
            playsound = True

        self.rect.y += self.vectory

        if self.rect.top < 0:
            self.rect.top = 0
            self.vectory *= -1
            playsound = True

        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.vectory *= -1
            playsound = True

        if playsound: self.collision_sound.play()

    def collide(self, mob):
            
        if not isinstance(mob, Goal):
            self.collision_sound.play()

            overlap_x = min(self.rect.right - mob.rect.left, mob.rect.right - self.rect.left)
            overlap_y = min(self.rect.bottom - mob.rect.top, mob.rect.bottom - self.rect.top)

            # Check which overlap is smaller to determine the collision axis
            if overlap_x < overlap_y:
                # Collision occurred on the x-axis (left or right side)
                if self.rect.centerx < mob.rect.centerx:
                    collision_message = "Collision with right side of wall!"
                    self.rect.right = mob.rect.left
                    
                else:
                    collision_message = "Collision with left side of wall!"
                    self.rect.left = mob.rect.right
                # Reverse the x-speed to bounce off
                self.vectorx *= -1
            else:
                # Collision occurred on the y-axis (top or bottom side)
                if self.rect.centery < mob.rect.centery:
                    collision_message = "Collision with bottom side of wall!"
                    self.rect.bottom = mob.rect.top
                    
                else:
                    collision_message = "Collision with top side of wall!"
                    self.rect.top = mob.rect.bottom
                # Reverse the y-speed to bounce off
                self.vectory *= -1

            # print(collision_message)


            # if self.rect.bottom > mob.rect.top and self.rect.centery < mob.rect.centery and self.vectory > 0:
            #     self.rect.bottom = mob.rect.top
            #     self.vectory *= -1
            # elif self.rect.top < mob.rect.bottom and self.rect.centery > mob.rect.centery and self.vectory < 0:
            #     self.rect.top = mob.rect.bottom
            #     self.vectory *= -1
            # elif self.rect.left < mob.rect.right and self.rect.centerx > mob.rect.centerx and self.vectorx < 0:
            #     self.rect.left = mob.rect.right
            #     self.vectorx *= -1
            # elif self.rect.right > mob.rect.left and self.rect.centerx < mob.rect.centerx and self.vectorx > 0:
            #     self.rect.right = mob.rect.left
            #     self.vectorx *= -1


    # def animate(self):
    #     return True

    def update(self):
        self.event_handler()
        self.apply_physics()
        # self.animate()


class Paddle(pygame.sprite.Sprite):

    def __init__(self, location, paddle_height):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Pass in the color of the paddle, its width and height.
        # Set the background color and set it to be transparent
        self.image = pygame.Surface((PADDLE_WIDTH, paddle_height))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        pygame.draw.rect(self.image, 'White', [0, 0, PADDLE_WIDTH, paddle_height])
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]

        self.pewstate = False

    # def event_handler(self):
    #     return True

    # def apply_physics(self):
    #     return True
    #
    # def animate(self):
    #     return True
    #

    # def update(self):
    #     self.event_handler()
        # self.apply_physics()
        # self.animate()


class PlayerPaddle(Paddle):

    def __init__(self, paddle_height):
        # Call the parent class (Sprite) constructor
        super().__init__((50, int(WINDOW_HEIGHT/2)), paddle_height)
        self.paddlespeed = 15
        self.lastpewtime = pygame.time.get_ticks()
        self.pewfreq = 250

    def event_handler(self):
        self.rect.y += pygame.mouse.get_rel()[1]

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.rect.y -= self.paddlespeed

        if keys[pygame.K_s]:
            self.rect.y += self.paddlespeed

        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.lastpewtime > self.pewfreq:
            self.lastpewtime = pygame.time.get_ticks()
            projectiles.add(PewPew((self.rect.right, self.rect.centery), PewPew.pewspeed))                  

        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        if self.rect.top < 0:
            self.rect.top = 0

    # def apply_physics(self):
    #     return True
    #
    # def animate(self):
    #     return True
    #

    def update(self):
        self.event_handler()
    # self.apply_physics()
    # self.animate()

class ComputerPaddle(Paddle):

    def __init__(self, pongball, paddle_height):
        # Call the parent class (Sprite) constructor
        super().__init__((WINDOW_WIDTH - 50, int(WINDOW_HEIGHT/2)), paddle_height)
        self.pongball = pongball
        self.paddlespeed = 5
        self.pewprob = 0.015


    def event_handler(self):
        if pongball.rect.y > self.rect.y:
            self.rect.y += self.paddlespeed

        if pongball.rect.y < self.rect.y:
            self.rect.y -= self.paddlespeed

        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        if self.rect.top < 0:
            self.rect.top = 0

        if random.random() < self.pewprob:
             projectiles.add(PewPew((self.rect.left, self.rect.centery), -1 * PewPew.pewspeed))           
    
        

    # def apply_physics(self):
    #     return True
    #
    # def animate(self):
    #     return True
    #

    def update(self):
        self.event_handler()

class Goal(pygame.sprite.Sprite):

    def __init__(self, location):
        super().__init__()

        self.image = pygame.Surface((1, WINDOW_HEIGHT))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        pygame.draw.rect(self.image, 'Red', [0, 0, 1, WINDOW_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]

    def update(self):
        return True


class Border(pygame.sprite.Sprite):

    def __init__(self, location):
        super().__init__()

        self.image = pygame.Surface((WINDOW_WIDTH, 1))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        pygame.draw.rect(self.image, 'Red', [0, 0, WINDOW_WIDTH, 1])
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]

    def update(self):
        return True

class PewPew(pygame.sprite.Sprite):

    # pewpew_sound = pygame.mixer.Sound(r'.\Pong\Sounds\laser-bolt-89300.mp3')
    pewpew_sound = pygame.mixer.Sound(r'.\Pong\Sounds\mixkit-short-laser-gun-shot-1670.wav')
    pewspeed = 25

    def __init__(self, location, speed):
        super().__init__()

        self.image = pygame.Surface((10, 1))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        pygame.draw.rect(self.image, 'Red', [0, 0, 10, 1])
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]

        self.direction = speed
        PewPew.pewpew_sound.play()

    def update(self):
        self.rect.x += self.direction
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()



class Obstacle(pygame.sprite.Sprite):

    impact_sound = pygame.mixer.Sound(r'.\Pong\Sounds\mixkit-impact-of-a-blow-2150.wav')

    def __init__(self):
        super().__init__()

# Define obstacles
class Block(Obstacle):

    minxsize = 50
    minysize = 50

    maxxsize = 200
    maxysize = 200
    
    spawnprob = 0.25
    maxblocks = 6

    @classmethod
    def spawn(cls):
        if random.random() < Block.spawnprob:
            blocklist = [ x for x in players if isinstance(x, Obstacle) ]
            if len(blocklist) < Block.maxblocks:
                newblock = Block()
                while len([x for x in blocklist if x.rect.colliderect(newblock.rect)]) > 0:
                    newblock = Block()
                players.add(newblock)        
        

    def __init__(self):
        super().__init__()

        self.xsize = random.randint(Block.minxsize,Block.maxxsize)
        self.ysize = random.randint(Block.minxsize,Block.maxxsize)
        self.image = pygame.Surface((self.xsize, self.ysize))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        self.colour = (255,255,255)
        self.startcolour = (255,255,255)

        pygame.draw.rect(self.image, self.colour, [0, 0, self.xsize, self.ysize])
        # pygame.draw.rect(self.image, self.colour, [0, 0, self.xsize, self.ysize], self.colour,5)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(200, WINDOW_WIDTH - 200), random.randint(self.ysize, WINDOW_HEIGHT - self.ysize))

        self.health = self.xsize * self.ysize 
        self.maxhealth = self.health

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
            Obstacle.impact_sound.play()

class Circle(Obstacle):

    minradius = 30
    maxradius = 60

    spawnprob = 0.25
    maxcircles = 6

    @classmethod
    def spawn(cls):
        if random.random() < Circle.spawnprob:
            circlelist = [ x for x in players if isinstance(x, Obstacle) ]
            if len(circlelist) < Circle.maxcircles:
                newcircle = Circle()
                while len([x for x in circlelist if x.rect.colliderect(newcircle.rect)]) > 0:
                    newcircle = Circle()
                players.add(newcircle)        
        

    def __init__(self):
        super().__init__()

        self.radius = random.randint(Circle.minradius,Circle.maxradius)

        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.fill('Black')
        self.image.set_colorkey('Black')

        self.colour = (255,255,255)
        self.startcolour = (255,255,255)

        pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
        # pygame.draw.rect(self.image, self.colour, [0, 0, self.xsize, self.ysize], self.colour,5)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(200, WINDOW_WIDTH - 200), random.randint(self.radius, WINDOW_HEIGHT - self.radius))

        self.health = int(3.1416 * self.radius ** 2)
        self.maxhealth = self.health

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
            pygame.draw.circle(self.image, newcolour, (self.radius, self.radius), self.radius)
            Obstacle.impact_sound.play()



def display_score(start_time):
    current_time = pygame.time.get_ticks()
    score_surf = test_font.render(f'Current Score: {int((current_time - start_time) / 1000)}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 80))
    display_surface.blit(score_surf, score_rect)




display_surface  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Pong')
display_surface.fill((0,0,0))
clock = pygame.time.Clock()

test_font = pygame.font.Font(r'.\Runner\font\PixelType.ttf', 50)
title_surf = test_font.render('Ready to Pong?', False, (255, 255, 255))
title_rect = title_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)))

winner_surf = test_font.render('Winner is: ', False, (255, 255, 255))
winner_rect = winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)+50))

round_winner_surf = test_font.render('Round Winner is: ', False, (255, 255, 255))
round_winner_rect = round_winner_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)))

round_continue_surf = test_font.render('Press any key to continue', False, (255, 255, 255))
round_continue_rect = round_continue_surf.get_rect(center=(int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/3)+80))

player_1_score_surf = test_font.render('P1 Score: ', False, (255, 255, 255))
player_1_score_rect = player_1_score_surf.get_rect(midleft=(50, 80))

player_2_score_surf = test_font.render('P2 Score: ', False, (255, 255, 255))
player_2_score_rect = player_2_score_surf.get_rect(midright=(WINDOW_WIDTH-50, 80))

round_surf = test_font.render(f'Round:1', False, (255, 255, 255))
round_rect = round_surf.get_rect(center =(int(WINDOW_WIDTH/2), 80))

game_state = STATE_GAME_ACTIVE

block_timer = pygame.USEREVENT + 1
pygame.time.set_timer(block_timer, 900)

playedgame = False

pongball = PongBall()
ball = pygame.sprite.GroupSingle()
ball.add(pongball)

players = pygame.sprite.Group()
players.add(PlayerPaddle(100))
players.add(ComputerPaddle(pongball,100))
players.add(Goal((0,0)))
players.add(Goal((WINDOW_WIDTH-1,0)))
players.add(Block())
players.add(Circle())

projectiles = pygame.sprite.Group()

# obstacles = pygame.sprite.Group()
# obstacles.add(Block())

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

        player_1_score_surf = test_font.render(f'P1 Score: {player1_score}', False, (255, 255, 255))
        player_2_score_surf = test_font.render(f'P2 Score: {player2_score}', False, (255, 255, 255))
        display_surface.blit(player_1_score_surf,player_1_score_rect)
        display_surface.blit(player_2_score_surf,player_2_score_rect)
        display_surface.blit(round_surf,round_rect)

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