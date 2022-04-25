#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import copy
import csv
import random
import time
import unittest

from queue import PriorityQueue
from sys import maxsize

"""
Assignment Description
------------------------------------------
In this assignment you will implement and compare A* and RBFS, and experiment with heuristics for 15-puzzle (8-puzzle generalized to 4 X 4 board). Fix the goal configuration to be the one on the right. The problem is to take any initial configuration of the puzzle to the goal configuration with a sequence of moves in the smallest number of steps. It turns out that only half of the problems are solvable for any goal in this domain. For example, the following problem is solvable.

1  5  9  13      1  2  3  4
2  6  10 14  =>  5  6  7  8
3  7  11 15      9  10 11 12 
4  8  12         13 14 15 
Implement and experiment with the following heuristic functions.

CB: City block distance

MY: Any other heuristic (>= CB) that you can come up with that performs better in terms of the number of nodes searched by one or both of the algorithms. This heuristic may or may not be admissible.

To study how the amount of search varies with the problem difficulty, we will generate random solvable problems by perturbing the goal state with a random sequence of moves. Define Scramble(Goal, m) to be the distribution of problems generated by applying a random m-move sequence to the goal state.  Make sure that the successive moves in the random sequence are not reversals of each other (eg. Right followed by Left).

  For m= 10, 20, 30, 40, 50 do  
    For n=10 random problems p generated by Scramble(m) 
       For the two algorithms A
	  For each heuristic function h, 
            Solve p using A and h 
	    Record the length of the solution found, the number of nodes 
	         searched, and the total CPU time spent on evaluating
                 the heuristic and on solving the whole problem. 
For each m, plot the average time consumed, nodes searched, and the optimal solution lengths for the 2 algorithms and the 2 heuristics. You might find that your algorithm is taking too long for some inputs and heuristics. Bound the time and/or the number of nodes searched to a maximum and report what fraction of the problems are solved in that bound. Report the other statistics on the solved problems.
"""

emptySquare = '_'
puzzleSize = 4              # number of rows and cols for puzzle (4 means 4x4 grid with 15 numbers and one emtpy cell)
collectData = True          # set to True to generate test data (long runtime)
csvFilename = 'data.csv'    # where test runtimes are written
debug = False               # prints debug messages when enabled
maxNodesPerSearch = 100000    # max nodes to search before rbfs gives up

moveL = 'L'                 # movement the empty tile can do: left, right, up, down
moveR = 'R'                 # if tile is on an edge, some movements will not be allowed
moveU = 'U'
moveD = 'D'

class Puzzle:

    def __init__(self, tiles=None, parent=None, move=None, cost=0):
        self.tiles = tiles      # state of all tiles (2D array)
        self.parent = parent    # parent node of this puzzle (None=root node)
        self.move = move        # direction the empty tile was moved to get here (from parent)

        if not tiles:           # if board config is not given, start with solved board
            self.tiles = self.getSolvedPuzzle()

        if parent:              # total cost to get here is parent + node cost (1)
            self.cost = parent.cost + cost
        else:
            self.cost = cost

        self.evalFunc = self.cost   # estimate value (updated by search funcs)

        if debug:
            print('New node: move=%s, cost=%s' % (self.move, self.cost))

    def getSolvedPuzzle(self):
        """
        Build and return an ordered grid of puzzleSize x puzzleSize (last cell is empty)
        For a 4x4 grid, it should look like:
        [1,   2,  3,  4],
        [5,   6,  7,  8],
        [9,  10, 11, 12],
        [13, 14, 15, emptySquare]
        :return:
        """
        puzzle = []
        for row in range(puzzleSize):
            line = []
            for col in range(puzzleSize):
                line.append(row * puzzleSize + col + 1)         # add 1 to start tiles at 1 instead of 0
            puzzle.append(line)

        # set the last squaue to blank
        puzzle[puzzleSize - 1][puzzleSize - 1] = emptySquare
        return puzzle

    def isPuzzleSolved(self):
        return self.tiles == self.getSolvedPuzzle()

    def scramblePuzzle(self, m):
        """
        Scramble the current puzzle by moving m random tiles
        :param m: Number of moves to scramble puzzle
        :return: Nothing (self.tiles is now scrambled)
        """
        moves = []
        lastMove = None                                     # do not repeat the same move (both moves can

        for i in range(m):
            # get possible move directions
            possibleMoves = self.getEmptyMoves()

            # ensure the next move is not the opposite of the last (would undo previous move)
            if lastMove:                                    # does not apply to first iteration since there is no prev
                reverse = self.getReverseMove(lastMove)
                possibleMoves.remove(reverse)

            # pick a random move from those
            nextMove = random.choice(possibleMoves)

            # move the empty square and add to move list, save last state for next iteration
            self.moveEmpty(nextMove)
            moves.append(nextMove)
            lastMove = nextMove

        if debug:
            print('Scrambled %d moves: %s' % (len(moves), ', '.join(moves)))
        return moves

    def getReverseMove(self, move):
        """
        Given a move, return the oppostive. This is used to prevent the random scramble
        from undoing a previous action.
        :param move:
        :return:
        """
        if move == moveU:           # opposite of up is down
            return moveD
        elif move == moveD:
            return moveU
        elif move == moveL:         # left and right are opposites
            return moveR
        elif move == moveR:
            return moveL

    def print(self):
        """
        Print the current configuration
        :return:
        """
        str = ""
        for row in self.tiles:
            for col in row:
                if col == emptySquare:
                    str += "   "
                else:
                    str += "%2d " % col
            str += "\n"
        print(str)

    def getPosition(self, target):
        """
        Return the row and col of the target number (or empty cell)
        :param target:
        :return:
        """
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                if self.tiles[row][col] == target:
                    return(row, col)

    def getEmptyPosition(self):
        """
        Return the row and col where the empty square is
        :return:
        """
        return self.getPosition(emptySquare)

    def getNeighbors(self, target):
        """
        Return neighbors of the given target (numbers that it can swap with)
        :param target:
        :return:
        """
        row, col = self.getPosition(target)

        neighbors = []
        # up
        if row > 0:
            neighbors.append(self.tiles[row - 1][col])
        # left
        if col > 0:
            neighbors.append(self.tiles[row][col - 1])
        # right
        if col < puzzleSize - 1:
            neighbors.append(self.tiles[row][col + 1])
        # down
        if row < puzzleSize - 1:
            neighbors.append(self.tiles[row + 1][col])

        return neighbors

    def getEmptyMoves(self):
        """
        Return the legal positions that the empty tile can move
        :return:
        """
        row, col = self.getEmptyPosition()

        moves = []
        if row > 0:                     # up
            moves.append(moveU)
        if col > 0:                     # left
            moves.append(moveL)
        if col < puzzleSize - 1:        # right
            moves.append(moveR)
        if row < puzzleSize - 1:        # down
            moves.append(moveD)

        return moves

    def moveEmpty(self, move):
        """
        Move the empty square up, left, right, or down (swap values with numbered tile)
        :param move:
        :return:
        """
        row, col = self.getEmptyPosition()

        # replace the numbered tile in place of the empty
        if move == moveU:               # up
            self.tiles[row][col] = self.tiles[row - 1][col]
            row -= 1
        elif move == moveL:             # left
            self.tiles[row][col] = self.tiles[row][col - 1]
            col -= 1
        elif move == moveR:             # right
            self.tiles[row][col] = self.tiles[row][col + 1]
            col += 1
        elif move == moveD:             # down
            self.tiles[row][col] = self.tiles[row + 1][col]
            row += 1

        # put the empty square where the numbered tile previously was
        self.tiles[row][col] = emptySquare

    def moveToEmptyCell(self, target):
        """
        Move the given number into the empty cell
        :param target:
        :return: True if moved, Exception if blocked
        """
        neighbors = self.getNeighbors(target)
        if emptySquare not in neighbors:
            raise Exception("Target number %d is not adjacent to empty cell, cannot move" % target)

        # if they are neighbors, swap the positions
        tarRow, tarCol = self.getPosition(target)       # position of target number that is moving
        empRow, empCol = self.getEmptyPosition()        # position of empty cell

        self.tiles[tarRow][tarCol] = emptySquare
        self.tiles[empRow][empCol] = target

        return True


    def generateChildren(self):
        """
        Generate valid children tile configurations given the current tiles
        One child node for each direction the empty square can move
        :return:
        """
        children = []

        moves = self.getEmptyMoves()
        for move in moves:
            # copy tiles into new child node
            tiles = copy.deepcopy(self.tiles)
            child = Puzzle(tiles, self, move, 1)
            # move the empty square in the child node
            child.moveEmpty(move)
            children.append(child)

        return children

    def printSolution(self):
        """
        Print the moves to get here from initial setup (reverse the parent moves)
        :return:
        """
        moves = []
        moves.append(self.move)       # TODO: is this needed at root?
        path = self
        while path.parent != None:
            path = path.parent
            moves.append(path.move)
        moves = moves[:-1]
        moves.reverse()

        moveStr = ", ".join(moves)
        # TODO include length
        print("Solution: %s" % moveStr)

    def getPuzzleId(self, puzzle):
        """
        Calculate a unique id for the given puzzle. This is needed for the rbfs prioirity queue
        if two nodes have the same fValue.
        This routine multiplies every existing tile against the expected tile in the solved puzzle.
        As long as two puzzles are different, this number should be different.
        :param puzzle:
        :return:
        """
        sum = 0
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                # expected tile position (+1 because arrays start at 0, tiles start at 1)
                expectedTile = row * puzzleSize + col + 1
                actualTile = puzzle[row][col]
                if actualTile == emptySquare:           # ignore empty square
                    continue
                sum += expectedTile * actualTile

        return sum

def heuristicCityBlock(puzzle):
    """
    City block heuristic: estimate number of moves for each tile to intended location
    This is admissible since it never over-estimates the number of moves
    :return:
    """
    # for each tile, count the number of moves to its intended position (assume no other tiles)
    sum = 0

    for row in range(puzzleSize):
        for col in range(puzzleSize):
            # expected tile position (+1 because arrays start at 0, tiles start at 1)
            expectedTile = row * puzzleSize + col + 1

            # the last spot in the board is reserved for empty space, ignore for this heuristic
            if expectedTile == (puzzleSize * puzzleSize):
                continue

            # get location of expected tile and calculate distance (absolute in case it moves up/left)
            actRow, actCol = puzzle.getPosition(expectedTile)
            dist = abs(actRow - row) + abs(actCol - col)
            # if debug:
            #     print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')

            sum += dist

    return sum

def heuristicMy(puzzle):
    """
    Heuristic defined by us
    Use the city block estimate plus the distance to the empty square
    This is not admissible since it may over-estimate the number of moves
    -i.e. if the give tile is one move away from its intended location and the emtpy square
    is there, it only needs to move once (but this algo returns 2 for that tile)
    :return:
    """
    sum = 0
    (emptyRow, emptyCol) = puzzle.getEmptyPosition()

    for row in range(puzzleSize):
        for col in range(puzzleSize):
            # expected tile position (+1 because arrays start at 0, tiles start at 1)
            expectedTile = row * puzzleSize + col + 1

            # the last spot in the board is reserved for empty space, ignore for this heuristic
            if expectedTile == (puzzleSize * puzzleSize):
                continue

            # get location of expected tile and calculate distance (absolute in case it moves up/left)
            actRow, actCol = puzzle.getPosition(expectedTile)
            dist = abs(actRow - row) + abs(actCol - col)
            if debug:
                print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')

            # if at correct spot, do not consider moving empty tile
            if dist == 0:
                continue

            # otherwise add distance to empty tile (this makes the algo not admissible)
            emptyDist = abs(actRow - emptyRow) + abs(actCol - emptyCol)
            if debug:
                print('myHeuristic moves from emtpy: %d' % emptyDist)
            sum += dist + emptyDist

    return sum

def aStar(tiles, whichHeuristic):
    """
    A* search
    :return: Number of nodes checked
    """

    global  count
    count = 0
    node = None 
    expanded = []
    Q = PriorityQueue()
    # get parent node
    parentNode = Puzzle(tiles, None, None, 0)
    # Get huristic value in var 'estimate'
    estimate = whichHeuristic(parentNode)
    # put the parent node, node count, and heuristic value in the queue
    Q.put((estimate, count, parentNode))
    
    while not Q.empty():
        (nodeEstimate, nodeCount, node) = Q.get()

        # append the expanded list with the state of the variable 'node'. Unbale to do so, idk why?
        expanded.append(node.tiles)
        if node.isPuzzleSolved():
            return node, None, count
        children = node.generateChildren()

        for child in children:
            if child.tiles not in expanded:
                count += 1
                # get new F value
                estimate = child.cost + whichHeuristic(child)
                Q.put((estimate, count, child))

   
    return (node, fLimit, nodesChecked)

nodesChecked = 0                                # global var to keep track of nodes checked (both searches should reset at start)

def rbfs(tiles, whichHeuristic):
    global nodesChecked

    nodesChecked = 0

    puzzle = Puzzle(tiles, None, None, 0)

    try:
        (node, fLimit) = rbfsMain(puzzle, maxsize, whichHeuristic)
    except Exception:
        node = None

    if node:
        node.printSolution()
        return (node, fLimit, nodesChecked)
    else:
        print("No solution found")
        return (None, maxsize, nodesChecked)

def rbfsMain(node, fLimit, whichHeuristic):
    global nodesChecked
    successors = []
    # result = None

    if node.isPuzzleSolved():
        return node, None

    nodesChecked += 1
    if nodesChecked > maxNodesPerSearch:
        print('Max nodes exceeded, terminating search. Nodes checked: %d' % nodesChecked)
        raise Exception('node limit exceeded')

    children = node.generateChildren()
    if len(children) == 0:
        return None, maxsize

    childPos = 0        # used to differentiate between nodes with the same f value

    for child in children:
        childPos += 1
        estimate = child.cost + whichHeuristic(child)
        successors.append((estimate, childPos, child))
        child.evalFunc = estimate

        if debug:
            print("\t%s estimate = %d, cost = %d" % (child.move, estimate, child.cost))
            child.print()

    while len(successors) > 0:
        successors.sort()
        (bestF, bestPos, bestNode) = successors[0]
        if bestNode.evalFunc > fLimit:
            return None, bestNode.evalFunc

        (altF, altPos, altNode) = successors[1]
        minF = min(fLimit, altF)

        (result, bestNode.evalFunc) = rbfsMain(bestNode, minF, whichHeuristic)
        successors[0] = (bestNode.evalFunc, bestPos, bestNode)

        if result != None:
            break

    return result, None

class TestPuzzle(unittest.TestCase):

    def test_scramble(self):
        puzzle = Puzzle()
        solved = puzzle.getSolvedPuzzle()
        puzzle.scramblePuzzle(10)
        self.assertNotEqual(solved, puzzle.tiles)
        puzzle.print()

    def test_getPosition(self):
        """
        Tests for getPosition
        :return:
        """
        puzzle = Puzzle()
        target = 1
        exp = (0, 0)
        self.assertEqual(exp, puzzle.getPosition(target))

    def test_getEmptyPosition(self):
        """
        Test the get empty position function.
        For a solved puzzle, it should be in the final cell (row = puzzleSize - 1, col = puzzleSize - 1)
        FOr a 4x4 grid, this will be in position 3,3
        :return:
        """
        puzzle = Puzzle()
        row, col = puzzle.getEmptyPosition()
        self.assertEqual(3, row)
        self.assertEqual(3, col)

    def test_getNeighbors(self):
        """
        Test the getNeighbors function in various positions.
        Use the solved puzzle (below) as a reference
        1  2  3  4
        5  6  7  8
        9  10 11 12
        13 14 15 _
        :return:
        """
        puzzle = Puzzle()

        # top left (only 2 neighbors)
        target = 1
        exp = [2, 5]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # top right (only 2 neighbors)
        target = 4
        exp = [3, 8]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # middle number (4 neighbors)
        target = 7
        exp = [3, 6, 8, 11]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # bottom left (2 neighbors)
        target = 13
        exp = [9, 14]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # middle bottom (3 neighbors)
        target = 14
        exp = [10, 13, 15]
        self.assertEqual(exp, puzzle.getNeighbors(target))

        # bottom left (2 neighbors)
        target = emptySquare
        exp = [12, 15]
        self.assertEqual(exp, puzzle.getNeighbors(target))

    def test_moveToEmptyCell(self):
        """
        Verify the move command works as expected. Start with solved puzzle:
        1  2  3  4
        5  6  7  8
        9  10 11 12
        13 14 15 _
        :return:
        """
        puzzle = Puzzle()

        # try to move number 1 (it is not adjacent to empty cell so exception expected)
        self.assertRaises(Exception, puzzle.moveToEmptyCell, 1)

        # move 12 to empty cell (adjacent so valid)
        puzzle.moveToEmptyCell(12)
        """ Current configuration
        1  2  3  4
        5  6  7  8
        9  10 11 _
        13 14 15 12        
        """

        puzzle.moveToEmptyCell(11)
        """ Current configuration
        1  2  3  4
        5  6  7  8
        9  10 _  11
        13 14 15 12        
        """

        puzzle.moveToEmptyCell(7)
        """ Current configuration
        1  2  3  4
        5  6  _  8
        9  10 7  11
        13 14 15 12        
        """
        expected = [
            [1,   2, 3,           4],
            [5,   6, emptySquare, 8],
            [9,  10, 7,          11],
            [13, 14, 15,         12]
        ]
        self.assertEqual(puzzle.tiles, expected)

    def runTest(self, tiles, searchFunc, heuristic):
        """
        Run the specified search function using given heuristic and return runtime in seconds
        :param puzzle:
        :param searchFunc:
        :param heuristic:
        :return:
        """
        start = time.time()                             # get start time
        (node, fLimit, nodesChecked) = searchFunc(tiles, heuristic)            # run the search function with selected heuristic
        end = time.time()                               # record runtime

        moves = node.cost
        return (nodesChecked, moves, end - start)              # return number of nodes checked and runtime

    def test_data_collection(self):
        """
        Try all combinations of searches and collect performance data into a csv
        :return:
        """
        # TODO : this has not been updated to new methods (4/23)
        # TODO : Matthew update after search functions complete
        if not collectData:
            self.skipTest("Data collection skipped")

        # TODO save to csv
        csvFH = open(csvFilename, 'w', newline='')
        writer = csv.writer(csvFH)
        writer.writerow(['m', 'puzzleNum', 'searchFunc', 'heuristic', 'moves', 'nodesChecked', 'runTime (seconds)'])

        # collect data into run data and write it later
        runData = {}
        for algo in ['astar', 'rbfs']:
            runData[algo] = {}
            for heuristic in ['cityBlock', 'myHeuristic']:
                runData[algo][heuristic] = {}

        puzzle = Puzzle()
        for m in [10, 20, 30, 40, 50]:                      # run for increasing number of moves from solved puzzle

            runData['astar']['cityBlock'][m] = []
            runData['astar']['myHeuristic'][m] = []
            runData['rbfs']['cityBlock'][m] = []
            runData['rbfs']['myHeuristic'][m] = []

            for n in range(10):                             # TODO : run 10 trials at each m
                base = Puzzle()
                base.scramblePuzzle(m)         # ensure all 4 configurations use the same scrambled puzzle
                baseTiles = base.tiles
                print('Puzzle Number %d (m=%d)' % (n, m))
                base.print()

                # # astar with city block heuristic
                (nodesChecked, moves, runTime) = self.runTest(baseTiles, aStar, heuristicCityBlock)
                runData['astar']['cityBlock'][m].append([moves, nodesChecked, runTime])
                print('aStar w/ cityBlock: moves=%3d, nodes=%5d, time=%1.6f' % (moves, nodesChecked, runTime))

                # astar with my heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, aStar, heuristicMy)
                # runData['astar']['myHeuristic'][m].append([moves, nodesChecked, runTime])
                # print('aStar w/ myHeur:    moves=%3d, nodes=%5d, time=%1.6f' % (moves, nodesChecked, runTime))

                # rbfs with city block heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, rbfs, heuristicCityBlock)
                # runData['rbfs']['cityBlock'][m].append([moves, nodesChecked, runTime])
                # print('rbfs  w/ cityBlock: moves=%3d, nodes=%5d, time=%f' % (moves, nodesChecked, runTime))

                # rbfs with my heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, rbfs, heuristicMy)
                # runData['rbfs']['myHeuristic'][m].append([moves, nodesChecked, runTime])
                # print('rbfs  w/ myHeur:    moves=%3d, nodes=%5d, time=%f' % (moves, nodesChecked, runTime))

        # now that all data has been collected, write it grouped by algo/heuristic
        for algo in runData:
            for heuristic in runData[algo]:
                for mValue in runData[algo][heuristic]:
                    for puzzleNum, trial in enumerate(runData[algo][heuristic][m]):
                        (moves, nodesChecked, runTime) = trial
                        writer.writerow([mValue, puzzleNum, algo, heuristic, moves, nodesChecked, runTime])
        print('Data collection complete, results written to: %s' % csvFilename)

    def test_rbfs(self):
        """
        Functional tests for rbfs search algo
        :return:
        """
        # base case: already solved puzzle (0 moves)
        puzzle = Puzzle()
        (node, fLimit, nodesChecked) = rbfs(puzzle.tiles, heuristicCityBlock)
        print('node %s' % node)
        self.assertEqual(0, node.cost)

        # simple case: puzzle off by one move
        puzzle = Puzzle()
        puzzle.moveToEmptyCell(15)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked) = rbfs(puzzle.tiles, heuristicCityBlock)
        self.assertIsNotNone(node, "failed to solve puzzle")
        self.assertEqual(1, node.cost)

        # simple case: puzzle off by 2 moves
        puzzle = Puzzle()
        puzzle.moveToEmptyCell(15)
        puzzle.moveToEmptyCell(11)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked) = rbfs(puzzle.tiles, heuristicCityBlock)
        self.assertEqual(2, node.cost)

        # use puzzle scrambled by m moves
    # def test_rbfs_m_values(self):
        m = 30
        puzzle = Puzzle()
        puzzle.scramblePuzzle(m)
        # puzzle.moveToEmptyCell(15)
        # puzzle.moveToEmptyCell(11)
        # puzzle.moveToEmptyCell(10)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked) = rbfs(puzzle.tiles, heuristicCityBlock)
        self.assertIsNotNone(node, "Failed to find solution")
        self.assertTrue(node.cost <= m, 'Solution took move moves than scramble')
        print('Nodes checked: %d' % nodesChecked)


    def test_astar(self):
        """
        Functional tests for Sstar search algo
        :return:
        """
        # base case: already solved puzzle (0 moves)
        puzzle = Puzzle()
        (node, fLimit, count) = aStar(puzzle.tiles, heuristicCityBlock)
        print('node %s' % node)
        self.assertEqual(0, node.cost)

        # simple case: puzzle off by one move
        puzzle = Puzzle()
        puzzle.moveToEmptyCell(15)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count) = aStar(puzzle.tiles, heuristicCityBlock)
        if node:
            print('Solved with cost %d' % node.cost)
        self.assertEqual(1, node.cost)

        # simple case: puzzle off by 2 moves
        puzzle = Puzzle()
        puzzle.moveToEmptyCell(15)
        puzzle.moveToEmptyCell(11)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count) = aStar(puzzle.tiles, heuristicCityBlock)
        if node:
            print('Solved with cost %d' % node.cost)
        self.assertEqual(2, node.cost)

    def test_cityBlock(self):
        """
        Unit tests for city block heuristic
        :return:
        """
        puzzle = Puzzle()

        # base case: solved puzzle, city block should return 0
        self.assertEqual(0, heuristicCityBlock(puzzle))

        scrambled = [
            [4,   1, 3,           2],
            [5,   6, emptySquare, 8],
            [10,  9, 7,          11],
            [15, 14, 13,         12]
        ]

        puzzle.tiles = scrambled

        # using above puzzle, expected city block is (tiles 1 through 15 distances added):
        # e.g. tile 1 is 1 spot away, tile 2 is 2, tile 3 is where it belongs, etc
        expected = 1 + 2 + 0 + 3 + 0 + 0 + 1 + 0 + 1 + 1 + 1 + 1 + 2 + 0 + 2
        # tiles    1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
        self.assertEqual(expected, heuristicCityBlock(puzzle))

    def test_myHeuristic(self):
        """
        Unit tests for my heuristic
        :return:
        """
        puzzle = Puzzle()

        # base case: solved puzzle, city block should return 0
        self.assertEqual(0, heuristicCityBlock(puzzle))

        scrambled = [
            [4,   1, 3,           2],
            [5,   6, emptySquare, 8],
            [10,  9, 7,          11],
            [15, 14, 13,         12]
        ]

        puzzle.tiles = scrambled

        # using above puzzle, expected my heuristic is (tiles 1 through 15 distances added):
        # e.g. tile 1 is 1 spot away from target and 2 away from emtpy,
        # tile 2 is 2 away from target and 2 from empty,
        # tile 3 is where it belongs, etc
        expected =  (1 + 2) + (2 + 2) + 0 + (3 + 3) + 0 + 0 + (1 + 1) + 0
        # tile       1         2        3    4        5   6    7        8
        expected += (1 + 2) + (1 + 3) + (1 + 2) + (1 + 3) + (2 + 2) + 0 + (2 + 4)
        #            9         10        11       12        13        14   15
        self.assertEqual(expected, heuristicMy(puzzle))


if __name__ == '__main__':
    unittest.main()

