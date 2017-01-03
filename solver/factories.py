import factory
from . import models
from sudoku_solver import utils

EASY_PUZZLE = (
    (0, 0, 0, 7, 0, 0, 4, 2, 8),
    (7, 1, 4, 8, 0, 0, 0, 5, 0),
    (2, 0, 0, 9, 4, 0, 0, 1, 0),
    (8, 9, 0, 0, 0, 0, 0, 0, 1),
    (0, 0, 2, 0, 6, 0, 7, 0, 0),
    (6, 0, 0, 0, 0, 0, 0, 4, 9),
    (0, 2, 0, 0, 8, 4, 0, 0, 5),
    (0, 5, 0, 0, 0, 2, 1, 7, 4),
    (4, 6, 9, 0, 0, 7, 0, 0, 0)
)


class SudokuPuzzleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SudokuPuzzle

    unsolved_puzzle = utils.clone_list(list(EASY_PUZZLE))
    solved_puzzle = factory.LazyAttribute(
        lambda obj: utils.clone_list(obj.unsolved_puzzle))


class PuzzleCellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PuzzleCell

    puzzle = factory.SubFactory(SudokuPuzzleFactory)
    row = 0
    col = 0
