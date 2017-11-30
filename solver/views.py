import numpy as np
import time

from collections import OrderedDict
from django.shortcuts import render
from silk.profiling.profiler import silk_profile

from .models import SudokuPuzzle
from .tasks import solve_puzzle

TESTS = ('easy', 'medium', 'hard')
POLL_FREQ = 1  # poll frequency. One poll every POLL_FREQ seconds
POLL_TIMEOUT = 20  # time to wait before giving up on a puzzle


def choose_method(request):
    return render(request, 'choose_method.html')


def input_numbers(request):
    return render(request, 'input_numbers.html')


@silk_profile()
def test_solver(request):
    global TESTS
    unsolved_db = {}
    solved_db = {}
    unsolved_disp = {}
    passed_test = {}
    context = {}
    context["tests"] = OrderedDict({})
    celery_res = {}

    for test in TESTS:
        f = open('static/txt/test_%s.txt' % test)
        # sets key in this dictionaries to the name of the difficulty and the
        # value as an empty puzzle
        unsolved_db[test] = []
        solved_db[test] = []
        unsolved_disp[test] = []
        f.readline()  # first line should contain 'UNSOLVED' so we skip it

        for i in range(9):
            row = f.readline()
            row = row[0:-1]  # remove /n at the end
            unsolved_db[test].append([])  # appends an empty row to
            # the puzzle

            for j in range(9):
                unsolved_db[test][i].append(int(row[j]))
                # appends a number to the row

            row = row.replace('0', ' ')
            unsolved_disp[test].append(row)

        f.readline()  # skips line with 'SOLVED' text

        for i in range(9):
            row = f.readline()
            row = row[0:-1]  # remove /n at the end
            solved_db[test].append([])

            for j in range(9):
                solved_db[test][i].append(int(row[j]))

        f.close()
        puzzle = SudokuPuzzle(unsolved_puzzle=unsolved_db[test])
        puzzle.save()
        celery_res[test] = solve_puzzle.delay(puzzle.pk)

        context["tests"][test] = {
            "unsolved": unsolved_disp[test],
            "solved": unsolved_disp[test],
            "passed_test": False,
            "solving_time": 0.0}

    timeout = time.time() + POLL_TIMEOUT
    while True:
        for k, v in celery_res.items():
            if v.ready():
                puzzle = SudokuPuzzle.objects.get(pk=int(v.result))
                if puzzle.solved and \
                        np.array_equal(solved_db[k], puzzle.solved_puzzle):
                    passed_test = True
                else:
                    passed_test = False

                context["tests"][k].update({
                    "solved": puzzle.solved_puzzle,
                    "passed_test": passed_test,
                    "solving_time": puzzle.solving_time})
                del celery_res[k]

        if not len(celery_res) or time.time() > timeout:
            break
        else:
            time.sleep(POLL_FREQ)

    return render(request, 'test_solver.html', context)
