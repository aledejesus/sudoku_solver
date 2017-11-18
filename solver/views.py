from django.shortcuts import render
from .models import SudokuPuzzle
from collections import OrderedDict
import numpy as np
from silk.profiling.profiler import silk_profile


def choose_method(request):
    return render(request, 'choose_method.html')


def input_numbers(request):
    return render(request, 'input_numbers.html')


@silk_profile()
def test_solver(request):
    tests = ['easy', 'medium', 'hard']
    unsolved_db = {}
    solved_db = {}
    unsolved_disp = {}
    passed_test = {}
    context = {}
    context["tests"] = OrderedDict({})

    for test in tests:
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
        puzzle.solve()

        if puzzle.solved and \
                np.array_equal(solved_db[test], puzzle.solved_puzzle):
            passed_test[test] = True
        else:
            passed_test[test] = False

        context["tests"][test] = {
            "unsolved": unsolved_disp[test],
            "solved": puzzle.solved_puzzle,
            "passed_test": passed_test[test],
            "solving_time": puzzle.solving_time}

    return render(request, 'test_solver.html', context)
