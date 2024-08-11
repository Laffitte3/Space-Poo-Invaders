import pygame
import random

pygame.init()

WINDOW_WIDTH=800
WINDOW_HEIGHT=600

display_surface=pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))

FPS=60
clock=pygame.time.Clock()

#Define Classes

#Game class
class Game():
    """A class to control and update the game"""
    def __init__(self,player_bullet_group,player_group,alien_group,alien_bullet_group):
        """Initialize the game"""
        #set game values
        self.round_number = 1
        self.score = 0

        self.player_bullet_group =player_bullet_group
        self.player_group = player_group
        self.alien_group = alien_group
        self.alien_bullet_group = alien_bullet_group

        #set sounds and music
        self.new_round_sound = pygame.mixer.Sound("new_round.wav")
        self.breach_sound= pygame.mixer.Sound("breach.wav")
        self.alien_hit_sound = pygame.mixer.Sound("alien_hit.wav")
        self.player_hit_sound = pygame.mixer.Sound("player_hit.wav")

        #set Font
        self.font= pygame.font.Font("Facon.ttf",24)

    def update(self):
        """update the game"""
        """El update method se va a llamar cada iteracion del loop while
        Lo que queremos verificar es: si los alien tocaron la parte baja de la pantalla,
        si existe alguna colision, si se acabo una ronda,  ya tenemos metodos para eso, solo tenemos que llamarlos
        en update"""
        
        self.shift_aliens()
        self.check_collision()
        self.check_round_completion()
    
    def draw(self):
        """Draw the HUD and other information to display"""
        #set colors
        WHITE=(255,255,255)

        #set text
        score_text= self.font.render("Score: "+ str(self.score),True,WHITE)
        score_rect=score_text.get_rect()
        score_rect.centerx=WINDOW_WIDTH/2
        score_rect.top=10

        round_text= self.font.render("Round: "+ str(self.round_number),True,WHITE)
        round_rect=round_text.get_rect()
        round_rect.topleft=(20,10)

        lives_text= self.font.render("Lives: "+ str(self.player_group.lives),True,WHITE)
        lives_rect=lives_text.get_rect()
        lives_rect.topright=(WINDOW_WIDTH-20,10)

        #Blit the HUD to the display
        display_surface.blit(score_text,score_rect)
        display_surface.blit(round_text,round_rect)
        display_surface.blit(lives_text,lives_rect)
        pygame.draw.line(display_surface,WHITE,(0,50), (WINDOW_WIDTH,50),4)
        pygame.draw.line(display_surface,WHITE,(0,WINDOW_HEIGHT-100), (WINDOW_WIDTH,WINDOW_HEIGHT-100),4)

    def shift_aliens(self):
        alien_sprite_group= self.alien_group.sprites()
        #shift significa desplazar
        """Shift a wave of aliens down the screen and reverse direction"""
        #determine if alien group has hit an edge
        shift= False
        for alien in alien_sprite_group:

            if alien.rect.left < 0 or alien.rect.right >WINDOW_WIDTH:

                shift = True
        
        #shift every alien down, check direction and check for a breach
        if shift:
            breach=False
            for alien in alien_sprite_group:
                #shift down
                alien.rect.y += 10 * self.round_number

                #reverse the direction and move the alien to the other corner
                alien.direction *= -1
                alien.rect.x  +=alien.direction * alien.velocity

                #check if an alien reach the ship
                if alien.rect.bottom >= WINDOW_HEIGHT -100:
                    breach = True

            #Alien breach the line
            if breach:
                self.breach_sound.play()
                self.player_group.lives -=1
                self.check_game_status("Alien breach the line","Press 'Enter to continue")



    def check_collision(self):
        """Check for collisions between an alien group and alien group"""
        #check for collision between a bullet in the player bullet group hit an alien in the alien group

        if pygame.sprite.groupcollide(self.player_bullet_group,self.alien_group,True,True):
            self.alien_hit_sound.play()
            self.score += 100

        #see if the player collide with a bullet in the alien bullet group
        if pygame.sprite.spritecollide(self.player_group,self.alien_bullet_group,True):
            
            self.player_hit_sound.play()
            self.player_group.lives -=1
            self.check_game_status("You have been hit","Press 'Enter' to continue")




    def start_new_round(self):
        """start a new round"""
        for i in range(2):
            for j in range(5):
                alien=Alien(64+i*64,64+j*64,self.round_number,alien_bullet_group)
                self.alien_group.add(alien)

        #Pause the game and prompt user to start
        self.new_round_sound.play()
        self.pause_game("Space invaders Round " +str(self.round_number),"Press Enter to begin")

    def check_round_completion(self):
        """Comprobamos si la ronda finalizo"""
        if len(self.alien_group) ==0:
            self.score+= 1000*self.round_number
            self.round_number +=1

            self.start_new_round()


    def check_game_status(self,main_text,sub_text):
        """Check to see the status of the game and how the player died"""
        #Empty the bullet groups and reset the player an remaining alien
        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()
        self.player_group.reset()
        #Con esto buscas en el grupo alien y reseteas solo a los alien en pantalla y no a todo el grupo
        for alien in self.alien_group:
            alien.reset()
        #Check if the game is over or is a simple round reset
        if self.player_group.lives<=0:
            self.reset_game()
        else:
            self.pause_game(main_text,sub_text)
    
    def pause_game(self,main_text,sub_text):
        #set colors
        global running
        WHITE=(255,255,255)
        BLACK=(0,0,0)

        #Create a main pause text
        main_text=self.font.render(main_text,True,WHITE)
        main_rect = main_text.get_rect()
        main_rect.center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2)

        #Create a sub pause text
        sub_text=self.font.render(sub_text,True,WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2 + 64)

        #Blit the text

        display_surface.fill(BLACK)
        display_surface.blit(main_text,main_rect)
        display_surface.blit(sub_text,sub_rect)
        pygame.display.update()

        #Pause the game unil the user hit enter
        is_paused=True
        while is_paused:

            for event in pygame.event.get():
                #THE USER want to play again
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:

                        is_paused = False
                #The user wants to quit
                if event.type == pygame.QUIT:

                    is_paused=False
                    running=False


    def reset_game(self):
        
        self.pause_game("Final score"+str(self.score), "Press Enter to play again")

        #Reset game values
        self.score =0
        self.player_group.lives=5
        self.round_number=1

        #Ensure that the bullet groups are empty
        self.alien_group.empty()
        self.alien_bullet_group.empty()
        self.player_bullet_group.empty()

        #Start new game
        self.start_new_round()


#class player

class Player(pygame.sprite.Sprite):

    def __init__(self,player_bullet_group):
        super().__init__()

        self.image = pygame.image.load("player_ship.png")
        self.rect= self.image.get_rect()
        self.rect.centerx= WINDOW_WIDTH/2
        self.rect.bottom = WINDOW_HEIGHT

        self.lives= 5
        self.velocity = 8

        self.player_bullet_group= player_bullet_group

        self.shoot_sound= pygame.mixer.Sound("player_fire.wav")

    def update(self):
        """Update the player and the movement"""
        keys= pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.rect.left>0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right<WINDOW_WIDTH:
            self.rect.x += self.velocity

    def fire(self):
        """Fire a bullet"""
        if len(self.player_bullet_group) < 1:
            self.shoot_sound.play()
            PlayerBullet(self.rect.centerx, self.rect.top, self.player_bullet_group)

    def reset(self):
        """Reset the player position once he die"""
        self.rect.centerx= WINDOW_WIDTH/2
        self.rect.bottom = WINDOW_HEIGHT

#Alien class

class Alien(pygame.sprite.Sprite):

    def __init__(self, x, y, velocity,bullet_group):
        super().__init__()

        self.image=pygame.image.load("alien.png")
        self.rect=self.image.get_rect()
        self.rect.topleft = (x,y)

        self.starting_x=x
        self.starting_y=y

        self.direction = 1
        self.velocity= velocity
        self.bullet_group=bullet_group

        self.shoot_sound=pygame.mixer.Sound("alien_fire.wav")

    def update(self):
        """Update the Alien and the movement"""
        self.rect.x += self.direction * self.velocity

        #Randomly fire a bullet

        if random.randint(0,1000)> 999 and len(self.bullet_group) < 3:

            #self.shoot_sound.play()
            print("hiiiiiiiiiii")
            self.fire()

    def fire(self):
        """Fire a bullet"""
        AlienBullet(self.rect.centerx,self.rect.bottom,alien_bullet_group)

    def reset(self):
        """Reset the alien position """
        self.rect.topleft = (self.starting_x,self.starting_y)
        self.direction=1


#class player bullet

class PlayerBullet(pygame.sprite.Sprite):
    """A class to model a bullet fire by a player"""
    def __init__(self,x,y,player_bullet_group):
        super().__init__()

        self.image = pygame.image.load("green_laser.png")
        self.rect= self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10
        player_bullet_group.add(self)
        

    def update(self):
        self.rect.y -= self.velocity

        if self.rect.top <0:
            self.kill()


#class Alien bullet

class AlienBullet(pygame.sprite.Sprite):
    """A class to model a bullet fire by an alien"""
    def __init__(self,x,y,alien_bullet_group):
        super().__init__()
        self.image = pygame.image.load("red_laser.png")
        self.rect= self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10
        alien_bullet_group.add(self)

    def update(self):
        self.rect.y += self.velocity

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

#Create bullet groups
alien_bullet_group= pygame.sprite.Group()
player_bullet_group= pygame.sprite.Group()

#Create a player group and a player object
player_group= pygame.sprite.Group()
my_player = Player(player_bullet_group)
player_group.add(my_player)


#Create a alien group, we wull add Alien objects via the game start new round
alien_group= pygame.sprite.Group()


#Create a game object
#le paso los grupos como argumentos y asi puedo utilizarlos dengtro de la clase Game
my_game = Game(player_bullet_group,my_player,alien_group,alien_bullet_group)

my_game.start_new_round()


running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False
        #the player wants to fire

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.fire()

    display_surface.fill((0,0,0))

    #Update and display all sprites groups
    player_group.update()
    player_group.draw(display_surface)

    alien_group.update()
    alien_group.draw(display_surface)

    player_bullet_group.update()
    player_bullet_group.draw(display_surface)

    alien_bullet_group.update()
    alien_bullet_group.draw(display_surface)

    #Update an draw game object
    my_game.update()
    #No se le coloca display surface porque este draw es creado por nosotros y no es el que viene por default ya que game no es un grupo
    my_game.draw()

    
    clock.tick(FPS)

    pygame.display.update()
