#!/usr/bin/env python
# A Snakey clone made with Pygame.
# Requires Pygame: http://pygame.org/download.shtml
# Includes various fruits with different effects in regards to score,
# snake size, and other in-game effects.
# Includes various Snake AIs and game modes (Arcade, Duel, Party).

import random, pygame, sys
from pygame.locals import *

FPS = 12
MIN_FPS = 3
MAX_FPS = 60
FREEZING_POINT = 9  # target FPS when Blueberry (slow) is in effect.

WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20

# displays in-game info
# set so that 1 cell is reserved for 640x480, 2 cells for 800x600
TOP_BUFFER = CELLSIZE * int(WINDOWWIDTH * WINDOWHEIGHT / 200000)
assert WINDOWWIDTH % CELLSIZE == 0, \
       "Window width must be a multiple of cell size."
assert (WINDOWHEIGHT - TOP_BUFFER) % CELLSIZE == 0, \
       "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int((WINDOWHEIGHT - TOP_BUFFER) / CELLSIZE)

# colors - (R G B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
COBALTGREEN = (61, 145, 64)
DARKBLUE = (25, 25, 112)
DARKGRAY = (40, 40, 40)
FORESTGREEN = (34, 139, 34)
GOLDENROD = (218, 165, 32)
GREEN = (0, 255, 0)
IVORY = (205, 205, 193)
ORANGE = (255, 127, 0)
PINK = (255, 105, 180)
PURPLE = (142, 56, 142)
RED = (255, 0, 0)
SLATEBLUE = (131, 111, 255)
YELLOW = (238, 238, 0)

BACKGROUNDCLR = BLACK
BUTTONCLR = GREEN
BUTTONTXT = DARKGRAY
BUTTONCLR_SEL = COBALTGREEN
BUTTONTXT_SEL = GOLDENROD
MESSAGECLR = GREEN

# text sizes for titles
MEDIUMTITLE = int(WINDOWWIDTH * WINDOWHEIGHT / 9600)
LARGETITLE = int(WINDOWWIDTH * WINDOWHEIGHT / 6400)
XLARGETITLE = int(WINDOWWIDTH * WINDOWHEIGHT / 4800)

# for consistency
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
SNAKEY = 'snakey'
LINUS = 'linus'
WIGGLES = 'wiggles'
GOOBER = 'goober'

# index of snake's head
HEAD = 0

# minimum and maximum frames fruit remains on screen - determined randomly
POISONTIMER = (100, 200)
ORANGETIMER = (35, 65)
RASPBERRYTIMER = (30, 45)
BLUEBERRYTIMER = (20, 40)
LEMONTIMER = (100, 100)
EGGTIMER = (40, 70)


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
    def __init__(self, n=SNAKEY, c=False, colorsnake=GREEN, colorborder=COBALTGREEN):
        self.name = n
        if self.name == SNAKEY:
            self.player = True
        else:
            self.player = False
        self.alive = True
        
        if c == False:
            self.coords = getStartCoords(1)
        else:
            self.coords = c
        
        # determine direction if length supports
        if len(self.coords) > 1:
            if self.coords[0]['x'] > self.coords[1]['x']:
                self.direction = RIGHT
            else:
                self.direction = LEFT
        # egg -- for now until AI direction fixed
        else:
             self.direction = LEFT
        
        self.color = {'red': 0, 'green': 0, 'blue': 0}
        self.updateColor({'red': colorsnake[0], 'green': colorsnake[1], 'blue': colorsnake[2]})
        self.colorCurrent = self.color
        
        self.colorBorder = {'red': 0, 'green': 0, 'blue': 0}
        self.updateColorBorder({'red': colorborder[0], 'green': colorborder[1], 'blue': colorborder[2]})
        self.colorBorderCurrent = self.colorBorder
        
        self.growth = 0
        self.multiplier = 1
        self.multipliertimer = 0
        self.score = 0
        self.place = False
        self.scored = True
        self.fruitEaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0,
                           'blueberry':0, 'lemon':0, 'egg':0}

    def updateScore(self, points_input):
        """
        This updates score of snake, factoring multiplier.
        Argument (points_input) should be int.
        """
        self.score = self.score + (points_input * self.multiplier)

    def updateGrowth(self, growth_input):
        """
        This updates growth "owed" to snake, allowing amount to stack.
        Argument (growth_input) should be int.
        """
        self.growth = self.growth + growth_input

    def updateMultiplier(self, multiplier_input, timer_input):
        """
        This updates multiplier value and time (game iterations) multiplier is active. Only time stacks.
        """
        # multiplier value does not stack, but time does
        self.multiplier = multiplier_input
        self.multipliertimer = self.multipliertimer + timer_input
        
    def updateColor(self, change):
        """
        Adjusts color of snake.
        Argument (change) is dictionary.
        Factors in maximums and minimums.
        """
        for color in change:
            if self.color.has_key(color):
                if change[color] > 0:
                    if self.color[color] + change[color] > 255:
                        self.color[color] = 255
                    else:
                        self.color[color] = self.color[color] + change[color]
                elif change[color] < 0:
                    if self.color[color] + change[color] < 0:
                        self.color[color] = 0
                    else:
                        self.color[color] = self.color[color] + change[color]
                        
    def updateColorBorder(self, change):
        """
        Adjusts border color of snake.
        Argument (change) is dictionary.
        Factors in maximums and minimums.
        """
        for color in change:
            if self.colorBorder.has_key(color):
                if change[color] > 0:
                    if self.colorBorder[color] + change[color] > 255:
                        self.colorBorder[color] = 255
                    else:
                        self.colorBorder[color] = self.colorBorder[color] + change[color]
                elif change[color] < 0:
                    if self.colorBorder[color] + change[color] < 0:
                        self.colorBorder[color] = 0
                    else:
                        self.colorBorder[color] = self.colorBorder[color] + change[color]
        
    def setColorCurrent(self, color):
        """
        Sets current color.
        Argument (color) is a tuple.
        """
        self.colorCurrent = {'red': color[0], 'green': color[1], 'blue': color[2]}
        
    def setColorBorderCurrent(self, color):
        """
        Sets current border color.
        Argument (color) is a tuple.
        """
        self.colorBorderCurrent = {'red': color[0], 'green': color[1], 'blue': color[2]}
        
    def getColor(self):
        """
        Returns tuple of snake color.
        """
        return (self.color['red'], self.color['green'], self.color['blue'])
        
    def getColorCurrent(self):
        """
        Returns tuple of snake color, currently.
        """
        return (self.colorCurrent['red'], self.colorCurrent['green'], self.colorCurrent['blue'])
        
    def getColorBorder(self):
        """
        Returns tuple of snake color, border.
        """
        return (self.colorBorder['red'], self.colorBorder['green'], self.colorBorder['blue'])
        
    def getColorBorderCurrent(self):
        """
        Returns tuple of snake color, current border.
        """
        return (self.colorBorderCurrent['red'], self.colorBorderCurrent['green'], self.colorBorderCurrent['blue'])
        
    def resetColor(self):
        """
        Sets current color to color.
        """
        self.colorCurrent = self.color
        
    def resetColorBorder(self):
        """
        Sets current border color to border color.
        """
        self.colorBorderCurrent = self.colorBorder
        
    def getPlace(self, totaldead, totalscored):
        """
        Returns a string containing the 'place' of a snake (longest lasting = 1st)
        If game aborted early, will grant all living snakes '1st (alive)'
        """
        totalalive = totalscored - totaldead

        # snake not dead
        if self.place == False:
            return '1st*'
        # if not aborted early
        elif totalalive == 0:
            if self.place == totalscored:
                return '1st'
            elif self.place + 1 == totalscored:
                return '2nd'
            elif self.place + 2 == totalscored:
                return '3rd'
            else:
                return 'last'
        # aborted early; factor in living snakes
        elif self.place == totalscored - totalalive:
            return '2nd'
        elif self.place + 1 == totalscored - totalalive:
            return '3rd'
        else:
            return 'last'
            
    def checkCoords(self, x, y):
        """
        Returns True if snake (head) matches (x,y) coordinates provided.
        Will always return False if coordinates < 1.
        """
        if len(self.coords) > 0:
            if self.coords[HEAD]['x'] == x and self.coords[HEAD]['y'] == y:
                return True
        return False
        
    def getCoords(self, axis):
        """
        Returns x or y (axis) coordinates of head of snake.
        Will always return False if coordinates < 1.
        """
        if len(self.coords) > 0:
            return self.coords[HEAD][axis]

    def boundsCollision(self):
        """
        This returns True if snake (head) is ever out of grid parameters.
        """
        # check if out of bounds -- offset on on 'y' for buffer.
        if self.getCoords('x') == -1 or \
           self.getCoords('x') == CELLWIDTH or \
           self.getCoords('y') == -1 + (TOP_BUFFER / CELLSIZE) or \
           self.getCoords('y') == CELLHEIGHT + (TOP_BUFFER / CELLSIZE):
            return True
        else:
            return False
            
    def snakeCollision(self, snake):
        """
        This returns True if snake (head) collides with any part of a given snake (outside of own head if checking against self).
        Will always return False if coordinates of self or snake < 1.
        """
        if len(self.coords) > 0 and len(snake.coords) > 0:
            if self is snake:
                # exclude head if checked against self
                for snakebody in snake.coords[1:]:
                    if snakebody['x'] == self.coords[HEAD]['x'] and \
                       snakebody['y'] == self.coords[HEAD]['y']:
                        return True    
            else:
                for snakebody in snake.coords:
                    if snakebody['x'] == self.coords[HEAD]['x'] and \
                       snakebody['y'] == self.coords[HEAD]['y']:
                        return True
        # no collision
        return False
        
    def fruitCollision(self, fruit):
        """
        This returns True if snake (head) has collided with a given fruit.
        """
        if self.getCoords('x') == fruit.coords['x'] and \
           self.getCoords('y') == fruit.coords['y']:
            return True
        else:
            return False

    def move(self, trailing=False):
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
                # implement positive growth by not deleting last segment
                self.growth = self.growth - 1
            elif trailing == False:
                # no growth factor, delete last segment if trailing is off
                del self.coords[-1]

            # determine new head coordinates by direction
            if self.direction == UP:
                newhead = {'x': self.getCoords('x'), 
                           'y': self.getCoords('y') - 1}
            elif self.direction == DOWN:
                newhead = {'x': self.getCoords('x'), 
                           'y': self.getCoords('y') + 1}
            elif self.direction == LEFT:
                newhead = {'x': self.getCoords('x') - 1, 
                           'y': self.getCoords('y')}
            elif self.direction == RIGHT:
                newhead = {'x': self.getCoords('x') + 1, 
                           'y': self.getCoords('y')}

            # insert new head segment
            self.coords.insert(HEAD, newhead)

        # dead snake -- remove last segment
        elif len(self.coords) > 0:
            del self.coords[-1]
            
    def drawSnake(self):
        """
        Responsible for drawing snake image to screen.
        """
        for coord in self.coords:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            snakeSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, self.getColorBorderCurrent(), snakeSegmentRect)
            snakeInnerSegmentRect = pygame.Rect(x + 3, y + 3, CELLSIZE - 6, CELLSIZE - 6)
            pygame.draw.rect(DISPLAYSURF, self.getColorCurrent(), snakeInnerSegmentRect)
            
    def drawScore(self, position, allsnake):
        """
        Responsible for drawing snake score to screen.
        Coordinates of where drawn so that 'y' depends on number of snakes being scored, 'x' at the top (where buffer is)
        """
        # get number of snakes in allsnake that will be scored.
        totalscored = 0
        for snake in allsnake:
            if snake.scored == True:
                totalscored = totalscored + 1
        drawMessage(self.name + ': ' + str(self.score), \
                    getPosition(position, allsnake, totalscored), 1, \
                    self.getColorCurrent())
        
        
class Opponent(Snake):
    """
    Derived from Snake class, this adds functionality for determining direction.
    """
    def __init__(self, n='bot', c=False, sc=COBALTGREEN, sb=GOLDENROD, r=20, p=10, a=-15, g=[50,-10,30,20,35,100,30]):
        Snake.__init__(self, n, c, sc, sb)
        self.avoidBoundaries = True
        self.depthPerception = 20
        self.randomness = r
        self.preferSameDirection = p
        self.avoidSnake = a
        self.goal = {'apple': g[0], 'poison': g[1], 'orange': g[2], 'raspberry': g[3], 'blueberry': g[4], 'lemon': g[5], 'egg': g[6]}

    def updateDirection(self, grid):
        """
        Responsible for determining opponent's direction choice.
        Takes one argument - grid representation of playing board. Copied and marked as cells are 'explored'
        Neighboring 
        """
        # copy grid to snake -- this will allow cells already searched to be marked 'visited'
        self.grid = grid
    
        # all directions have value adjusted -- reset
        self.nextDirection = {LEFT:0, RIGHT:0, UP:0, DOWN:0}
        
        # coords of own snake head
        x = self.getCoords('x')
        y = self.getCoords('y')

        # opposite direction kills snake
        if self.direction == LEFT:
            self.nextDirection[RIGHT] = self.nextDirection[RIGHT] - 1000
        elif self.direction == RIGHT:
            self.nextDirection[LEFT] = self.nextDirection[LEFT] - 1000
        elif self.direction == UP:
            self.nextDirection[DOWN] = self.nextDirection[DOWN] - 1000
        elif self.direction == DOWN:
            self.nextDirection[UP] = self.nextDirection[UP]- 1000

        # avoid boundaries
        if self.avoidBoundaries == True:
            if x == 0:
                self.nextDirection[LEFT] = self.nextDirection[LEFT] - 1000
            if x == CELLWIDTH - 1:
                self.nextDirection[RIGHT] = self.nextDirection[RIGHT] - 1000
            if y == (TOP_BUFFER / CELLSIZE):
                self.nextDirection[UP] = self.nextDirection[UP] - 1000
            if y == CELLHEIGHT + (TOP_BUFFER / CELLSIZE) - 1:
                self.nextDirection[DOWN] = self.nextDirection[DOWN] - 1000
                
        # prefer same direction
        self.nextDirection[self.direction] = self.nextDirection[self.direction] + self.preferSameDirection

        # avoid immediate snakes
        if grid.has_key((x-1,y)) and (grid[(x-1,y)] == 'snake'):
            self.nextDirection[LEFT] = self.nextDirection[LEFT] - 1000
        if grid.has_key((x+1,y)) and (grid[(x+1,y)] == 'snake'):
            self.nextDirection[RIGHT] = self.nextDirection[RIGHT] - 1000
        if grid.has_key((x,y-1)) and (grid[(x,y-1)] == 'snake'):
            self.nextDirection[UP] = self.nextDirection[UP] - 1000
        if grid.has_key((x,y+1)) and (grid[(x,y+1)] == 'snake'):
            self.nextDirection[DOWN] = self.nextDirection[DOWN] - 1000
            
        # 'look' to neighboring squares for possible snakes and fruits
        self.look(x, y, self.depthPerception)

        # factor in randomness
        for d in self.nextDirection:
            self.nextDirection[d] = self.nextDirection[d] + random.randint(0,self.randomness)
            
        # report if debugging
        if DEBUG == True:
            print self.name
            print self.nextDirection

        # update snake direction to direction with highest score
        self.direction = max(self.nextDirection, key=self.nextDirection.get)
        
    def look(self, x, y, depth):
        """
        recursively looks in all directions unless depth is exhausted.
        visited coords are ignored.
        coords containing a snake are affected by avoidSnake variable
        """
        #if DEBUG == True:
        #    print 'look for %s at (%s, %s)- depth %s' % (self.name, x, y, depth)
        if depth < 1:
            return
        elif self.grid.has_key((x,y)):
            if self.grid[(x,y)] == 'visited':
                return
            elif self.grid[(x,y)] == 'snake':
                if DEBUG == True:
                    print '..snake:'
                self.influenceDirection(x, y, self.avoidSnake)
                self.grid[(x,y)] = 'visited'
                self.look(x-1, y, depth -1)
                self.look(x+1, y, depth -1)
                self.look(x, y+1, depth -1)
                self.look(x, y-1, depth -1)
            elif self.grid[(x,y)] != 0:  # implied fruit
                fruit = self.grid[(x,y)]
                if DEBUG == True:
                    print '..fruit: %s' % (fruit)
                self.influenceDirection(x, y, self.goal[fruit])
                self.grid[(x,y)] = 'visited'
                self.look(x-1, y, depth -1)
                self.look(x+1, y, depth -1)
                self.look(x, y+1, depth -1)
                self.look(x, y-1, depth -1)
            else: #empty cell
                self.grid[(x,y)] = 'visited'
                self.look(x-1, y, depth -1)
                self.look(x+1, y, depth -1)
                self.look(x, y+1, depth -1)
                self.look(x, y-1, depth -1)
        else: #bound collision
            return

    def influenceDirection(self, x, y, base):
        """
        Finds difference between (x,y) coord and point of origin.
        Direction is then altered by 'base' amount, decayed 1 per distance from.
        """
        if DEBUG == True:
            print '....%s (%s, %s)-->' % (self.nextDirection, x, y)
        xdiff = self.getCoords('x') - x
        ydiff = self.getCoords('y') - y
        if xdiff > 0:  # positive = left
            if (base - xdiff > 0 and base > 0) or (base - xdiff < 0 and base < 0):
                self.nextDirection[LEFT] = self.nextDirection[LEFT] + base - xdiff
        elif xdiff < 0:  # negative = right
            if (base + xdiff > 0 and base > 0) or (base + xdiff < 0 and base < 0):
                self.nextDirection[RIGHT] = self.nextDirection[RIGHT] + base + xdiff
        if ydiff > 0:  # positive = up
            if (base - ydiff > 0 and base > 0) or (base - ydiff < 0 and base < 0):
                self.nextDirection[UP] = self.nextDirection[UP] + base - ydiff
        elif ydiff < 0:  # negative = down
            if (base + ydiff > 0 and base > 0) or (base + ydiff < 0 and base < 0):
                self.nextDirection[DOWN] = self.nextDirection[DOWN] + base + ydiff
        if DEBUG == True:
            print '....%s' % (self.nextDirection)

    def getPlace(self, totaldead, totalsnakes):
        return Snake.getPlace(self, totaldead, totalsnakes)
        
    def updateColor(self, change):
        Snake.updateColor(self, change)
        
    def updateColorBorder(self, change):
        Snake.updateColorBorder(self, change)

    def setColorCurrent(self, color):
        Snake.setColorCurrent(self, color)
        
    def setColorBorderCurrent(self, color):
        Snake.setColorBorderCurrent(self, color)
        
    def getColor(self):
        return Snake.getColor(self)
        
    def getColorCurrent(self):
        return Snake.getColorCurrent(self)
        
    def getColorBorder(self):
        return Snake.getColorBorder(self)
        
    def getColorBorderCurrent(self):
        return Snake.getColorBorderCurrent(self)
        
    def resetColor(self):
        Snake.resetColor(self)
    
    def resetColorBorder(self):
        Snake.resetColorBorder(self)

    def updateScore(self, points_input):
        Snake.updateScore(self, points_input)

    def updateGrowth(self, growth_input):
        Snake.updateGrowth(self, growth_input)

    def updateMultiplier(self, multiplier_input, timer_input):
        Snake.updateMultiplier(self, multiplier_input, timer_input)
        
    def checkCoords(self, x, y):
        return Snake.checkCoords(self, x, y)
        
    def getCoords(self, axis):
        return Snake.getCoords(self, axis)

    def boundsCollision(self):
        return Snake.boundsCollision(self)

    def snakeCollision(self, snake):
        return Snake.snakeCollision(self, snake)

    def fruitCollision(self, fruit):
        return Snake.fruitCollision(self, fruit)

    def move(self, trailing):
        Snake.move(self, trailing)

    def drawSnake(self):
        Snake.drawSnake(self)

    def drawScore(self, position, allsnake):
        Snake.drawScore(self, position, allsnake)        
        
        
class Fruit:
    """
    Fruit class houses all information for fruit objects. 
    Base class is not meant to be instantiated, but rather provide base methods shared by all fruit.
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
                y = random.randint((TOP_BUFFER / CELLSIZE), CELLHEIGHT - 1)
            # ensure coordinates are not already occupied by fruit
            for fruit in allfruit:
                if fruit.coords['x'] == x and fruit.coords['y'] == y:
                    conflict = True
            # ensure coordinates are not already occupied by snake head
            for snake in allsnake:
                if snake.getCoords('x') == x and snake.getCoords('y') == y:
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
        snake.updateColor({'red': 6, 'green': -5, 'blue': -5})

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
        snake.updateColor({'red': -20, 'green': 20})

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
        snake.updateColor({'red': 10, 'green': 3, 'blue': -10})

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
        snake.updateColor({'red': 12, 'green': -15, 'blue': 13})

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
        snake.updateColor({'red': -20, 'green': -15, 'blue': 60})

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)


class Lemon(Fruit):
    """
    Lemon will grow snake to mythic proportions.
    """
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(LEMONTIMER[0], LEMONTIMER[1])
        self.color = YELLOW
        self.score = 500
        self.growth = 20

    def isEaten(self, snake, game):
        snake.fruitEaten['lemon'] = snake.fruitEaten['lemon'] + 1
        game.fruitEaten['lemon'] = game.fruitEaten['lemon'] + 1
        snake.updateScore(self.score)
        snake.updateGrowth(self.growth)
        snake.updateColor({'blue': -20})

    def updateTimer(self):
        return Fruit.updateTimer(self)

    def drawFruit(self):
        Fruit.drawFruit(self)
        
        
class Egg(Fruit):
    """
    Eggs spawn another snake if not eaten.
    """
    def __init__(self, allfruit, allsnake, game):
        self.coords = Fruit.getRandomLocation(self, allfruit, allsnake, game)
        self.timer = random.randint(EGGTIMER[0], EGGTIMER[1])
        self.color = GOLDENROD
        self.colorBorder = WHITE
        self.points = 250
        self.growth = 1
        self.radius = CELLSIZE / 2

    def isEaten(self, snake, game):
        snake.fruitEaten['egg'] = snake.fruitEaten['egg'] + 1
        game.fruitEaten['egg'] = game.fruitEaten['egg'] + 1
        snake.updateScore(self.points)
        snake.updateGrowth(self.growth)
        snake.updateColor({'red': -35, 'green': -30, 'blue': -25})

    def updateTimer(self):
        """
        Also adjusts radius size depending on time remaining.
        """
        if self.timer < (EGGTIMER[0] + EGGTIMER[1]) * 2 / 3:
            self.radius = CELLSIZE / 3
        if self.timer < (EGGTIMER[0] + EGGTIMER[1]) / 2:
            self.radius = CELLSIZE / 4
        if self.timer < (EGGTIMER[0] + EGGTIMER[1]) / 3:
            self.radius = CELLSIZE / 5
        return Fruit.updateTimer(self)

    def isHatched(self, allsnake):
        """
        Add new snake with coords as coords of fruit, and growth of 3.
        Snake is not scored (name and score does not appear).
        """
        junior = Opponent('junior', [{'x':self.coords['x'] , 'y':self.coords['y']}], PINK, GREEN, 10, 10, -20, [35, 5, 40, 30, 35, 15, 0])
        junior.growth = 3
        junior.scored = False
        allsnake.append(junior)

    def drawFruit(self):
        """
        Responsible for drawing image to screen.
        """
        x = self.coords['x'] * CELLSIZE
        y = self.coords['y'] * CELLSIZE
        xNext = (self.coords['x'] + 1) * CELLSIZE
        yNext = (self.coords['y'] + 1) * CELLSIZE
        center = ((xNext + x) / 2, (yNext + y) / 2)
        fruitRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, self.colorBorder, fruitRect)
        pygame.draw.circle(DISPLAYSURF, self.color, center, self.radius)


class GameData:
    """
    Responsible for dynamics for a particular game instance.
    fruitEaten - a dictionary containing a numeric tally of each fruit eaten.
    speedTrigger - the frequency (based on apples consumed) in which gamespeed is increased by one.
    bonusFruitTrigger - the frequency (based on apples consumed) in which a bonus game is launched.
    easyTrigger - a threshold (apples consumed); once reached fruit can be placed anywhere on screen (as opposed to away from edges).
    currentplace - the current 'place' of snake. When snake has died.
    apples - number of apples on screen.
    """
    def __init__(self, st=20, bft=10, et=20, a=1):
        self.fruitEaten = {'apple':0, 'poison':0, 'orange':0, 'raspberry':0,
                           'blueberry':0, 'lemon':0, 'egg':0}
        self.speedTrigger = st
        self.bonusFruitTrigger = bft
        self.easyTrigger = et
        self.currentplace = 1
        self.apples = a
        self.basespeed = FPS
        self.currentspeed = self.basespeed
        self.slowtimer = 0
        self.trailing = False
        self.poisonDrop = 4
        self.orangeDrop = 5
        self.raspberryDrop = 6
        self.blueberryDrop = 25
        self.lemonDrop = 100
        self.eggDrop = 12

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
        if self.fruitEaten['apple'] % self.bonusFruitTrigger == 0:
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
            if snake.scored == True:
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
        if (self.basespeed + value > MIN_FPS) and \
           (self.basespeed + value < MAX_FPS):
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
        
    def runDrop(self, allfruit, allsnake):
        """
        Adds fruit randomly to screen.
        If newapple is turned on, replaces apple that was eaten.
        """
        # chance of poison drop
        if self.poisonDrop != False and random.randint(1,self.poisonDrop) == 1:
            p = Poison(allfruit, allsnake, self)
            allfruit.append(p)
        # chance of orange drop
        if self.orangeDrop != False and random.randint(1,self.orangeDrop) == 1:
            o = Orange(allfruit, allsnake, self)
            allfruit.append(o)
        # chance of raspberry drop
        if self.raspberryDrop != False and random.randint(1,self.raspberryDrop) == 1:
            r = Raspberry(allfruit, allsnake, self)
            allfruit.append(r)
        # chance of blueberry drop
        if self.blueberryDrop != False and random.randint(1,self.blueberryDrop) == 1:
            b = Blueberry(allfruit, allsnake, self)
            allfruit.append(b)
        # chance of lemon drop
        if self.lemonDrop != False and random.randint(1,self.lemonDrop) == 1:
            l = Lemon(allfruit, allsnake, self)
            allfruit.append(l)
        # chance of egg drop
        if self.eggDrop != False and random.randint(1,self.eggDrop) == 1:
            e = Egg(allfruit, allsnake, self)
            allfruit.append(e)
        # create new apple
        a = Apple(allfruit, allsnake, self)
        allfruit.append(a)

    def runBonusFruit(self, allfruit, allsnake):
        """
        Returns a list containing fruit (as strings) to be added to game from bonus game.
        An integer (determined randomly between typeMin and typeMax) corresponds to bonus game run.
        A basic set-up would randomly choose between 1 and 10; 6 through 10 initiating a fruit specific bonus.
        Default will contain an assortment of fruit.
        """
        bonus = []
        type = random.randint(1, 20)
        
        # drop amounts based on size of playing field
        squares = CELLWIDTH * CELLHEIGHT
        tinyLower = int(squares / 600)
        tinyUpper = int(squares / 135)
        smallLower = int(squares / 68)
        smallUpper = int(squares / 45)
        largeLower = int(squares / 34)
        largeUpper = int(squares / 19)
        
        # based on bonus type, create fruits
        if type == 1:
            counter = random.randint(smallLower,smallUpper)
            while counter > 0:
                bonus.append('egg')
                counter = counter - 1
        elif type == 2 or type == 3:
            counter = random.randint(largeLower,largeUpper)
            while counter > 0:
                bonus.append('poison')
                counter = counter - 1
        elif type == 4 or type == 5:
            counter = random.randint(largeLower,largeUpper)
            while counter > 0:
                bonus.append('orange')
                counter = counter - 1
        elif type == 6:
            counter = random.randint(largeLower,largeUpper)
            while counter > 0:
                bonus.append('raspberry')
                counter = counter - 1
        elif type == 7:
            counter = random.randint(largeLower,largeUpper)
            while counter > 0:
                bonus.append('blueberry')
                counter = counter - 1
        # default bonus
        else:
            counter = random.randint(tinyLower, tinyUpper)
            while counter > 0:
                bonus.append('poison')
                counter = counter - 1
            counter = random.randint(5,20)
            while counter > 0:
                bonus.append('orange')
                counter = counter - 1
            counter = random.randint(tinyLower, tinyUpper)
            while counter > 0:
                bonus.append('raspberry')
                counter = counter - 1
            counter = random.randint(tinyLower, tinyUpper)
            while counter > 0:
                bonus.append('blueberry')
                counter = counter - 1
        
        # add fruits
        for bonusfruit in bonus:
            if bonusfruit == 'poison':
                f = Poison(allfruit, allsnake, self)
            elif bonusfruit == 'orange':
                f = Orange(allfruit, allsnake, self)
            elif bonusfruit == 'raspberry':
                f = Raspberry(allfruit, allsnake, self)
            elif bonusfruit == 'blueberry':
                f = Blueberry(allfruit, allsnake, self)
            elif bonusfruit == 'lemon':
                f = Lemon(allfruit, allsnake, self)
            elif bonusfruit == 'egg':
                f = Egg(allfruit, allsnake, self)
            allfruit.append(f)
            
    def drawScreen(self, allfruit, allsnake, player):
        """
        Responsible for drawing everything onto screen.
        """
        # clear background
        DISPLAYSURF.fill(BACKGROUNDCLR)

        # check slow and adjust fps as needed
        # draw grid to screen as well (color based on slow or normal)
        if self.checkSlowTimer():
            self.updateSlowTimer()
            self.updateCurrentSpeed(FREEZING_POINT)
            self.drawGrid(DARKBLUE)
        else:
            self.updateCurrentSpeed()
            self.drawGrid()

        # draw everything else to screen
        for fruit in allfruit:
            fruit.drawFruit()
        for snake in allsnake:
            snake.drawSnake()
            
        # print scores only if snake is scored
        position = 1
        for snake in allsnake:
            if snake.scored == True:
                snake.drawScore(position, allsnake)
                position = position + 1

        # if player is dead, print extra messages
        if player == False or player.alive == False:
            endMessage = 'press (e) to end game early'
            fastMessage = 'press (f) to fast-forward game'
            slowMessage = 'press (s) to slow game'
            drawMessage(endMessage, WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 16)
            drawMessage(fastMessage, WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 17)
            drawMessage(slowMessage, WINDOWWIDTH / 2, WINDOWHEIGHT / 20 * 18)
        pygame.display.update()
        FPSCLOCK.tick(self.currentspeed)
        
    def drawGrid(self, color=DARKGRAY):
        """
        Draws grid to screen.
        """
        for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
            pygame.draw.line(DISPLAYSURF, color, (x, TOP_BUFFER), (x, WINDOWHEIGHT))
        for y in range(TOP_BUFFER, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
            pygame.draw.line(DISPLAYSURF, color, (0, y), (WINDOWWIDTH, y))


class Button():
    """
    A clickable button that is rendered on screen.
    """
    def __init__(self, text, x, y):
        self.text = text
        size = int (WINDOWWIDTH / 18)
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.startSurf = self.font.render(self.text, True, BUTTONCLR, BUTTONTXT)
        self.rect = self.startSurf.get_rect()
        self.rect.center = x,y

    def display(self):
        DISPLAYSURF.blit(self.startSurf, self.rect)

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0] and \
           mouse[1] > self.rect.topleft[1] and \
           mouse[0] < self.rect.bottomright[0] and \
           mouse[1] < self.rect.bottomright[1]:
            return True
        else:
            return False


class SelectButton(Button):
    """
    Selected by color. Clicking will turn active state to True.
    Contains a value that is returned with getValue().
    """
    def __init__(self, text, x, y, v, a=False):
        Button.__init__(self, text, x, y)
        self.value = v
        self.active = a
        
    def display(self):
        if self.active == True:
            self.startSurf = self.font.render(self.text, True, BUTTONCLR_SEL, BUTTONTXT_SEL)
        else:
            self.startSurf = self.font.render(self.text, True, BUTTONCLR, BUTTONTXT)
            
        DISPLAYSURF.blit(self.startSurf, self.rect)
        
    def pressed(self, mouse):
        return Button.pressed(self, mouse)

    def getActive(self):
        return self.active

    def setActive(self, buttonlist):
        for button in buttonlist:
            if button == self:
                self.active = True
            else:
                button.active = False
                
    def getValue(self):
        return self.value


class InputButton(Button, SelectButton):
    """
    still in testing
    """
    def __init__(self, value, x, y, min=1, max=9999, a=False):
        # set-up center rectangle
        self.value = value
        size = int (WINDOWWIDTH / 18)
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.startSurf = self.font.render('-', True, BUTTONCLR, BUTTONTXT)
        self.rect = self.startSurf.get_rect()
        self.rect.center = x,y
        self.min = min
        self.max = max
        self.active = a
        # set-up decrease arrow
        self.decreaseSurf = pygame.Surface((size, size))
        self.decreaseSurf.fill(GREEN)
        # set-up increase arrow
        self.increaseSurf = pygame.Surface((size, size))
        self.increaseSurf.fill(GREEN)
        #arrowcenterleft = (self.rect.left - size, self.rect.centery)
        #self.decrease = pygame.draw.lines(self.decreaseSurf, BLACK, True, [self.rect.topleft, arrowcenterleft, self.rect.bottomleft], 3)
        self.decrease = self.decreaseSurf.get_rect(topleft=(self.rect.topleft[0] - size, self.rect.topleft[1]))
        self.increase = self.increaseSurf.get_rect(topleft=(self.rect.topright[0] + size, self.rect.topright[1]))

    def display(self):
        if self.active == True:
            self.startSurf = self.font.render(str(self.value), True, BUTTONCLR_SEL, BUTTONTXT_SEL)
        else:
            self.startSurf = self.font.render(str(self.value), True, BUTTONCLR, BUTTONTXT)

        DISPLAYSURF.blit(self.startSurf, self.rect)
        DISPLAYSURF.blit(self.decreaseSurf, self.decrease)
        DISPLAYSURF.blit(self.increaseSurf, self.increase)
        
    def pressed(self, mouse, buttonlist):
        # if decrease is pressed
        if mouse[0] > self.decrease.topleft[0] and \
           mouse[1] > self.decrease.topleft[1] and \
           mouse[0] < self.decrease.bottomright[0] and \
           mouse[1] < self.decrease.bottomright[1]:
            self.setActive(buttonlist)
            self.setValue(-1)
        # if increase is pressed
        elif mouse[0] > self.increase.topleft[0] and \
           mouse[1] > self.increase.topleft[1] and \
           mouse[0] < self.increase.bottomright[0] and \
           mouse[1] < self.increase.bottomright[1]:
            self.setActive(buttonlist)
            self.setValue(1)
        elif Button.pressed(self, mouse):
            self.setActive(buttonlist)

    def getActive(self):
        return SelectButton.getActive(self)
        
    def setActive(self, buttonlist):
        SelectButton.setActive(self, buttonlist)
        
    def getValue(self):
        return SelectButton.getValue(self)
        
    def setValue(self, change):
        newValue = self.value + change
        if newValue <= self.max and newValue >= self.min:
            self.value = newValue
            

def main():
    global FPSCLOCK, DISPLAYSURF, DEBUG
    
    # for debugging
    if len(sys.argv) < 2:
        DEBUG = False
    else:
        DEBUG = True

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Snakey Party')

    arcadebutton = Button('(a)rcade mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 2/8)
    duelbutton = Button('(d)uel mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 3/8)
    partybutton = Button('(p)arty mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 4/8)
    tronybutton = Button('(t)ron-y mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 5/8)
    sandboxbutton = Button('(s)andbox mode', WINDOWWIDTH / 2, WINDOWHEIGHT * 6/8)
    instructbutton = Button('(i)nstructions', WINDOWWIDTH / 2, WINDOWHEIGHT * 7/8)

    while True: ### need to update this

        DISPLAYSURF.fill(BACKGROUNDCLR)
        drawTitle('Snakey Party', WINDOWWIDTH / 2, WINDOWHEIGHT * 1/8, XLARGETITLE, GREEN, True)
        arcadebutton.display()
        duelbutton.display()
        partybutton.display()
        tronybutton.display()
        sandboxbutton.display()
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
                    players = getPlayers()
                    runGame(game, players)
                    showGameOverScreen()
                elif tronybutton.pressed(mouse):
                    pygame.event.get()
                    game = GameData(25, 12, 0, 0)
                    game.trailing = True
                    runGame(game, [SNAKEY, LINUS, WIGGLES, GOOBER])
                    showGameOverScreen()
                elif sandboxbutton.pressed(mouse):
                    showSandboxScreen()
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
                    players = getPlayers()
                    runGame(game, players)
                    showGameOverScreen()
                elif event.key == K_t:
                    pygame.event.get()
                    game = GameData(25, 12, 0, 0)
                    game.trailing = True
                    runGame(game, [SNAKEY, LINUS, WIGGLES, GOOBER])
                    showGameOverScreen()
                elif event.key == K_s:
                    showSandboxScreen()
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
    pos = 1
    for snake in players:
        if snake == SNAKEY:
            player = Snake(SNAKEY, getStartCoords(pos))
            allsnake.append(player)
            pos = pos + 1
        elif snake == LINUS:
            linus = Opponent(LINUS, getStartCoords(pos), IVORY, DARKGRAY, 5, 20, -10)
            allsnake.append(linus)
            pos = pos + 1
        elif snake == WIGGLES:
            wiggles = Opponent(WIGGLES, getStartCoords(pos), SLATEBLUE, COBALTGREEN, 15, 5, -5, [60, -10, 40, 10, 25, 100, 5])
            allsnake.append(wiggles)
            pos = pos + 1
        elif snake == GOOBER:
            goober = Opponent(GOOBER, getStartCoords(pos), PINK, RED, 10, 10, -15, [30, 5, 60, 30, 35, 100, 100])
            allsnake.append(goober)
            pos = pos + 1

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
            if event.type == KEYDOWN and \
               (event.key == K_ESCAPE or event.key == K_q):
                terminate()
            elif event.type == KEYDOWN and event.key == K_e:
                showGameStats(allsnake)
                return 1
            elif event.type == KEYDOWN and event.key == K_g and DEBUG == True:
                stop = True
                debugPrintGrid(grid)
            # if player is dead / does not exist - check for speed controls
            elif event.type == KEYDOWN and event.key == K_f and \
                 (player == False or player.alive == False):
                game.updateBaseSpeed(10)
                game.updateCurrentSpeed(False, True)
            elif event.type == KEYDOWN and event.key == K_s and \
                 (player == False or player.alive == False):
                game.updateBaseSpeed(-10)
                game.updateCurrentSpeed(False, True)

            # if player exists - check for direction input
            if event.type == KEYDOWN and \
               player != False and stop == False:
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
                        # check for fruit bonus drop
                        if game.checkBonusTrigger():
                            game.runBonusFruit(allfruit, allsnake)
                        # run usual fruid drop
                        game.runDrop(allfruit, allsnake)
                    # blueberries have special speed adjusting properties
                    elif fruit.__class__ == Blueberry:
                        # update game frames to be 'slow' by 7 seconds
                        game.slowtimer = game.slowtimer + game.currentspeed * 7
                    # remove fruit
                    allfruit.remove(fruit)

        # check for snake death, update place and end game if no more snakes are alive
        if game.checkSnakeDeath(allsnake):
            showGameStats(allsnake)
            return 1

        # check for size changes / move snake
        for snake in allsnake:
            snake.move(game.trailing)

        # check multiplier and adjust color and multiplier as needed
        for snake in allsnake:
            if snake.multipliertimer > 0:
                snake.multipliertimer = snake.multipliertimer - 1
                snake.setColorBorderCurrent(PURPLE)
            else:
                # make sure multiplier is 1, color is normal
                snake.multiplier = 1
                snake.resetColorBorder()

        # update timers on fruits, remove if necessary
        for fruit in allfruit:
            if fruit.__class__ != Apple:
                if fruit.updateTimer() == False:
                    # if timer on Egg expires, hatch new snake
                    if fruit.__class__ == Egg:
                        fruit.isHatched(allsnake)
                    allfruit.remove(fruit)
                    
        # draw everything to screen
        game.drawScreen(allfruit, allsnake, player)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE or keyUpEvents[0].key == K_q:
        terminate()
    return keyUpEvents[0].key
    
    
def waitForInput():
    """
    Returns when key pressed or mouse clicked.
    Escapes/Quits as normal.
    """
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    terminate()
                else:
                    return
            elif event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed() != None:
                    return


def getPlayers(num=3):
    """
    Returns list containing Snakey and a number (only argument) of random snakes.
    """
    players = [SNAKEY]

    while num > 0:
        nextPlayer = ''
        randPlayer = random.randint(1,3)
        if randPlayer == 1:
            nextPlayer = LINUS
        elif randPlayer == 2:
            nextPlayer = WIGGLES
        elif randPlayer == 3:
            nextPlayer = GOOBER
        players.append(nextPlayer)
        num = num - 1
        
    return players


def showSelectPlayersScreen():
    """
    Blits player/opponent select onto screen. Returns selection as list.
    """
    playerbuttons = []
    playersnakeybutton = SelectButton('(s)nakey', WINDOWWIDTH / 3, WINDOWHEIGHT * 2/7, SNAKEY, True)
    playerbuttons.append(playersnakeybutton)
    playerlinusbutton = SelectButton('(l)inus', WINDOWWIDTH / 3, WINDOWHEIGHT * 3/7, LINUS)
    playerbuttons.append(playerlinusbutton)
    playerwigglesbutton = SelectButton('(w)iggles', WINDOWWIDTH / 3, WINDOWHEIGHT * 4/7, WIGGLES)
    playerbuttons.append(playerwigglesbutton)
    playergooberbutton = SelectButton('(g)oober', WINDOWWIDTH / 3, WINDOWHEIGHT * 5/7, GOOBER)
    playerbuttons.append(playergooberbutton)
    
    opponentbuttons = []
    opponentlinusbutton = SelectButton('(l)inus', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 3/7, LINUS, True)
    opponentbuttons.append(opponentlinusbutton)
    opponentwigglesbutton = SelectButton('(w)iggles', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 4/7, WIGGLES)
    opponentbuttons.append(opponentwigglesbutton)
    opponentgooberbutton = SelectButton('(g)oober', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 5/7, GOOBER)
    opponentbuttons.append(opponentgooberbutton)
    
    cancelbutton = Button('(e)xit', WINDOWWIDTH / 3, WINDOWHEIGHT * 6/7)
    acceptbutton = Button('(d)uel!', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 6/7)
    
    DISPLAYSURF.fill(BACKGROUNDCLR)

    while True:
        
        drawTitle('Choose Match-up:')
        drawTitle('Player 1:', WINDOWWIDTH / 3, WINDOWHEIGHT * 1/7, MEDIUMTITLE, GOLDENROD, True)
        drawTitle('Player 2:', WINDOWWIDTH / 3 * 2, WINDOWHEIGHT * 1/7, MEDIUMTITLE, GOLDENROD, True)

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
                    for button in playerbuttons:
                        if button.getActive():
                            final.append(button.getValue())
                    for button in opponentbuttons:
                        if button.getActive():
                            final.append(button.getValue())
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
                    opponentgooberbutton.setActive(opponentbuttons)
                elif event.key == K_d:
                    pygame.event.get()
                    final = []
                    for button in playerbuttons:
                        if button.getActive():
                            final.append(button.getValue())
                    for button in opponentbuttons:
                        if button.getActive():
                            final.append(button.getValue())
                    return final
                elif event.key == K_e:
                    pygame.event.get()
                    return False
                elif event.key == K_ESCAPE or event.key == K_q:
                    terminate()

        pygame.display.update()


def showSandboxScreen():
    """
    Blits sandbox mode onto screen.
    """
    
    buttons = []
    snakesbutton = InputButton(1, WINDOWWIDTH * 2/3, WINDOWHEIGHT * 2/8, 1, 4, True)
    buttons.append(snakesbutton)
    fpsbutton = InputButton(12, WINDOWWIDTH * 2/3, WINDOWHEIGHT * 3/8, 3, 60)
    buttons.append(fpsbutton)
    

    cancelbutton = Button('(e)xit', WINDOWWIDTH * 1/3, WINDOWHEIGHT * 7/8)
    acceptbutton = Button('(s)tart', WINDOWWIDTH * 2/3, WINDOWHEIGHT * 7/8)

    while True:
    
        DISPLAYSURF.fill(BACKGROUNDCLR)
        
        drawTitle('Sandbox Mode:')
        drawTitle('Snakes:', WINDOWWIDTH * 1/3, WINDOWHEIGHT * 2/8, MEDIUMTITLE, GOLDENROD, True)
        drawTitle('Starting FPS:', WINDOWWIDTH * 1/3, WINDOWHEIGHT * 3/8, MEDIUMTITLE, GOLDENROD, True)

        # display all buttons
        
        snakesbutton.display()
        fpsbutton.display()
        cancelbutton.display()
        acceptbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                # check buttons
                for button in buttons:
                    button.pressed(mouse, buttons)
                # check cancel/accept buttons
                if cancelbutton.pressed(mouse):
                    pygame.event.get()
                    return False
                elif acceptbutton.pressed(mouse):
                    pygame.event.get()
                    return False

            elif event.type == KEYDOWN:
                if event.key == K_s:
                    pygame.event.get()
                    return False
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
    
    def drawFruit(x, y, color):
        """
        Responsible for drawing demo fruit to screen
        """
        fruitRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, color, fruitRect)
    
    endbutton = Button('(e)xit', WINDOWWIDTH * 3/6, WINDOWHEIGHT * 15/16)
    nextbutton = Button('(n)ext (->)', WINDOWWIDTH * 5/6, WINDOWHEIGHT * 15/16)
    prevbutton = Button('(<-) (p)rev', WINDOWWIDTH * 1/6, WINDOWHEIGHT * 15/16)
    
    page = 1
    
    while True:
    
        DISPLAYSURF.fill(BACKGROUNDCLR)

        drawTitle('Snakey Party', WINDOWWIDTH / 2, WINDOWHEIGHT * 1/16, MEDIUMTITLE, GREEN, True)
        drawTitle('Instructions', WINDOWWIDTH / 2, WINDOWHEIGHT * 3/16, MEDIUMTITLE, GREEN, True)
        
        if page == 1:
            drawMessage('A variation on a classic game, Snakey Party is a', 5, WINDOWHEIGHT * 4/16, GOLDENROD)
            drawMessage('Snakey clone made with Pygame.', 5, WINDOWHEIGHT * 5/16, GOLDENROD)
            drawMessage('Navigating Snakey with the arrow keys, avoid', 5, WINDOWHEIGHT * 6/16, GOLDENROD)
            drawMessage('boundaries and other snakes while enjoying a', 5, WINDOWHEIGHT * 7/16, GOLDENROD)
            drawMessage('buffet of tasty fruits!', 5, WINDOWHEIGHT * 8/16, GOLDENROD)
        elif page == 2:
            drawMessage('Fruits when eaten have different effects.', 5, WINDOWHEIGHT * 4/16, GOLDENROD)
            drawFruit(5, WINDOWHEIGHT * 5/16, RED)
            drawMessage('Apple (10 points) When eaten will generate more', 55, WINDOWHEIGHT * 5/16, RED)
            drawMessage('apples. They may also generate other fruits to appear.', 5, WINDOWHEIGHT * 6/16, RED)
            drawFruit(5, WINDOWHEIGHT * 7/16, GREEN)
            drawMessage('Poison (-25 points) Causes Snakey to shrink.', 55, WINDOWHEIGHT * 7/16, GREEN)
            drawFruit(5, WINDOWHEIGHT * 8/16, ORANGE)
            drawMessage('Orange (50 points) Worth lots of points, and will', 55, WINDOWHEIGHT * 8/16, ORANGE)
            drawMessage('cause Snakey to grow!', 5, WINDOWHEIGHT * 9/16, ORANGE)
            drawFruit(5, WINDOWHEIGHT * 10/16, PURPLE)
            drawMessage('Raspberry  Will cause all fruit to be worth double', 55, WINDOWHEIGHT * 10/16, PURPLE)
            drawMessage('for a short period of time (time stacks).', 5, WINDOWHEIGHT * 11/16, PURPLE)
            drawFruit(5, WINDOWHEIGHT * 12/16, BLUE)
            drawMessage('Blueberry (100 points) Slows everything down for a', 55, WINDOWHEIGHT * 12/16, BLUE)
            drawMessage('short period of time (time stacks).', 5, WINDOWHEIGHT * 13/16, BLUE)
        elif page == 3:
            drawMessage('Modes.', 5, WINDOWHEIGHT * 4/16, GOLDENROD)
        elif page == 4:
            drawMessage('AIs.', 5, WINDOWHEIGHT * 4/16, GOLDENROD)

        endbutton.display()
        if page > 1:
            prevbutton.display()
        if page < 4:
            nextbutton.display()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if endbutton.pressed(mouse):
                    pygame.event.get()
                    return
                elif nextbutton.pressed(mouse):
                    page = page + 1
                elif prevbutton.pressed(mouse):
                    page = page - 1
            elif event.type == KEYDOWN:
                if event.key == K_e or event.key == K_i:
                    pygame.event.get()
                    return
                elif (event.key == K_LEFT or event.key == K_p) and page > 1:
                    page = page - 1
                elif (event.key == K_RIGHT or event.key == K_n) and page < 4:
                    page = page + 1
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
    Displays game stats for all snakes (scored) at end of game.
    Returns when any key pressed.
    """
    totaldead = 0
    totalscored = 0
    for snake in allsnake:
        if snake.scored == True:
            totalscored = totalscored + 1
            if snake.alive == False:
                totaldead = totaldead + 1
    
    position = 1
    for snake in allsnake:
        if snake.scored == True:
            pos_x = getPosition(position, allsnake, totalscored)
            pos_y = WINDOWHEIGHT / 20
            drawMessage(snake.name, pos_x, WINDOWHEIGHT / 20 * 3, snake.getColor())
            if totalscored != 1:
                drawMessage('place: ' + str(snake.getPlace(totaldead, totalscored)), pos_x, pos_y * 5, snake.getColor())
            drawMessage('score: ' + str(snake.score), pos_x, pos_y * 6, snake.getColor())
            drawMessage('apples: ' + str(snake.fruitEaten['apple']), pos_x, pos_y * 7, RED)
            drawMessage('poison: ' + str(snake.fruitEaten['poison']), pos_x, pos_y * 8, GREEN)
            drawMessage('oranges: ' + str(snake.fruitEaten['orange']), pos_x, pos_y * 9, ORANGE)
            drawMessage('raspberries: ' + str(snake.fruitEaten['raspberry']), pos_x, pos_y * 10, PURPLE)
            drawMessage('blueberries: ' + str(snake.fruitEaten['blueberry']), pos_x, pos_y * 11, BLUE)
            drawMessage('eggs: ' + str(snake.fruitEaten['egg']), pos_x, pos_y * 12, WHITE)
            position = position + 1

    drawMessage('Press any key.', WINDOWWIDTH / 2, pos_y * 19, GOLDENROD)
    pygame.display.update()
    pygame.time.wait(300)
    pygame.event.get() # clear event queue
    showGameOverScreen()
    waitForInput()


def showGameOverScreen():
    """
    Displays 'Game Over' message.
    Returns when any key pressed.
    """
    drawTitle('Game Over', WINDOWWIDTH / 2, WINDOWHEIGHT * 3/4, LARGETITLE, WHITE, True)
    pygame.display.update()


def getGrid(allsnake, allfruit):
    """
    Returns dictionary representation of all snakes and fruits on screen.
    Coordinates are entered as tuple (x,y).
    Used by AI when choosing best path.
    """
    # refresh grid, dictionary representation of playing board used by AI
    grid = {(x,y):0 for x in range(CELLWIDTH) for y in range(CELLHEIGHT + (TOP_BUFFER / CELLSIZE))}
    
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
        elif fruit.__class__ == Egg:
            grid[(fruit.coords['x'], fruit.coords['y'])] = 'egg'

    return grid
    
    
def drawMessage(text, x=1, y=1, color=MESSAGECLR, center=False):
    """
    Draws message to screen.
    Size scales depending on window width / height
    Set so that 640x480 -> 18 pts.
        800x600 -> 28 pts.
    """
    size = int (WINDOWWIDTH * WINDOWHEIGHT / 17000)
    font = pygame.font.Font('freesansbold.ttf', size)
    messageSurf = font.render(text, True, color, BACKGROUNDCLR)
    messageRect = messageSurf.get_rect()
    if center == False:
        messageRect.topleft = (x, y)
    else:
        messageRect.center = (x, y)
        
    DISPLAYSURF.blit(messageSurf, messageRect)
    
    
def drawTitle(text, x=1, y=1, size=MEDIUMTITLE, color=GREEN, center=False):
    titleFont = pygame.font.Font('freesansbold.ttf', size)
    titleSurf = titleFont.render(text, True, color, BACKGROUNDCLR)
    titleRect = titleSurf.get_rect()
    if center == False:
        titleRect.topleft = (x, y)
    else:
        titleRect.center = (x, y)

    DISPLAYSURF.blit(titleSurf, titleRect)


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


def getPosition(position, allsnake, totalscored):
    return (WINDOWWIDTH - (float(position) / float(totalscored) * WINDOWWIDTH))
    

def getStartCoords(pos=1):
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

