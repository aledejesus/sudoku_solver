from django.test import TestCase
from factories import SudokuPuzzleFactory, PuzzleCellFactory
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

    def test_get_sqr_with_valid_cell(self):
        expected_sqr = [7, 1, 4, 2]
        actual_sqr = self.puzzle.get_sqr(0, 0)
        self.assertTrue(np.array_equal(expected_sqr, actual_sqr))

    def test_get_sqr_with_invalid_cell(self):
        with self.assertRaises(Exception):
            self.puzzle.get_sqr(-1, -1)

    def test_create_puzzle_cells(self):
        i = 0
        j = 0
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 0)

        self.puzzle.create_puzzle_cells()
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 81)

        first_cell = models.PuzzleCell.objects.get(
            puzzle=self.puzzle, row=i, col=j)
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
            puzzle=self.puzzle, row=i, col=j)
        self.assertFalse(first_cell.filled)
        self.assertEqual(first_cell.value, 0)

        cell_poss = first_cell.determine_possibilities()
        self.puzzle.single_cand_algo(first_cell, cell_poss)
        first_cell = models.PuzzleCell.objects.get(
            puzzle=self.puzzle, row=i, col=j)
        self.assertTrue(first_cell.filled)
        self.assertEqual(first_cell.value, expected_val)

    def test_set_missing_vals_pos(self):
        self.assertEqual(len(self.puzzle.missing_vals_pos), 0)

        self.puzzle.set_missing_vals_pos()
        self.assertEqual(len(self.puzzle.missing_vals_pos), 46)


class PuzzleCellTestCase(TestCase):
    def setUp(self):
        self.cell = PuzzleCellFactory()
        self.cell.puzzle.solved_puzzle = self.cell.puzzle.unsolved_puzzle
        self.cell.puzzle.save()
        # self.cell.save()

    def test_determine_possibilities(self):
        exp_poss = [3, 5, 9]  # expected possibilities
        cell_poss = self.cell.determine_possibilities()
        self.assertEqual(len(set(exp_poss).difference(set(cell_poss))), 0)

    def test_determine_possibilities_raises_exception(self):
        i = 0
        self.cell.puzzle.solved_puzzle[i] = [9, 3, 6, 7, 5, 1, 4, 2, 8]
        with self.assertRaises(Exception):
            self.cell.determine_possibilities()

    def test_update_possibilities(self):
        exp_poss = []
        self.assertEqual(len(set(exp_poss).difference(
            set(self.cell.possibilities))), 0)

        cell_poss = set([1, 2, 3])
        self.cell.update_possibilities(cell_poss)
        self.assertEqual(len(set(cell_poss).difference(
            set(self.cell.possibilities))), 0)
