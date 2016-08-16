from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.SudokuPuzzle)
admin.site.register(models.PuzzleCell)
