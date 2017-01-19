import factory
import copy
from . import models

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

    unsolved_puzzle = factory.LazyAttribute(
        lambda obj: [list(item) for item in EASY_PUZZLE])
    solved_puzzle = factory.LazyAttribute(
        lambda obj: copy.deepcopy(obj.unsolved_puzzle))


class PuzzleCellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PuzzleCell

    puzzle = factory.SubFactory(SudokuPuzzleFactory)
    row = 0
    col = 0


def prov_puzzle_factory():
    # provisional SudokuPuzzle factory
    puzzle = models.SudokuPuzzle.objects.create(
        unsolved_puzzle=[list(it) for it in EASY_PUZZLE])
    puzzle.solved_puzzle = copy.deepcopy(puzzle.unsolved_puzzle)
    puzzle.save()

    return puzzle
