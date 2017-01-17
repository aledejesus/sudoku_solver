from django.test import TestCase
from factories import (
    SudokuPuzzleFactory, PuzzleCellFactory, prov_puzzle_factory)
import numpy as np
from . import models
from sudoku_solver import utils


class SudokuPuzzleTestCase(TestCase):
    def setUp(self):
        # self.puzzle = SudokuPuzzleFactory.create()
        self.puzzle = prov_puzzle_factory()

    def test_str_with_saved_puzzle(self):
        pk = self.puzzle.pk
        solved = self.puzzle.solved

        self.assertEqual(
            "pk:%i - solved:%s" % (pk, solved), self.puzzle.__str__())

    def test_str_with_unsaved_puzzle(self):
        puzzle = SudokuPuzzleFactory.build()

        self.assertEqual(
            "pk:unsaved - solved:%s" % puzzle.solved, puzzle.__str__())

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

    def test_puzzle_not_solved(self):
        self.assertFalse(self.puzzle.solved)
        known_vals = len(utils.remove_zeroes(
            np.ravel(self.puzzle.solved_puzzle).tolist()))
        self.assertTrue(known_vals < 81)

        lst = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(3):  # replace fisrt 3 rows with lst
            self.puzzle.unsolved_puzzle[i] = utils.clone_list(lst, False)

        self.puzzle.save()
        self.puzzle.solve()
        known_vals = len(utils.remove_zeroes(
            np.ravel(self.puzzle.solved_puzzle).tolist()))
        self.assertTrue(known_vals < 81)
        self.assertFalse(self.puzzle.solved)

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
        lst = [0, 3, 6, 7, 5, 1, 4, 2, 8]
        self.puzzle.solved_puzzle[0] = utils.clone_list(lst, False)
        self.puzzle.save()
        self.puzzle.create_puzzle_cells()
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
        self.assertTrue(self.puzzle.missing_vals_pos is None)

        self.puzzle.set_missing_vals_pos()
        self.assertEqual(len(self.puzzle.missing_vals_pos), 46)


class PuzzleCellTestCase(TestCase):
    def setUp(self):
        self.puzzle = SudokuPuzzleFactory.create()
        self.cell = PuzzleCellFactory(puzzle=self.puzzle)

    def test_str(self):
        val = self.cell.value
        row = self.cell.row
        col = self.cell.col

        self.assertEqual(
            "v:%i - r:%i - c:%i" % (val, row, col),
            self.cell.__str__())

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
