#!/usr/bin/python3

# AI 531 - Project 2 - 15 Puzzle
# Wadood Alam
# Joe Nguyen
# Matthew Pacey

import csv
import time
import unittest

from linear_conflict import heuristicMy
from puzzle import Puzzle, emptySquare, collectData, csvFilename, rbfs, heuristicCityBlock, aStar

moveL = 'L'  # movement the empty tile can do: left, right, up, down
moveR = 'R'  # if tile is on an edge, some movements will not be allowed
moveU = 'U'
moveD = 'D'


class TestPuzzle(unittest.TestCase):
    """
    Unit tests and data collection for 15 puzzle routines
    """

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

    def runTest(self, tiles, searchFunc, heuristic):
        """
        Run the specified search function using given heuristic and return runtime in seconds
        :param puzzle:
        :param searchFunc:
        :param heuristic:
        :return:
        """
        start = time.time()  # get start time
        (node, fLimit, nodesChecked, moves) = searchFunc(tiles,
                                                         heuristic)  # run the search function with selected heuristic
        end = time.time()  # record runtime

        solutionFound = False
        if node:
            moves = node.cost
            solutionFound = True

        return (nodesChecked, moves, end - start, solutionFound)  # return number of nodes checked and runtime

    def test_data_collection(self):
        """
        Try all combinations of searches and collect performance data into a csv
        :return:
        """
        # global heuristicTime

        # TODO : this has not been updated to new methods (4/23)
        # TODO : Matthew update after search functions complete
        if not collectData:
            self.skipTest("Data collection skipped")

        # save raw data to csv file
        csvFH = open(csvFilename, 'w', newline='')
        writer = csv.writer(csvFH)

        # header of csv
        writer.writerow(
            ['m', 'puzzleNum', 'searchFunc', 'heuristic', 'moves', 'nodesChecked', 'runTime (seconds)', 'solutionFound',
             'heuristic % runTime', 'heuristic time'])

        # collect data into run data and write it later
        runData = {}
        for algo in ['astar', 'rbfs']:
            runData[algo] = {}
            for heuristic in ['cityBlock', 'myHeuristic']:
                runData[algo][heuristic] = {}

        numTrials = 10  # run this many tests at each m
        TRIALS = [10, 20, 30, 40, 50]
        # TRIALS = [10]
        for m in TRIALS:  # run for increasing number of moves from solved puzzle

            runData['astar']['cityBlock'][m] = []
            runData['astar']['myHeuristic'][m] = []
            runData['rbfs']['cityBlock'][m] = []
            runData['rbfs']['myHeuristic'][m] = []

            for n in range(numTrials):
                base = Puzzle()
                base.scramblePuzzle(m)  # ensure all 4 configurations use the same scrambled puzzle

                baseTiles = base.tiles
                print('Puzzle Number %d (m=%d)' % (n, m))
                base.print()

                # # astar with city block heuristic
                heuristicTime = 0  # reset heuristic timer
                (nodesChecked, moves, runTime, solutionFound) = self.runTest(baseTiles, aStar, heuristicCityBlock)
                heuristicPct = heuristicTime / runTime * 100
                runData['astar']['cityBlock'][m].append(
                    [moves, nodesChecked, runTime, solutionFound, heuristicPct, heuristicTime])
                print('aStar w/ cityBlock: moves=%3d, nodes=%5d, time=%1.6f, heuristicPct=%2.4f' % (
                    moves, nodesChecked, runTime, heuristicPct))

                # astar with my heuristic
                heuristicTime = 0  # reset heuristic timer
                (nodesChecked, moves, runTime, solutionFound) = self.runTest(baseTiles, aStar,
                                                                             heuristicMy)
                heuristicPct = heuristicTime / runTime * 100
                runData['astar']['myHeuristic'][m].append(
                    [moves, nodesChecked, runTime, solutionFound, heuristicPct, heuristicTime])
                print('aStar w/ myHeuristic: moves=%3d, nodes=%5d, time=%1.6f, heuristicPct=%2.4f' % (
                    moves, nodesChecked, runTime, heuristicPct))

                # rbfs with city block heuristic
                heuristicTime = 0  # reset heuristic timer
                (nodesChecked, moves, runTime, solutionFound) = self.runTest(baseTiles, rbfs, heuristicCityBlock)
                heuristicPct = heuristicTime / runTime * 100
                runData['rbfs']['cityBlock'][m].append(
                    [moves, nodesChecked, runTime, solutionFound, heuristicPct, heuristicTime])
                print('rbfs  w/ cityBlock: moves=%3d, nodes=%5d, time=%f, heuristicPct=%2.4f' % (
                    moves, nodesChecked, runTime, heuristicPct))

                # rbfs with my heuristic
                heuristicTime = 0  # reset heuristic timer
                (nodesChecked, moves, runTime, solutionFound) = self.runTest(baseTiles, rbfs, heuristicMy)
                heuristicPct = heuristicTime / runTime * 100
                runData['rbfs']['myHeuristic'][m].append(
                    [moves, nodesChecked, runTime, solutionFound, heuristicPct, heuristicTime])
                print('rbfs  w/ myHeuristic: moves=%3d, nodes=%5d, time=%f, heuristicPct=%2.4f' % (
                    moves, nodesChecked, runTime, heuristicPct))

        # now that all data has been collected, write it grouped by algo/heuristic
        for algo in runData:
            for heuristic in runData[algo]:
                print('Algo = %s, Heuristic = %s' % (algo, heuristic))

                for mValue in runData[algo][heuristic]:
                    moveSum = 0
                    nodeSum = 0
                    timeSum = 0
                    solnCount = 0

                    for puzzleNum, trial in enumerate(runData[algo][heuristic][mValue]):
                        (moves, nodesChecked, runTime, solutionFound, heuristicPct, heuristicTime) = trial
                        writer.writerow(
                            [mValue, puzzleNum, algo, heuristic, moves, nodesChecked, runTime, solutionFound,
                             heuristicPct, heuristicTime])
                        moveSum += moves
                        nodeSum += nodesChecked
                        timeSum += runTime
                        if solutionFound:
                            solnCount += 1

                    moveAvg = 0
                    if solnCount:  # only average if a puzzle was solved, else 0
                        moveAvg = int(moveSum / solnCount)  # average the moves on SOLVED puzzles only
                    nodeAvg = int(nodeSum / numTrials)
                    timeAvg = "%.4f" % (timeSum / numTrials)
                    solnAvg = int(solnCount / numTrials * 100)

                    # printout for tables in latex report
                    print(f' & {mValue} & {timeAvg} & {nodeAvg} & {moveAvg} & {solnAvg} \\\\')

        print('Data collection complete, results written to: %s' % csvFilename)

    def test_rbfs(self):
        """
        Functional tests for rbfs search algo
        :return:
        """
        # base case: already solved puzzle (0 moves)
        puzzle = Puzzle()
        (node, fLimit, nodesChecked, moves) = rbfs(puzzle.tiles, heuristicCityBlock)
        print('node %s' % node)
        self.assertEqual(0, node.cost)

        # simple case: puzzle off by one move
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked, moves) = rbfs(puzzle.tiles, heuristicCityBlock)
        self.assertIsNotNone(node, "failed to solve puzzle")
        self.assertEqual(1, node.cost)

        # simple case: puzzle off by 2 moves
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        puzzle.moveEmpty(moveU)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked, moves) = rbfs(puzzle.tiles, heuristicCityBlock)
        self.assertEqual(2, node.cost)

        # use puzzle scrambled by m moves

    def test_rbfs_m_values(self):
        m = 20
        puzzle = Puzzle()
        puzzle.scramblePuzzle(m)
        # puzzle.moveEmpty(moveL)
        # puzzle.moveEmpty(moveL)
        # puzzle.moveEmpty(moveU)
        # puzzle.moveEmpty(moveR)
        # puzzle.moveEmpty(moveU)
        # puzzle.moveEmpty(moveL)
        # puzzle.moveEmpty(moveD)

        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked, moves) = rbfs(puzzle.tiles, heuristicCityBlock)
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
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristicCityBlock)
        print('node %s' % node)
        self.assertEqual(0, node.cost)

        # simple case: puzzle off by one move
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristicCityBlock)
        if node:
            print('Solved with cost %d' % node.cost)
        self.assertEqual(1, node.cost)

        # simple case: puzzle off by 2 moves
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        puzzle.moveEmpty(moveU)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristicCityBlock)
        if node:
            print('Solved with cost %d' % node.cost)
        self.assertEqual(2, node.cost)

    def test_rbfs_m_values(self):
        m = 8
        puzzle = Puzzle()
        puzzle.scramblePuzzle(m)
        # puzzle.moveToEmptyCell(15)
        # puzzle.moveToEmptyCell(11)
        # puzzle.moveToEmptyCell(10)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked, moves) = rbfs(puzzle.tiles, heuristicMy)
        self.assertTrue(node.cost <= m, 'Solution took move moves than scramble')

    def test_cityBlock(self):
        """
        Unit tests for city block heuristic
        :return:
        """
        puzzle = Puzzle()

        # base case: solved puzzle, city block should return 0
        self.assertEqual(0, heuristicCityBlock(puzzle))

        scrambled = [
            [4, 1, 3, 2],
            [5, 6, emptySquare, 8],
            [10, 9, 7, 11],
            [15, 14, 13, 12]
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
            [4, 1, 3, 2],
            [5, 6, emptySquare, 8],
            [10, 9, 7, 11],
            [15, 14, 13, 12]
        ]

        puzzle.tiles = scrambled

        # using above puzzle, expected my heuristic is (tiles 1 through 15 distances added):
        # e.g. tile 1 is 1 spot away from target and 2 away from emtpy,
        # tile 2 is 2 away from target and 2 from empty,
        # tile 3 is where it belongs, etc
        expected = (1 + 2) + (2 + 2) + 0 + (3 + 3) + 0 + 0 + (1 + 1) + 0
        # tile       1         2        3    4        5   6    7        8
        expected += (1 + 2) + (1 + 3) + (1 + 2) + (1 + 3) + (2 + 2) + 0 + (2 + 4)
        #            9         10        11       12        13        14   15
        self.assertEqual(expected, heuristicMy(puzzle))

    def test_getTargetPosition(self):
        puzzle = Puzzle()
        print(f'{puzzle.target_pos=}')
        self.assertEqual(puzzle.getTargetPosition(4), (0, 3))

    def test_astart_linearconfict(self):
        # base case: already solved puzzle (0 moves)
        heuristic = heuristicMy

        puzzle = Puzzle()
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristic)
        print('node %s' % node)
        self.assertEqual(0, node.cost)

        # simple case: puzzle off by one move
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristic)
        if node:
            print('Solved with cost %d' % node.cost)
        self.assertEqual(1, node.cost)

        # simple case: puzzle off by 2 moves
        puzzle = Puzzle()
        puzzle.moveEmpty(moveL)
        puzzle.moveEmpty(moveU)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, count, moves) = aStar(puzzle.tiles, heuristic)
        if node:
            print('Solved with cost %d' % node.cost)
            print(node)
        self.assertEqual(2, node.cost)


if __name__ == '__main__':
    unittest.main()
