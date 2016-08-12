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

    f.close()
    puzzle = SudokuPuzzle(unsolved_puzzle=json.dumps(unsolved_easy_db))
    puzzle.save()
    puzzle.solve()

    # TODO: compare with solution in file

    context = {
        "unsolved_easy": unsolved_easy_disp,
        "solved_easy": json.loads(puzzle.solved_puzzle)
    }

    # TODO: DELETE PUZZLES FROM DATABASE AFTER TEST

    return render(request, 'test_solver.html', context)
