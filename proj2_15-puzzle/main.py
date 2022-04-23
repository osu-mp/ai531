import csv
import time
import unittest

from puzzle import Puzzle, emptySquare, collectData, csvFilename


class TestPuzzle(unittest.TestCase):

    def test_scramble(self):
        puzzle = Puzzle()
        solved = puzzle.getSolvedPuzzle()
        puzzle.scramblePuzzle(10)
        self.assertNotEqual(solved, puzzle.puzzle)
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
        self.assertEqual(puzzle.puzzle, expected)

    def runTest(self, puzzleObj, searchFunc, heuristic):
        """
        Run the specified search function using given heuristic and return runtime in seconds
        :param puzzle:
        :param searchFunc:
        :param heuristic:
        :return:
        """
        start = time.time()                             # get start time
        nodesChecked = searchFunc(heuristic)            # run the search function with selected heuristic
        end = time.time()                               # record runtime

        return (nodesChecked, end - start)              # return number of nodes checked and runtime

    def test_data_collection(self):
        """
        Try all combinations of searches and collect performance data into a csv
        :return:
        """
        if not collectData:
            self.skipTest("Data collection skipped")

        # TODO save to csv
        csvFH = open(csvFilename, 'w', newline='')
        writer = csv.writer(csvFH)
        writer.writerow(['m', 'puzzleNum', 'searchFunc', 'heuristic', 'nodesChecked', 'runTime (seconds)'])

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

            for n in range(10):                             # run 10 trials at each m
                base = Puzzle()
                basePuzzle = base.scramblePuzzle(m)         # ensure all 4 configurations use the same scrambled puzzle
                print('Puzzle Number %d' % n)
                print(base.print())

                # astar with city block heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(test, puzzle.aStar, puzzle.cityBlock)
                runData['astar']['cityBlock'][m].append([nodesChecked, runTime])

                # astar with my heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(test, puzzle.aStar, puzzle.myHeuristic)
                runData['astar']['myHeuristic'][m].append([nodesChecked, runTime])

                # rbfs with city block heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(basePuzzle, puzzle.rbfs, puzzle.cityBlock)
                runData['rbfs']['cityBlock'][m].append([nodesChecked, runTime])

                # rbfs with my heuristic
                test = Puzzle()
                test.puzzle = basePuzzle
                (nodesChecked, runTime) = self.runTest(basePuzzle, puzzle.rbfs, puzzle.myHeuristic)
                runData['rbfs']['myHeuristic'][m].append([nodesChecked, runTime])

        # now that all data has been collected, write it grouped by algo/heuristic
        for algo in runData:
            for heuristic in runData[algo]:
                for mValue in runData[algo][heuristic]:
                    for puzzleNum, trial in enumerate(runData[algo][heuristic][m]):
                        (nodesChecked, runTime) = trial
                        writer.writerow([mValue, puzzleNum, algo, heuristic, nodesChecked, runTime])
        print('Data collection complete, results written to: %s' % csvFilename)

if __name__ == '__main__':
    unittest.main()
