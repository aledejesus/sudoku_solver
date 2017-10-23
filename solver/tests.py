from django.test import TestCase, Client
from factories import (
    SudokuPuzzleFactory, PuzzleCellFactory)
import numpy as np
from . import models
from .templatetags.return_item import return_item
from .templatetags.sudoku_grid import sudoku_grid
from django.db.models import Q


class SudokuPuzzleTestCase(TestCase):
    def setUp(self):
        self.puzzle = SudokuPuzzleFactory.create()

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

    def test_get_sqr(self):
        exp_sqr = [7, 1, 4, 2]
        act_sqr = self.puzzle.get_sqr(0, 0)
        self.assertTrue(np.array_equal(exp_sqr, act_sqr))

    def test_get_sqr_def_with_valid_cell(self):
        exp_sqr_def = [0, 0, 2, 2]
        act_sqr_def = self.puzzle.get_sqr_def(0, 0)
        self.assertTrue(np.array_equal(exp_sqr_def, act_sqr_def))

    def test_get_sqr_def_with_invalid_cell(self):
        with self.assertRaises(ValueError):
            self.puzzle.get_sqr_def(-1, -1)

    def test_create_puzzle_cells_auto_fill_on(self):
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 0)
        exp_vals = 35
        act_vals = self.puzzle.get_known_vals_qty()
        self.assertEqual(exp_vals, act_vals)

        self.puzzle.create_puzzle_cells()
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 81)
        exp_vals = 45
        act_vals = self.puzzle.get_known_vals_qty()
        self.assertEqual(exp_vals, act_vals)

        # Test a known value cell
        cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, filled=True).first()
        self.assertTrue(self.puzzle.solved_puzzle[
            cell.row][cell.col] == cell.value)
        self.assertTrue(cell.value != 0)

        # Test an unknown value cell
        cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, filled=False).first()
        self.assertTrue(self.puzzle.unsolved_puzzle[
            cell.row][cell.col] == cell.value)
        self.assertTrue(cell.value == 0)

    def test_create_puzzle_cells_auto_fill_off(self):
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 0)
        exp_vals = 35
        act_vals = self.puzzle.get_known_vals_qty()
        self.assertEqual(exp_vals, act_vals)

        self.puzzle.create_puzzle_cells(auto_fill=False)
        cells = models.PuzzleCell.objects.filter(puzzle=self.puzzle)
        self.assertTrue(cells.count() == 81)
        exp_vals = 35
        act_vals = self.puzzle.get_known_vals_qty()
        self.assertEqual(exp_vals, act_vals)

        # Test a known value cell
        cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, filled=True).first()
        self.assertTrue(self.puzzle.solved_puzzle[
            cell.row][cell.col] == cell.value)
        self.assertTrue(cell.value != 0)

        # Test an unknown value cell
        cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, filled=False).first()
        self.assertTrue(self.puzzle.unsolved_puzzle[
            cell.row][cell.col] == cell.value)
        self.assertTrue(cell.value == 0)

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

    def test_get_sqr_def(self):
        i = 1
        j = 0
        exp_sqr = [0, 0, 2, 2]
        act_sqr = self.puzzle.get_sqr_def(i, j)

        self.assertTrue(np.array_equal(exp_sqr, act_sqr))

    def test_rec_sca_call(self):
        i = 0
        j = 0
        emp_arr = [[0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.puzzle.solved_puzzle = list(emp_arr*9)
        self.puzzle.save()

        first_row = [0, 3, 6, 7, 5, 1, 4, 2, 8]
        first_col = [0, 7, 2, 8, 5, 6, 1, 0, 4]
        first_sqr = [[0, 3, 6], [7, 1, 4], [2, 0, 5]]
        np_arr = np.array(self.puzzle.solved_puzzle)
        np_arr[:3, :3] = list(first_sqr)
        np_arr[0] = list(first_row)
        np_arr[:, 0] = list(first_col)
        self.puzzle.solved_puzzle = np_arr.tolist()
        self.puzzle.save()

        self.puzzle.create_puzzle_cells(auto_fill=False)
        EXP_VALS_BEF = 18
        act_vals_bef = self.puzzle.get_known_vals_qty()
        self.assertEqual(EXP_VALS_BEF, act_vals_bef)

        EXP_VALS_AFT = 21
        cell = models.PuzzleCell.objects.get(puzzle=self.puzzle, row=i, col=j)
        self.puzzle.rec_sca_call(cell)
        act_vals_aft = self.puzzle.get_known_vals_qty()
        self.assertEqual(EXP_VALS_AFT, act_vals_aft)

    def test_single_pos_algo(self):
        i = 0
        j = 0
        self.puzzle.create_puzzle_cells(auto_fill=False)

        fru_cells = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, row=i, filled=False)
        # ^ first row unsolved cells

        first_cell = fru_cells.get(col=j)
        self.assertTrue(first_cell)  # asserts cell (i,j) is in qs
        FC_VAL = 9  # first cell value

        # Remove FC_VAL from the possibilities of all cells
        # except from the possibilities of cell in (i,j)
        for cell in list(fru_cells):
            if cell.row != i and cell.col != j:
                if FC_VAL in cell.possibilities:
                    cell.possibilities.remove(FC_VAL)
                    cell.save()

        self.puzzle.single_pos_algo(first_cell)
        first_cell = models.PuzzleCell.objects.get(
            puzzle=self.puzzle, row=i, col=j)

        self.assertTrue(first_cell.filled)
        self.assertEqual(first_cell.value, FC_VAL)

    def test_single_pos_algo_raises_exception(self):
        i = 0
        j = 0
        self.puzzle.create_puzzle_cells(auto_fill=False)

        q_gen = Q(puzzle=self.puzzle, filled=False)
        q_col = self.puzzle.get_col_q(i)
        q_row = self.puzzle.get_row_q(j)
        q_sqr = self.puzzle.get_sqr_q(i, j)

        col_cells = models.PuzzleCell.objects.filter(
            q_gen, q_col)
        row_cells = models.PuzzleCell.objects.filter(
            q_gen, q_row)
        sqr_cells = models.PuzzleCell.objects.filter(
            q_gen, q_sqr)
        related_cells_lst = list(col_cells)
        related_cells_lst.extend(list(row_cells))
        related_cells_lst.extend(list(sqr_cells))

        first_cell = row_cells.get(col=j)
        self.assertTrue(first_cell)  # asserts cell (i,j) is in qs
        FC_UNIQUE_POSS = [3, 9]  # first cell unique possibilities

        # Remove FC_UNIQUE_POSS from the possibilities of all cells
        # except from the possibilities of cell in (i,j)
        for cell in related_cells_lst:
            if cell.pk != first_cell.pk:
                for u_poss in FC_UNIQUE_POSS:
                    if u_poss in cell.possibilities:
                        cell.possibilities.remove(u_poss)
                cell.save()

        with self.assertRaises(ValueError):
            self.puzzle.single_pos_algo(first_cell)

    def test_single_pos_algo_no_unique_poss(self):
        i = 0
        j = 0
        self.puzzle.create_puzzle_cells(auto_fill=False)

        q_gen = Q(puzzle=self.puzzle, filled=False)
        q_col = self.puzzle.get_col_q(i)
        q_row = self.puzzle.get_row_q(j)
        q_sqr = self.puzzle.get_sqr_q(i, j)

        col_cells = models.PuzzleCell.objects.filter(
            q_gen, q_col)
        row_cells = models.PuzzleCell.objects.filter(
            q_gen, q_row)
        sqr_cells = models.PuzzleCell.objects.filter(
            q_gen, q_sqr)
        related_cells_lst = list(col_cells)
        related_cells_lst.extend(list(row_cells))
        related_cells_lst.extend(list(sqr_cells))

        first_cell = row_cells.get(col=j)
        self.assertTrue(first_cell)  # asserts cell (i,j) is in qs
        FC_UNIQUE_POSS = range(1, 10)

        # Remove FC_UNIQUE_POSS from the possibilities of all cells
        # except from the possibilities of cell in (i,j)
        for cell in related_cells_lst:
            if cell.pk != first_cell.pk:
                cell.possibilities = list(FC_UNIQUE_POSS)
                cell.save()

        self.puzzle.single_pos_algo(first_cell)

        first_cell = models.PuzzleCell.objects.get(
            puzzle=self.puzzle, row=i, col=j)

        self.assertFalse(first_cell.filled)

    def test_get_row_q(self):
        """ Tests that get_row_q returns correct Q object """
        DESIRED_ROW = 0
        row_q = self.puzzle.get_row_q(DESIRED_ROW)

        self.assertEqual(len(row_q.children), 1)
        self.assertEqual(row_q.children[0][0], 'row')
        self.assertEqual(row_q.children[0][1], DESIRED_ROW)

    def test_get_col_q(self):
        """ Tests that get_col_q returns correct Q object """
        DESIRED_COL = 1
        col_q = self.puzzle.get_col_q(DESIRED_COL)

        self.assertEqual(len(col_q.children), 1)
        self.assertEqual(col_q.children[0][0], 'col')
        self.assertEqual(col_q.children[0][1], DESIRED_COL)

    def test_get_sqr_q(self):
        """ Tests that get_col_q returns correct Q object """
        I = 1  # row zero index
        J = 3  # col zero index
        EXP_CHILDREN = [
            ('row__gte', models.SQUARE_DEFS[1][0]),
            ('col__gte', models.SQUARE_DEFS[1][1]),
            ('row__lte', models.SQUARE_DEFS[1][2]),
            ('col__lte', models.SQUARE_DEFS[1][3])]
        # ^ expected sqr_q children

        sqr_q = self.puzzle.get_sqr_q(I, J)

        for child in sqr_q.children:
            self.assertTrue(child in EXP_CHILDREN)

    def test_get_related_cells_filled_true(self):
        """ Tests that get_related_cells returns only filled PuzzleCells. """
        EXP_REL_CELL_CNT = 14  # expected number of related cells
        self.puzzle.create_puzzle_cells()
        first_cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, row=0, col=0).first()
        related_cells = self.puzzle.get_related_cells(
            first_cell, filled=True)

        self.assertEqual(len(related_cells), EXP_REL_CELL_CNT)
        self.assertEqual(type(related_cells[0]), models.PuzzleCell)
        self.assertTrue(first_cell not in related_cells)

    def test_get_related_cells_filled_false(self):
        """ Tests that get_related_cells returns only unfilled PuzzleCells. """
        EXP_REL_CELL_CNT = 6  # expected number of related cells
        self.puzzle.create_puzzle_cells()
        first_cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, row=0, col=0).first()
        related_cells = self.puzzle.get_related_cells(
            first_cell, filled=False)

        self.assertEqual(len(related_cells), EXP_REL_CELL_CNT)
        self.assertEqual(type(related_cells[0]), models.PuzzleCell)
        self.assertTrue(first_cell not in related_cells)

    def test_get_related_cells_filled_none(self):
        """ Tests that get_related_cells returns all related PuzzleCells. """
        EXP_REL_CELL_CNT = 20  # expected number of related cells
        self.puzzle.create_puzzle_cells()
        first_cell = models.PuzzleCell.objects.filter(
            puzzle=self.puzzle, row=0, col=0).first()
        related_cells = self.puzzle.get_related_cells(
            first_cell, filled=None)

        self.assertEqual(len(related_cells), EXP_REL_CELL_CNT)
        self.assertEqual(type(related_cells[0]), models.PuzzleCell)
        self.assertTrue(first_cell not in related_cells)


class PuzzleCellTestCase(TestCase):
    def setUp(self):
        self.puzzle = SudokuPuzzleFactory.create()
        # self.puzzle = prov_puzzle_factory()
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


class ReturnItemFilterTestCase(TestCase):
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


class SudokuGridTemplateTagTestCase(TestCase):
    def test_sudoku_grid_without_key_without_numbers(self):
        """ Tests sudoku_grid without key and without numbers. """
        grid_id = "grid_id"

        res = sudoku_grid(grid_id)
        self.assertTrue(res["grid_id"] == "grid_id")
        self.assertTrue(len(res["numbers"]) == 0)

    def test_sudoku_grid_with_key_without_numbers(self):
        """ Tests sudoku_grid with key and without numbers. """
        grid_id = "grid_id_{{key}}"
        key = "test"

        res = sudoku_grid(grid_id, key)
        self.assertTrue(res["grid_id"] == "grid_id_%s" % key)
        self.assertTrue(len(res["numbers"]) == 0)

    def test_sudoku_grid_without_key_with_numbers(self):
        """ Tests sudoku_grid without key and with numbers. """
        grid_id = "grid_id"
        numbers = [1, 2, 3]

        res = sudoku_grid(grid_id, numbers=numbers)
        self.assertTrue(res["grid_id"] == "grid_id")
        self.assertTrue(res["numbers"] == numbers)

    def test_sudoku_grid_with_key_with_numbers(self):
        """ Tests sudoku_grid with key and with numbers. """
        grid_id = "grid_id_{{key}}"
        key = "test"
        numbers = [1, 2, 3]

        res = sudoku_grid(grid_id, key, numbers)
        self.assertTrue(res["grid_id"] == "grid_id_%s" % key)
        self.assertTrue(res["numbers"] == numbers)
