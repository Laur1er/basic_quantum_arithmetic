# Effectuer l'opération unitaire |c,x,0> -> |c,x,ax (mod N)>
import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation
from basic_quantum_arithmetic.addition_modulo import build_addition_modulo_gate


def quantum_product_modulo(a: int, x: int, N: int):
    """
    Computes the product ax (mod N) of two integers smaller than N using only a quantum computer.
    Params:
        a(int): Must be smaller than N
        x(int): Must be smaller than N
        N (int): Modulo
    Returns:
        int : The result of the product modulo
    """

    x_bin = np.array(list(f"{x:b}"[::-1])).astype(np.int8)
    N_bin = np.array(list(f"{N:b}"[::-1])).astype(np.int8)

    # Initialisation du circuit et des registres
    num_qubits = N_bin.size

    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_x = QuantumRegister(num_qubits, "x")  # initialement a x (on multiplie par a)
    reg_ancilla = QuantumRegister(2 * num_qubits + 1, "ancilla")  # reviens 0
    reg_ctrl = QuantumRegister(1, "ctrl")

    creg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(
        reg_b_to_res,
        reg_N,
        reg_x,
        reg_ancilla,
        reg_ctrl,
        creg_res,
    )

    # On charge le registre |x> et |N>
    circuit.x(reg_x[np.nonzero(x_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(N_bin)[0].tolist()])

    # Activons le registre de control
    circuit.x(reg_ctrl)

    multiplication_mod_gate = build_controlled_product_modulo_gate(num_qubits, N, a)
    circuit.compose(
        multiplication_mod_gate,
        reg_b_to_res[:] + reg_N[:] + reg_x[:] + reg_ancilla[:] + reg_ctrl[:],
        inplace=True,
    )

    return run_quantum_arithmetic_operation(circuit, reg_b_to_res, creg_res)


def build_controlled_product_modulo_gate(num_qubits: int, N: int, multiplier: int):
    """
    This does the trick, |x> et |N> doivent etre loader, le resultat est dans |b>
    """
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_x = QuantumRegister(num_qubits, "x")
    reg_ancilla = QuantumRegister(2 * num_qubits + 1, "ancilla_add")
    reg_ctrl = QuantumRegister(1, "ctrl")

    circuit = QuantumCircuit(reg_b_to_res, reg_N, reg_x, reg_ancilla, reg_ctrl)

    adder_mod = build_addition_modulo_gate(num_qubits, N)

    # Boucle d'addition modulaires itératives
    for i, x_i in enumerate(reg_x):

        # On doit utiliser des portes Toffoli afin d'écrire 2**i * a (mod N) dans le registre |a> afin de l'additionner dans |b>
        a2i = ((2**i) * multiplier) % N
        a2i_bin = np.array(list(f"{a2i:b}"[::-1])).astype(np.int8)
        for pos in np.nonzero(a2i_bin)[0].tolist():
            circuit.ccx(x_i, reg_ctrl[0], reg_ancilla[pos])

        # On fait l'addition modulo N pour ajouter le contenu de |a> dans |res>
        circuit.compose(
            adder_mod,
            reg_ancilla[:num_qubits]
            + reg_b_to_res[:]
            + reg_N[:]
            + reg_ancilla[num_qubits:],
            inplace=True,
        )

        # Remettre a letat initial
        for pos in np.nonzero(a2i_bin)[0].tolist():
            circuit.ccx(x_i, reg_ctrl[0], reg_ancilla[pos])

    # Si le control est a zero, alors aucune addition n'a été faite. On veux copier |x> dans |res> grace à une copie conditionnelle.
    circuit.x(reg_ctrl)
    for i, x_i in enumerate(reg_x):
        circuit.ccx(reg_ctrl[0], x_i, reg_b_to_res[i])
    circuit.x(reg_ctrl)

    return circuit.to_gate(label="Ctrl_Mult_mod")
