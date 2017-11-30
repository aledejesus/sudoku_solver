from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sudoku_solver.settings')
app = Celery('sudoku_solver', backend='rpc://')
app.autodiscover_tasks()


@app.task
def test_task():
    return 1+2
