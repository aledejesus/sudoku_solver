from .models import SudokuPuzzle
from celery import shared_task


@shared_task
def solve_puzzle(puzzle_pk):
    """ Calls SudokuPuzzle.solve(). This is done
        to make the puzzle solving asynchronously.
    """
    puzzle = SudokuPuzzle.objects.get(pk=int(puzzle_pk))
    puzzle.solve()
    return puzzle_pk
