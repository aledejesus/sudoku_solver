from django.shortcuts import render
from .models import SudokuPuzzle
import json


def choose_method(request):
    return render(request, 'choose_method.html')


def input_numbers(request):
    return render(request, 'input_numbers.html')


def test_solver(request):
    f = open('static/txt/test_easy.txt')
    unsolved_easy_db = []
    solved_easy_db = []
    unsolved_easy_disp = []
    f.readline()  # first line should contain 'UNSOLVED' so we skip it

    for i in range(9):
        row = f.readline()
        row = row[0:-1]  # remove /n at the end
        unsolved_easy_db.append([])

        for j in range(9):
            unsolved_easy_db[i].append(int(row[j]))

        row = row.replace('0', ' ')
        unsolved_easy_disp.append(row)

    f.readline()  # skips line with 'SOLVED' text

    for i in range(9):
        row = f.readline()
        row = row[0:-1]  # remove /n at the end
        solved_easy_db.append([])

        for j in range(9):
            solved_easy_db[i].append(int(row[j]))

    f.close()
    puzzle = SudokuPuzzle(unsolved_puzzle=json.dumps(unsolved_easy_db))
    puzzle.save()
    puzzle.solve()

    # TODO: research if this is the best way to compare solutions. STACKOVERF
    if (json.dumps(solved_easy_db) == puzzle.solved_puzzle):
        passed_easy_test = True
    else:
        passed_easy_test = False

    context = {
        "unsolved_easy": unsolved_easy_disp,
        "solved_easy": json.loads(puzzle.solved_puzzle),
        "passed_easy_test": passed_easy_test
    }

    # TODO: DELETE PUZZLES FROM DATABASE AFTER TEST

    return render(request, 'test_solver.html', context)
