from django.test import TestCase, Client
from factories import (
    SudokuPuzzleFactory, PuzzleCellFactory, prov_puzzle_factory)
import numpy as np
from . import models
from .templatetags.return_item import return_item


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
        known_vals = self.puzzle.get_known_vals_qty()
        self.assertTrue(known_vals < 81)

        self.puzzle.solve()
        self.assertTrue(self.puzzle.solved)
        known_vals = self.puzzle.get_known_vals_qty()
        self.assertTrue(known_vals == 81)
        self.assertTrue(self.puzzle.solving_time > 0.0)

    def test_puzzle_not_solved(self):
        self.assertFalse(self.puzzle.solved)
        known_vals = self.puzzle.get_known_vals_qty()
        self.assertTrue(known_vals < 81)

        lst = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(3):  # replace fisrt 3 rows with lst
            self.puzzle.unsolved_puzzle[i] = list(lst)

        self.puzzle.save()
        self.puzzle.solve()
        known_vals = self.puzzle.get_known_vals_qty()
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
        self.puzzle.solved_puzzle[0] = list(lst)
        self.puzzle.save()
        first_cell = models.PuzzleCell.objects.create(
            puzzle=self.puzzle, row=0, col=0)
        self.assertFalse(first_cell.filled)
        self.assertEqual(first_cell.value, 0)

        cell_poss = first_cell.determine_possibilities()
        first_cell.update_possibilities(cell_poss)
        self.puzzle.single_cand_algo(first_cell)
        first_cell = models.PuzzleCell.objects.get(
            puzzle=self.puzzle, row=i, col=j)
        self.assertTrue(first_cell.filled)
        self.assertEqual(first_cell.value, expected_val)

    def test_set_missing_vals_pos(self):
        self.assertTrue(self.puzzle.missing_vals_pos is None)

        self.puzzle.set_missing_vals_pos()
        self.assertEqual(len(self.puzzle.missing_vals_pos), 46)

    def test_get_known_vals_qty(self):
        exp_qty = 35  # expected quantity
        act_qty = self.puzzle.get_known_vals_qty()  # actual quantity

        self.assertEqual(exp_qty, act_qty)


class PuzzleCellTestCase(TestCase):
    def setUp(self):
        # self.puzzle = SudokuPuzzleFactory.create()
        self.puzzle = prov_puzzle_factory()
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


class SolverViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_choose_method(self):
        response = self.client.get('/solver/')
        self.assertEqual(response.status_code, 200)

    def test_input_numbers(self):
        response = self.client.get('/solver/numbers/')
        self.assertEqual(response.status_code, 200)

    def test_test_solver(self):
        TESTS = ('easy', 'medium')
        response = self.client.get('/solver/test_solver/')
        self.assertEqual(response.status_code, 200)
        correct_ids = list()

        for test in TESTS:
            id_unsolved = 'id_grid_%s_unsolved' % test
            id_solved = 'id_grid_%s_solved' % test

            pos_id_unsolved = response.content.find(id_unsolved)
            pos_id_solved = response.content.find(id_solved)

            if pos_id_unsolved > -1:
                start = pos_id_unsolved + len(id_unsolved)
                pos_id_unsolved = response.content.find(id_unsolved, start)

                if pos_id_unsolved == -1:
                    correct_ids.append(id_unsolved)

            if pos_id_solved > -1:
                start = pos_id_solved + len(id_solved)
                pos_id_solved = response.content.find(id_solved, start)

                if pos_id_solved == -1:
                    correct_ids.append(id_solved)

        self.assertEqual(len(correct_ids), len(TESTS)*2)


class TemplateTagsTestCase(TestCase):
    def test_return_item_returns_space(self):
        arr = [0, 1, 2]
        i = 0

        res = return_item(arr, i)
        self.assertEqual(res, " ")

    def test_return_item_returns_int(self):
        arr = [0, 1, 2]
        i = 1

        res = return_item(arr, i)
        self.assertEqual(res, 1)

    def test_return_item_returns_none(self):
        arr = [0, 1, 2]
        i = 'whatever'

        res = return_item(arr, i)
        self.assertTrue(res is None)
