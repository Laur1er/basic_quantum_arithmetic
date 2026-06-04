from basic_quantum_arithmetic import (
    quantum_addition,
    quantum_addition_modulo,
    quantum_product_modulo,
    quantum_subtraction,
    quantum_exponential,
)

import numpy as np
import pytest


@pytest.mark.parametrize(
    "x, y, mod", [(5, 10, 12), (2, 12, 24), (24, 13, 27), (55, 19, 61)]
)
def test_addition_modulo(x, y, mod):
    assert quantum_addition_modulo(x, y, mod) == (x + y) % mod


@pytest.mark.parametrize("x, y", [(5, 10), (2, 12), (24, 13), (55, 19)])
def test_addition(x, y):
    assert quantum_addition(x, y) == x + y


@pytest.mark.parametrize("x,a,mod", [(5, 0, 12), (2, 12, 24), (4, 7, 8)])
def test_product_modulo(x, a, mod):
    assert quantum_product_modulo(a, x, mod) == (a * x) % mod


@pytest.mark.parametrize("x,y", [(5, 10), (2, 12), (24, 13), (55, 19)])
def test_subtraction(x, y):
    assert quantum_subtraction(x, y) == np.abs(x - y)


@pytest.mark.parametrize("a,x,mod", [(3, 7, 7), (2, 8, 15), (5, 2, 9)])
def test_exponential(a, x, mod):
    assert quantum_exponential(a, x, mod) == (a**x) % mod
