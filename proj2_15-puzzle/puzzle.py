#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import copy
import random
import time
from queue import PriorityQueue
from sys import maxsize
from typing import Dict

# heuristicTime = 0
import main

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
puzzleSize = 4  # number of rows and cols for puzzle (4 means 4x4 grid with 15 numbers and one emtpy cell)
collectData = True  # set to True to generate test data (long runtime)
csvFilename = 'data.csv'  # where test runtimes are written
debug = False  # prints debug messages when enabled
maxNodesPerSearch = 50000  # max nodes to search before rbfs gives up

moveL = 'L'  # movement the empty tile can do: left, right, up, down
moveR = 'R'  # if tile is on an edge, some movements will not be allowed
moveU = 'U'
moveD = 'D'


class Puzzle:
    totalNodes = 0  # global counter of total nodes in total tree

    def __init__(self, tiles=None, parent=None, move=None, cost=0):
        self.tiles = tiles  # state of all tiles (2D array)
        self.parent = parent  # parent node of this puzzle (None=root node)
        self.move = move  # direction the empty tile was moved to get here (from parent)

        if not tiles:  # if board config is not given, start with solved board
            self.tiles = self.getSolvedPuzzle()

        if parent:  # total cost to get here is parent + node cost (1)
            self.cost = parent.cost + cost
        else:
            self.cost = cost

        self.evalFunc = self.cost  # estimate value (updated by search funcs)

        if debug:
            print('New node: move=%s, cost=%s' % (self.move, self.cost))

        if tiles is None:
            # self.size = puzzleSize
            self.tiles = self.getSolvedPuzzle()
        else:
            # self.size = len(self.tiles)
            assert all(len(e) == len(self.tiles) for e in self.tiles)

        self.evalFunc = self.cost  #
        Puzzle.totalNodes += 1
        self.target_pos = self.generateTargetPosition()

    def generateTargetPosition(self) -> Dict[int, tuple]:
        target = self.getSolvedPuzzle()
        target_pos = {}
        for i in range(puzzleSize):
            for j in range(puzzleSize):
                target_val = target[i][j]
                target_pos[target_val] = (i, j)
        return target_pos

    def getTargetPosition(self, val) -> tuple:
        return self.target_pos[val]

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
                line.append(row * puzzleSize + col + 1)  # add 1 to start tiles at 1 instead of 0
            puzzle.append(line)

        # set the last square to blank
        puzzle[puzzleSize - 1][puzzleSize - 1] = emptySquare
        return puzzle

    def isPuzzleSolved(self):
        """
        Return True if the tiles are in the goal state, else False
        :return:
        """
        return self.tiles == self.getSolvedPuzzle()

    def scramblePuzzle(self, m):
        """
        Scramble the current puzzle by moving the empty square m times
        If the puzzle starts in the goal state, this will result in a solvable puzzle (all moves will be legal)
        :param m: Number of moves to scramble puzzle
        :return: Nothing (self.tiles is now scrambled)
        """
        moves = []
        lastMove = None  # do not repeat the same move (both moves can

        for i in range(m):
            # get possible move directions
            possibleMoves = self.getEmptyMoves()

            # ensure the next move is not the opposite of the last (would undo previous move)
            if lastMove:  # does not apply to first iteration since there is no prev
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
        Given a move, return the opposite. This is used to prevent the random scramble
        from undoing a previous action.
        :param move:
        :return:
        """
        if move == moveU:  # opposite of up is down
            return moveD
        elif move == moveD:
            return moveU
        elif move == moveL:  # left and right are opposites
            return moveR
        elif move == moveR:
            return moveL

    def print(self):
        """
        Print the current configuration (for debug)
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
        return str

    #
    def __str__(self):
        return self.print()

    def getPosition(self, target):
        """
        Return the row and col of the target number (or empty cell)
        :param target:
        :return:
        """
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                if self.tiles[row][col] == target:
                    return (row, col)

    def getEmptyPosition(self):
        """
        Return the row and col where the empty square is
        :return:
        """
        return self.getPosition(emptySquare)

    def getEmptyMoves(self):
        """
        Return the legal positions that the empty tile can move
        :return:
        """
        row, col = self.getEmptyPosition()

        moves = []
        if row > 0:  # up (cannot be on top/first row)
            moves.append(moveU)
        if col > 0:  # left (cannot be on left col)
            moves.append(moveL)
        if col < puzzleSize - 1:  # right (cannot be on right column)
            moves.append(moveR)
        if row < puzzleSize - 1:  # down (cannot be on bottom row)
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
        if move == moveU:  # up
            self.tiles[row][col] = self.tiles[row - 1][col]
            row -= 1
        elif move == moveL:  # left
            self.tiles[row][col] = self.tiles[row][col - 1]
            col -= 1
        elif move == moveR:  # right
            self.tiles[row][col] = self.tiles[row][col + 1]
            col += 1
        elif move == moveD:  # down
            self.tiles[row][col] = self.tiles[row + 1][col]
            row += 1

        # put the empty square where the numbered tile previously was
        self.tiles[row][col] = emptySquare

    def generateChildren(self):
        """
        Generate valid children tile configurations given the current tiles
        One child node for each direction the empty square can move
        :return:
        """
        children = []

        # get list of valid moves the empty tile can do
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
        moves.append(self.move)  # TODO: is this needed at root?
        path = self
        while path.parent != None:
            path = path.parent
            moves.append(path.move)
        moves = moves[:-1]
        moves.reverse()

        # moveStr = ", ".join(moves)


# def heuristicCityBlock(puzzle):
#     """
#     City block heuristic: estimate number of moves for each tile to intended location
#     This is admissible since it never over-estimates the number of moves
#     :return:
#     """
#     # for each tile, count the number of moves to its intended position (assume no other tiles)
#     sum = 0
#
#     for row in range(puzzleSize):
#         for col in range(puzzleSize):
#             # expected tile position (+1 because arrays start at 0, tiles start at 1)
#             expectedTile = row * puzzleSize + col + 1
#
#             # the last spot in the board is reserved for empty space, ignore for this heuristic
#             if expectedTile == (puzzleSize * puzzleSize):
#                 continue
#
#             # get location of expected tile and calculate distance (absolute in case it moves up/left)
#             actRow, actCol = puzzle.getPosition(expectedTile)
#             dist = abs(actRow - row) + abs(actCol - col)
#             # if debug:
#             #     print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')
#
#             sum += dist
#
#     return sum


def heuristicCityBlock(puzzle: Puzzle):
    """
    City block heuristic: estimate number of moves for each tile to intended location
    This is admissible since it never over-estimates the number of moves
    :return:
    """

    start = time.time()

    # for each tile, count the number of moves to its intended position (assume no other tiles)
    sum = 0
    # puzzle.print()

    for row in range(puzzleSize):
        for col in range(puzzleSize):
            val = puzzle.tiles[row][col]
            if val == emptySquare:
                continue
            actRow, actCol = puzzle.getTargetPosition(val)
            dist = abs(actRow - row) + abs(actCol - col)
            if debug:
                print(f'{actRow=}, {actCol=}, {val=}, {dist=}')
            sum += dist

    end = time.time()
    runtime = end - start
    main.heuristicTime += runtime

    return sum


# def heuristicMy(puzzle):
#     """
#     Heuristic defined by us
#     Use the city block estimate plus the distance to the empty square
#     This is not admissible since it may over-estimate the number of moves
#     -i.e. if the give tile is one move away from its intended location and the emtpy square
#     is there, it only needs to move once (but this algo returns 2 for that tile)
#     :return:
#     """
#     sum = 0
#     (emptyRow, emptyCol) = puzzle.getEmptyPosition()
#
#     for row in range(puzzleSize):
#         for col in range(puzzleSize):
#             # expected tile position (+1 because arrays start at 0, tiles start at 1)
#             expectedTile = row * puzzleSize + col + 1
#
#             # the last spot in the board is reserved for empty space, ignore for this heuristic
#             if expectedTile == (puzzleSize * puzzleSize):
#                 continue
#
#             # get location of expected tile and calculate distance (absolute in case it moves up/left)
#             actRow, actCol = puzzle.getPosition(expectedTile)
#             dist = abs(actRow - row) + abs(actCol - col)
#             if debug:
#                 print(f'Expected at {row},{col} is Tile {expectedTile}; actually at {actRow},{actCol} (dist={dist})')
#
#             # if at correct spot, do not consider moving empty tile
#             if dist == 0:
#                 continue
#
#             # otherwise add distance to empty tile (this makes the algo not admissible)
#             emptyDist = abs(actRow - emptyRow) + abs(actCol - emptyCol)
#             if debug:
#                 print('myHeuristic moves from emtpy: %d' % emptyDist)
#             sum += dist + emptyDist
#
#     return sum


def aStar(tiles, whichHeuristic):
    """
    A* search
    :return: Solution node (or None if no solution found), fLimit, nodes checked, moves
    """
    global count
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
    # heuristic_time = 0

    while not Q.empty():
        if count >= maxNodesPerSearch:
            print('Max nodes exceeded, terminating search. Nodes checked: %d' % nodesChecked)
            moves = node.cost
            return None, None, count, moves
        (nodeEstimate, nodeCount, node) = Q.get()

        # append the expanded list with the state of the variable 'node'. Unbale to do so, idk why?
        expanded.append(node.tiles)
        if node.isPuzzleSolved():
            return node, None, count, node.cost
        children = node.generateChildren()

        for child in children:
            if child.tiles not in expanded:
                count += 1
                # get new F value
                # heuristicEst, runtime = whichHeuristic(child)
                # estimate = child.cost + heuristicEst
                # heuristic_time += runtime
                estimate = child.cost + whichHeuristic(child)
                Q.put((estimate, count, child))

    return node, None, count, node.cost


nodesChecked = 0  # global var to keep track of nodes checked in rbfs (both searches should reset at start)


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
        return (node, fLimit, nodesChecked, node.cost)
    else:
        print("No solution found")
        return (None, maxsize, nodesChecked, 0)


def rbfsMain(node, fLimit, whichHeuristic):
    global nodesChecked
    successors = []
    # result = None

    # if debug:
    #     print('rbfsMain flimit=%d, move=%s:' % (fLimit, node.move))
    #     node.print()

    if node.isPuzzleSolved():
        return node, None

    nodesChecked += 1
    if nodesChecked >= maxNodesPerSearch:
        print('Max nodes exceeded, terminating search. Nodes checked: %d' % nodesChecked)
        raise Exception('node limit exceeded')

    children = node.generateChildren()
    if len(children) == 0:
        return None, maxsize

    childPos = 0  # used to differentiate between nodes with the same f value

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

        # fBefore = bestNode.evalFunc
        (result, bestNode.evalFunc) = rbfsMain(bestNode, minF, whichHeuristic)
        # print(f'Backout fBefore={fBefore}, fAfter={bestNode.evalFunc}')
        successors[0] = (bestNode.evalFunc, bestPos, bestNode)

        if result != None:
            break

    return result, None
