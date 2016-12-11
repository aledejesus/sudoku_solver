from django.test import TestCase
from factories import SudokuPuzzleFactory
import numpy as np


class SudokuPuzzleTestCase(TestCase):
    def setUp(self):
        self.puzzle = SudokuPuzzleFactory()

    def test_get_row(self):
        self.puzzle.solved_puzzle = self.puzzle.unsolved_puzzle
        expected_row = [7, 4, 2, 8]
        actual_row = self.puzzle.get_row(0)
        self.assertTrue(np.array_equal(expected_row, actual_row))
