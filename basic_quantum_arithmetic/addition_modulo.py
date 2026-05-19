import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Gate
from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation

from basic_quantum_arithmetic import build_addition_gate, build_subtraction_gate


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

    reg_add = QuantumRegister(num_qubits, "add")
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_temp_mod = QuantumRegister(1, "temp_mod")
    reg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(
        reg_add, reg_b_to_res, reg_ancilla_add, reg_N, reg_temp_mod, reg_res
    )

    circuit.x(reg_add[np.nonzero(a_bin)[0].tolist()])
    circuit.x(reg_b_to_res[np.nonzero(b_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(mod_bin)[0].tolist()])

    addition_modulo_gate = build_addition_modulo_gate(num_qubits, mod)
    circuit.compose(
        addition_modulo_gate,
        reg_add[:] + reg_b_to_res[:] + reg_ancilla_add[:] + reg_N[:] + reg_temp_mod[:],
        inplace=True,
    )

    return run_quantum_arithmetic_operation(circuit, reg_b_to_res, reg_res)


def build_addition_modulo_gate(num_qubits: int, N: int) -> Gate:
    """
    Build
    """
    N_bin = np.array(list(f"{N:b}"[::-1])).astype(np.int8)

    reg_add = QuantumRegister(num_qubits, "add")
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_temp_mod = QuantumRegister(1, "temp_mod")

    circuit = QuantumCircuit(
        reg_add, reg_b_to_res, reg_ancilla_add, reg_N, reg_temp_mod
    )

    # Étape 1: Effectuer l'operation unitaire |a,b> -> |a,b+a>
    addition = build_addition_gate(num_qubits)
    circuit.compose(
        addition, reg_add[:] + reg_b_to_res[:] + reg_ancilla_add[:], inplace=True
    )

    # Étape 2: Échanger la valeur du premier registre avec la valeur de N
    # Je ne ferai qu'utiliser reg_N pour le faire

    # Étape 3: Faire une soustraction de |N, b+a> -> |N, b+a-N>
    soustraction = build_subtraction_gate(num_qubits)
    circuit.compose(
        soustraction, reg_N[:] + reg_b_to_res[:] + reg_ancilla_add[:], inplace=True
    )

    # Étape 4: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b_to_res[-1], reg_temp_mod[0], ctrl_state=0)

    # Étape 5: On met le registre N à 0 si |t> = |1>. Pour ce faire, on fait plusieurs portes controllées.
    for qubit in np.nonzero(N_bin)[0].tolist():
        circuit.cx(reg_temp_mod[0], reg_N[qubit])

    # Étape 6: On fait une addition pour revenir avant la soustraction.
    circuit.compose(
        addition, reg_N[:] + reg_b_to_res[:] + reg_ancilla_add[:], inplace=True
    )

    # Remettre N s'il avait ete enleve
    for qubit in np.nonzero(N_bin)[0].tolist():
        circuit.cx(reg_temp_mod[0], reg_N[qubit])

    # Étape 7: On soustrait a du registre b afin de verifier remettre |t> a |0>. Le bit de point fort sera 0 si oui.
    circuit.compose(
        soustraction, reg_add[:] + reg_b_to_res[:] + reg_ancilla_add[:], inplace=True
    )

    # Étape 8: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b_to_res[-1], reg_temp_mod[0])

    # Étape 9: On annule la soustraction précédente afin de retrouver le bon b
    circuit.compose(
        addition, reg_add[:] + reg_b_to_res[:] + reg_ancilla_add[:], inplace=True
    )

    return circuit.to_gate(label="Adder MOD")
