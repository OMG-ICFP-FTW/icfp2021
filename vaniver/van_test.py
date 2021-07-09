import pytest

from vaniver.search import check_line_intersection


def test_check_line_intersection_1():
    """Checks some lines."""
    assert(not(check_line_intersection([[0,0], [1,1]], [[2,0], [3,1]])))
    assert(not(check_line_intersection([[0,0], [0,0]], [[2,0], [3,1]])))
    # Intersecting ones
    assert(check_line_intersection([[0,0], [1,1]], [[1,0], [0,1]]))
    assert(check_line_intersection([[0,0], [1,1]], [[1,0], [1,1]]))
    assert(check_line_intersection([[0,0], [1,1]], [[-1,0], [1,0]]))