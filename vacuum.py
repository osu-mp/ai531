#!/us#!/usr/bin/python3

# AI 531 - Vacuum agents
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import random
import unittest

# constants
floorDirty = 'x'                        # environment characters
floorClean = 'o'
floorWall = 'W'

roomSize = 10                           # default room is N x N grid

orientLeft = '<'                        # vacuum orientations
orientRight = '>'
orientUp = '^'
orientDown = 'v'

debug = False                           # set true to print env after every action
"""
TODO
Report:
1   each
2   each
3   Joe
4   Wadood
5   Matthew
6   Wadood & Joe
7   Joe (each too)
"""

"""
The environment is a grid of states:
    x = dirty
    o = clean
    <^>v = agent facing left, up, right, down

Available actions:
-go forward
-turn right 90 degrees
-turn left 90 degrees
-suck dirt
-turn off
"""


class VacuumAgent:
    """
    Parent class for all agents. Maintains an copy of the environment and the position
    of the agent in the environment.

    Each agent should put their specific implementation in 'runAction'
        -This routine is if <condition> fire <action>
        -The if conditionals are based on the three percepts:
            -is cell dirtry/clean
            -is a wall directly in front of agent
            -is the agent in the home cell
        -No memory can be used in the runAction routine (except the memory agent which can use 3 bits)
    """
    def __int__(self, name, env):
        """
        Init shared agent constants
        :param name:
        :param env:
        :return:
        """
        if debug:
            print("Agent: %s" % name)
        self.name = name
        self.env = env
        self.rowPos = roomSize - 1
        self.colPos = 0

        self.cellState = self.env[self.rowPos][self.colPos]  # saves dirty/clean state of cell
        self.orientation = orientRight
        self.env[self.rowPos][self.colPos] = self.orientation

        self.num_clean_cells = 0
        self.num_actions = 0
        self.running = True

    def isHome(self):
        """
        Return True if the agent is in the lower left corner of the env, else False
        :return:
        """
        return self.rowPos == roomSize - 1 and self.colPos == 0

    def print_result(self):
        """
        Print the number of actions run and number of cells cleaned
        :return:
        """
        self.printEnv()
        print(f'{self.num_actions=}, {self.num_clean_cells=}')

    def goForward(self):
        """
        Given the current orientation, move one cell forward
        :return: True if the agent moved forward, False if the agent is blocked
        """
        if self.isWallInFront() > 0:
            print("Wall in front of vacuum, unable to move forward")
            return False

        if debug:
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

        # save the cell state and put the agent in the new position
        self.cellState = self.env[self.rowPos][self.colPos]
        self.env[self.rowPos][self.colPos] = self.orientation

        if debug:
            self.printEnv()

        return True

    def turnRight(self):
        if debug:
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
        if debug:
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
        if debug:
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
        """
        Print the environment (used for debugging)
        :return:
        """
        print("Current Environment:")
        print("Orientation: %s" % self.orientation)
        print(*(' '.join(row) for row in self.env), sep='\n')
        print()

    def runAction(self):
        """
        Run a single action (each agent must implement their own version of this)
        :return:
        """
        raise Exception("This should be implemented by agent")

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
        Return a copy of the current environment
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
        # turn off action needs to be implemented if the agent is at starting location
        # action list for randomly genrating an action if the cell if clean
        actionListCleanCell = ["goForward", "goRight", "goLeft"]

        if self.isWallInFront() > 0:
            randNum = random.randint(0, 100)
            # biased to turn right 85% of the time, left 15%
            if randNum <= 85:
                return self.turnRight()
            else:
                return self.turnLeft()

        #if the no wall in front
        else:
            if self.cellState == floorDirty: 
                return self.suckDirt() 

            # Check which action is genrated randomly and does it    
            if self.cellState == floorClean:
                # biased to move forward 85% of the time, turn right 10%, left 5%
                randNum = random.randint(0, 100)
                if randNum <= 85:
                    return self.goForward()
                if randNum <= 95:
                    return self.turnRight()
                else:
                    return self.turnLeft()


class DeterministicAgentWithMemory(VacuumAgent):
    def __init__(self, env):
        super().__int__("Model-based reflex agent with memory", env)


        self.currState = 0

        """
        states (start facing right)        
        0 go right until you hit a wall; if wall, turn left (facing up)
        1 go forward once 
        2 turn left (facing left)
        3 go forward until wall, if wall go to next
        4 turn right (facing up)
        5 if wall in front, turn right and go to state 0
          if no wall, go forward (once) and go to state 6
        6 turn right (facing down), go to 0
            
        """

    def runAction(self):
        if debug:
            print("CurrentState %d" % self.currState)
        if self.cellState == floorDirty:
            return self.suckDirt()
        # else cell is clean

        if self.isHome():
            #print("HOME, state %d" % self.currState)
            if self.currState != 0:
                return self.turnRight()
            #self.printEnv()


        if self.currState == 0:
            if not self.isWallInFront():
                return self.goForward()
            self.currState = 1
            return self.turnLeft()

        if self.currState == 1:
            self.currState = 2
            if not self.isWallInFront():
                return self.goForward()

        if self.currState == 2:
            self.currState = 3
            return self.turnLeft()

        if self.currState == 3:
            if not self.isWallInFront():
                return self.goForward()
            self.currState = 4
            return self.turnRight()

        if self.currState == 4:
            self.currState = 5
            return self.goForward()

            #self.currState = 0
            #return self.turnRight()

        if self.currState == 5:

            # NOTE: if you return to state 0 (instead of 6) here, the agent can clean
            # 100% of the single room environment. However, by moving to state 6, the
            # agent can clean more of the 4 room case, so it's likely better in a real world env.
            self.currState = 6
            return self.turnRight()

        if self.currState == 6:
            if self.isWallInFront():
                self.currState = 0
                return self.turnLeft()
            self.currState = 7
            return self.turnRight()

        if self.currState == 7:
            self.currState = 0
            return self.turnLeft()

        # should not get here
        raise Exception("Agent should have picked an action before getting here")

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
                else:
                    print

        return (cleanCount, dirtyCount)

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

    def test_nomem_DeterministicAgent_single_room(self):
        env = self.getDirtyGrid()
        agent = ReflexAgent(env)
        clean, dirty = self.getCellStatusCount(env)
        starting_dirty = dirty

        ninety_percent = dirty * .9

        print("AGENT: %s" % agent.name)
        #print("Starting:    CLEAN: %d,  DIRTY %d" % (clean, dirty))

        actionCount = 0
        for i in range(500):
            agent.runAction()
            actionCount += 1

            clean, dirty = self.getCellStatusCount(agent.getEnv())
            if clean == 36 or clean > ninety_percent:
                break

        print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

        if debug:
            agent.printEnv()

        self.assertTrue(clean >= 36)
        print("Cleaned %d of %d cells in %d actions\n" % (clean, starting_dirty, actionCount))

    def test_nomem_DeterministicAgent_4_room(self):
        env = self.get4RoomGrid()
        agent = ReflexAgent(env)
        clean, dirty = self.getCellStatusCount(env)
        starting_dirty = dirty

        ninety_percent = dirty * .9

        print("AGENT: %s" % agent.name)
        # print("Starting:    CLEAN: %d,  DIRTY %d" % (clean, dirty))

        actionCount = 0
        for i in range(500):
            agent.runAction()
            actionCount += 1

            clean, dirty = self.getCellStatusCount(agent.getEnv())
            if clean == 36 or clean > ninety_percent:
                break

        print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

        if debug:
            agent.printEnv()

        self.assertTrue(clean >= 36)
        print("Cleaned %d of %d cells in %d actions\n" % (clean, starting_dirty, actionCount))


    def test_random_Agent(self):
        totalActionCounter = []
        Avg = 0
        for i in range(50):
            clean = 0
            actionCounter = 0
            env = self.getDirtyGrid()
            reflex = RandomReflexAgent(env)
            while clean < 90:
                reflex.runAction()
                clean, dirty = self.getCellStatusCount(env)
                actionCounter = actionCounter + 1

            if debug:
                reflex.printEnv()
                print("CLEAN CELLS: %d " % clean)
            totalActionCounter.append(actionCounter)
        Avg = sum(totalActionCounter) / len(totalActionCounter)
        print(totalActionCounter)
        print("Avg of 50 trials (single room): %d " % Avg)

    def test_random_Agent_4_room(self):
        totalActionCounter = []
        Avg = 0

        env = self.get4RoomGrid()
        clean, dirty = self.getCellStatusCount(env)
        cleanThreshold = dirty * .9                     # 90% of initial cells cleaned

        for i in range(50):
            clean = 0
            actionCounter = 0
            env = self.get4RoomGrid()
            reflex = RandomReflexAgent(env)
            while clean < cleanThreshold:
                reflex.runAction()
                clean, dirty = self.getCellStatusCount(env)
                actionCounter = actionCounter + 1

            if debug:
                reflex.printEnv()
                print("CLEAN CELLS: %d " % clean)
            totalActionCounter.append(actionCounter)
        Avg = sum(totalActionCounter) / len(totalActionCounter)
        print(totalActionCounter)
        print("Avg of 50 trials (4 room): %d" % Avg)

    def test_MemoryAgent(self):
        """
        Analysis for model based deterministic w/ memory agent
        :return:
        """
        env = self.getDirtyGrid()
        agent = DeterministicAgentWithMemory(env)
        clean, dirty = self.getCellStatusCount(env)

        print("AGENT: %s" % agent.name)

        actionCount = 0
        for i in range(1300):
           agent.runAction()
           actionCount += 1

           clean, dirty = self.getCellStatusCount(agent.getEnv())
           # current implementation maxes out at 49 clean cells, break here
           if dirty == 0:
               break

        print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

        if debug:
            agent.printEnv()

        print("Cleaned %d cells in %d actions\n" % (clean, actionCount))

        self.assertTrue(clean == 100, "Only cleaned %d cells" % clean)

    def test_MemoryAgent_4Room(self):
        """
        Analysis for model based deterministic w/ memory agent in 4 room environment
        :return:
        """
        env = self.get4RoomGrid()
        agent = DeterministicAgentWithMemory(env)
        clean, dirty = self.getCellStatusCount(env)
        starting_dirty = dirty

        print("AGENT: %s" % agent.name)
        # print("Starting:    CLEAN: %d,  DIRTY %d" % (clean, dirty))

        actionCount = 0
        for i in range(300):
            agent.runAction()
            actionCount += 1

            clean, dirty = self.getCellStatusCount(agent.getEnv())
            if dirty == 0: # or clean > ninety_percent:
                break

        print("Ending:     CLEAN: %d,  DIRTY %d" % (clean, dirty))

        if debug:
            agent.printEnv()

        print("Cleaned %d of %d cells in %d actions\n" % (clean, starting_dirty, actionCount))

        # self.assertTrue(clean > ninety_percent)


if __name__ == '__main__':
    unittest.main()
