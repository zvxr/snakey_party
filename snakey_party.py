#!/usr/bin/env python
# a snakey clone using pygame

import random, pygame, sys
from pygame.locals import *

WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 12
MIN_FPS = 3
MAX_FPS = 60
CELLSIZE = 20
BUFFER = CELLSIZE * 1 # number of cells to exclude from grid height; displays in-game info
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert (WINDOWHEIGHT - BUFFER) % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int((WINDOWHEIGHT - BUFFER) / CELLSIZE)

# colors - (R G B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGRAY = (40, 40, 40)
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
ORANGE = (255, 127, 0)
PURPLE = (142, 56, 142)
MAROON = (255, 52, 179)
BACKGROUNDCOLOR = BLACK

# for consistency in direction types
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# for consistency in snake names
SNAKEY = 'snakey'
WIGGLES = 'wiggles'
GIGGLES = 'giggles'
LINUS = 'linus'

# index of snake's head
HEAD = 0

# minimum and maximum frames fruit remains on screen - determined randomly
POISONTIMER = (100, 200)
ORANGETIMER = (35, 65)
RASPBERRYTIMER = (30, 45)
BLUEBERRYTIMER = (20, 40)
LEMONTIMER = (100, 100)

FREEZING_POINT = 8

POISONBONUS = 7
ORANGEBONUS = 8
RASPBERRYBONUS = 9
BLUEBERRYBONUS = 10
LEMONBONUS = 11


class Snake:
    """
    Snake class houses all information for a particular snake.
    player - if snake is the player. Player snake is also referenced directly when player snake object is created.
    name - name of snake.
    alive - if snake is alive. Rather than delete, this allows snake to slowly shrink to the point of where it died.
    coords - a list of dictionaries containing coordinates 'x' and 'y'. A special global variable HEAD (0).
    direction - where snake moves for every game iteration ('left', 'up', etc).
    color - body of snake's color.
    colorBorder - outline of body.
    growth - when a snake is to grow, this is stored in this buffer so that every game iteration can add one growth, only.
    multiplier - all fruit eaten which cause points to be scored are multiplied by this.
    multipliertimer - number of game iterations multiplier stays in effect.
    score - the number of points snake has accumulated.
    place - used to determine death order.
    """
    def __init__(self, n=SNAKEY, c=False, sc=GREEN, sb=COBALTGREEN):
        self.name = n
        if self.name == SNAKEY:
            self.player = True
        else:
            self.player = False
        self.alive = True
        
        if c == False:
            self.coords = getStartPosition(1)
        else:
            self.coords = c
        # ensure snake length
        assert len(self.coords) > 1
        
        # determine direction -- currently only supports right or left
        if self.coords[0]['x'] > self.coords[1]['x']:
            self.direction = RIGHT
        else:
            self.direction = LEFT
        self.color = sc
        self.colorCurrent = self.color
        self.colorBorder = sb
        self.colorBorderCurrent = self.colorBorder
        self.growth = 0
        self.multiplier = 1
        self.multipliertimer = 0
        self.score = 0
        self.place = False
        self.fruitEaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0, 'blueberry':0, 'lemon':0}

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
        
    def getPlace(self, snakes):
        """
        Returns a string containing the death order of snake, based on number of snakes.
        """
        if self.place == snakes:
            return '1st'
        elif self.place + 1 == snakes:
            return '2nd'
        elif self.place + 2 == snakes:
            return '3rd'
        else:
            return 'Last'

    def boundsCollision(self):
        """
        This returns True if snake (head) is ever out of grid parameters.
        """
        # check if out of bounds -- offset on on 'y' for buffer.
        if self.coords[HEAD]['x'] == -1 or self.coords[HEAD]['x'] == CELLWIDTH or self.coords[HEAD]['y'] == -1 + (BUFFER / CELLSIZE) or self.coords[HEAD]['y'] == CELLHEIGHT + (BUFFER / CELLSIZE):
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
            pygame.draw.rect(DISPLAYSURF, self.colorBorderCurrent, snakeSegmentRect)
            snakeInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
            pygame.draw.rect(DISPLAYSURF, self.colorCurrent, snakeInnerSegmentRect)
            
    def drawScore(self, position, allsnake):
        """
        Responsible for drawing snake score to screen.
        """
        scoreSurf = BASICFONT.render('%s: %s' % (self.name, self.score), True, self.colorCurrent)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (getPosition(position, allsnake), 1)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        
        
class Opponent(Snake):
    """
    Derived from Snake class, this adds functionality for determining direction.
    """
    def __init__(self, n='bot', c=False, sc=COBALTGREEN, sb=GOLDENROD, r=20, p=10):
        Snake.__init__(self, n, c, sc, sb)
        self.avoidBoundaries = True
        self.randomness = r
        self.preferSameDirection = p

    def updateDirection(self, grid):
        # all directions have value adjusted
        nextDirection = {LEFT:0, RIGHT:0, UP:0, DOWN:0}
        
        # coords of own snake head
        x = self.coords[HEAD]['x']
        y = self.coords[HEAD]['y']

        # opposite direction kills snake
        if self.direction == LEFT:
            nextDirection[RIGHT] = nextDirection[RIGHT] - 100
        elif self.direction == RIGHT:
            nextDirection[LEFT] = nextDirection[LEFT] - 100
        elif self.direction == UP:
            nextDirection[DOWN] = nextDirection[DOWN] - 100
        elif self.direction == DOWN:
            nextDirection[UP] = nextDirection[UP]- 100

        # avoid boundaries
        if self.avoidBoundaries == True:
            if x == 0:
                nextDirection[LEFT] = nextDirection[LEFT] - 100
            if x == CELLWIDTH - 1:
                nextDirection[RIGHT] = nextDirection[RIGHT] - 100
            if y == (BUFFER / CELLSIZE):
                nextDirection[UP] = nextDirection[UP] - 100
            if y == CELLHEIGHT + (BUFFER / CELLSIZE) - 1:
                nextDirection[DOWN] = nextDirection[DOWN] - 100
                
        # prefer same direction
        nextDirection[self.direction] = nextDirection[self.direction] + self.preferSameDirection

        # avoid immediate snakes
        if grid.has_key((x-1,y)) and (grid[(x-1,y)] == 'snake'):
            nextDirection[LEFT] = nextDirection[LEFT] - 100
        if grid.has_key((x+1,y)) and (grid[(x+1,y)] == 'snake'):
            nextDirection[RIGHT] = nextDirection[RIGHT] - 100
        if grid.has_key((x,y-1)) and (grid[(x,y-1)] == 'snake'):
            nextDirection[UP] = nextDirection[UP] - 100
        if grid.has_key((x,y+1)) and (grid[(x,y+1)] == 'snake'):
            nextDirection[DOWN] = nextDirection[DOWN] - 100
            
        # favor direction of apple -- this approach will need to be replaced eventually
        for cell in grid:
            if grid[cell] == 'apple':
                # get x and y differences and favor direction of apple inversely proportionate to distance
                x_difference = cell[0] - x
                y_difference = cell[1] - y
                if x_difference > 0:
                    nextDirection[RIGHT] = nextDirection[RIGHT] + (CELLWIDTH - x_difference)
                else:
                    nextDirection[LEFT] = nextDirection[LEFT] + (CELLWIDTH - x_difference)
                if y_difference < 0:
                    nextDirection[UP] = nextDirection[UP] + (CELLHEIGHT - y_difference)
                else:
                    nextDirection[DOWN] = nextDirection[DOWN] + (CELLHEIGHT - y_difference)

        # factor in randomness
        for d in nextDirection:
            nextDirection[d] = nextDirection[d] + random.randint(0,self.randomness)
            
        # report if debugging
        if DEBUG == True:
            print self.name
            print nextDirection

        # update snake direction to direction with highest score
        self.direction = max(nextDirection, key=nextDirection.get)

    def getPlace(self, snakes):
        return Snake.getPlace(self, snakes)

    def updateScore(self, points_input):
        Snake.updateScore(self, points_input)

    def updateGrowth(self, growth_input):
        Snake.updateGrowth(self, growth_input)

    def updateMultiplier(self, multiplier_input, timer_input):
        Snake.updateMultiplier(self, multiplier_input, timer_input)

    def boundsCollision(self):
        return Snake.boundsCollision(self)

    def snakeCollision(self, snake):
        return Snake.snakeCollision(self, snake)

    def fruitCollision(self, fruit):
        return Snake.fruitCollision(self, fruit)

    def move(self):
        Snake.move(self)

    def drawSnake(self):
        Snake.drawSnake(self)

    def drawScore(self, position, allsnake):
        Snake.drawScore(self, position, allsnake)        
        
        
class Fruit:
    """
    Fruit class houses all information for fruit objects. Base class is not meant to be instantiated, but rather provide base methods shared by all fruit.
    """
    def __init__(self):
        self.timer = 0

    def getRandomLocation(self, allfruit, allsnake, game):
        """
        Returns random coordinates (for fruit to be placed). Ensures that coordinates are not occupied by fruit or snake head.
        Will keep fruit away from edges (outside 20%) if in an "easy mode" determined in Tally object.
        """
        while True:
            conflict = False
            if game.checkEasyTrigger():
                x = random.randint(int(CELLWIDTH/5), CELLWIDTH - int(CELLWIDTH/5) - 1)
                y = random.randint(int(CELLHEIGHT/5), CELLHEIGHT - int(CELLHEIGHT/5) - 1)
            else:
                x = random.randint(0, CELLWIDTH - 1)
                y = random.randint((BUFFER / CELLSIZE), CELLHEIGHT - 1)
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
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.color = RED
        self.points = 10
        self.growth = 1

    def isEaten(self, snake, game):
        snake.fruitEaten['apple'] = snake.fruitEaten['apple'] + 1
        game.fruitEaten['apple'] = game.fruitEaten['apple'] + 1
        snake.updateScore(self.points)
        snake.updateGrowth(self.growth)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Poison(Fruit):
    """
    Poison will shorten a snake (by adding a negative growth value) and reduce points.
    """
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(POISONTIMER[0], POISONTIMER[1])
        self.color = GREEN
        self.points = -25
        self.growth = -3

    def isEaten(self, snake, game):
        snake.fruitEaten['poison'] = snake.fruitEaten['poison'] + 1
        game.fruitEaten['poison'] = game.fruitEaten['poison'] + 1
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
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(ORANGETIMER[0], ORANGETIMER[1])
        self.color = ORANGE
        self.points = 50
        self.growth = 3

    def isEaten(self, snake, game):
        snake.fruitEaten['orange'] = snake.fruitEaten['orange'] + 1
        game.fruitEaten['orange'] = game.fruitEaten['orange'] + 1
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
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(RASPBERRYTIMER[0], RASPBERRYTIMER[1])
        self.color = PURPLE
        self.multiplier = 2
        self.multipliertimer = 100

    def isEaten(self, snake, game):
        snake.fruitEaten['raspberry'] = snake.fruitEaten['raspberry'] + 1
        game.fruitEaten['raspberry'] = game.fruitEaten['raspberry'] + 1
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
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(BLUEBERRYTIMER[0], BLUEBERRYTIMER[1])
        self.color = BLUE
        self.score = 100
        self.slowtimer = 80

    def isEaten(self, snake, game):
        snake.fruitEaten['blueberry'] = snake.fruitEaten['blueberry'] + 1
        game.fruitEaten['blueberry'] = game.fruitEaten['blueberry'] + 1
        snake.updateScore(self.score)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Lemon(Fruit):
    """
    TBD... currently worth 1000 points.
    """
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(LEMONTIMER[0], LEMONTIMER[1])
        self.color = YELLOW
        self.score = 1000

    def isEaten(self, snake, game):
        snake.fruitEaten['lemon'] = snake.fruitEaten['lemon'] + 1
        game.fruitEaten['lemon'] = game.fruitEaten['lemon'] + 1
        snake.updateScore(self.score)

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class GameData:
    """
    Responsible for dynamics for a particular game instance.
    fruitEaten - a dictionary containing a numeric tally of each fruit eaten.
    speedTrigger - the frequency (based on apples consumed) in which gamespeed is increased by one.
    bonusTrigger - the frequency (based on apples consumed) in which a bonus game - runBonus() - is launched.
    easyTrigger - a threshold (apples consumed); once reached fruit can be placed anywhere on screen (as opposed to away from edges).
    currentplace - the current 'place' of snake. When snake has died.
    apples - number of apples on screen.
    typeMin - the minimum value in determining bonus game type.
    typeMax - the maximum value in determining bonus game type.
    """
    def __init__(self, st=20, bt=10, et=20, a=1, tmin=1, tmax=10):
        self.fruitEaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0, 'blueberry':0, 'lemon':0}
        self.speedTrigger = st
        self.bonusTrigger = bt
        self.easyTrigger = et
        self.currentplace = 1
        self.apples = a
        self.typeMin = tmin
        self.typeMax = tmax
        self.basespeed = FPS
        self.currentspeed = self.basespeed
        self.slowtimer = 0

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
            
    def checkSnakeDeath(self, allsnake):
        """
        Returns true if there are no more living snakes.
        Sets place of snake if recently died.
        """
        gameover = True
        for snake in allsnake:
            if snake.alive == True:
                gameover = False
            elif snake.place == False:
                snake.place = self.currentplace
                self.currentplace = self.currentplace + 1
        return gameover
        
    def updateBaseSpeed(self, value):
        """
        Updates basespeed by value inputted.
        Checks against parameters
        """
        if (self.basespeed + value > MIN_FPS) and (self.basespeed + value < MAX_FPS):
            self.basespeed = self.basespeed + value
            self.currentspeed = self.basespeed
            
    def updateCurrentSpeed(self, goal=False, force=False):
        """
        Adjusts currentspeed one towards goal.
        Goal defaults to basespeed.
        Optional 'force' will set currentspeed to goal instead.
        """
        if goal == False:
            goal = self.basespeed
            
        if force != False:
            self.currentspeed = goal
        else:
            if self.currentspeed < goal:
                self.currentspeed = self.currentspeed + 1
            elif self.currentspeed > goal:
                self.currentspeed = self.currentspeed - 1

    def checkSlowTimer(self):
        """
        Returns true if slowtimer is greater than 0.
        """
        if self.slowtimer > 0:
            return True
        else:
            return False

    def updateSlowTimer(self):
        """
        Decrements slowtimer by one
        """
        self.slowtimer = self.slowtimer - 1

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
    """
    A clickable button that is rendered on screen.
    """
    def __init__(self, text, x, y):
        self.text = text
        startSurf = BUTTONFONT.render(self.text, True, GREEN, DARKGRAY)
        self.rect = startSurf.get_rect()
        self.rect.center = x,y

    def display(self):
        startSurf = BUTTONFONT.render(self.text, True, GREEN, DARKGRAY)
        DISPLAYSURF.blit(startSurf, self.rect)

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False


class SelectButton(Button):
    """
    Selected by color. Clicking will turn active state to True.
    """
    def __init__(self, text, x, y, a=False):
        Button.__init__(self, text, x, y)
        self.active = a
        
    def display(self):
        if self.active == True:
            startSurf = BUTTONFONT.render(self.text, True, COBALTGREEN, GOLDENROD)
        else:
            startSurf = BUTTONFONT.render(self.text, True, GREEN, DARKGRAY)
            
        DISPLAYSURF.blit(startSurf, self.rect)
        
    def pressed(self, mouse):
        return Button.pressed(self, mouse)

    def setActive(self, buttonlist):
        for button in buttonlist:
            if button == self:
                self.active = True
            else:
                button.active = False


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BUTTONFONT, DEBUG
    
    # for debugging
    if len(sys.argv) < 2:
        DEBUG = False
    else:
        DEBUG = True

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BUTTONFONT = pygame.font.Font('freesansbold.ttf', 30)
    pygame.display.set_caption('Snakey Party')

    titleFont = pygame.font.Font('freesansbold.ttf', 64)
    titleSurf = titleFont.render('Snakey Party', True, WHITE, FORESTGREEN)
    titleRect = titleSurf.get_rect()
    titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT * 2/8)

    arcadebutton = Button('(a)rcade mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 3/8)
    duelbutton = Button('(d)uel mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 4/8)
    partybutton = Button('(p)arty mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 5/8)
    instructbutton = Button('(i)nstructions', WINDOWWIDTH / 2, WINDOWHEIGHT * 6/8)

    while True: ### need to update this

        DISPLAYSURF.fill(BACKGROUNDCOLOR)
        DISPLAYSURF.blit(titleSurf, titleRect)
        arcadebutton.display()
        duelbutton.display()
        partybutton.display()
        instructbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if arcadebutton.pressed(mouse):
                    pygame.event.get()
                    game = GameData()
                    runGame(game, [SNAKEY])
                    showGameOverScreen()
                elif duelbutton.pressed(mouse):
                    pygame.event.get()
                    players = False
                    players = showSelectPlayersScreen()
                    if players != False:
                        game = GameData(10, 10, 9, 2)
                        runGame(game, players)
                        showGameOverScreen()
                elif partybutton.pressed(mouse):
                    pygame.event.get()
                    game = GameData(25, 12, 0, 4)
                    runGame(game, [SNAKEY, LINUS, WIGGLES, GIGGLES])
                    showGameOverScreen()
                elif instructbutton.pressed(mouse):
                    showInstructScreen()
            elif event.type == KEYDOWN:
                if event.key == K_a:
                    pygame.event.get()
                    game = GameData()
                    runGame(game, [SNAKEY])
                    showGameOverScreen()
                elif event.key == K_d:
                    pygame.event.get()
                    players = False
                    players = showSelectPlayersScreen()
                    if players != False:
                        game = GameData(10, 10, 9, 2)
                        runGame(game, players)
                        showGameOverScreen()
                elif event.key == K_p:
                    pygame.event.get()
                    game = GameData(25, 12, 0, 4)
                    runGame(game, [SNAKEY, LINUS, WIGGLES, GIGGLES])
                    showGameOverScreen()
                elif event.key == K_i:
                    showInstructScreen()
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        game = False
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        

def runGame(game, players=[]):

    # in game variables
    allsnake = []
    allfruit = []
    nextEvent = 0

    # create snakes based on name. 'player' is set to false initially to handle input
    player = False
    cur_position = 1
    for snake in players:
        if snake == SNAKEY:
            player = Snake(SNAKEY, getStartPosition(cur_position))
            allsnake.append(player)
            cur_position = cur_position + 1
        elif snake == LINUS:
            linus = Opponent(LINUS, getStartPosition(cur_position), IVORY, COBALTGREEN, 5, 20)
            allsnake.append(linus)
            cur_position = cur_position + 1
        elif snake == WIGGLES:
            wiggles = Opponent(WIGGLES, getStartPosition(cur_position), OLIVEGREEN, PURPLE, 20, 5)
            allsnake.append(wiggles)
            cur_position = cur_position + 1
        elif snake == GIGGLES:
            giggles = Opponent(GIGGLES, getStartPosition(cur_position), PURPLE, EMERALDGREEN, 10, 10)
            allsnake.append(giggles)
            cur_position = cur_position + 1

    # create initial apple(s)
    appleCounter = game.apples
    while appleCounter > 0:
        a = Apple(allfruit, allsnake, game)
        allfruit.append(a)
        appleCounter = appleCounter - 1
    
    # main game loop
    while True:
    
        # get grid representation for AIs
        grid = getGrid(allsnake, allfruit)
        
        # event handling loop -- get player's direction choice
        stop = False
        
        # get events in queue. This updates players direction and other key instructions (quit, debug...)
        # if the next event after direction update suggests sharp direction change, following direction is stored.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif nextEvent != 0 and player != False:
                player.direction = nextEvent
                nextEvent = 0
                stop = True
            # check for exit/quit/debug keys
            if event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q):
                terminate()
            elif event.type == KEYDOWN and event.key == K_e:
                showGameStats(allsnake)
                return 1
            elif event.type == KEYDOWN and event.key == K_g and DEBUG == True:
                stop = True
                debugPrintGrid(grid)
            # if player is dead / does not exist - check for speed controls
            elif event.type == KEYDOWN and event.key == K_f and (player == False or player.alive == False):
                game.updateBaseSpeed(10)
                game.updateCurrentSpeed(False, True)
            elif event.type == KEYDOWN and event.key == K_s and (player == False or player.alive == False):
                game.updateBaseSpeed(-5)
                game.updateCurrentSpeed(False, True)

            # if player exists - check for direction input
            if event.type == KEYDOWN and player != False and stop == False:
                if event.key == K_LEFT and player.direction != RIGHT:
                    player.direction = LEFT
                    stop = True
                elif event.key == K_RIGHT and player.direction != LEFT:
                    player.direction = RIGHT
                    stop = True
                elif event.key == K_UP and player.direction != DOWN:
                    player.direction = UP
                    stop = True
                elif event.key == K_DOWN and player.direction != UP:
                    player.direction = DOWN
                    
            # peak into very next event. If key suggests sharp direction change, store in nextEvent
            elif event.type == KEYDOWN and player != False and nextEvent == 0:
                if event.key == K_LEFT and player.direction != RIGHT:
                    nextEvent = LEFT
                elif event.key == K_RIGHT and player.direction != LEFT:
                    nextEvent = RIGHT
                elif event.key == K_UP and player.direction != DOWN:
                    nextEvent = UP
                elif event.key == K_DOWN and player.direction != UP:
                    nextEvent = DOWN
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()
                elif event.key == K_g and DEBUG == True:
                    debugPrintGrid(grid)
                    
        if DEBUG == True:
            debugPause()
        
        # update all other snake's direction choice
        for snake in allsnake:
            if snake.alive and snake.player == False:
                snake.updateDirection(grid)

        # collision detection
        for snake in allsnake:
            # check if the snake has hit boundary
            if snake.alive and snake.boundsCollision():
                snake.alive = False
            # check if snake has hit another snake
            for othersnake in allsnake:
                if snake.alive and snake.snakeCollision(othersnake):
                    snake.alive = False

        # check score - change color accordingly
        # only looks at player snake
        if player != False:
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
                    fruit.isEaten(snake, game)
                    # apples have special adding properties
                    if fruit.__class__ == Apple:
                        # check for speed increase
                        if game.checkSpeedTrigger():
                            game.updateBaseSpeed(1)
                        # check for bonus drop
                        if game.checkBonusTrigger():
                            bonus = game.runBonus()
                            for bonusfruit in bonus:
                                if bonusfruit == 'poison':
                                    f = Poison(allfruit, allsnake, game)
                                elif bonusfruit == 'orange':
                                    f = Orange(allfruit, allsnake, game)
                                elif bonusfruit == 'raspberry':
                                    f = Raspberry(allfruit, allsnake, game)
                                elif bonusfruit == 'blueberry':
                                    f = Blueberry(allfruit, allsnake, game)
                                else:
                                    f = Lemon(allfruit, allsnake, game)
                                allfruit.append(f)
                        # chance of poison drop
                        if random.randint(1,4) == 1:
                            p = Poison(allfruit, allsnake, game)
                            allfruit.append(p)
                        # chance of orange drop
                        if random.randint(1,5) == 1:
                            o = Orange(allfruit, allsnake, game)
                            allfruit.append(o)
                        # chance of raspberry drop
                        if random.randint(1,6) == 1:
                            r = Raspberry(allfruit, allsnake, game)
                            allfruit.append(r)
                        # create new apple
                        a = Apple(allfruit, allsnake, game)
                        allfruit.append(a)
                    elif fruit.__class__ == Blueberry:
                        # update speed
                        game.slowtimer = game.slowtimer + game.currentspeed * 9    # add 9 seconds
                    # remove fruit
                    allfruit.remove(fruit)

        # check for snake death, update place and end game if no more snakes are alive
        if game.checkSnakeDeath(allsnake):
            showGameStats(allsnake)
            return 1

        # check for size changes / move snake
        for snake in allsnake:
            snake.move()

        # check multiplier and adjust color and multiplier as needed
        for snake in allsnake:
            if snake.multipliertimer > 0:
                snake.multipliertimer = snake.multipliertimer - 1
                snake.colorBorderCurrent = PURPLE
            else:
                # make sure multiplier is 1, color is normal
                snake.multiplier = 1
                snake.colorBorderCurrent = snake.colorBorder

        # check slow and adjust color and fps as needed
        if game.checkSlowTimer():
            game.updateSlowTimer()
            game.updateCurrentSpeed(FREEZING_POINT)
            for snake in allsnake:
                snake.colorCurrent = BLUE
        else:
            game.updateCurrentSpeed()
            # make sure color is normal
            for snake in allsnake:
                snake.colorCurrent = snake.color

        # update timers on fruits, remove if necessary
        for fruit in allfruit:
            if fruit.__class__ != Apple:
                if fruit.updateTimer() == False:
                    allfruit.remove(fruit)

        DISPLAYSURF.fill(BACKGROUNDCOLOR)
        drawGrid()
        for fruit in allfruit:
            fruit.drawFruit()
        for snake in allsnake:
            snake.drawSnake()
            
        # print scores
        position = 1
        for snake in allsnake:
            snake.drawScore(position, allsnake)
            position = position + 1
        # if player is dead, print extra messages
        if player == False or player.alive == False:
            drawMessage('press (e) to end game early', WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 16)
            drawMessage('press (f) to fast-forward game', WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 17)
            drawMessage('press (s) to slow game', WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 18)
        pygame.display.update()
        FPSCLOCK.tick(game.currentspeed)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE or keyUpEvents[0].key == K_q:
        terminate()
    return keyUpEvents[0].key


def showSelectPlayersScreen():
    """
    Blits player/opponent select onto screen. Returns selection as list.
    """
    playerbuttons = [] # not yet implemented
    playersnakeybutton = SelectButton('(s)nakey', WINDOWWIDTH / 3, WINDOWHEIGHT * 2/7, True)
    playerbuttons.append(playersnakeybutton)
    playerlinusbutton = SelectButton('(l)inus', WINDOWWIDTH / 3, WINDOWHEIGHT * 3/7)
    playerbuttons.append(playerlinusbutton)
    playerwigglesbutton = SelectButton('(w)iggles', WINDOWWIDTH / 3, WINDOWHEIGHT * 4/7)
    playerbuttons.append(playerwigglesbutton)
    playergigglesbutton = SelectButton('(g)iggles', WINDOWWIDTH / 3, WINDOWHEIGHT * 5/7)
    playerbuttons.append(playergigglesbutton)
    
    opponentbuttons = [] # not yet implemented
    opponentlinusbutton = SelectButton('(l)inus', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 3/7, True)
    opponentbuttons.append(opponentlinusbutton)
    opponentwigglesbutton = SelectButton('(w)iggles', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 4/7)
    opponentbuttons.append(opponentwigglesbutton)
    opponentgigglesbutton = SelectButton('(g)iggles', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 5/7)
    opponentbuttons.append(opponentgigglesbutton)
    
    
    cancelbutton = Button('(e)xit', WINDOWWIDTH / 3, WINDOWHEIGHT * 6/7)
    acceptbutton = Button('(d)uel!', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 6/7)

    while True:

        choiceFont = pygame.font.Font('freesansbold.ttf', 36)
        choiceSurf = choiceFont.render('Choose Opponent:', True, WHITE, FORESTGREEN)
        choiceRect = choiceSurf.get_rect()

        DISPLAYSURF.fill(BACKGROUNDCOLOR)
        DISPLAYSURF.blit(choiceSurf, choiceRect)

        # display all buttons
        for button in playerbuttons:
            button.display()
        for button in opponentbuttons:
            button.display()
        cancelbutton.display()
        acceptbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                # check each button for player
                for button in playerbuttons:
                    if button.pressed(mouse):
                        button.setActive(playerbuttons)
                # check each button for opponent
                for button in opponentbuttons:
                    if button.pressed(mouse):
                        button.setActive(opponentbuttons)
                # check cancel/accept buttons
                if cancelbutton.pressed(mouse):
                    pygame.event.get()
                    return False
                elif acceptbutton.pressed(mouse):
                    pygame.event.get()
                    final = []
                    if playersnakeybutton.active:
                        final.append(SNAKEY)
                    elif playerlinusbutton.active:
                        final.append(LINUS)
                    elif playerwigglesbutton.active:
                        final.append(WIGGLES)
                    elif playergigglesbutton.active:
                        final.append(GIGGLES)
                    if opponentlinusbutton.active:
                        final.append(LINUS)
                    elif opponentwigglesbutton.active:
                        final.append(WIGGLES)
                    elif opponentgigglesbutton.active:
                        final.append(GIGGLES)
                    return final
                                                                
            elif event.type == KEYDOWN:
                if event.key == K_s:
                    pygame.event.get()
                    playersnakeybutton.setActive(playerbuttons)
                elif event.key == K_l:
                    pygame.event.get()
                    opponentlinusbutton.setActive(opponentbuttons)
                elif event.key == K_w:
                    pygame.event.get()
                    opponentwigglesbutton.setActive(opponentbuttons)
                elif event.key == K_g:
                    pygame.event.get()
                    opponentgigglesbutton.setActive(opponentbuttons)
                elif event.key == K_d:
                    final = []
                    if playersnakeybutton.active:
                        final.append(SNAKEY)
                    elif playerlinusbutton.active:
                        final.append(LINUS)
                    elif playerwigglesbutton.active:
                        final.append(WIGGLES)
                    elif playergigglesbutton.active:
                        final.append(GIGGLES)
                    if opponentlinusbutton.active:
                        final.append(LINUS)
                    elif opponentwigglesbutton.active:
                        final.append(WIGGLES)
                    elif opponentgigglesbutton.active:
                        final.append(GIGGLES)
                    return final
                elif event.key == K_e:
                    pygame.event.get()
                    return False
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        pygame.display.update()


def showInstructScreen():
    """
    Blits instructions onto screen. Returns when exit button clicked / key pressed.
    """
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
    """
    Clean exit from pygame.
    """
    pygame.quit()
    sys.exit()
    

def showGameStats(allsnake):
    """
    Displays game stats for all snakes at end of game.
    Returns when any key pressed.
    """
    position = 1
    for snake in allsnake:
        drawMessage(snake.name, getPosition(position, allsnake), WINDOWHEIGHT / 20 * 3, snake.color)
        if len(allsnake) != 1:
            drawText('place:', snake.getPlace(len(allsnake)), getPosition(position, allsnake), WINDOWHEIGHT / 20 * 5, snake.color)
        drawText('score:', snake.score, getPosition(position, allsnake), WINDOWHEIGHT / 20 * 6, snake.color)
        drawText('apples:', snake.fruitEaten['apple'], getPosition(position, allsnake), WINDOWHEIGHT / 20 * 7, RED)
        drawText('poison:', snake.fruitEaten['poison'], getPosition(position, allsnake), WINDOWHEIGHT / 20 * 8, GREEN)
        drawText('oranges:', snake.fruitEaten['orange'], getPosition(position, allsnake), WINDOWHEIGHT / 20 * 9, ORANGE)
        drawText('raspberries:', snake.fruitEaten['raspberry'], getPosition(position, allsnake), WINDOWHEIGHT / 20 * 10, PURPLE)
        drawText('blueberries:', snake.fruitEaten['blueberry'], getPosition(position, allsnake), WINDOWHEIGHT / 20 * 11, BLUE)
        position = position + 1

    drawMessage('Press any key.', WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 19, GOLDENROD)
    pygame.display.update()
    pygame.time.wait(300)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def showGameOverScreen():
    """
    Displays 'Game Over' message.
    Returns when any key pressed.
    """
    gameOverFont = pygame.font.Font('freesansbold.ttf', 48)
    gameOverSurf = gameOverFont.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 3 * 2)

    DISPLAYSURF.blit(gameOverSurf, gameOverRect)
    drawMessage('Press any key.', WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 19, GOLDENROD)
    pygame.display.update()
    pygame.time.wait(300)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def getGrid(allsnake, allfruit):
    """
    Returns dictionary representation of all snakes and fruits on screen.
    Coordinates are entered as tuple (x,y).
    Used by AI when choosing best path.
    """
    # refresh grid, dictionary representation of playing board used by AI
    grid = {(x,y):0 for x in range(CELLWIDTH) for y in range(CELLHEIGHT + (BUFFER / CELLSIZE))}
    
    # add snakes to grid
    for snake in allsnake:
        for snakebody in snake.coords:
            grid[(snakebody['x'], snakebody['y'])] = 'snake'
               
     # add fruits to grid
    for fruit in allfruit:
        if fruit.__class__ == Apple:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'apple'
        elif fruit.__class__ == Poison:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'poison'
        elif fruit.__class__ == Orange:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'orange'
        elif fruit.__class__ == Raspberry:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'raspberry'
        elif fruit.__class__ == Blueberry:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'blueberry'
        elif fruit.__class__ == Lemon:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'lemon'

    return grid


def drawText(text, value, x=1, y=1, color=WHITE, background=BLACK):
    """
    Draws text & value with background to screen.
    """
    scoreSurf = BASICFONT.render('%s %s' % (text, value), True, color, background)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (x, y)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    
    
def drawMessage(text, x=1, y=1, color=GREEN):
    """
    Draws message to screen.
    """
    messageSurf = BASICFONT.render(text, True, color)
    messageRect = messageSurf.get_rect()
    messageRect.topleft = (x, y)
    DISPLAYSURF.blit(messageSurf, messageRect)


def drawGrid():
    """
    Draws grid to screen.
    """
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, BUFFER), (x, WINDOWHEIGHT))
    for y in range(BUFFER, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


def debugPause():
    while True:
        if checkForKeyPress():
            return
            
            
def debugPrintGrid(grid):
    x = 0
    y = 0
    line = ""
    while grid.has_key((0,y)):
        if grid.has_key((x,y)):
            line = line + str(grid[(x,y)])[0]
            x = x + 1
        else:
            print line
            line = ""
            y = y + 1
            x = 0


def getPosition(position, allsnake):
    return (WINDOWWIDTH - (float(position) / float(len(allsnake)) * WINDOWWIDTH))
    

def getStartPosition(pos=1):
    if pos == 1:
        return [{'x':5, 'y':5},{'x':4, 'y':5},{'x':3, 'y':5}]
    elif pos == 2:
        return [{'x':CELLWIDTH-5, 'y':CELLHEIGHT-5},{'x':CELLWIDTH-4, 'y':CELLHEIGHT-5},{'x':CELLWIDTH-3, 'y':CELLHEIGHT-5}]
    elif pos == 3:
        return [{'x':CELLWIDTH-5, 'y':5},{'x':CELLWIDTH-4, 'y':5},{'x':CELLWIDTH-3, 'y':5}]
    elif pos == 4:
        return [{'x':5, 'y':CELLHEIGHT-5},{'x':4, 'y':CELLHEIGHT-5},{'x':3, 'y':CELLHEIGHT-5}]


if __name__ == '__main__':
    main()

