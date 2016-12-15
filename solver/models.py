from __future__ import unicode_literals
from django.db import models
import json
from sets import ImmutableSet
import numpy as np
from sudoku_solver import utils
from django.contrib.postgres.fields import ArrayField

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

ALL_POSS = ImmutableSet(range(1, 10))  # all possibilities


class SudokuPuzzle(models.Model):
    unsolved_puzzle = ArrayField(
        base_field=ArrayField(
            base_field=models.IntegerField(), size=9),
        size=9)

    solved_puzzle = ArrayField(
        base_field=ArrayField(
            base_field=models.IntegerField(), size=9, blank=True, null=True,
            default=[]),
        size=9, blank=True, null=True, default=[])
    solved = models.BooleanField(default=False)
    missing_vals_pos = ArrayField(
        base_field=models.CharField(max_length=2),
        blank=True, null=True, default=[])

    def solve(self):
        #  MAIN SOLVING FLOW. CALL ALGO FUNCTIONS/METHODS FROM HERE
        self.solved_puzzle = self.unsolved_puzzle
        self.set_missing_vals_pos()
        self.create_puzzle_cells()
        run_again = True

        # if values were found run again
        while run_again:
            qty_vals_bef = len(utils.remove_zeroes(
                np.ravel(self.solved_puzzle).tolist()))
            # known vals qty BEFORE running single_cand_algo

            for i in range(9):
                for j in range(9):
                    if self.solved_puzzle[i][j] == 0:
                        cell_poss = self.get_possibilities(i, j)

                        if len(cell_poss) == 1:
                            self.single_cand_algo(i, j, cell_poss)

                        else:
                            self.update_possibilities(i, j, cell_poss)

            qty_vals_aft = len(utils.remove_zeroes(
                np.ravel(self.solved_puzzle).tolist()))
            # known vals qty AFTER running single_cand_algo

            run_again = qty_vals_bef < qty_vals_aft

        self.solved = True
        self.save()

    def get_row(self, i):
        return utils.remove_zeroes(self.solved_puzzle[i])

    def get_col(self, j):
        np_arr = np.array(self.solved_puzzle)
        return utils.remove_zeroes(np_arr[:, j].tolist())

    def get_sqr(self, i, j):
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

        # assert that sqr is valid
        if (tuple(sqr_boundaries) not in SQUARE_DEFS):
            raise Exception("Invalid square")

        np_arr = np.array(self.solved_puzzle)
        sqr = np_arr[
            sqr_boundaries[0]:sqr_boundaries[2]+1,
            sqr_boundaries[1]:sqr_boundaries[3]+1]

        # np.ravel puts array values in a 1D list
        return utils.remove_zeroes(np.ravel(sqr).tolist())

    def create_puzzle_cells(self):
        for i in range(9):
            for j in range(9):

                if self.solved_puzzle[i][j] != 0:
                    cell_poss = set()
                    cell_poss.add(self.solved_puzzle[i][j])

                else:
                    cell_poss = self.get_possibilities(i, j)

                cell = PuzzleCell(
                    puzzle_pk=self.pk,
                    possibilities=json.dumps(list(cell_poss)),
                    row=i, col=j)

                cell.save()

    def single_cand_algo(self, i, j, cell_poss):
        # single candidate algorithm

        cell = PuzzleCell.objects.get(
            puzzle_pk=self.pk, row=i, col=j)
        cell.value = list(cell_poss)[0]
        cell.filled = True
        self.solved_puzzle[i][j] = cell.value  # add value to puzzle if found

        cell.save()

    def update_possibilities(self, i, j, cell_poss):
        cell = PuzzleCell.objects.get(
            puzzle_pk=self.pk, row=i, col=j)
        cell.possibilities = json.dumps(
            list(cell_poss))

        cell.save()

    def set_missing_vals_pos(self):
        for i in range(9):
            for j in range(9):
                if self.solved_puzzle[i][j] == 0:
                    self.missing_vals_pos.append(str(i) + str(j))

    # def single_pos_algo(self, i, j):
        # single position algorithm

        # cell_poss = self.get_possibilities(puzzle, i, j)

        # for poss in cell_poss:
        #     qs = PuzzleCell.objects.filter(
        #         puzzle_pk=self.pk, possibilities='[]',
        #         position__startswith=str(i))

    def get_possibilities(self, i, j):
        # returns all possibilities for a given cell

        cell_poss = set(ALL_POSS)
        row = self.get_row(i)
        col = self.get_col(j)
        sqr = self.get_sqr(i, j)

        cell_poss = cell_poss.difference(set(row))
        cell_poss = cell_poss.difference(set(col))
        cell_poss = cell_poss.difference(set(sqr))

        if len(cell_poss) < 1 or len(cell_poss) > 9:
            raise Exception("Invalid number of possibilities")

        return cell_poss


class PuzzleCell(models.Model):
    puzzle_pk = models.IntegerField()
    value = models.IntegerField(default=0, blank=True, null=True)
    possibilities = models.CharField(
        default='[]', max_length=50, blank=True, null=True)
    filled = models.BooleanField(default=False)
    row = models.IntegerField(default=-1, blank=True)
    col = models.IntegerField(default=-1, blank=True)

    def __str__(self):
        return "v:%i - r:%i - c:%i" % (self.value, self.row, self.col)
