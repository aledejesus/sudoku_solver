from __future__ import unicode_literals
from django.db import models
import json
from sets import ImmutableSet


class SudokuPuzzle(models.Model):
    unsolved_puzzle = models.CharField(
        max_length=300, blank=True, null=False)  # json dump
    solved_puzzle = models.CharField(max_length=300)
    solved = models.BooleanField(default=False)
    SQUARE_DEFS = (
        # ('SQR#', first_cell_row, first_cell_col,
        #   last_cell_row, last_cell_col)
        ('SQR0', 0, 0, 2, 2),
        ('SQR1', 0, 3, 2, 5),
        ('SQR2', 0, 6, 2, 8),
        ('SQR3', 3, 0, 5, 2),
        ('SQR4', 3, 3, 5, 5),
        ('SQR5', 3, 6, 5, 8),
        ('SQR6', 6, 0, 8, 2),
        ('SQR7', 6, 3, 8, 5),
        ('SQR8', 6, 6, 8, 8)
    )

    def solve(self):
        #  MAIN SOLVING THREAD. CALL FUNCTIONS FROM HERE
        puzzle = json.loads(self.unsolved_puzzle)

        all_poss = ImmutableSet([1, 2, 3, 4, 5, 6, 7, 8, 9])

        # LOOP TO CREATE PUZZLE CELLS
        for i in range(9):
            for j in range(9):
                cell_poss = all_poss
                row = self.get_row(puzzle, i)
                col = self.get_col(puzzle, j)
                sqr = self.get_sqr()

    def get_row(arr, i):
        return arr[i]

    def get_col(arr, i):
        return arr[:, i]

    # GIVE SQUARE BASED ON CELL INDEXES
    # def get_sqr(self, i):
    #     sqr_def = self.SQUARE_DEFS[i]

        # return self.unsolved_puzzlearr[
        #     sqr_def[1]:sqr_def[2]+1, sqr_def[3]:sqr_def[4]+1]

    # def get_qty_items(arr): RESEARCH IF NEEDED


class PuzzleCell(models.Model):
    puzzle_id = models.IntegerField()
    value = models.IntegerField()
    possibilities = models.CharField(max_length=9)
    filled = models.BooleanField(default=False)
    # position needed ??
