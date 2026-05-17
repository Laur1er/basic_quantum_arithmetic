from basic_quantum_arithmetic.addition_modulo import quantum_addition_modulo


def test_addition():

    x1, y1, mod1 = 5, 10, 12
    x2, y2, mod2 = 2, 12, 24
    x3, y3, mod3 = 24, 13, 27
    x4, y4, mod4 = 55, 19, 61

    exp1 = (x1 + y1) % mod1
    exp2 = (x2 + y2) % mod2
    exp3 = (x3 + y3) % mod3
    exp4 = (x4 + y4) % mod4

    res1 = quantum_addition_modulo(x1, y1, mod1)
    res2 = quantum_addition_modulo(x2, y2, mod2)
    res3 = quantum_addition_modulo(x3, y3, mod3)
    res4 = quantum_addition_modulo(x4, y4, mod4)

    assert res1 == exp1 and res2 == exp2 and res3 == exp3 and res4 == exp4
