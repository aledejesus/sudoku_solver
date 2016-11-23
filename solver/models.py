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

ALL_POSS = ImmutableSet([1, 2, 3, 4, 5, 6, 7, 8, 9])  # all possibilities


class SudokuPuzzle(models.Model):
    unsolved_puzzle = models.CharField(
        max_length=300, blank=True, null=False)  # json dump
    solved_puzzle = models.CharField(max_length=300)
    solved = models.BooleanField(default=False)
    missing_vals_pos = ArrayField(
        base_field=models.CharField(max_length=2),
        blank=True, null=True, default=[])

    def solve(self):
        #  MAIN SOLVING FLOW. CALL ALGO FUNCTIONS/METHODS FROM HERE
        puzzle = json.loads(self.unsolved_puzzle)
        self = self.set_missing_vals_pos(puzzle)  # TODO: CHECK IF WORKING
        qty_vals_bef = len(utils.remove_zeroes(np.ravel(puzzle).tolist()))
        # known vals qty BEFORE running single_cand_algo
        qty_vals_aft = 0  # known vals qty AFTER running single_cand_algo
        first_run = True  # first time running single_cand_algo

        # if values were found run again
        while qty_vals_bef < qty_vals_aft or first_run:
            qty_vals_bef = len(utils.remove_zeroes(np.ravel(puzzle).tolist()))

            for i in range(9):
                for j in range(9):
                    if puzzle[i][j] == 0:
                        puzzle = self.single_cand_algo(puzzle, i, j, first_run)

            first_run = False
            qty_vals_aft = len(utils.remove_zeroes(np.ravel(puzzle).tolist()))

        # TODO: CALL SINGLE_POS_ALGO METHOD
        # TODO: put inside if len(puzzle) == 81:
        self.solved_puzzle = json.dumps(puzzle)
        self.solved = True
        self.save()

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

        # assert that sqr is valid
        # TODO: move this to unit tests ???
        if (tuple(sqr_boundaries) not in SQUARE_DEFS):
            # TODO: raise exception
            pass

        np_arr = np.array(arr)
        sqr = np_arr[
            sqr_boundaries[0]:sqr_boundaries[2]+1,
            sqr_boundaries[1]:sqr_boundaries[3]+1]

        # np.ravel puts array values in a 1D list
        return utils.remove_zeroes(np.ravel(sqr).tolist())

    def single_cand_algo(self, puzzle, i, j, first_run):
        # single candidate algorithm

        cell_poss = self.get_possibilities(puzzle, i, j)

        if len(cell_poss) <= 0 or len(cell_poss) > 9:
            pass
            # TODO: raise exception

        elif len(cell_poss) == 1:
            # create PuzzleCell if first time algo is run
            # get PuzzleCell if not
            if first_run:
                cell = PuzzleCell(
                    puzzle_pk=self.pk, value=list(cell_poss)[0], filled=True,
                    row=i, col=j)
            else:
                cell = PuzzleCell.objects.get(
                    puzzle_pk=self.pk, row=i, col=j)
                cell.value = list(cell_poss)[0]
                cell.filled = True

            # add value to puzzle if found
            puzzle[i][j] = cell.value

        else:
            # TODO: PUT AT THE BEGINNING OF METHOD SO GET_POSS CAN BE CALLED
            if first_run:
                cell = PuzzleCell(
                    puzzle_pk=self.pk,
                    possibilities=json.dumps(list(cell_poss)),
                    row=i, col=j)
            # END TODO

            else:
                cell = PuzzleCell.objects.get(
                    puzzle_pk=self.pk, row=i, col=j)
                cell.possibilities = json.dumps(
                    list(cell_poss))

        cell.save()
        return puzzle

    def set_missing_vals_pos(self, puzzle):
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    self.missing_vals_pos.append(str(i) + str(j))

        return self

    def single_pos_algo(self, puzzle, i, j):
        # single position algorithm
        # TODO: THINK THROUGH

        # cell_poss = self.get_possibilities(puzzle, i, j)

        # # TODO: LOOK FOR ANOTHER ALTERNATIVE (MAYBE CHANGE FOR LOOP)
        # for poss in cell_poss:
        #     qs = PuzzleCell.objects.filter(
        #         puzzle_pk=self.pk, possibilities='[]',
        #         position__startswith=str(i))
        pass

    def get_possibilities(self, puzzle, i, j):
        # returns all possibilities for a given cell
        # TODO: THIS SHOULD BE A METHOD OF THE PUZZLE_CELL CLASS!! MODIFY

        cell_poss = set(ALL_POSS)
        row = self.get_row(puzzle, i)
        col = self.get_col(puzzle, j)
        sqr = self.get_sqr(puzzle, i, j)

        cell_poss = cell_poss.difference(set(row))
        cell_poss = cell_poss.difference(set(col))
        cell_poss = cell_poss.difference(set(sqr))

        return cell_poss

    # TODO: CLEAN CODE AFTER SOLVING MEDIUM DIFF TEST
    # TODO: MOVE GET_SQR, GET_COL, GET_ROW TO UTILS SO IT CAN BE USED IN OTHER
    #       CLASSES (MANY CHANGES, MEDITATE)
    # TODO: WRITE SINGLE POS ALGORITHM
    # TODO: WRITE UPDATE CELL POSSIBILITIES RECURSIVE METHOD
    # TODO: OVERRIDE __STR__ METHOD
    # TODO: CHANGE UNSOLVED AND SOLVED PUZZLE FIELD TYPES BY ARRAYFIELD
    # TODO: WRITE METHOD THAT TAKES A PUZZLE, I, J AND A STRING AND CALCULATES
    #       THE POSSIBILITIES FOR THAT ROW, COL OR SQR (CALC_POSS)
    # TODO: SINGLE_CAND_ALGO IS ALSO UPDATING THE POSSIBILITIES. CHECK HOW I
    #       CAN SEPARATE THOSE TWO PROCESSES. ONCE I FIND ONE OR MULTIPLE
    #       VALUES USING A CERTAIN ALGO I CAN UPDATE THE POSS IN A METHOD. IN
    #       ANOTHER METHOD I CAN RUN A QUERY TO SEE IF THERE ARE ANY CELLS WITH
    #       ONLY ONE POSSIBILITY
    # TODO: FIX BUG. NOT ALL PUZZLE CELLS ARE BEING CREATED. THIS IS BECAUSE
    #       THE WAY THE SOLVE METHOD IS IMPLEMENTED ONLY THE MISSING PUZZLE
    #       CELLS GET TO BE CREATED. THINK IF YOU CAN WORK LIKE THIS OR IF IT
    #       WOULD BE BETTER TO CREATE ALL PUZZLE CELLS EVEN IF THEIR VALUE IS
    #       KNOWN.


class PuzzleCell(models.Model):
    puzzle_pk = models.IntegerField()
    value = models.IntegerField(default=0, blank=True, null=True)
    possibilities = models.CharField(
        default='[]', max_length=50, blank=True, null=True)
    filled = models.BooleanField(default=False)
    # position = models.CharField(max_length=2, blank=True, null=True)
    row = models.IntegerField(default=-1, blank=True)
    col = models.IntegerField(default=-1, blank=True)

    def __str__(self):
        return "v:%i - r:%i - c:%i" % (self.value, self.row, self.col)
