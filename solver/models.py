from __future__ import unicode_literals
from django.db import models
import json
from sets import Set, ImmutableSet
import numpy as np
from sudoku_solver import utils


class SudokuPuzzle(models.Model):
    unsolved_puzzle = models.CharField(
        max_length=300, blank=True, null=False)  # json dump
    solved_puzzle = models.CharField(max_length=300)
    solved = models.BooleanField(default=False)
    SQUARE_DEFS = (
        # (first_cell_row, first_cell_col, last_cell_row, last_cell_col) # SQR#
        (0, 0, 2, 2),  # SQR0
        (0, 3, 2, 5),  # SQR1
        (0, 6, 2, 8),  # SQR2
        (3, 0, 5, 2),  # SQR3
        (3, 3, 5, 5),  # SQR4
        (3, 6, 5, 8),  # SQR5
        (6, 0, 8, 2),  # SQR6
        (6, 3, 8, 5),  # SQR7
        (6, 6, 8, 8)  # SQR8
    )

    def solve(self):
        #  MAIN SOLVING THREAD. CALL FUNCTIONS FROM HERE
        puzzle = json.loads(self.unsolved_puzzle)

        all_poss = ImmutableSet([1, 2, 3, 4, 5, 6, 7, 8, 9])

        # LOOP TO CREATE PUZZLE CELLS
        for i in range(9):
            for j in range(9):
                cell_poss = Set(all_poss)
                row = self.get_row(puzzle, i)
                col = self.get_col(puzzle, j)
                sqr = self.get_sqr(puzzle, i, j)

                cell_poss = cell_poss.difference(set(row))
                cell_poss = cell_poss.difference(set(col))
                cell_poss = cell_poss.difference(set(sqr))

                # if cell_poss has only one value then create PuzzleCell
                # with that value and put filled as True

                # if not then create the PuzzleCell with the possibilities

                # change puzzle value for the generated object

    def get_row(self, arr, i):
        return utils.remove_zeroes(arr[i])

    def get_col(self, arr, j):
        np_arr = np.array(arr)
        return utils.remove_zeroes(np_arr[:, j].tolist())

    def get_sqr(self, arr, i, j):
        sqr_boundaries = [0, 0, 0, 0]

        # get square row boundaries
        if (i >= 0 and i <= 2):
            sqr_boundaries[0] = 0
            sqr_boundaries[2] = 2
        elif (i >= 3 and i <= 5):
            sqr_boundaries[0] = 3
            sqr_boundaries[2] = 5
        elif (i >= 6 and i <= 8):
            sqr_boundaries[0] = 6
            sqr_boundaries[2] = 8

        # get square col boundaries
        if (j >= 0 and j <= 2):
            sqr_boundaries[1] = 0
            sqr_boundaries[3] = 2
        elif (j >= 3 and j <= 5):
            sqr_boundaries[1] = 3
            sqr_boundaries[3] = 5
        elif (j >= 6 and j <= 8):
            sqr_boundaries[1] = 6
            sqr_boundaries[3] = 8

        sqr_def = [item for item in self.SQUARE_DEFS if set(
            sqr_boundaries).issubset(set(item))][0]
        np_arr = np.array(arr)
        sqr = np_arr[sqr_def[0]:sqr_def[2]+1, sqr_def[1]:sqr_def[3]+1]

        # np.ravel puts array values in a 1D list
        return utils.remove_zeroes(np.ravel(sqr).tolist())


class PuzzleCell(models.Model):
    puzzle_id = models.IntegerField()
    value = models.IntegerField()
    possibilities = models.CharField(max_length=9)
    filled = models.BooleanField(default=False)
    position = models.CharField(max_length=2)

    def __str__(self):
        return self.value
