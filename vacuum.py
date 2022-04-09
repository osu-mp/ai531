#!/us#!/usr/bin/python3

# AI 531 - Vacuum agents
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import random
import unittest

# constants
floorDirty = 'x'
floorClean = 'o'

roomSize = 10                                           # room is N x N grid

# vacuum orientation
orientLeft = '<'
orientRight = '>'
orientUp = '^'
orientDown = 'v'

debug = False                                           # set true to print env after every action
"""
TODO
-add wall       Joe
-add counter    Joe
-reflex agent   Joe
-random agent   Wadood
-memory agent   Matthew
"""

"""
The environment is a grid of states:
    x = dirty
    o = clean
    <^>v = agent facing left, up, right, down
"""

"""
Available actions:
-go forward
-turn right 90 degrees
-turn left 90 degrees
-suck dirt
-turn off
"""


class VacuumAgent:
    def __int__(self, name, env):
        print("Agent: %s" % name)
        self.name = name
        self.env = env
        self.rowPos = roomSize - 1
        self.colPos = 0


        self.cellState = self.env[self.rowPos][self.colPos]              # saves dirty/clean state of cell
        self.orientation = orientUp
        self.env[self.rowPos][self.colPos] = self.orientation

    def keepPositionValid(self):
        """
        Ensure the agent stays in the room
        NOTE: hardcoded to 10x10 room
        :return:
        """
        self.rowPos = min(self.rowPos, roomSize)
        self.rowPos = max(self.rowPos, 0)
        self.colPos = min(self.colPos, roomSize)
        self.colPos = max(self.colPos, 0)

    def goForward(self):
        """
        Given the current orientation, move one cell forward
        :return:
        """
        if self.isWallInFront() > 0:
            print("Wall in front of vacuum, unable to move forward")
            return

        print("Moving forward")
        # restore cell in env to previous state (clean or dirty)
        self.env[self.rowPos][self.colPos] = self.cellState

        # do movement
        if self.orientation == orientUp:
            self.rowPos -= 1
        if self.orientation == orientDown:
            self.rowPos += 1
        if self.orientation == orientRight:
            self.colPos += 1
        if self.orientation == orientLeft:
            self.colPos -= 1

        # ensure the agent remains on the board
        self.keepPositionValid()                    # TODO: is this needed anymore?

        # save the cell state and put the agent in the new position
        self.cellState = self.env[self.rowPos][self.colPos]
        self.env[self.rowPos][self.colPos] = self.orientation

        if debug:
            self.printEnv()

    def turnRight(self):
        print("Turning Right")

        # rotate the agent 90 degrees right
        if self.orientation == orientUp:
            self.orientation = orientRight
        elif self.orientation == orientDown:
            self.orientation = orientLeft
        elif self.orientation == orientRight:
            self.orientation = orientDown
        elif self.orientation == orientLeft:
            self.orientation = orientUp

        self.env[self.rowPos][self.colPos] = self.orientation

        if debug:
            self.printEnv()

    def turnLeft(self):
        print("Turning Left")

        # rotate the agent 90 degrees left
        if self.orientation == orientUp:
            self.orientation = orientLeft
        elif self.orientation == orientDown:
            self.orientation = orientRight
        elif self.orientation == orientRight:
            self.orientation = orientUp
        elif self.orientation == orientLeft:
            self.orientation = orientDown

        self.env[self.rowPos][self.colPos] = self.orientation

        if debug:
            self.printEnv()

    def suckDirt(self):
        print("Sucking dirt")
        self.cellState = floorClean
        if debug:
            self.printEnv()

    def turnOff(self):
        print("Turning off")
        if debug:
            self.printEnv()

    def printEnv(self):
        print("Current Environment:")
        print(*(' '.join(row) for row in self.env), sep='\n')
        print()

    def runAction(self):
        """

        :return:
        """
        print("Do something")

    def isWallInFront(self):
        """
        Return 1 if there is a wall directly in front of vacuum, else 0
        :return:
        """
        # if facing left, wall is at colPos of 0
        if self.orientation == orientLeft and self.colPos == 0:
            return 1
        # if facing right, wall is at colPos of 'roomSize'
        if self.orientation == orientRight and self.colPos == roomSize - 1:
            return 1
        # if facing down, wall is at rowPos of roomSize
        if self.orientation == orientDown and self.rowPos == roomSize - 1:
            return 1
        # if facing up, wall is at rowPos of 0
        if self.orientation == orientUp and self.rowPos == 0:
            return 1


        return 0

    def getEnv(self):
        """
        Return the a copy of the current environment
        Replace the vacuum cell with correct clean/dirty status
        :return:
        """
        envCopy = self.env.copy()
        envCopy[self.rowPos][self.colPos] = self.cellState

        return envCopy

class ReflexAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Memory-less deterministic reflex agent", env)

    def runAction(self):
        if self.cellState == floorDirty:
            return self.suckDirt()
        if self.cellState == floorClean:
            return self.goForward()
        # TODO : implement rest of reflex logic

class RandomReflexAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Random reflex agent", env)

    def runAction(self):
        # action list for randomly genrating an action if the cell if dirty
        actionListDirtyCell = ["goForward", "goRight", "goLeft", "suckDirt"]
        # action list for randomly genrating an action if the cell if clean
        actionListCleanCell = ["goForward", "goRight", "goLeft"]

        if self.isWallInFront():
            #need to implement logic for when up against the wall
            return random.choice(actionListDirtyCell) #randomly calls one method/function in the rotation action list

        #if the no wall in front
        else:
            if self.cellState == floorDirty: 
                # randomly genrates an action to do
                actionChoise = random.choice(actionListDirtyCell)
                # Check which action is genrated randomly and does it
                if actionChoise == "goForward":
                    return self.goForward()
                if actionChoise == "goRight":
                    return self.turnRight()
                if actionChoise == "goLeft":
                    return self.turnLeft()
                if actionChoise == "suckDirt":
                    return self.suckDirt()             
            
            # Check which action is genrated randomly and does it(sucking dirt action not available/applicable?)    
            if self.cellState == floorClean:
                actionChoise = random.choice(actionListCleanCell) 
                if actionChoise == "goForward":
                    return self.goForward()
                if actionChoise == "goRight":
                    return self.turnRight()
                if actionChoise == "goLeft":
                    return self.turnLeft()

        # TODO : implement random logic

class DeterministicAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Model-based reflex agent with memory", env)
        self.turnRight()

        # use this var to tell the agent to go as far right as possible
        # then up one and then start moving left until a wall is hit
        # repeat until the top
        self.movingRight = 1        #

        # if we have hit a wall and turned, try to go up one when this equals 1
        self.moveUpOne = 0

    def runAction(self):
        if self.cellState == floorDirty:
            return self.suckDirt()
        if self.cellState == floorClean:
            # if it runs into a wall: go up one cell and turn 180 degrees the other way
            if self.isWallInFront():
                # if going right, turn up (and set var to go up one cell)
                if self.orientation == orientRight and self.movingRight:
                    self.moveUpOne = 1
                    self.movingRight = 0            # stop moving right, go left
                    return self.turnLeft()          # turn facing up
                # if going left, turn up (and set var to go up one cell)
                if self.orientation == orientLeft and self.movingRight == 0:
                    self.moveUpOne = 1
                    self.movingRight = 1            # stop moving left, go right
                    return self.turnRight()

                if self.movingRight == orientUp and self.movingRight:
                    self.movingRight = 0
                    return self.goForward()
            # no wall in front
            else:
                # pointed up and move up enabled, go forward one
                if self.orientation == orientUp and self.moveUpOne:
                    self.moveUpOne = 0
                    return self.goForward()
                # pointed up and move up one disabled, turn left or right
                if self.orientation == orientUp and self.moveUpOne == 0:
                    if self.movingRight:
                        return self.turnRight()
                    else:
                        return self.turnLeft()

            return self.goForward()

class TestAgents(unittest.TestCase):

    def getDirtyGrid(self):
        # init environment to 10x10 grid of dirty cells
        return [[floorDirty for x in range(10)] for y in range(10)]

    def getCellStatusCount(self, env):
        """
        Given an env, return the number of clean and dirty cells
        :param env:
        :return:
        """
        cleanCount = 0
        dirtyCount = 0

        for row in env:
            for val in row:
                if val == floorClean:
                    cleanCount += 1
                elif val == floorDirty:
                    dirtyCount += 1

        return (cleanCount, dirtyCount)

    def get4RoomGrid(self):
        env = '''
x x x x x x x x x x
x x x x | x x x x x
x x x x | x x x x x
x x x x | x x x x x
x | | | | | | | | x
x x x x | x x x x x
x x x x | x x x x x
x x x x | x x x x x
x x x x | x x x x x
x x x x x x x x x x'''

    #def test_agent_actions(self):
    #    # init environment to 10x10 grid of dirty cells
    #    env = self.getDirtyGrid()
    #
    #    reflex = ReflexAgent(env)
    #    reflex.printEnv()

    #    reflex.suckDirt()               # clean first square
    #    reflex.goForward()              # move up one and clean
    #    reflex.suckDirt()
    #    reflex.turnRight()              # turn around (2 right turns = 180 deg)
    #    reflex.turnRight()
    #    reflex.goForward()
    #    reflex.goForward()              # try to leave board, should stay
    #    reflex.turnLeft()               # turn left
    #    reflex.goForward()              # go forward twice, skipping to clean a cell
    #    reflex.goForward()
    #    reflex.printEnv()

    def test_relfex_run(self):
        """
        Run X actions for reflex agent
        :return:
        """
        env = self.getDirtyGrid()
        reflex = RandomReflexAgent(env)
        reflex.runAction()              # suck dirt
        reflex.runAction()              # move forward
        reflex.runAction()              # suck dirt
        reflex.runAction()              # move forward
        reflex.printEnv()


   # def test_DeterministicAgent(self):
        """
        Analysis for model based deterministic w/ memory agent
        :return:
        """
    #    env = self.getDirtyGrid()
    #    agent = DeterministicAgent(env)
    #    clean, dirty = self.getCellStatusCount(env)
    #    print("Starting:    CLEAN: %d,  DIRTY %d" % (clean, dirty))

    #    for i in range(197):
    #        agent.runAction()

    #    clean, dirty = self.getCellStatusCount(env)
    #    print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

    #    agent.printEnv()

        # this agent is currently able to clean 90% of the room in 197 moves
    #    self.assertEqual(90, clean, "Only cleaned: %d" % clean)
    #    print("Memory agent cleaned 90 cells in 197 moves")



if __name__ == '__main__':
    unittest.main()
