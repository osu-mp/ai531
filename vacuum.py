#!/us#!/usr/bin/python3

# AI 531 - Vacuum agents
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

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

        self.printEnv()

    def suckDirt(self):
        print("Sucking dirt")
        self.cellState = floorClean
        self.printEnv()

    def turnOff(self):
        print("Turning off")
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
        # TODO : implement random logic
        pass

class DeterministicAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Model-based reflex agent", env)

    def runAction(self):
        # TODO : implement deterministic logic
        pass

class TestAgents(unittest.TestCase):

    def getDirtyGrid(self):
        # init environment to 10x10 grid of dirty cells
        return [[floorDirty for x in range(10)] for y in range(10)]


    def test_agent_actions(self):
        # init environment to 10x10 grid of dirty cells
        env = self.getDirtyGrid()

        reflex = ReflexAgent(env)
        reflex.printEnv()

        reflex.suckDirt()               # clean first square
        reflex.goForward()              # move up one and clean
        reflex.suckDirt()
        reflex.turnRight()              # turn around (2 right turns = 180 deg)
        reflex.turnRight()
        reflex.goForward()
        reflex.goForward()              # try to leave board, should stay
        reflex.turnLeft()               # turn left
        reflex.goForward()              # go forward twice, skipping to clean a cell
        reflex.goForward()
        reflex.printEnv()

    def test_relfex_run(self):
        """
        Run X actions for reflex agent
        :return:
        """
        env = self.getDirtyGrid()
        reflex = ReflexAgent(env)
        reflex.runAction()              # suck dirt
        reflex.runAction()              # move forward
        reflex.runAction()              # suck dirt
        reflex.runAction()              # move forward
        reflex.printEnv()



if __name__ == '__main__':
    unittest.main()
