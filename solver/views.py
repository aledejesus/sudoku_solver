from django.shortcuts import render
from .models import SudokuPuzzle
import json
from collections import OrderedDict


def choose_method(request):
    return render(request, 'choose_method.html')


def input_numbers(request):
    return render(request, 'input_numbers.html')


def test_solver(request):
    tests = ['easy', 'medium']
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

        # TODO: research if this is the best way to compare solutions. ST.OVERF
        if puzzle.solved and \
                json.dumps(solved_db[test]) == puzzle.solved_puzzle:
            passed_test[test] = True
        else:
            passed_test[test] = False

        context["tests"][test] = {
            "unsolved": unsolved_disp[test],
            "solved": json.loads(puzzle.solved_puzzle),
            "passed_test": passed_test[test]
        }

    # TODO: DELETE PUZZLES FROM DATABASE AFTER TEST

    return render(request, 'test_solver.html', context)
