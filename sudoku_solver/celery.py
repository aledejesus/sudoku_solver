from celery import Celery

app = Celery()


@app.task
def solve_puzzle(puzzle):
    """ Calls SudokuPuzzle.solve(). This is done
        to make the puzzle solving asynchronously.
    """
    puzzle.solve()
    return puzzle
