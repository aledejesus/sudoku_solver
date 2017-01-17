from django.test import TestCase
import numpy as np
from . import utils


class UtilsTestCase(TestCase):
    def test_remove_zeroes(self):
        arr = [0, 1, 2, 0, 3, 0]
        exp_arr = [1, 2, 3]  # expected list
        act_arr = utils.remove_zeroes(arr)  # actual list

        self.assertTrue(np.array_equal(exp_arr, act_arr))

    def test_clone_list(self):
        arr2d = [[1, 2], [3, 4]]
        act_arr2d = utils.clone_list(arr2d, True)

        self.assertFalse(arr2d is act_arr2d)
        self.assertTrue(np.array_equal(arr2d, act_arr2d))
