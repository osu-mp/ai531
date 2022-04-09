#!/us#!/usr/bin/python3

# AI 531 - Vacuum agents
# Wadood Alam
# Joe Nguyen
# Matthew Pacey
import random
import unittest

# constants
from unittest import TestSuite

floorDirty = 'x'
floorClean = 'o'
floorWall = 'W'

roomSize = 10  # room is N x N grid

# vacuum orientation
orientLeft = '<'
orientRight = '>'
orientUp = '^'
orientDown = 'v'

debug = False  # set true to print env after every action
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

        self.cellState = self.env[self.rowPos][self.colPos]  # saves dirty/clean state of cell
        self.orientation = orientUp
        self.env[self.rowPos][self.colPos] = self.orientation

        self.num_clean_cells = 0
        self.num_actions = 0
        self.running = True

    def isHome(self):
        return self.rowPos == roomSize - 1 and self.colPos == 0

    def print_result(self):
        self.printEnv()
        print(f'{self.num_actions=}, {self.num_clean_cells=}')

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
        self.num_actions += 1
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
        self.keepPositionValid()  # TODO: is this needed anymore?

        # save the cell state and put the agent in the new position
        self.cellState = self.env[self.rowPos][self.colPos]
        self.env[self.rowPos][self.colPos] = self.orientation

        if debug:
            self.printEnv()

    def turnRight(self):
        print("Turning Right")
        self.num_actions += 1
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
        self.num_actions += 1
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
        if self.cellState == floorDirty:
            self.num_clean_cells += 1
        self.cellState = floorClean
        if debug:
            self.printEnv()

    def turnOff(self):
        print("Turning off")
        self.num_actions += 1
        self.running = False
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

    def isBoundaryInFront(self):
        # boundary
        # if facing left, wall is at colPos of 0
        if self.orientation == orientLeft and self.colPos == 0:
            return True
        # if facing right, wall is at colPos of 'roomSize'
        if self.orientation == orientRight and self.colPos == roomSize - 1:
            return True
        # if facing down, wall is at rowPos of roomSize
        if self.orientation == orientDown and self.rowPos == roomSize - 1:
            return True
        # if facing up, wall is at rowPos of 0
        if self.orientation == orientUp and self.rowPos == 0:
            return True
        return False

        # def isAtBoundary(self)

    def isActualWallInFront(self):
        """
        Return 1 if there is a wall directly in front of vacuum, else 0
        :return:
        """

        # wall
        # if facing left, wall is at colPos of 0
        if self.orientation == orientLeft and self.colPos >= 1:
            if self.env[self.rowPos][self.colPos - 1] == floorWall:
                return True

                # if facing right, wall is at colPos of 'roomSize'
        if self.orientation == orientRight and self.colPos < roomSize - 1:
            if self.env[self.rowPos][self.colPos + 1] == floorWall:
                return True

                # if facing down, wall is at rowPos of roomSize
        if self.orientation == orientDown and self.rowPos < roomSize - 1:
            if self.env[self.rowPos + 1][self.colPos] == floorWall:
                return True

                # if facing up, wall is at rowPos of 0
        if self.orientation == orientUp and self.rowPos >= 1:
            if self.env[self.rowPos - 1][self.colPos] == floorWall:
                return True

        return False

    def isWallInFront(self):
        """
        Return 1 if there is a wall directly or the boundary in front of vacuum, else 0
        :return:
        """

        return self.isBoundaryInFront() or self.isActualWallInFront()

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
        assert self.running
        if self.cellState == floorDirty:
            return self.suckDirt()

        # if self.isHome():
        #     return self.turnOff()

        if self.cellState == floorClean:
            if self.isWallInFront():
                return self.turnRight()
            else:
                return self.goForward()

    def run(self, max_loop=100):
        for i in range(max_loop):
            if self.running:
                self.runAction()


class RandomReflexAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Random reflex agent", env)

    def runAction(self):
        # TODO : implement random logic
        pass


class DeterministicAgent(VacuumAgent):
    def __init__(self, env):
        super().__int__("Model-based reflex agent with memory", env)
        self.turnRight()

        # use this var to tell the agent to go as far right as possible
        # then up one and then start moving left until a wall is hit
        # repeat until the top
        self.movingRight = 1  #

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
                    self.movingRight = 0  # stop moving right, go left
                    return self.turnLeft()  # turn facing up
                # if going left, turn up (and set var to go up one cell)
                if self.orientation == orientLeft and self.movingRight == 0:
                    self.moveUpOne = 1
                    self.movingRight = 1  # stop moving left, go right
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

    # def get4RoomGrid(self):
    # assert room_size > 2, "no space left for splitting walls"
    # # split_X = random.choice(list(range(1, room_size)))
    # # split_Y = random.choice(list(range(1, room_size)))
    # X = random.randint(2, room_size - 1)
    # Y = random.randint(2, room_size - 1)
    # env = self.getDirtyGrid(room_size)
    # env[X] = floorWall
    # env[:, Y] = floorWall
    # before_X = random.randint(1, X - 1)
    # before_Y = random.randint(1, Y - 1)
    # after_X = random.randint(X + 1, room_size)
    # after_Y = random.randint(Y + 1, room_size)
    # env[before_X][Y] = floorDirty
    # env[after_X][Y] = floorDirty
    # env[X][before_Y] = floorDirty
    # env[X][after_Y] = floorDirty
    # return env

    def get4RoomGrid(self):
        env = self.getDirtyGrid()
        X = roomSize // 2
        Y = roomSize // 2
        env[X] = [floorWall for i in range(roomSize)]
        for i in range(roomSize):
            env[i][Y] = floorWall
        env[0][Y] = floorDirty
        env[roomSize - 1][Y] = floorDirty
        env[X][0] = floorDirty
        env[X][roomSize - 1] = floorDirty
        return env

    def test_4room(self):
        env = self.get4RoomGrid()
        reflex = ReflexAgent(env)
        reflex.printEnv()

        reflex.suckDirt()  # clean first square

        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.turnRight()
        reflex.suckDirt()
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()

        reflex.print_result()
        # reflex.printEnv()

        # print(env)

    def test_agent_actions(self):
        # init environment to 10x10 grid of dirty cells
        env = self.getDirtyGrid()

        reflex = ReflexAgent(env)
        reflex.printEnv()

        reflex.suckDirt()  # clean first square
        reflex.goForward()  # move up one and clean
        reflex.suckDirt()
        reflex.turnRight()  # turn around (2 right turns = 180 deg)
        reflex.turnRight()
        reflex.goForward()
        reflex.goForward()  # try to leave board, should stay
        reflex.turnLeft()  # turn left
        reflex.goForward()  # go forward twice, skipping to clean a cell
        reflex.goForward()
        reflex.printEnv()

    def test_relfex_run(self):
        """
        Run X actions for reflex agent
        :return:
        """
        env = self.getDirtyGrid()
        reflex = ReflexAgent(env)
        reflex.runAction()  # suck dirt
        reflex.runAction()  # move forward
        reflex.runAction()  # suck dirt
        reflex.runAction()  # move forward
        reflex.printEnv()

    def test_nomem_DeterministicAgent(self):
        env = self.get4RoomGrid()
        agent = ReflexAgent(env)
        agent.run()
        agent.print_result()

    def test_DeterministicAgent(self):
        """
        Analysis for model based deterministic w/ memory agent
        :return:
        """
        env = self.getDirtyGrid()
        agent = DeterministicAgent(env)
        clean, dirty = self.getCellStatusCount(env)
        print("Starting:    CLEAN: %d,  DIRTY %d" % (clean, dirty))

        for i in range(197):
            agent.runAction()

        clean, dirty = self.getCellStatusCount(env)
        print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

        agent.printEnv()

        # this agent is currently able to clean 90% of the room in 197 moves
        self.assertEqual(90, clean, "Only cleaned: %d" % clean)
        print("Memory agent cleaned 90 cells in 197 moves")


if __name__ == '__main__':
    unittest.main()
    # cur_test = TestSuite()
    # cur_test.addTests(TestAgents('test_4room'))
