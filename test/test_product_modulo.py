from basic_quantum_arithmetic.controlled_product_modulo import quantum_product_modulo


def test_product_modulo():

    x1, a1, mod1 = 5, 0, 12
    x2, a2, mod2 = 2, 12, 24
    x3, a3, mod3 = 24, 13, 27

    exp1 = (x1 * a1) % mod1
    exp2 = (x2 * a2) % mod2
    exp3 = (x3 * a3) % mod3

    res1 = quantum_product_modulo(a1, x1, mod1)
    res2 = quantum_product_modulo(a2, x2, mod2)
    res3 = quantum_product_modulo(a3, x3, mod3)

    assert res1 == exp1 and res2 == exp2 and res3 == exp3
