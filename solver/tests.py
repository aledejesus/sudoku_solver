from django.test import TestCase
from factories import SudokuPuzzleFactory
import numpy as np
from . import models
from sudoku_solver import utils


class SudokuPuzzleTestCase(TestCase):
    def setUp(self):
        self.puzzle = SudokuPuzzleFactory()
        self.puzzle.solved_puzzle = self.puzzle.unsolved_puzzle
        self.puzzle.save()

    def test_solve(self):
        self.assertFalse(self.puzzle.solved)
        known_vals = len(utils.remove_zeroes(
            np.ravel(self.puzzle.solved_puzzle).tolist()))
        self.assertTrue(known_vals < 81)

        self.puzzle.solve()
        self.assertTrue(self.puzzle.solved)
        known_vals = len(utils.remove_zeroes(
            np.ravel(self.puzzle.solved_puzzle).tolist()))
        self.assertTrue(known_vals == 81)

    def test_get_row(self):
        expected_row = [7, 4, 2, 8]
        actual_row = self.puzzle.get_row(0)
        self.assertTrue(np.array_equal(expected_row, actual_row))

    def test_get_col(self):
        expected_col = [7, 2, 8, 6, 4]
        actual_col = self.puzzle.get_col(0)
        self.assertTrue(np.array_equal(expected_col, actual_col))

    def test_get_sqr(self):
        expected_sqr = [7, 1, 4, 2]
        actual_sqr = self.puzzle.get_sqr(0, 0)
        self.assertTrue(np.array_equal(expected_sqr, actual_sqr))

    def test_create_puzzle_cells(self):
        cells = models.PuzzleCell.objects.filter(puzzle_pk=self.puzzle.pk)
        self.assertTrue(cells.count() == 0)

        self.puzzle.create_puzzle_cells()
        cells = models.PuzzleCell.objects.filter(puzzle_pk=self.puzzle.pk)
        self.assertTrue(cells.count() == 81)

        i = 0
        j = 0
        first_cell = models.PuzzleCell.objects.get(
            puzzle_pk=self.puzzle.pk, row=i, col=j)
        self.assertTrue(self.puzzle.unsolved_puzzle[i][j] == first_cell.value)

        if self.puzzle.unsolved_puzzle[i][j] == 0:
            self.assertFalse(first_cell.filled)
        else:
            self.assertTrue(first_cell.filled)
