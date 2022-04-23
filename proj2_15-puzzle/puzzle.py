#!/us#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import csv
import random
import time
import unittest

"""
TODO: Define classes/tests
Heuristic: City Block
Heuristic: MY: Any other heuristic (>= CB) that you can come up with that performs better in terms of the number of nodes searched by one or both of the algorithms. This heuristic may or may not be admissible.

Helpers:
scramble(goal, m): given a valid board, scramble by m moves (watch out for moves that cancel each other out, e.g. up followed by down)
timer: time how long a function takes
correctCount: return how many numbers are in their correct cell
distanceFromEmpty: return 

Searches:
generic:    count number of nodes searched? 
            set some max node threshold?
            set some max time threshold?
aStar:
RBFS

Min Heap walkthrough: https://www.geeksforgeeks.org/min-heap-in-python/
A* algo 

"""

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
collectData = False         # set to True to generate test data (long runtime)
maxNodes = 1000             # TODO tune to a sensible value
csvFilename = 'data.csv'    # where test runtimes are written

class Puzzle:
    def __init__(self):
        self.puzzleSize = puzzleSize
        self.puzzle = self.getSolvedPuzzle()

    def graphPuzzle(self):
        """

        :return:
        """
        '''
        16 nodes: e.g. 1 connected to 2 and 5, 
        
        Use heap: 
        '''
        pass

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

        # set the last sqaure to blank
        puzzle[puzzleSize - 1][puzzleSize - 1] = emptySquare
        return puzzle

    def isPuzzleSolved(self):
        return self.puzzle == self.getSolvedPuzzle()

    def scramblePuzzle(self, m):
        """
        Scramble the current puzzle by moving m random tiles
        :param m: Number of moves to scramble puzzle
        :return: Nothing (self.puzzle is now scrambled)
        """
        lastMoved = None
        for i in range(m):
            # get neighbors of empty cell
            neighbors = self.getNeighbors(emptySquare)

            # pick a random number from those
            next = random.choice(neighbors)

            # as long as it is not 'last' move it
            while next == lastMoved:
                next = random.choice(neighbors)

            self.moveToEmptyCell(next)
            print("Scramble: moved %d to empty cell" % next)
            # self.print()
            lastMoved = next

        # return a copy for data collection (allows to use same scrambled puzzle for different configs)
        return self.puzzle.copy()

    def print(self):
        """
        Print the current configuration
        :return:
        """
        str = ""
        for row in self.puzzle:
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
        # TODO does using modulo or caching significantly help?
        for row in range(puzzleSize):
            for col in range(puzzleSize):
                if self.puzzle[row][col] == target:
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
            neighbors.append(self.puzzle[row - 1][col])
        # left
        if col > 0:
            neighbors.append(self.puzzle[row][col - 1])
        # right
        if col < puzzleSize - 1:
            neighbors.append(self.puzzle[row][col + 1])
        # down
        if row < puzzleSize - 1:
            neighbors.append(self.puzzle[row + 1][col])

        return neighbors

    def moveToEmptyCell(self, target):
        """
        Move the given number into the empty cell
        :param target:
        :return: True if moved, Exception if blocked
        """
        neighbors = self.getNeighbors(target)
        if emptySquare not in neighbors:
            raise Exception("Target number %d is not adjacent to empty cell, cannot move")

        # if they are neighbors, swap the positions
        tarRow, tarCol = self.getPosition(target)       # position of target number that is moving
        empRow, empCol = self.getEmptyPosition()        # position of empty cell

        self.puzzle[tarRow][tarCol] = emptySquare
        self.puzzle[empRow][empCol] = target

        return True

    def cityBlock(self):
        """
        City block heuristic: estimate number of cells
        :return:
        """
        print('This is the cityBlock heuristic')
        return 8
        # raise Exception('TODO: Joe')

    def myHeuristic(self):
        """
        TBD heuristic defined by us
        :return:
        """
        print('This is my heuristic')
        return 9
        # raise Exception('TODO: Joe')

    def aStar(self, whichHeuristic, maxNodes=1000):
        """
        A* search
        :return: Number of nodes checked
        """
        estimate = whichHeuristic()
        print('astar search with %s (estimate %d)' % (whichHeuristic.__name__, estimate))
        time.sleep(1)
        #raise Exception('TODO: Wadood & Joe')
        nodesChecked = 10
        return nodesChecked

    def rbfs(self, whichHeuristic, maxNodes=1000):
        """
        Recursive best first search
        :return: Number of nodes checked
        """
        estimate = whichHeuristic()
        print('rbfs search with %s (estimate %d)' % (whichHeuristic.__name__, estimate))
        time.sleep(2)
        #raise Exception('TODO: Matthew')
        nodesChecked = 20
        return nodesChecked


