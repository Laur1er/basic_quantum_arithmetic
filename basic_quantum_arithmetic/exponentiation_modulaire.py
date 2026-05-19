# Effectuer l'opération unitaire |exp,0> -> |exp,a**exp (mod N)>
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation

from basic_quantum_arithmetic.controlled_product_modulo import (
    build_controlled_multiplication_modulo_gate,
)


def quantum_exponential(a, exp, N):
    """ """

    exp_bin = np.array(list(f"{exp:b}"[::-1])).astype(np.int8)
    N_bin = np.array(list(f"{N:b}"[::-1])).astype(np.int8)

    # Initialisation du circuit et des registres
    num_qubits = N_bin.size

    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_x = QuantumRegister(num_qubits, "x")
    reg_ancilla = QuantumRegister(2 * num_qubits + 1, "ancilla")
    reg_exp = QuantumRegister(num_qubits, "exp")

    creg_res = ClassicalRegister(num_qubits, "resu")

    circuit = QuantumCircuit(
        reg_b_to_res,
        reg_N,
        reg_x,
        reg_ancilla,
        reg_exp,
        creg_res,
    )

    # On charge le registre |exp> et |N>
    circuit.x(reg_exp[np.nonzero(exp_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(N_bin)[0].tolist()])

    # On prepare |x> a |1>
    circuit.x(reg_x[0])

    for i, x_i in enumerate(reg_exp):
        a2i = pow(a, 2**i, N)
        inv_a2i = pow(a2i, -1, N)

        # Étape 1 :
        multiplication_mod_gate = build_controlled_multiplication_modulo_gate(
            num_qubits, N, a2i
        )
        circuit.compose(
            multiplication_mod_gate,
            reg_b_to_res[:] + reg_N[:] + reg_x[:] + reg_ancilla[:] + [x_i],
            inplace=True,
        )

        # Étape 2 : SWAP reg_b_to_res avec res_x (bit par bit)
        for j in range(num_qubits):
            circuit.swap(reg_b_to_res[j], reg_x[j])

        # Étape 3 : Faire la multiplication inverse
        inv_multiplication_mod_gate = build_controlled_multiplication_modulo_gate(
            num_qubits, N, inv_a2i
        ).inverse()
        circuit.compose(
            inv_multiplication_mod_gate,
            reg_b_to_res[:] + reg_N[:] + reg_x[:] + reg_ancilla[:] + [x_i],
            inplace=True,
        )

    resultat = run_quantum_arithmetic_operation(circuit, reg_x, creg_res)

    print(f"Grâce à l'ordinateur quantique: ({a}^{exp}) % {N} = {resultat}")
    print(f"Grâce à l'ordinateur classique: ({a}^{exp}) % {N} = {(a**exp) %N}")

    return resultat
