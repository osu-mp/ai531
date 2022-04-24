import csv
import time
import unittest

from puzzle import Puzzle, emptySquare, collectData, csvFilename, rbfs, heuristicCityBlock, heuristicMy, aStar


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
            [1, 2, 3, 4],
            [5, 6, emptySquare, 8],
            [9, 10, 7, 11],
            [13, 14, 15, 12]
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
        start = time.time()  # get start time
        (node, fLimit, nodesChecked) = searchFunc(tiles, heuristic)  # run the search function with selected heuristic
        end = time.time()  # record runtime

        moves = node.cost
        return (nodesChecked, moves, end - start)  # return number of nodes checked and runtime

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
        for m in [
            10]:  # , 20, 30, 40, 50]:                      # run for increasing number of moves from solved puzzle

            runData['astar']['cityBlock'][m] = []
            runData['astar']['myHeuristic'][m] = []
            runData['rbfs']['cityBlock'][m] = []
            runData['rbfs']['myHeuristic'][m] = []

            for n in range(5):  # TODO : run 10 trials at each m
                base = Puzzle()
                base.scramblePuzzle(m)  # ensure all 4 configurations use the same scrambled puzzle
                baseTiles = base.tiles
                print('Puzzle Number %d (m=%d)' % (n, m))
                base.print()

                # # # astar with city block heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, aStar, heuristicCityBlock)
                # runData['astar']['cityBlock'][m].append([moves, nodesChecked, runTime])
                #
                # # astar with my heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, aStar, heuristicMy)
                # runData['astar']['myHeuristic'][m].append([moves, nodesChecked, runTime])

                # rbfs with city block heuristic
                (nodesChecked, moves, runTime) = self.runTest(baseTiles, rbfs, heuristicCityBlock)
                runData['rbfs']['cityBlock'][m].append([moves, nodesChecked, runTime])

                # rbfs with my heuristic
                # (nodesChecked, moves, runTime) = self.runTest(baseTiles, rbfs, heuristicMy)
                # runData['rbfs']['myHeuristic'][m].append([moves, nodesChecked, runTime])

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

    def test_rbfs_m_values(self):
        m = 8
        puzzle = Puzzle()
        puzzle.scramblePuzzle(m)
        # puzzle.moveToEmptyCell(15)
        # puzzle.moveToEmptyCell(11)
        # puzzle.moveToEmptyCell(10)
        print("Solving puzzle below")
        puzzle.print()
        (node, fLimit, nodesChecked) = rbfs(puzzle.tiles, heuristicMy)
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


if __name__ == '__main__':
    unittest.main()
