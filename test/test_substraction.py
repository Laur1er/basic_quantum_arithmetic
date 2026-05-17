from basic_quantum_arithmetic.substraction import quantum_substraction


def test_substraction():

    x1, y1 = 5, 10
    x2, y2 = 2, 12
    x3, y3 = 24, 13
    x4, y4 = 55, 19

    exp1 = abs(x1 - y1)
    exp2 = abs(x2 - y2)
    exp3 = abs(x3 - y3)
    exp4 = abs(x4 - y4)

    res1 = quantum_substraction(x1, y1)
    res2 = quantum_substraction(x2, y2)
    res3 = quantum_substraction(x3, y3)
    res4 = quantum_substraction(x4, y4)

    assert res1 == exp1 and res2 == exp2 and res3 == exp3 and res4 == exp4
