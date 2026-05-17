from basic_quantum_arithmetic.addition import quantum_addition


def test_addition_modulo():

    x1, y1 = 5, 10
    x2, y2 = 2, 12
    x3, y3 = 24, 13
    x4, y4 = 55, 19

    exp1 = x1 + y1
    exp2 = x2 + y2
    exp3 = x3 + y3
    exp4 = x4 + y4

    res1 = quantum_addition(x1, y1)
    res2 = quantum_addition(x2, y2)
    res3 = quantum_addition(x3, y3)
    res4 = quantum_addition(x4, y4)

    assert res1 == exp1 and res2 == exp2 and res3 == exp3 and res4 == exp4
