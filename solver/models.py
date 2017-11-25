from __future__ import unicode_literals
from django.db import models
import numpy as np
from sudoku_solver import utils
from django.contrib.postgres.fields import ArrayField
import copy
from timeit import default_timer as timer
from django.db.models import Q
from silk.profiling.profiler import silk_profile

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
    (6, 6, 8, 8))  # SQR8

ALL_POSS = frozenset(range(1, 10))  # all possibilities
MIN_CLUES = 17  # minimum clue count


class SudokuPuzzle(models.Model):
    unsolved_puzzle = ArrayField(
        base_field=ArrayField(
            base_field=models.IntegerField(), size=9),
        size=9)

    solved_puzzle = ArrayField(
        base_field=ArrayField(
            base_field=models.IntegerField(), size=9, blank=True, null=True,
            default=list()),
        size=9, blank=True, null=True, default=list())
    solved = models.BooleanField(default=False)
    correct = models.BooleanField(default=True)
    missing_vals_pos = ArrayField(
        base_field=ArrayField(
                base_field=models.IntegerField(), size=2,
                blank=True, null=True),
        blank=True, null=True)
    solving_time = models.FloatField(default=float(0.0))

    @silk_profile()
    def __str__(self):
        try:
            return "pk:%i - solved:%s" % (self.pk, self.solved)
        except TypeError:
            return "pk:unsaved - solved:%s" % self.solved

    @silk_profile()
    def solve(self):
        #  MAIN SOLVING FLOW. CALL ALGO FUNCTIONS/METHODS FROM HERE
        self.solved_puzzle = copy.deepcopy(self.unsolved_puzzle)
        self.set_missing_vals_pos()

        if not self.is_correct():
            self.save()
            return False

        start = timer()
        self.create_puzzle_cells()
        qty_vals_bef = 0
        qty_vals_aft = 0

        # if values were found run again
        while True:
            qty_vals_bef = self.get_known_vals_qty()
            # known vals qty BEFORE running solving methods

            puzzle_cells = None

            while True:
                puzzle_cells = PuzzleCell.objects.filter(
                    puzzle=self, filled=False)

                for cell in puzzle_cells:
                    found = self.rec_sca_call(cell)

                    if found:
                        break
                else:
                    break

            while True:
                puzzle_cells = PuzzleCell.objects.filter(
                    puzzle=self, filled=False)

                for cell in puzzle_cells:
                    found = self.single_pos_algo(cell)
                    if found:
                        break
                else:
                    break

            qty_vals_aft = self.get_known_vals_qty()
            # known vals qty AFTER running solving methods

            if not (qty_vals_bef < qty_vals_aft):
                break

        end = timer()
        self.solving_time = end - start
        self.solved = True
        if not self.is_correct():
            return False
        self.save()
        return True

    @silk_profile()
    def get_row_q(self, i):
        """ Gets the row's Q object

            Args:
                - i (int): row zero index

            Returns:
                - django.db.models.Q: filter params to get
                    the ith row.
        """
        return Q(row=i)

    @silk_profile()
    def get_row(self, i):
        """ Gets the known numbers in the ith row. Doesn't use
            get_row_q to avoid unnecessary database hit.

            Args:
                - i (int): row zero index

            Returns:
                - list: contains the row's known numbers
        """
        return utils.remove_zeroes(self.solved_puzzle[i])

    @silk_profile()
    def get_col_q(self, j):
        """ Gets the column's Q object.

            Args:
                - j (int): column's zero index

            Returns:
                - django.db.models.Q: filter params to get
                    the ith column.
        """
        return Q(col=j)

    @silk_profile()
    def get_col(self, j):
        """ Gets the known numbers in the jth column. Doesn't use
            get_col_q to avoid unnecessary database hit.

            Args:
                - j (int): column zero index

            Returns:
                - list: contains the column's known numbers
        """
        np_arr = np.array(self.solved_puzzle)
        return utils.remove_zeroes(np_arr[:, j].tolist())

    @silk_profile()
    def get_sqr_def(self, i, j):
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
            raise ValueError("Invalid square")

        return sqr_boundaries

    @silk_profile()
    def get_sqr_q(self, i, j):
        """ Gets the square's Q object.

            Args:
                - i (int): row zero index
                - j (int): column zero index

            Returns:
                - django.db.models.Q: filter params to get
                    the square of i x j.
        """
        sqr_def = self.get_sqr_def(i, j)

        return Q(row__gte=sqr_def[0],  col__gte=sqr_def[1]) & \
            Q(row__lte=sqr_def[2], col__lte=sqr_def[3])

    @silk_profile()
    def get_sqr(self, i, j):
        """ Gets the square's known values. Doesn't use
            qet_sqr_q to avoid extra database hit.

            Args:
                - i (int): row zero index
                - j (int): column zero index

            Returns:
                - list: contains known square numbers.
        """
        sqr_boundaries = self.get_sqr_def(i, j)

        np_arr = np.array(self.solved_puzzle)
        sqr = np_arr[
            sqr_boundaries[0]:sqr_boundaries[2]+1,
            sqr_boundaries[1]:sqr_boundaries[3]+1]

        # np.ravel puts array values in a 1D list
        return utils.remove_zeroes(np.ravel(sqr).tolist())

    @silk_profile()
    def create_puzzle_cells(self, auto_fill=True):
        to_create = []
        for i in range(9):
            for j in range(9):
                cell = PuzzleCell(puzzle=self, row=i, col=j)

                if self.solved_puzzle[i][j] == 0:
                    cell_poss = cell.determine_possibilities(self)
                    cell.update_possibilities(cell_poss)

                    if auto_fill and len(cell_poss) == 1:
                        cell = self.single_cand_algo(cell, save=False)

                else:
                    cell.value = self.solved_puzzle[i][j]
                    cell.filled = True

                to_create.append(cell)
        PuzzleCell.objects.bulk_create(to_create)

    @silk_profile()
    def single_cand_algo(self, cell, save=True):
        """ Applies the single candidate algorithm to a cell.

            Args:
                - cell (PuzzleCell): cell to apply the algorithm to.
                - save (bool): whether to save the instance
                    or return it. This is a temporary argument and will
                    be removed after issue #121 is solved.

            Returns:
                PuzzleCell when save is False
        """

        cell.value = cell.possibilities[0]
        cell.filled = True
        self.solved_puzzle[
            cell.row][cell.col] = cell.value  # add value to puzzle if found

        if save:
            cell.save()
        else:
            return cell

    @silk_profile()
    def set_missing_vals_pos(self):
        self.missing_vals_pos = list()

        for i in range(9):
            for j in range(9):
                if self.solved_puzzle[i][j] == 0:
                    self.missing_vals_pos.append(list([i, j]))

    @silk_profile()
    def get_known_vals_qty(self):
        """ Gets the quantity of known values in the puzzle.

            No arguments nor return values.
        """
        return len(utils.remove_zeroes(np.ravel(
            self.solved_puzzle).tolist()))

    @silk_profile()
    def get_related_cells(self, cell, filled=False):
        """ Gets the related cells of a given cell.

            Args:
                - cell (PuzzleCell)
                - filled (bool or None): True if only filled cells
                    are desired. False if only unfilled cells are desired.
                    None if all related cells are desired.

            Returns:
                - django.db.models.query.QuerySet: contains all
                    related cell objects.
        """
        gen_dict = {'puzzle': self}

        if filled in [True, False]:
            gen_dict['filled'] = filled

        q_gen = Q(**gen_dict)

        return PuzzleCell.objects.filter(
            q_gen, (self.get_row_q(cell.row) | self.get_col_q(cell.col) |
                    self.get_sqr_q(cell.row, cell.col))).\
            distinct().exclude(pk=cell.pk)

    @silk_profile()
    def rec_sca_call(self, cell):
        """
            Recursive single candidate algorithm (single_cand_algo) call.
        """

        cell_poss = cell.determine_possibilities(self)
        cell.update_possibilities(cell_poss)
        cell.save()
        vals_found = False

        if len(cell_poss) == 1:
                vals_found = True
                self.single_cand_algo(cell)

                for related_cell in list(self.get_related_cells(cell)):
                    if self.solved_puzzle[related_cell.row][
                            related_cell.col] == 0:
                        self.rec_sca_call(related_cell)

        return vals_found

    @silk_profile()
    def single_pos_algo(self, cell):
        """
            Applies the single position algorithm to the provided cell.

            Args:
                - cell (PuzzleCell)

            Returns:
                - bool: True if values found
        """

        q_gen = Q(puzzle=self)
        q_col = self.get_col_q(cell.col)
        q_row = self.get_row_q(cell.row)
        q_sqr = self.get_sqr_q(cell.col, cell.row)

        col_cells = PuzzleCell.objects.filter(
            q_gen, q_col).exclude(pk=cell.pk)
        row_cells = PuzzleCell.objects.filter(
            q_gen, q_row).exclude(pk=cell.pk)
        sqr_cells = PuzzleCell.objects.filter(
            q_gen, q_sqr).exclude(pk=cell.pk)
        related_cells_lst = [
            list(col_cells),
            list(row_cells),
            list(sqr_cells)]

        for related_cells in related_cells_lst:
            repeated_poss = set()
            poss = set(cell.possibilities)

            for related_cell in related_cells:
                if related_cell.filled:
                    known_poss = set([related_cell.value])
                else:
                    known_poss = set(related_cell.possibilities)
                poss = poss.difference(known_poss)
                # repeated_poss = repeated_poss.update(known_poss)
                # REVIEW THIS APPROACH ^
                # len(poss) == 0 means no unique possibilities
                if len(poss) == 0:
                    break

            else:
                if len(poss) == 1:
                    cell.possibilities = list(poss)
                    self.single_cand_algo(cell)
                    return True

                else:
                    raise ValueError("Invalid number of unique possiblities")

    @silk_profile()
    def is_correct(self):
        """
            Determines if numbers in puzzle don't repeat in the same square,
            row or col. For solved puzzles also checks if amount of solved
            cells is 81.

            Args:
                None
            Returns:
                - bool: whether puzzle is correct or not.
         """
        if self.get_known_vals_qty() < MIN_CLUES:
            self.correct = False

        else:
            for idx in range(9):
                sqr = self.get_sqr(SQUARE_DEFS[idx][0], SQUARE_DEFS[idx][1])
                row = self.get_row(idx)
                col = self.get_col(idx)

                for lst in [sqr, row, col]:
                    unique_vals = set(lst)

                    if not unique_vals.issubset(ALL_POSS) or\
                            len(lst) != len(unique_vals) or\
                            (self.solved and (len(unique_vals) != 9)):
                        self.correct = False
                        return self.correct
            self.correct = True
        return self.correct


class PuzzleCell(models.Model):
    puzzle = models.ForeignKey(
        SudokuPuzzle, default=None, on_delete=models.CASCADE)
    value = models.IntegerField(default=0, blank=True, null=True)
    possibilities = ArrayField(
        base_field=models.IntegerField(), size=9,
        blank=True, null=True, default=list())
    filled = models.BooleanField(default=False)
    row = models.IntegerField(default=-1, blank=True)
    col = models.IntegerField(default=-1, blank=True)

    def __str__(self):
        return "v:%i - r:%i - c:%i" % (self.value, self.row, self.col)


    @silk_profile()
    def determine_possibilities(self, puzzle):
        """ Determines all possibilities for a given cell.

            Args:
                - puzzle: SudokuPuzzle instance. It is passed as
                    an argument given that the related instance
                    may not be saved.
        """

        cell_poss = set(ALL_POSS)
        row = puzzle.get_row(self.row)
        col = puzzle.get_col(self.col)
        sqr = puzzle.get_sqr(self.row, self.col)

        cell_poss = cell_poss.difference(set(row))
        cell_poss = cell_poss.difference(set(col))
        cell_poss = cell_poss.difference(set(sqr))

        if len(cell_poss) < 1 or len(cell_poss) > 9:
            raise Exception("Invalid number of possibilities")

        return cell_poss

    @silk_profile()
    def update_possibilities(self, cell_poss):
        self.possibilities = list(cell_poss)
