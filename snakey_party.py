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
ORANGECOLOR = (255, 127, 0)
PURPLE = (142, 56, 142)
MAROON = (255, 52, 179)

BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 #index of snake's head

# fruit types
APPLE=1
POISON=2
ORANGE=3
RASPBERRY=4
BLUEBERRY=5
LEMON=6

# fruit time remains on screen
POISONMIN=100
POISONMAX=200
ORANGEMIN=35
ORANGEMAX=65
RASPBERRYMIN=30
RASPBERRYMAX=45
BLUEBERRYMIN=20
BLUEBERRYMAX=40
LEMONMIN=100
LEMONMAX=100


class Snake:
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
        
        
class Fruit:
    def __init__(self,t,min=0,max=0):
        self.type = t
        self.coords = self.getRandomLocation()
        if max >= min:
            self.timer = random.randint(min,max)

    # for random locations
    def getRandomLocation(self):
        while True:
            conflict = False
            if fruiteaten['apple'] < 20:
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

    def updatetimer(self):
        if self.timer > 0:
            self.timer = self.timer - 1
            return True 
        else:
            return False


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

    # set up globals
    global allsnake, allfruit, fruiteaten
    allsnake = []
    allfruit = []
    fruiteaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0, 'blueberry':0, 'lemon':0}

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
    a = Fruit(APPLE)
    allfruit.append(a)

    while True: # main game loop
        stop = False
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN and stop == False:
                if (event.key == K_LEFT or event.key == K_a) and player.direction != RIGHT:
                    player.direction = LEFT
                    stop = True
                elif (event.key == K_RIGHT or event.key == K_d) and player.direction != LEFT:
                    player.direction = RIGHT
                    stop = True
                elif (event.key == K_UP or event.key == K_w) and player.direction != DOWN:
                    player.direction = UP
                    stop = True
                elif (event.key == K_DOWN or event.key == K_s) and player.direction != UP:
                    player.direction = DOWN
                    stop = True
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        # check if the snake has hit itself or the edge
        
        # check for snake collision
        for snake in allsnake:
            if snake.coords[HEAD]['x'] == -1 or snake.coords[HEAD]['x'] == CELLWIDTH or snake.coords[HEAD]['y'] == -1 or snake.coords[HEAD]['y'] == CELLHEIGHT:
                snake.alive = False
            # warning -- does not check other snakes
            for snakebody in snake.coords[1:]:
                if snakebody['x'] == snake.coords[HEAD]['x'] and snakebody['y'] == snake.coords[HEAD]['y']:
                    snake.alive = False
                    
        # check for snake death
        for snake in allsnake:
            if snake.alive == False:
                if snake.player == True:
                    clearAll()
                    return 1

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
            fruitfound = False
            for fruit in allfruit:
                if snake.coords[HEAD]['x'] == fruit.coords['x'] and snake.coords[HEAD]['y'] == fruit.coords['y'] and fruitfound == False:
                    # determine type
                    if fruit.type == APPLE:
                    # update count, score, growth
                        fruiteaten['apple'] = fruiteaten['apple'] + 1
                        snake.score = snake.score + (10 * snake.multiplier)
                        snake.growth = snake.growth + 1
                        # check for bonus round
                        if fruiteaten['apple'] % 50 == 0:
                            bonus(11)
                        elif fruiteaten['apple'] % 10 == 0:
                            bonus()
                        # check for speed increase
                        if fruiteaten['apple'] % 20 == 0:
                            basespeed = basespeed + 1
                        # chance of adding poison apple
                        if random.randint(1,4) == 1:
                            p = Fruit(POISON,POISONMIN,POISONMAX)
                            allfruit.append(p)
                        # chance of adding orange if it doesn't yet exist
                        if random.randint(1,5) == 1:
                            o = Fruit(ORANGE,ORANGEMIN,ORANGEMAX)
                            allfruit.append(o)
                        # chance of adding raspberry if it doesn't yet exist
                        if random.randint(1,6) == 1:
                            r = Fruit(RASPBERRY,RASPBERRYMIN,RASPBERRYMAX)
                            allfruit.append(r)
                        # create new apple
                        a = Fruit(APPLE)
                        allfruit.append(a)
                    elif fruit.type == POISON:
                        # update count, score, growth
                        fruiteaten['poison'] = fruiteaten['poison'] + 1
                        snake.score = snake.score - (25 * snake.multiplier)
                        snake.growth = snake.growth - 3
                    elif fruit.type == ORANGE:
                        # update count, score, growth
                        fruiteaten['orange'] = fruiteaten['orange'] + 1
                        snake.score = snake.score + (50 * snake.multiplier)
                        snake.growth = snake.growth + 3
                    elif fruit.type == RASPBERRY:
                        # update count, multiplier, timer
                        fruiteaten['raspberry'] = fruiteaten['raspberry'] + 1
                        snake.multiplier = 2
                        snake.multipliertimer = snake.multipliertimer + currentspeed * 8    # add 8 seconds
                    elif fruit.type == BLUEBERRY:
                        # update count, score, timer
                        fruiteaten['raspberry'] = fruiteaten['raspberry'] + 1
                        snake.score = snake.score + (100 * snake.multiplier)
                        slowtimer = slowtimer + currentspeed * 12    # add 12 seconds
                    elif fruit.type == LEMON:
                        # update count
                        fruiteaten['lemon'] = fruiteaten['lemon'] + 1
                    # remove fruit
                    allfruit.remove(fruit)
                    del fruit
                    # mark flag
                    fruitfound = True

        # check for size changes
        for snake in allsnake:
            if snake.growth < 0:
                # update growth, snake size
                snake.growth = snake.growth + 1
                if len(snake.coords) > 3:
                    del snake.coords[-1]
                    del snake.coords[-1]
                else:
                    del snake.coords[-1]
            elif snake.growth > 0:
                # update growth
                snake.growth = snake.growth - 1
            else:
                # move snake
                del snake.coords[-1]

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
            if fruit.type != APPLE:
                if fruit.updatetimer() == False:
                    allfruit.remove(fruit)
                    del fruit  
                    
        # move snakes
        for snake in allsnake:
            if snake.direction == UP:
                newHead = {'x': snake.coords[HEAD]['x'], 'y': snake.coords[HEAD]['y'] - 1}
            elif snake.direction == DOWN:
                newHead = {'x': snake.coords[HEAD]['x'], 'y': snake.coords[HEAD]['y'] + 1}
            elif snake.direction == LEFT:
                newHead = {'x': snake.coords[HEAD]['x'] - 1, 'y': snake.coords[HEAD]['y']}
            elif snake.direction == RIGHT:
                newHead = {'x': snake.coords[HEAD]['x'] + 1, 'y': snake.coords[HEAD]['y']}
            snake.coords.insert(HEAD, newHead)
            
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        for fruit in allfruit:
            drawFruit(fruit.type, fruit.coords)
        for snake in allsnake:
            drawSnake(snake.coords, snake.color, snake.colorBorder)
        drawScore(player.score)
        pygame.display.update()
        FPSCLOCK.tick(currentspeed)


def clearAll():
    for snake in allsnake:
        allsnake.remove(snake)
        del snake
    for fruit in allfruit:
        allfruit.remove(fruit)
        del fruit

# for bonus drop
def bonus(type = random.randint(1,10)):
    # bonus types
    p_bonus = 0
    o_bonus = 0
    r_bonus = 0
    b_bonus = 0
    l_bonus = 0
    # lemon bonus
    if type == 11:
        l_bonus = 1
        o_bonus = 10
    # poison bonus
    if type == 10:
        p_bonus = random.randint(20,35)
    # orange bonus
    if type == 9:   
        o_bonus = random.randint(20,35)
    # raspberry bonus
    if type == 8:
        r_bonus = random.randint(20,35)
    # blueberry bonus
    if type == 7:
        b_bonus = random.randint(20,30)
    # standard
    else:
        p_bonus = random.randint(0,3)
        o_bonus = random.randint(5,20)
        r_bonus = random.randint(1,4)
        b_bonus = random.randint(0,2)

    while p_bonus > 0:
        p_bonus = p_bonus - 1
        p = Fruit(POISON,POISONMIN,POISONMAX)
        allfruit.append(p)
    while o_bonus > 0:
        o_bonus = o_bonus - 1
        o = Fruit(ORANGE,ORANGEMIN,ORANGEMAX)
        allfruit.append(o)
    while r_bonus > 0:
        r_bonus = r_bonus - 1
        r = Fruit(RASPBERRY,RASPBERRYMIN,RASPBERRYMAX)
        allfruit.append(r)
    while b_bonus > 0:
        b_bonus = b_bonus - 1
        b = Fruit(BLUEBERRY,BLUEBERRYMIN,BLUEBERRYMAX)
        allfruit.append(b)
    while l_bonus > 0:
        l_bonus = l_bonus - 1
        l = Fruit(LEMON,LEMONMIN,LEMONMAX)
        allfruit.append(l)



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


def drawPoints(score, color=WHITE, x=1, y=1):
    scoreSurf = BASICFONT.render('%s!' % (score), True, color)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawSnake(snakecoords, snakecolor, snakecolorBorder):
    for coord in snakecoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        snakeSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, snakecolorBorder, snakeSegmentRect)
        snakeInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, snakecolor, snakeInnerSegmentRect)

    
def drawFruit(type, coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    if type == APPLE:
        color = RED
    elif type == POISON:
        color = GREEN
    elif type == ORANGE:
        color = ORANGECOLOR
    elif type == RASPBERRY:
        color = PURPLE
    elif type == BLUEBERRY:
        color = BLUE
    elif type == LEMON:
        color = YELLOW
    else:
        color = WHITE
    fruitRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, color, fruitRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()

