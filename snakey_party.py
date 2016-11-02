#!/usr/bin/env python
# A Snakey clone made with Pygame.
# Requires Pygame: http://pygame.org/download.shtml
# Includes various fruits with different effects in regards to score,
# snake size, and other in-game effects.
# Includes various Snake AIs and game modes (Arcade, Duel, Party).

import classes.hue
import copy
import pygame
import random
import sys

from pygame.locals import *
from classes.const import *
from classes.methods import *
from classes.button import *
from classes.snake import *
from classes.fruit import *
from classes.gamedata import *
from classes.game import Game


def main():
    #global FPSCLOCK, DISPLAYSURF, DEBUG
    classes.hue.activate()

    #pygame.init()
    #FPSCLOCK = pygame.time.Clock()
    #DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Snakey Party')
    col_header = WINDOWWIDTH * 1/2
    col_one = WINDOWWIDTH * 1/3
    col_two = WINDOWWIDTH * 2/3
    row_header = WINDOWHEIGHT * 1/8
    row_one = WINDOWHEIGHT * 3/8
    row_two = WINDOWHEIGHT * 4/8
    row_three = WINDOWHEIGHT * 5/8
    row_four = WINDOWHEIGHT * 6/8
    row_five = WINDOWHEIGHT * 7/8
    buttonlist = []

    # Set-up hue.
    light = classes.hue.get_light(classes.hue.LIGHT_ONE)

    # classic mode
    cbutton = Button('(c)lassic mode', (col_one, row_one), K_c)
    cbutton.game = Game(light=light)
    buttonlist.append(cbutton)
    # arcade mode
    abutton = Button('(a)rcade mode', (col_one, row_two), K_a)
    abutton.game = Game(apples=20, light=light)
    buttonlist.append(abutton)
    # duel mode
    dbutton = DuelButton('(d)uel mode', (col_one, row_three), K_d)
    dbutton.game = Game(apples=2, eggDrop=12, speedTrigger=10, easyTrigger=9, light=light)
    buttonlist.append(dbutton)
    # fast duel mode
    fbutton = DuelButton('(f)ast duel', (col_one, row_four), K_f)
    fbutton.game = Game(apples=2, speedTrigger=10, easyTrigger=19, basespeed=20, bonusFruitTrigger=7, eggDrop=10, orangeDrop=4, light=light)
    buttonlist.append(fbutton)
    # party mode
    pbutton = PartyButton('(p)arty mode', (col_one, row_five), K_p)
    pbutton.game = Game(apples=4, speedTrigger=25, easyTrigger=0, bonusFruitTrigger=12, light=light)
    buttonlist.append(pbutton)
    # tron mode
    tbutton = PartyButton('(t)ron mode', (col_two, row_one), K_t, light=light)
    tbutton.game = Game(trailing=True)
    buttonlist.append(tbutton)
    # TBD
    # (col_two, row_two)
    #
    # sandbox mode
    sbutton = SandboxButton('(s)andbox mode', (col_two, row_three), K_s)
    buttonlist.append(sbutton)
    # instructions
    ibutton = InstructButton('(i)nstructions', (col_two, row_four), K_i)
    buttonlist.append(ibutton)

    
    while True:
        DISPLAYSURF.fill(BACKGROUNDCOLOR)
        drawTitle('Snakey Party', col_header, row_header, XLARGETITLE, GREEN, True)
        for button in buttonlist:
            button.display()
            
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif (event.type == KEYDOWN and event.key == K_ESCAPE):
                terminate()
            for button in buttonlist:
                if (event.type == MOUSEBUTTONDOWN and button.pressed(pygame.mouse.get_pos())) or \
                    (event.type == KEYDOWN and button.keypressed(event.key)):
                    if button.game:
                        game = copy.copy(button.game)
                        # get players involved
                        if hasattr(button, 'getplayers'):
                            players = button.getplayers()
                        else:
                            players = [SNAKEY]
                        rungame(game, players)
                        showGameOverScreen()
                    elif hasattr(button, 'getgame'):
                        game, players = button.getgame()
                        rungame(game, players)
                        showGameOverScreen()
                    elif hasattr(button, 'showinstruct'):
                        button.showinstruct()
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def rungame(game, players=[]):

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
                game.changeHue(PURPLE)
            else:
                # make sure multiplier is 1, color is normal
                snake.multiplier = 1
                snake.resetColorBorder()
                game.changeHue(IVORY)

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


if __name__ == '__main__':
    main()
