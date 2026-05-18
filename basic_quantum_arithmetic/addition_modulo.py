import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Gate
from basic_quantum_arithmetic.utils import (
    build_addition_gate,
    build_substraction_gate,
    run_quantum_arithmetic_operation,
)


def quantum_addition_modulo(a: int, b: int, mod: int) -> int:
    """
    Computes the addition modulo of two numbers smaller than mod: (a+b) mod (mod)
    Params:
        a: Integer smaller than mod
        b: Integer smaller than mod
        mod: The modulo
    Returns:
        int : The result of a + b (mod mod)
    """
    assert 0 <= a < mod, "a must be greater than or equal to 0 and smaller than mod"
    assert 0 <= b < mod, "b must be greater than or equal to 0 and smaller than mod"
    assert mod > 0, "mod must be greater than 0"

    a_bin = np.array(list(f"{a:b}"[::-1])).astype(np.int8)
    b_bin = np.array(list(f"{b:b}"[::-1])).astype(np.int8)
    mod_bin = np.array(list(f"{mod:b}"[::-1])).astype(np.int8)

    num_qubits = mod_bin.size

    reg_a = QuantumRegister(num_qubits, "a")
    reg_b = QuantumRegister(num_qubits + 1, "b")
    reg_c = QuantumRegister(num_qubits, "c")
    reg_N = QuantumRegister(num_qubits, "mod")
    reg_t = QuantumRegister(1, "t")
    reg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(reg_a, reg_b, reg_c, reg_N, reg_t, reg_res)

    circuit.x(reg_a[np.nonzero(a_bin)[0].tolist()])
    circuit.x(reg_b[np.nonzero(b_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(mod_bin)[0].tolist()])

    # Étape 1: Effectuer l'operation unitaire |a,b> -> |a,b+a>
    addition = build_addition_gate(num_qubits)
    circuit.compose(addition, reg_a[:] + reg_b[:] + reg_c[:], inplace=True)

    # Étape 2: Échanger la valeur du premier registre avec la valeur de mod
    # Je ne ferai qu'utiliser reg_N pour le faire

    # Étape 3: Faire une soustraction de |mod, b+a> -> |mod, b+a-mod>
    soustraction = build_substraction_gate(num_qubits)
    circuit.compose(soustraction, reg_N[:] + reg_b[:] + reg_c[:], inplace=True)

    # Étape 4: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b[-1], reg_t[0], ctrl_state=0)

    # Étape 5: On met le registre mod à 0 si |t> = |1>. Pour ce faire, on fait plusieurs portes controllées.
    for qubit in np.nonzero(mod_bin)[0].tolist():
        circuit.cx(reg_t[0], reg_N[qubit])

    # Étape 6: On fait une addition pour revenir avant la soustraction.
    circuit.compose(addition, reg_N[:] + reg_b[:] + reg_c[:], inplace=True)

    # Remettre mod s'il avait ete enleve
    for qubit in np.nonzero(mod_bin)[0].tolist():
        circuit.cx(reg_t[0], reg_N[qubit])

    # Étape 7: On soustrait a du registre b afin de verifier remettre |t> a |0>. Le bit de point fort sera 0 si oui.
    circuit.compose(soustraction, reg_a[:] + reg_b[:] + reg_c[:], inplace=True)

    # Étape 8: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b[-1], reg_t[0])

    # Étape 9: On annule la soustraction précédente afin de retrouver le bon b
    circuit.compose(addition, reg_a[:] + reg_b[:] + reg_c[:], inplace=True)

    return run_quantum_arithmetic_operation(circuit, reg_b, reg_res)
