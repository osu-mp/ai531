import time
import main

from puzzle import Puzzle, emptySquare, puzzleSize, heuristicCityBlock

def count_conflicts_row(puzzle: Puzzle, row_id: int):
    res = 0
    for i in range(puzzleSize):
        val_i = puzzle.tiles[row_id][i]
        if val_i == emptySquare: continue
        target_x_i, target_y_i = puzzle.getTargetPosition(val_i)
        if target_x_i == row_id:

            for j in range(i + 1, puzzleSize):
                if i == j: continue

                val_j = puzzle.tiles[row_id][j]
                if val_j == emptySquare: continue

                target_x_j, target_y_j = puzzle.getTargetPosition(val_j)
                if target_x_j == row_id:
                    if target_y_i > target_y_j and i < j:
                        res += 1
                    if target_y_i < target_y_j and i > j:
                        res += 1

    return res

def count_conflicts_col(puzzle: Puzzle, col_id: int):
    res = 0
    for i in range(puzzleSize):
        val_i = puzzle.tiles[i][col_id]
        if val_i == emptySquare: continue
        target_x_i, target_y_i = puzzle.getTargetPosition(val_i)
        if target_y_i == col_id:

            for j in range(i + 1, puzzleSize):
                if i == j: continue

                val_j = puzzle.tiles[j][col_id]
                if val_j == emptySquare: continue

                target_x_j, target_y_j = puzzle.getTargetPosition(val_j)
                if target_y_j == col_id:
                    if target_x_i > target_x_j and i < j:
                        res += 1
                    if target_x_i < target_x_j and i > j:
                        res += 1

    return res

def heuristicMy(puzzle: Puzzle):
    """
    Count the total conflicts in the puzzle (rows + cols) and add this to the city block estimate
    """
    start = time.time()
    cnt_conflicts = 0
    city_block = heuristicCityBlock(puzzle)
    for i in range(puzzleSize):
        cnt_conflicts += count_conflicts_row(puzzle, i)

    for i in range(puzzleSize):
        cnt_conflicts += count_conflicts_col(puzzle, i)
    
    # print(f'{res=}')
    main.heuristicTime += time.time() - start

    return city_block + cnt_conflicts
