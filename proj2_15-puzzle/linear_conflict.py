from puzzle import Puzzle, emptySquare, puzzleSize, heuristicCityBlock


# def linear_conflicts(candidate, solved, size):
#     def count_conflicts(candidate_row, solved_row, size, ans=0):
#         counts = [0 for x in range(size)]
#         for i, tile_1 in enumerate(candidate_row):
#             if tile_1 in solved_row and tile_1 != 0:
#                 solved_i = solved_row.index(tile_1)
#                 for j, tile_2 in enumerate(candidate_row):
#                     if tile_2 in solved_row and tile_2 != 0 and i != j:
#                         solved_j = solved_row.index(tile_2)
#                         if solved_i > solved_j and i < j:
#                             counts[i] += 1
#                         if solved_i < solved_j and i > j:
#                             counts[i] += 1
#         if max(counts) == 0:
#             return ans * 2
#         else:
#             i = counts.index(max(counts))
#             candidate_row[i] = -1
#             ans += 1
#             return count_conflicts(candidate_row, solved_row, size, ans)
#
#     res = heuristicCityBlock(candidate)
#     candidate_rows = [[] for y in range(size)]
#     candidate_columns = [[] for x in range(size)]
#     solved_rows = [[] for y in range(size)]
#     solved_columns = [[] for x in range(size)]
#     for y in range(size):
#         for x in range(size):
#             idx = (y * size) + x
#             candidate_rows[y].append(candidate[idx])
#             candidate_columns[x].append(candidate[idx])
#             solved_rows[y].append(solved[idx])
#             solved_columns[x].append(solved[idx])
#     for i in range(size):
#         res += count_conflicts(candidate_rows[i], solved_rows[i], size)
#     for i in range(size):
#         res += count_conflicts(candidate_columns[i], solved_columns[i], size)
#     return res


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


def linear_conflict_heuristic(puzzle: Puzzle):
    cnt_conflicts = 0
    city_block = heuristicCityBlock(puzzle)
    for i in range(puzzleSize):
        cnt_conflicts += count_conflicts_row(puzzle, i)

    for i in range(puzzleSize):
        cnt_conflicts += count_conflicts_col(puzzle, i)
    # print(f'{res=}')

    return city_block + cnt_conflicts
