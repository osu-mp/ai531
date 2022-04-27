import copy
import time
import utility

from typing import List
from puzzle import Puzzle, emptySquare, puzzleSize, heuristicCityBlock

def count_conflicts_line(config: List[int], sol: List[int]):
    counts = [0 for x in range(puzzleSize)]
    for i in range(puzzleSize):
        val_i = config[i]
        if val_i == emptySquare:
            continue
        if val_i not in sol:
            continue
        solved_i_pos = sol.index(val_i)

        for j in range(i + 1, puzzleSize):
            val_j = config[j]
            if val_j == emptySquare:
                continue
            if val_j not in sol:
                continue

            solved_j_pos = sol.index(val_j)
            if solved_i_pos > solved_j_pos and i < j:
                counts[i] += 1
            if solved_i_pos < solved_j_pos and i > j:
                counts[i] += 1

    if max(counts) == 0:
        return 0
    else:
        argmax_id = counts.index(max(counts))
        config[argmax_id] = -1
        return 1 + count_conflicts_line(config, sol)

def linear_conflict_heuristic(puzzle: Puzzle):
    res = 0
    config = copy.deepcopy(puzzle.tiles)  # type: List[List[int]]
    row_configs = [config[i] for i in range(puzzleSize)]
    col_configs = list(map(list, zip(*config)))

    for i in range(puzzleSize):
        res += count_conflicts_line(row_configs[i], utility.row_sols[i]) * 2
    for i in range(puzzleSize):
        res += count_conflicts_line(col_configs[i], utility.col_sols[i]) * 2

    return res

def heuristicMy(puzzle: Puzzle):
    start = time.time()
    city_block = heuristicCityBlock(puzzle)
    linear_conflict = linear_conflict_heuristic(puzzle)
    utility.heuristicTime += time.time() - start
    return city_block + linear_conflict


if __name__ == '__main__':
    puzzle = Puzzle(tiles=[[4, 1, 2, 3], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, emptySquare]])
    # print(heuristicMy(puzzle))
    print(linear_conflict_heuristic(puzzle))
