#!/usr/bin/env python
# a snakey clone using pygame

import random, pygame, sys
from pygame.locals import *

FPS = 12
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGRAY = (40, 40, 40)

#snake colors
HONEYDEW = (240, 255, 240)
MINTGREEN = (189, 252, 201)
SEAGREEN = (84, 255, 159)
EMERALDGREEN = (0, 201, 87)
FORESTGREEN = (34, 139, 34)
COBALTGREEN = (61, 145, 64)
GREENYELLOW = (173, 255, 47)
OLIVEGREEN = (107, 142, 35)
IVORY = (205, 205, 193)
LIGHTYELLOW = (238, 238, 209)
YELLOW = (238, 238, 0)
KHAKI = (255, 246, 143)
GOLDENROD = (218, 165, 32)
CORAL = (255, 127, 80)
SIENNA = (255, 130, 71)

#other
ORANGE = (255, 127, 0)
PURPLE = (142, 56, 142)
MAROON = (255, 52, 179)

BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 #index of snake's head

# fruit time remains on screen
POISONTIMER = (100,200)
ORANGETIMER = (35,65)
RASPBERRYTIMER = (30,45)
BLUEBERRYTIMER = (20,40)
LEMONTIMER = (100,100)

POISONBONUS = 7
ORANGEBONUS = 8
RASPBERRYBONUS = 9
BLUEBERRYBONUS = 10
LEMONBONUS = 11


class Snake:
    """
    Snake class houses all information for a particular snake.
    player - if snake is the player. Player snake is also referenced directly when player snake object is created.
    alive - if snake is alive. Rather than delete, this allows snake to slowly shrink to the point of where it died.
    coords - a list of dictionaries containing coordinates 'x' and 'y'. A special global variable HEAD (0).
    direction - where snake moves for every game iteration ('left', 'up', etc).
    color - body of snake's color.
    colorBorder - outline of body.
    growth - when a snake is to grow, this is stored in this buffer so that every game iteration can add one growth, only.
    multiplier - all fruit eaten which cause points to be scored are multiplied by this.
    multipliertimer - number of game iterations multiplier stays in effect.
    score - the number of points snake has accumulated.
    """
    def __init__(self, c=[{'x':5, 'y':5},{'x':4, 'y':5},{'x':3, 'y':5}], d=RIGHT, sc=GREEN, sb=COBALTGREEN):
        self.player = False
        self.alive = True
        self.coords = c
        # ensure snake length
        assert len(self.coords) > 1
        self.direction = d
        self.color = sc
        self.colorBorder = sb
        self.growth = 0
        self.multiplier = 1
        self.multipliertimer = 0
        self.score = 0
        
    def updateDirection(self, direction_input):
        """
        This helps filter direction input to help ignore garbage direction input.
        """
        if direction_input == UP:
            self.direction = UP
        elif direction_input == DOWN:
            self.direction = DOWN
        elif direction_input == LEFT:
            self.direction = LEFT
        elif direction_input == RIGHT:
            self.direction = RIGHT

    def updateScore(self, points_input):
        """
        This updates score of snake, factoring multiplier.
        """
        self.score = self.score + (points_input * self.multiplier)

    def updateGrowth(self, growth_input):
        """
        This updates growth "owed" to snake, allowing amount to stack.
        """
        self.growth = self.growth + growth_input

    def updateMultiplier(self, multiplier_input, timer_input):
        """
        This updates multiplier value and time (game iterations) multiplier is active. Only time stacks.
        """
        # multiplier value does not stack, but time does
        self.multiplier = multiplier_input
        self.multipliertimer = self.multipliertimer + timer_input

    def boundsCollision(self):
        """
        This returns True if snake (head) is ever out of grid parameters.
        """
        # check if out of bounds
        if self.coords[HEAD]['x'] == -1 or self.coords[HEAD]['x'] == CELLWIDTH or self.coords[HEAD]['y'] == -1 or self.coords[HEAD]['y'] == CELLHEIGHT:
            return True
        else:
            return False
            
    def snakeCollision(self, snake):
        """
        This returns True if snake (head) collides with any part of a given snake (outside of own head if checking against self).
        """
        if self is snake:
            # exclude head if checked against self
            for snakebody in snake.coords[1:]:
                if snakebody['x'] == self.coords[HEAD]['x'] and snakebody['y'] == self.coords[HEAD]['y']:
                    return True    
        else:
            for snakebody in snake.coords:
                if snakebody['x'] == self.coords[HEAD]['x'] and snakebody['y'] == self.coords[HEAD]['y']:
                    return True
        # no collision
        return False
        
    def fruitCollision(self, fruit):
        """
        This returns True if snake (head) has collided with a given fruit.
        """
        if self.coords[HEAD]['x'] == fruit.coords['x'] and self.coords[HEAD]['y'] == fruit.coords['y']:
            return True
        else:
            return False

    def move(self):
        """
        This will update coords for snake, moving it one cell in given direction.
        It also factors in and updates growth if any growth is "owed" snake (one per game iteration).
        If snake is dead, will only remove the last segment of snake and ignore direction / not move snake.
        """
        if self.alive:
            # delete last segment first.
            if self.growth < 0:
                self.growth = self.growth + 1
                if len(self.coords) > 3:
                    # implement negative growth by removing last two segments
                    del self.coords[-2:]
                else:
                    # snake is too short -- remove last segment as normal
                    del self.coords[-1]
            elif self.growth > 0:
                self.growth = self.growth - 1
                # implement positive growth by not deleting last segment
            else:
                # no growth factor, delete last segment
                del self.coords[-1]

            # determine new head coordinates by direction
            if self.direction == UP:
                newhead = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] - 1}
            elif self.direction == DOWN:
                newhead = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] + 1}
            elif self.direction == LEFT:
                newhead = {'x': self.coords[HEAD]['x'] - 1, 'y': self.coords[HEAD]['y']}
            elif self.direction == RIGHT:
                newhead = {'x': self.coords[HEAD]['x'] + 1, 'y': self.coords[HEAD]['y']}
            
            # insert new head segment
            self.coords.insert(HEAD, newhead)

        # dead snake -- remove last segment as long as it isn't the last
        elif len(self.coords) > 1:
            del self.coords[-1]
            
    def drawSnake(self):
        """
        Responsible for drawing snake image to screen.
        """
        for coord in self.coords:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            snakeSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, self.colorBorder, snakeSegmentRect)
            snakeInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
            pygame.draw.rect(DISPLAYSURF, self.color, snakeInnerSegmentRect)
        
        
class Fruit:
    """
    Fruit class houses all information for fruit objects. Base class is not meant to be instantiated, but rather provide base methods shared by all fruit.
    """
    def __init__(self):
        self.timer = 0

    def getRandomLocation(self, allfruit, allsnake, gametally):
        """
        Returns random coordinates (for fruit to be placed). Ensures that coordinates are not occupied by fruit or snake head.
        Will keep fruit away from edges (outside 20%) if in an "easy mode" determined in Tally object.
        """
        while True:
            conflict = False
            if gametally.checkEasyTrigger():
                x = random.randint(int(CELLWIDTH/5), CELLWIDTH - int(CELLWIDTH/5) - 1)
                y = random.randint(int(CELLHEIGHT/5), CELLHEIGHT - int(CELLHEIGHT/5) - 1)
            else:
                x = random.randint(0, CELLWIDTH - 1)
                y = random.randint(0, CELLHEIGHT - 1)
            # ensure coordinates are not already occupied by fruit
            for fruit in allfruit:
                if fruit.coords['x'] == x and fruit.coords['y'] == y:
                    conflict = True
            # ensure coordinates are not already occupied by snake head
            for snake in allsnake:
                if snake.coords[HEAD]['x'] == x and snake.coords[HEAD]['y'] == y:
                    conflict = True
            if conflict == False:
                return {'x':x, 'y':y}

    def updateTimer(self):
        """
        Returns true and decrements if there is still time left for fruit to be on screen.
        """
        if self.timer > 0:
            self.timer = self.timer - 1
            return True 
        else:
            return False

    def drawFruit(self):
        """
        Responsible for drawing fruit image to screen.
        """
        x = self.coords['x'] * CELLSIZE
        y = self.coords['y'] * CELLSIZE
        fruitRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.color, fruitRect)


class Apple(Fruit):
    """
    Apples are a unique fruit in that they never leave the screen and once one is eaten, it is always replaced with another.
    They also add points and one growth
    """
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.color = RED
        self.points = 10
        self.growth = 1

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['apple'] = gametally.fruitEaten['apple'] + 1
        snake.updateScore(self.points)
        snake.updateGrowth(self.growth)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Poison(Fruit):
    """
    Poison will shorten a snake (by adding a negative growth value) and reduce points.
    """
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.timer = random.randint(POISONTIMER[0], POISONTIMER[1])
        self.color = GREEN
        self.points = -25
        self.growth = -3

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['poison'] = gametally.fruitEaten['poison'] + 1
        snake.updateScore(self.points)
        snake.updateGrowth(self.growth)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)
        

class Orange(Fruit):
    """
    Orange will grow snake substantially and are worth points.
    """
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.timer = random.randint(ORANGETIMER[0], ORANGETIMER[1])
        self.color = ORANGE
        self.points = 50
        self.growth = 3

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['orange'] = gametally.fruitEaten['orange'] + 1
        snake.updateScore(self.points)
        snake.updateGrowth(self.growth)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Raspberry(Fruit):
    """
    Raspberry will set snake's multiplier to two for a period of time.
    """
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.timer = random.randint(RASPBERRYTIMER[0], RASPBERRYTIMER[1])
        self.color = PURPLE
        self.multiplier = 2
        self.multipliertimer = 100

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['raspberry'] = gametally.fruitEaten['raspberry'] + 1
        snake.updateMultiplier(self.multiplier, self.multipliertimer)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Blueberry(Fruit):
    """
    Blueberry will reduce the frame rate (slowing down game iterations) for a period of time.
    It is also worth a lot of points.
    """
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.timer = random.randint(BLUEBERRYTIMER[0], BLUEBERRYTIMER[1])
        self.color = BLUE
        self.score = 100
        self.slowtimer = 120

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['blueberry'] = gametally.fruitEaten['blueberry'] + 1
        snake.updateScore(self.score)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Lemon(Fruit):
    def __init__(self, allfruit, allsnake, gametally):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, gametally)
        self.timer = random.randint(LEMONTIMER[0], LEMONTIMER[1])
        self.color = YELLOW
        self.score = 1000

    def isEaten(self, snake, gametally):
        gametally.fruitEaten['lemon'] = gametally.fruitEaten['lemon'] + 1
        snake.updateScore(self.score)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Tally:
    """
    Responsible for dynamics relating to the accumulation of fruits in a given game.
    fruitEaten - a dictionary containing a numeric tally of each fruit eaten.
    speedTrigger - the frequency (based on apples consumed) in which gamespeed is increased by one.
    bonusTrigger - the frequency (based on apples consumed) in which a bonus game - runBonus() - is launched.
    easyTrigger - a threshold (apples consumed); once reached fruit can be placed anywhere on screen (as opposed to away from edges).
    typeMin - the minimum value in determining bonus game type.
    typeMax - the maximum value in determining bonus game type.
    """
    def __init__(self, st=20, bt=10, et=20, tmin=1, tmax=10):
        self.fruitEaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0, 'blueberry':0, 'lemon':0}
        self.speedTrigger = st
        self.bonusTrigger = bt
        self.easyTrigger = et
        self.typeMin = tmin
        self.typeMax = tmax

    def checkSpeedTrigger(self):
        """
        Returns true if number of apples consumed modulo speedTrigger equals zero.
        """
        if self.fruitEaten['apple'] % self.speedTrigger == 0:
            return True
        else:
            return False

    def checkBonusTrigger(self):
        """
        Returns true if number of apples consumed modulo bonusTrigger equals zero.
        """
        if self.fruitEaten['apple'] % self.bonusTrigger == 0:
            return True
        else:
            return False

    def checkEasyTrigger(self):
        """
        Returns true if number of apples consumed is less than or equal to easyTrigger.
        """
        if self.fruitEaten['apple'] <= self.easyTrigger:
            return True
        else:
            return False

    def runBonus(self):
        """
        Returns a list containing fruit (as strings) to be added to game from bonus game.
        An integer (determined randomly between typeMin and typeMax) corresponds to bonus game run.
        A basic set-up would randomly choose between 1 and 10; 6 through 10 initiating a fruit specific bonus.
        Default will contain an assortment of fruit.
        """
        bonus = []
        type = random.randint(self.typeMin, self.typeMax)
        if type == LEMONBONUS:
            bonus.append('lemon')
        elif type == POISONBONUS:
            counter = random.randint(20,35)
            while counter > 0:
                bonus.append('poison')
                counter = counter - 1
        elif type == ORANGEBONUS:
            counter = random.randint(20,35)
            while counter > 0:
                bonus.append('orange')
                counter = counter - 1
        elif type == RASPBERRYBONUS:
            counter = random.randint(20,35)
            while counter > 0:
                bonus.append('raspberry')
                counter = counter - 1
        elif type == BLUEBERRYBONUS:
            counter = random.randint(20,30)
            while counter > 0:
                bonus.append('blueberry')
                counter = counter - 1
        else:  # default bonus
            counter = random.randint(0,3)
            while counter > 0:
                bonus.append('poison')
                counter = counter - 1
            counter = random.randint(5,20)
            while counter > 0:
                bonus.append('orange')
                counter = counter - 1
            counter = random.randint(1,4)
            while counter > 0:
                bonus.append('raspberry')
                counter = counter - 1
            counter = random.randint(0,2)
            while counter > 0:
                bonus.append('blueberry')
                counter = counter - 1
        return bonus


class Button():
    def __init__(self, text, x, y):
        self.text = text
        startSurf = BUTTONFONT.render(self.text, True, GREEN, DARKGRAY)
        self.rect = startSurf.get_rect()
        self.rect.center = x,y

    def display(self):
        startSurf = BUTTONFONT.render(self.text, True, GREEN, DARKGRAY)
        DISPLAYSURF.blit(startSurf, self.rect)

    def pressed(self,mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BUTTONFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BUTTONFONT = pygame.font.Font('freesansbold.ttf', 48)
    pygame.display.set_caption('Snakey!')

    showStartScreen()
    
    while True:
        runGame()
        showGameOverScreen()
        

def runGame():

    # set up globals
    #global allsnake, allfruit, fruiteaten
    allsnake = []
    allfruit = []
    gametally = Tally(20, 10, 19)

    # create player snake and add to all snakes
    player = Snake([{'x':5, 'y':5},{'x':4, 'y':5},{'x':3, 'y':5}], RIGHT, GREEN, COBALTGREEN)
    allsnake.append(player)
    
    # set beginning variables
    player.player = True
    player.score = 10
    basespeed = FPS
    currentspeed = basespeed
    slowtimer = 0

    # create initial fruit
    a = Apple(allfruit, allsnake, gametally)
    allfruit.append(a)

    # main game loop
    while True:
        stop = False
        # event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN and stop == False:
                if (event.key == K_LEFT or event.key == K_a) and player.direction != RIGHT:
                    player.updateDirection(LEFT)
                    stop = True
                elif (event.key == K_RIGHT or event.key == K_d) and player.direction != LEFT:
                    player.updateDirection(RIGHT)
                    stop = True
                elif (event.key == K_UP or event.key == K_w) and player.direction != DOWN:
                    player.updateDirection(UP)
                    stop = True
                elif (event.key == K_DOWN or event.key == K_s) and player.direction != UP:
                    player.updateDirection(DOWN)
                    stop = True
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        # check if the snake has hit boundary
        for snake in allsnake:
            if snake.alive and snake.boundsCollision():
                snake.alive = False
            # check if snake has hit another snake
            for othersnake in allsnake:
                if snake.alive and snake.snakeCollision(othersnake):
                    snake.alive = False

        # check score - change color accordingly
        # only looks at player snake
        if player.score > 2000:
            player.color = SIENNA
            player.colorBorder = CORAL
        elif player.score > 1500:
            player.color = CORAL
            player.colorBorder = GOLDENROD
        elif player.score > 1250:
            player.color = GOLDENROD
            player.colorBorder = EMERALDGREEN
        elif player.score > 1000:
            player.color = KHAKI
            player.colorBorder = LIGHTYELLOW
        elif player.score > 750:
            player.color = YELLOW
            player.colorBorder = GREEN
        elif player.score > 500:
            player.color = LIGHTYELLOW
            player.colorBorder = FORESTGREEN
        elif player.score > 400:
            player.color = IVORY #change this
            player.colorBorder = FORESTGREEN
        elif player.score > 300:
            player.color = GREENYELLOW
            player.colorBorder = OLIVEGREEN
        elif player.score > 200:
            player.color = HONEYDEW
            player.colorBorder = SEAGREEN   
        elif player.score > 100:
            player.color = SEAGREEN 
            player.colorBorder = EMERALDGREEN
        else:
            player.color = GREEN
            player.colorBorder = COBALTGREEN 

        # check if fruit has been eaten by a snake
        for snake in allsnake:
            for fruit in allfruit:
                if snake.alive and snake.fruitCollision(fruit):
                    fruit.isEaten(snake, gametally)
                    # apples have special adding properties
                    if fruit.__class__ == Apple:
                        # check for speed increase
                        if gametally.checkSpeedTrigger():
                            basespeed = basespeed + 1
                        # check for bonus drop
                        if gametally.checkBonusTrigger():
                            bonus = gametally.runBonus()
                            for bonusfruit in bonus: ##if this works, maybe try f = fruit.__class__()
                                if bonusfruit == 'poison':
                                    f = Poison(allfruit, allsnake, gametally)
                                elif bonusfruit == 'orange':
                                    f = Orange(allfruit, allsnake, gametally)
                                elif bonusfruit == 'raspberry':
                                    f = Raspberry(allfruit, allsnake, gametally)
                                elif bonusfruit == 'blueberry':
                                    f = Blueberry(allfruit, allsnake, gametally)
                                else:
                                    f = Lemon(allfruit, allsnake, gametally)
                                allfruit.append(f)
                        # chance of poison drop
                        if random.randint(1,4) == 1:
                            p = Poison(allfruit, allsnake, gametally)
                            allfruit.append(p)
                        # chance of orange drop
                        if random.randint(1,5) == 1:
                            o = Orange(allfruit, allsnake, gametally)
                            allfruit.append(o)
                        # chance of raspberry drop
                        if random.randint(1,6) == 1:
                            r = Raspberry(allfruit, allsnake, gametally)
                            allfruit.append(r)
                        # create new apple
                        a = Apple(allfruit, allsnake, gametally)
                        allfruit.append(a)
                    elif fruit.__class__ == Blueberry:
                        # update speed
                        slowtimer = slowtimer + currentspeed * 12    # add 12 seconds
                    # remove fruit
                    allfruit.remove(fruit)

        # check for snake death
        for snake in allsnake:
            if snake.alive == False:
                if snake.player == True:
                    return 1

        # check for size changes / move snake
        for snake in allsnake:
            snake.move()

        # check multiplier and adjust color and multiplier as needed
        for snake in allsnake:
            if snake.multipliertimer > 0:
                snake.multipliertimer = snake.multipliertimer - 1
                snake.colorBorder = PURPLE
            else:
                snake.multiplier = 1

        # check slow and adjust color and fps as needed
        if slowtimer > 0:
            slowtimer = slowtimer - 1
            for snake in allsnake:
                snake.color = BLUE
            if currentspeed > 8:
                currentspeed = currentspeed - 1
        else:
            if currentspeed < basespeed:
                currentspeed = currentspeed + 1

        # update timers on fruits, remove if necessary
        for fruit in allfruit:
            if fruit.__class__ != Apple:
                if fruit.updateTimer() == False:
                    allfruit.remove(fruit)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        for fruit in allfruit:
            fruit.drawFruit()
        for snake in allsnake:
            snake.drawSnake()
        drawScore(player.score)
        pygame.display.update()
        FPSCLOCK.tick(currentspeed)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE or keyUpEvents[0].key == K_q:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Snakey!', True, WHITE, FORESTGREEN)
    titleSurf2 = titleFont.render('Snakey!', True, GREEN)

    degrees1 = 0
    degrees2 = 0

    startbutton = Button('(s)tart game', WINDOWWIDTH / 2, WINDOWHEIGHT * 3/5)
    instructbutton = Button('(i)nstructions', WINDOWWIDTH / 2, WINDOWHEIGHT * 4/5)

    while True:

        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        startbutton.display()
        instructbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if startbutton.pressed(mouse):
                    pygame.event.get()
                    return
                elif instructbutton.pressed(mouse):
                    showInstructScreen()
            elif event.type == KEYDOWN:
                if event.key == K_s:
                    pygame.event.get()
                    return
                elif event.key == K_i:
                    showInstructScreen()
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def showInstructScreen():

    endinstructbutton = Button('(e)xit', WINDOWWIDTH / 2, WINDOWHEIGHT - 40)

    while True:

        instruct = pygame.image.load('snakey_party_instructions.png').convert()

        DISPLAYSURF.blit(instruct, (54, 10))

        endinstructbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if endinstructbutton.pressed(mouse):
                    pygame.event.get()
                    return
            elif event.type == KEYDOWN:
                if event.key == K_e or event.key == K_i:
                    pygame.event.get()
                    return
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawPoints(score, x=1, y=1, color=WHITE):
    scoreSurf = BASICFONT.render('%s!' % (score), True, color)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (x, y)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()

