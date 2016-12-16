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
        self.puzzle.refresh_from_db()

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

    def test_get_sqr_with_valid_cell(self):
        expected_sqr = [7, 1, 4, 2]
        actual_sqr = self.puzzle.get_sqr(0, 0)
        self.assertTrue(np.array_equal(expected_sqr, actual_sqr))

    def test_get_sqr_with_invalid_cell(self):
        with self.assertRaises(Exception):
            self.puzzle.get_sqr(-1, -1)

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

    def test_single_cand_algo(self):
        i = 0
        j = 0
        expected_val = 9
        self.puzzle.create_puzzle_cells()
        self.puzzle.solved_puzzle[0] = [0, 3, 6, 7, 5, 1, 4, 2, 8]
        self.puzzle.save()
        first_cell = models.PuzzleCell.objects.get(
            puzzle_pk=self.puzzle.pk, row=i, col=j)
        self.assertFalse(first_cell.filled)
        self.assertEqual(first_cell.value, 0)

        cell_poss = self.puzzle.get_possibilities(i, j)
        self.puzzle.single_cand_algo(i, j, cell_poss)
        first_cell = models.PuzzleCell.objects.get(
            puzzle_pk=self.puzzle.pk, row=i, col=j)
        self.assertTrue(first_cell.filled)
        self.assertEqual(first_cell.value, expected_val)

    def test_update_possibilities(self):
        i = 0
        j = 0
        exp_poss = [3, 5, 9]  # expected possibilities
        self.puzzle.create_puzzle_cells()
        first_cell = models.PuzzleCell.objects.get(
            puzzle_pk=self.puzzle.pk, row=i, col=j)
        self.assertEqual(len(set(exp_poss).difference(
            set(first_cell.possibilities))), 0)

        exp_poss = [3, 9]
        self.puzzle.solved_puzzle[0] = [0, 0, 0, 7, 5, 1, 4, 2, 8]
        cell_poss = self.puzzle.get_possibilities(i, j)
        self.puzzle.update_possibilities(i, j, cell_poss)
        first_cell = models.PuzzleCell.objects.get(
            puzzle_pk=self.puzzle.pk, row=i, col=j)
        self.assertEqual(len(set(exp_poss).difference(
            set(first_cell.possibilities))), 0)

    def test_set_missing_vals_pos(self):
        self.assertEqual(len(self.puzzle.missing_vals_pos), 0)

        self.puzzle.set_missing_vals_pos()
        self.assertEqual(len(self.puzzle.missing_vals_pos), 46)

    def test_get_possibilities(self):
        i = 0
        j = 0
        exp_poss = [3, 5, 9]  # expected possibilities
        cell_poss = self.puzzle.get_possibilities(i, j)
        self.assertEqual(len(set(exp_poss).difference(set(cell_poss))), 0)

    def test_get_possibilities_raises_exception(self):
        i = 0
        j = 0
        self.puzzle.solved_puzzle[i] = [9, 3, 6, 7, 5, 1, 4, 2, 8]
        with self.assertRaises(Exception):
            self.puzzle.get_possibilities(i, j)
