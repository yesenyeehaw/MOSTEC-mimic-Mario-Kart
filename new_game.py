import pygame, sys
from pygame.locals import *
import time
import pygame
import pygame.sprite as sprite
import random
import time
import spidev
import RPi.GPIO as GPIO  #import library to use input/output pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 2000000

#don't change the function below
def readChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return 3.3*data/1024



last_shoot = time.time()
SHOOT_TIMEOUT = 0.25

just_hit = time.time()
HIT_TIMEOUT = 1.5


pygame.init()


##GLOBAL VARIABLES!!!
##THINGS LIKE CONSTANTS WE WILL USE ALL CAPS VARIABLE NAMES FOR
FPS = 1099 # frames per second setting

FOODSIZE = 5 #dimensions of food (pixels)
ENEMYSIZE = 30 #dimensions of enemy (squares so x by x)
MISSILEWIDTH=3 #missile width
MISSILEHEIGHT=8 #missile height


TYPESOFENEMIES = 5
CHARWIDTH = 75 #your width
CHARHEIGHT = 75 #your height

MISSILERATE = 6 #movement rate of missiles
fpsClock = pygame.time.Clock()
FALL_RATE = 15 #fall rate of objects/food (how many pixels per clock tick)
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
TITLEFONT = pygame.font.Font('freesansbold.ttf', 18)
INSFONT = pygame.font.Font('freesansbold.ttf', 14)

# new bg
background = pygame.image.load("/home/pi/Downloads/red.jpg")
street = pygame.image.load("/home/pi/Downloads/straight.png")
street2 = pygame.transform.scale(street, (960,350))
street_size = street2.get_size()

background_rect = background.get_rect()
#screen = pygame.display.set_mode(street_size)
SCREENWIDTH, SCREENHEIGHT = street_size

x = 0
y = 0

x1 = 0
y1 = -SCREENHEIGHT

# set up the window
DISPLAYSURF = pygame.display.set_mode(street_size)
pygame.display.set_caption('')


#make some colors with easy to understand names for use throughout game:
#You can therefore use "RED" in stead of (255,0,0) in code.
WHITE = (255,255,255)
GREY = (200, 200, 200)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,100)
LIGHTBLUE = (0,0,255)
PURPLE = (255,0,255)
ORANGE = (255,165,0)
PINK = (255,192,203)
YELLOW = (255,255,0)
BLACK = (0,0,0)
DARKGREEN = (0,100,0)


#Max foods on screen at any point in time
FOOD_CAP = 15
ENEMY_CAP = 150

foods = [] #list to contain food instances
enemies = [] #list to contain enemy instances
missiles = [] #list to contain missile instances

input_pin = 20
shot_already = False
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

###important variables for player/character run time
#starting character position:
#REALLY IMPORTANT VARIABLE!  IT INDICATES WHERE THE STUDENTS ARE
char_posx = SCREENWIDTH/2
char_posy = SCREENHEIGHT-75
#how many missiles you've got left:
#score:
missile_stock = 10
score = 0
#lives:
lives =3

instructions = '''You are Mario.
The racetrack is filled with spontaneous bombs which will hurt you.
You must avoid these bombs or destroy them with missiles.
Fire missiles with the spacebar.
The small gold things are money. Aqcuire that bread. Gain that GRAIN!'''



#Main Game Loop! ALWAYS RUNNING
def main():
    global CLOCK, SURFACE
    pygame.init() #start pygame!
    CLOCK = pygame.time.Clock() #init clock
    SURFACE = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #create a "surface" for drawing
    pygame.display.set_caption('YAHOOWA Games') #
    startScreen() #run the startScreen Function!
    while True: #run the main loop of the game as a system...first instruction screen, then the actual game, then the ending screen
        instructionsScreen()
        gameRun()
        endScreen()

#start screen graphics
def startScreen():
    bg = pygame.image.load("/home/pi/Downloads/bg.jpg")
    logo = pygame.image.load("/home/pi/Downloads/mario.png")
    logoo = pygame.image.load("/home/pi/Downloads/mariokart.png")
    logoo2 = pygame.transform.scale(logoo, (350,70))
    peach = pygame.image.load("/home/pi/Downloads/peachp.png")
    peach2 = pygame.transform.scale(peach, (140,185))
    bowser = pygame.image.load("/home/pi/Downloads/bowserp.png")
    bowser2 = pygame.transform.scale(bowser, (150,160))
    luigi = pygame.image.load("/home/pi/Downloads/luigip.png")
    luigi2 = pygame.transform.scale(luigi, (200,150))
    DISPLAYSURF.blit(bg, (0, 0))
    SubTitleSurf = TITLEFONT.render('but not really...' , True, BLACK)
    InstructionSurf = TITLEFONT.render('PRESS ANY KEY TO START', True, BLACK)
    SubTitleRect = SubTitleSurf.get_rect()
    InstructionRect = InstructionSurf.get_rect()
    SubTitleRect.topleft = (SCREENWIDTH/2-30 , 90)
    InstructionRect.topleft = (SCREENWIDTH/2-120 , 140)
    DISPLAYSURF.blit(SubTitleSurf, SubTitleRect)
    DISPLAYSURF.blit(InstructionSurf, InstructionRect)
    DISPLAYSURF.blit(logo, (240, 170))
    DISPLAYSURF.blit(logoo2, (SCREENWIDTH/2-150 , 20))
    DISPLAYSURF.blit(peach2, (20 , 155))
    DISPLAYSURF.blit(bowser2, (490 , 180))
    DISPLAYSURF.blit(luigi2, (730 , 190))


    pygame.display.update()
    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

#instruction screen graphics:
def instructionsScreen():
    bg = pygame.image.load("/home/pi/Downloads/galaxy.jpg")
    DISPLAYSURF.blit(bg, (0, 0))
    TitleSurf = TITLEFONT.render('DIRECTIONS', True, WHITE)
    TitleRect = TitleSurf.get_rect()
    TitleRect.topleft = (SCREENWIDTH/2-80, 40)
    DISPLAYSURF.blit(TitleSurf, TitleRect)
    spot = 80
    b = instructions.split('\n')
    for q in b:
        SubTitleSurf = INSFONT.render(q , True, WHITE)
        SubTitleRect = SubTitleSurf.get_rect()
        SubTitleRect.topleft = (SCREENWIDTH/2-80 , spot)
        spot+=20
        DISPLAYSURF.blit(SubTitleSurf, SubTitleRect)
    InstructionSurf = TITLEFONT.render('PRESS ANY KEY TO START', True, WHITE)
    InstructionRect = InstructionSurf.get_rect()
    InstructionRect.topleft = (SCREENWIDTH/2-80 , spot)
    DISPLAYSURF.blit(InstructionSurf, InstructionRect)
    pygame.display.update()
    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
start = pygame.mixer.Sound("/home/pi/Downloads/begin.wav")


#Game running Function (this has the primary game loop where the "game" proper is run)
def gameRun():
    global char_posx
    global char_posy
    global missile_stock
    global foods
    global enemies
    global missiles
    global lives
    global score
    global last_shoot
    global background
    global street2
    global background_rect
    global x,y,x1,y1
    global shot_already
    score = 0 #start score at zero
    lives = 3 #start lives at 3
    missile_stock =10 #start missile stock at 10
    move_command = 0 #initial move command
    char_posx = SCREENWIDTH/2 #starting character x pos
    char_posy = SCREENHEIGHT-75 #starting character y pos
    foods = []
    enemies = []
    missiles = []
    start.play()
    while True: #main game loop...get out of it by calling "break"\
        move_command = 0 #initialize the move command to be "zero" (default)
        shoot_command = False #initialize the shoot command as False (default)
        shoot_input = GPIO.input(input_pin)
        if shoot_input == 1 and shot_already == False:
            shot_already = True
            shoot_command = True
        if shoot_input == 0 and shot_already == True:
            shot_already = False
            
        DISPLAYSURF.blit(background,background_rect)

        y1 += 15
        y += 15
        DISPLAYSURF.blit(background,(x,y))
        if y > SCREENHEIGHT:
            y = -SCREENHEIGHT
        if y1 > SCREENHEIGHT:
            y1 = -SCREENHEIGHT
        DISPLAYSURF.blit(street2, (0, 0))

               
        for event in pygame.event.get(): #check for inputs here!
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:# or GPIO.input(input_pin1)==1:
                    shoot_command = True
                    print("Pushed")
                if event.key == K_ESCAPE:
                    terminate()
        pressed = pygame.key.get_pressed() 

        if pressed[pygame.K_LEFT] or pressed[pygame.K_a] or readChannel(0) >= 1.6:
            move_command-=1
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d] or readChannel(0) < 1.6:
            move_command+=1
        if shoot_command:
            if missile_stock>0:
                missiles.append([char_posx + 0.5*CHARWIDTH-0.5*MISSILEWIDTH,char_posy])
                missile_stock-=1
        char_posx +=move_command*25
        char_posx = min(max(char_posx,20),SCREENWIDTH-100)
        updateFoods()
        updateEnemiesAndMissiles()
        if lives<=0:
            break
        drawCharacter([char_posx,char_posy])
        for food in foods:
            drawFood(food)
        for enemy in enemies:
            drawEnemy(enemy)
        for missile in missiles:
            drawMissile(missile)
        drawScore()
        pygame.display.update()
        fpsClock.tick(FPS)
        if time.time()-just_hit < HIT_TIMEOUT:
            GPIO.output(led_pin,1)
            GPIO.output(led_pin2,0)

        else:
            GPIO.output(led_pin,0)
            GPIO.output(led_pin2,1)
        
dead = pygame.mixer.Sound("/home/pi/Downloads/dead.wav")

#Ending Screen Graphics
def endScreen():
    dead.play()
    GPIO.output(led_pin,1)
    GPIO.output(led_pin2,0)
    DISPLAYSURF.fill(RED) #make a black screen
    TitleSurf = TITLEFONT.render('YOU DIED :(', True, WHITE) #write game over message
    SubTitleSurf = TITLEFONT.render('SCORE: %s' %(score), True, WHITE) #write score
    TitleRect = TitleSurf.get_rect()  #create place to write
    SubTitleRect = SubTitleSurf.get_rect() #create place to write
    TitleRect.topleft = (SCREENWIDTH/2-30, 40) #create
    SubTitleRect.topleft = (SCREENWIDTH/2-30 , 80)
    DISPLAYSURF.blit(TitleSurf, TitleRect)
    DISPLAYSURF.blit(SubTitleSurf, SubTitleRect)
    pygame.display.update()
    time.sleep(3) #let the results sink in
    pygame.event.get() #empty queue
    DISPLAYSURF.fill(BLACK)
    TitleSurf = TITLEFONT.render('GAME OVER :(', True, WHITE)
    SubTitleSurf = TITLEFONT.render('SCORE: %s' %(score), True, WHITE)
    InstructionSurf = TITLEFONT.render('PRESS ANY KEY TO RESTART', True, WHITE)
    TitleRect = TitleSurf.get_rect()
    SubTitleRect = SubTitleSurf.get_rect()
    InstructionRect = InstructionSurf.get_rect()
    TitleRect.topleft = (SCREENWIDTH/2-30, 40)
    SubTitleRect.topleft = (SCREENWIDTH/2-30 , 80)
    InstructionRect.topleft = (SCREENWIDTH/2-80 , 120)
    DISPLAYSURF.blit(TitleSurf, TitleRect)
    DISPLAYSURF.blit(SubTitleSurf, SubTitleRect)
    DISPLAYSURF.blit(InstructionSurf, InstructionRect)
    pygame.display.update()
    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


#Helper Functions!


#finish the game
def terminate():
    pygame.quit()
    sys.exit()


#generate a random X spot:
def randXSpot():
    return random.randint(SCREENWIDTH/2 - 5, SCREENWIDTH/2 + 5)

#generate a random choice based on a given probability
def rand(prob):
    return random.random()<prob

#choose a random type of enemy
def randtype():
    return random.randint(0,TYPESOFENEMIES-1) #returns a random number from 0 up to the types of enemies we have


#basic rectangular collision detection
def collision(coord1,w1,h1,coord2,w2,h2):
    #replace this function with your own better one!
    x1 = coord1[0]
    y1 = coord1[1]
    x2 = coord2[0]
    y2 = coord2[1]
    if x1 + w1 >= x2 and x1 <= x2 + w2 and y1 + h1 >= y2 and y1 <= y2 + h2:
        return True
    else:
        return False  
coin = pygame.mixer.Sound("/home/pi/Downloads/coin.wav")

#update the food on the screen!
def updateFoods():
    global foods 
    global score
    global missile_stock
    pygame.mixer.init()

    new_foods=[] #create a new list of foods
    for food in foods: #consider each food
        candidate = [food[0]+food[2],food[1]+FALL_RATE,food[2]] #possible new position for food!

        #if the user is colliding with the food under consideration, give user a missile and 
        #increase the score!
        if collision(candidate,FOODSIZE,FOODSIZE,[char_posx,char_posy],CHARWIDTH,CHARHEIGHT):
            coin.play()
            missile_stock+=1
            score +=1

        elif candidate[1]<SCREENHEIGHT: #check if food has gone beyond end of screen
            new_foods.append(candidate)
    if len(new_foods)< FOOD_CAP and rand(0.05):
        new_foods.append([randXSpot(),0,random.randint(-10,10)])
    foods = new_foods


##Returns a new X position for an enemy given the player's x position, the x position
# of the enemy under consider, and the type of the enemy under consideration.
# "Dumb" AI will just return enemyx since it means that it will fall in a straight line
def AI(playerx,enemyx,type):
    if type == 0:
        return enemyx
    if type == 1:
        return enemyx + (0.01 * (playerx - enemyx))
    if type == 2:
        if playerx - enemyx < 0:
            return enemyx-10
        if playerx - enemyx > 0:
            return enemyx+10
        if playerx == enemyx:
            return enemyx
    if type == 3:
        return enemyx - 10
    if type == 4:
        return enemyx + 10

# always releases a new enemy with 5% probability
def enemy_release(score):
    if score > 120:
        return 1
    return score * (1/120)

#goes through and updates lists of missiles and enemies.
#code will throw out  missiles and enemies which have successfully gone off screen.
hitm = pygame.mixer.Sound("/home/pi/Downloads/shot.wav")

led_pin = 4
led_pin2 = 17
GPIO.setup(led_pin,GPIO.OUT)
GPIO.setup(led_pin2,GPIO.OUT)

def updateEnemiesAndMissiles():
    global enemies
    global missiles
    global missile_stock
    global lives
    global score
    global just_hit
    
    new_enemies=[]
    new_missiles=[]
    for missile in missiles: #update missile position for each missile
        candidate = [missile[0],missile[1]-MISSILERATE]
        if candidate[1] >0:
            new_missiles.append(candidate)
    for enemy in enemies: #for each enemy do some stuff
        newx = AI(char_posx,enemy[0],enemy[2]) #get their new X position based on their type
        candidate = [newx,enemy[1]+FALL_RATE,enemy[2]] #create a new instance of the enemy at the new X and Y, 
        #We copy the enemy type since that does not change
        hit = False #start out and assume best for enemy (that it has not been hit by a missile)
        for m in range(len(new_missiles)): #for each missile scan through and see if any of them are 
            #running into the enemy being updated in the outer for loop
            #check if the missile collided with an enemy
            if collision(candidate[:2],ENEMYSIZE,ENEMYSIZE,new_missiles[m],MISSILEWIDTH,MISSILEHEIGHT):
                new_missiles.pop(m)
                hit=True # mark hit as true...
                score +=1
                print("HIT ")
                break #enemy hit and blown up!
        if hit:
            pass #don't do anything...do not add enemy to new list...it is dead.
        elif collision(candidate[:2],ENEMYSIZE,33,[char_posx,char_posy],CHARWIDTH,CHARHEIGHT):
            #if the enemy we're updating is colliding with the player
            hitm.play()
            lives-=1
            just_hit = time.time()
            #GPIO.output(led_pin,1)
            #time.sleep(0.05)
        elif candidate[1]<SCREENHEIGHT:
            new_enemies.append(candidate)
    if len(new_enemies)< ENEMY_CAP and rand(enemy_release(score)):
        new_enemies.append([randXSpot(),0,randtype()])
    missiles = new_missiles
    enemies = new_enemies

#draw a character at coordinates provide
def drawCharacter(coordinates):
    image = pygame.image.load("/home/pi/Downloads/marioo.png")
    mario = pygame.transform.scale(image, (75,75))
    dead = pygame.image.load("/home/pi/Downloads/dead.png")
    dead2 = pygame.transform.scale(dead, (75,75))
    if time.time()-just_hit >HIT_TIMEOUT:
        DISPLAYSURF.blit(mario, (char_posx, char_posy)) 
    else:
        DISPLAYSURF.blit(dead2, (char_posx, char_posy))

#draw food at input coordinates provided
def drawFood(coordinates):
    food = pygame.image.load("/home/pi/Downloads/coin.png")
    DISPLAYSURF.blit(food, (coordinates[0], coordinates[1]))

   
#draw an enemy at the x,y info provided and with the color provided by 3rd value in input list! 
def drawEnemy(enemy_info):
    enemy = pygame.image.load("/home/pi/Downloads/bomb.png")
    if enemy_info[2]==0:
        DISPLAYSURF.blit(enemy, (enemy_info[0], enemy_info[1]))
    elif enemy_info[2]==1:
        DISPLAYSURF.blit(enemy, (enemy_info[0], enemy_info[1]))
    elif enemy_info[2]==2:
        DISPLAYSURF.blit(enemy, (enemy_info[0], enemy_info[1]))
    elif enemy_info[2]==3:
        DISPLAYSURF.blit(enemy, (enemy_info[0], enemy_info[1]))
    elif enemy_info[2]==4:
        DISPLAYSURF.blit(enemy, (enemy_info[0], enemy_info[1]))

#draw a missile at the x, y coordinate provide.
def drawMissile(coordinates):
    missile = pygame.Rect(coordinates[0],coordinates[1], MISSILEWIDTH,MISSILEHEIGHT)
    pygame.draw.rect(DISPLAYSURF, GREY,missile)

#returns what the key press events are!
def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

#draws current score in corner of game filed of view.
def drawScore():
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    missilesSurf = BASICFONT.render('Missiles: %s' % (missile_stock), True, WHITE)
    livesSurf = BASICFONT.render('Lives: %s' % (lives), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    missilesRect = missilesSurf.get_rect()
    livesRect = livesSurf.get_rect()
    scoreRect.topleft = (SCREENWIDTH - 120, 10)
    missilesRect.topleft = (SCREENWIDTH - 120, 25)
    livesRect.topleft = (SCREENWIDTH - 120, 40)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    DISPLAYSURF.blit(livesSurf, livesRect)
    DISPLAYSURF.blit(missilesSurf, missilesRect)

#code below runs the main function when you just call python3 lab08.py in terminal
if __name__ == '__main__':
    main()
