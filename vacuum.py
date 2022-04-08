#!/us#!/usr/bin/python3

# AI 531 - Vacuum agents
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import unittest

floorDirty = 'x'
floorClean = 'o'

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
        self.rowPos = 9
        self.colPos = 0

        self.cellState = self.env[self.rowPos][self.colPos]              # saves dirty/clean state of cell
        self.orientation = '^'
        self.env[self.rowPos][self.colPos] = self.orientation

    def keepPositionValid(self):
        """
        Ensure the agent stays in the room
        NOTE: hardcoded to 10x10 room
        :return:
        """
        self.rowPos = min(self.rowPos, 9)
        self.rowPow = max(self.rowPos, 0)
        self.colPos = min(self.colPos, 9)
        self.colPow = max(self.colPos, 0)

    def goForward(self):
        """
        Given the current orientation, move one cell forward
        :return:
        """
        print("Moving forward")
        # restore cell in env to previous state (clean or dirty)
        self.env[self.rowPos][self.colPos] = self.cellState

        # do movement
        match self.orientation:
            case '^':
                self.rowPos -= 1
            case 'v':
                self.rowPos += 1
            case '>':
                self.colPos += 1
            case '<':
                self.colPos -= 1

        # ensure the agent remains on the board
        self.keepPositionValid()

        # save the cell state and put the agent in the new position
        self.cellState = self.env[self.rowPos][self.colPos]
        self.env[self.rowPos][self.colPos] = self.orientation

        self.printEnv()

    def turnRight(self):
        print("Turning Right")

        # rotate the agent 90 degrees right
        match self.orientation:
            case '^':
                self.orientation = '>'
            case 'v':
                self.orientation = '<'
            case '>':
                self.orientation = 'v'
            case '<':
                self.orientation = '^'

        self.env[self.rowPos][self.colPos] = self.orientation

        self.printEnv()

    def turnLeft(self):
        print("Turning Left")

        # rotate the agent 90 degrees left
        match self.orientation:
            case '^':
                self.orientation = '<'
            case 'v':
                self.orientation = '>'
            case '>':
                self.orientation = '^'
            case '<':
                self.orientation = 'v'

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
