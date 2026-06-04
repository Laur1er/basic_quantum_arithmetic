import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Gate
from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation

from basic_quantum_arithmetic.addition import build_addition_gate
from basic_quantum_arithmetic.subtraction import build_subtraction_gate


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
    reg_N = QuantumRegister(num_qubits, "N")
    reg_ancilla = QuantumRegister(num_qubits + 1, "ancilla")
    reg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(reg_add, reg_b_to_res, reg_N, reg_ancilla, reg_res)

    circuit.x(reg_add[np.nonzero(a_bin)[0].tolist()])
    circuit.x(reg_b_to_res[np.nonzero(b_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(mod_bin)[0].tolist()])

    addition_modulo_gate = build_addition_modulo_gate(num_qubits, mod)
    circuit.compose(
        addition_modulo_gate,
        reg_add[:] + reg_b_to_res[:] + reg_N[:] + reg_ancilla[:],
        inplace=True,
    )

    return run_quantum_arithmetic_operation(circuit, reg_b_to_res, reg_res)


def build_addition_modulo_gate(num_qubits: int, N: int) -> Gate:
    """
    Build a gate that performs the operation |a,b,N> -> |a,b+a mod N,N>
    using an ancilla register of num_qubits +1 qubits.
    The number of qubits is the lenght of the register representing |a>.
    The number of qubits of the register |b> should be num_qubits + 1.
    The number of qubits of the register |N> should be num_qubits.
    In order to use this gate, the registers must already be loaded with the right numbers and
    the order should be |a>, |b>, |N>, |ancilla>.

    Params:
        num_qubits: Number of qubits in the register |a> and |ancilla_add>.
        N: The modulo.
    Returns:
        Gate: Gate acting on 5 registers. Total number of qubits is (4 * num_qubits) + 2.
    """
    N_bin = np.array(list(f"{N:b}"[::-1])).astype(np.int8)

    reg_add = QuantumRegister(num_qubits, "add")
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_ancilla = QuantumRegister(num_qubits + 1, "ancilla")

    circuit = QuantumCircuit(
        reg_add,
        reg_b_to_res,
        reg_N,
        reg_ancilla,
    )

    # Étape 1: Effectuer l'operation unitaire |a,b> -> |a,b+a>
    addition = build_addition_gate(num_qubits)
    circuit.compose(
        addition, reg_add[:] + reg_b_to_res[:] + reg_ancilla[:-1], inplace=True
    )

    # Étape 2: Échanger la valeur du premier registre avec la valeur de N
    # Je ne ferai qu'utiliser reg_N pour le faire

    # Étape 3: Faire une soustraction de |N, b+a> -> |N, b+a-N>
    soustraction = build_subtraction_gate(num_qubits)
    circuit.compose(
        soustraction, reg_N[:] + reg_b_to_res[:] + reg_ancilla[:-1], inplace=True
    )

    # Étape 4: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b_to_res[-1], reg_ancilla[-1], ctrl_state=0)

    # Étape 5: On met le registre N à 0 si |t> = |1>. Pour ce faire, on fait plusieurs portes controllées.
    for qubit in np.nonzero(N_bin)[0].tolist():
        circuit.cx(reg_ancilla[-1], reg_N[qubit])

    # Étape 6: On fait une addition pour revenir avant la soustraction.
    circuit.compose(
        addition, reg_N[:] + reg_b_to_res[:] + reg_ancilla[:-1], inplace=True
    )

    # Remettre N s'il avait ete enleve
    for qubit in np.nonzero(N_bin)[0].tolist():
        circuit.cx(reg_ancilla[-1], reg_N[qubit])

    # Étape 7: On soustrait a du registre b afin de verifier remettre |t> a |0>. Le bit de point fort sera 0 si oui.
    circuit.compose(
        soustraction, reg_add[:] + reg_b_to_res[:] + reg_ancilla[:-1], inplace=True
    )

    # Étape 8: Copier l'information de dépassement du registre b, sur |t>
    circuit.cx(reg_b_to_res[-1], reg_ancilla[-1])

    # Étape 9: On annule la soustraction précédente afin de retrouver le bon b
    circuit.compose(
        addition, reg_add[:] + reg_b_to_res[:] + reg_ancilla[:-1], inplace=True
    )

    return circuit.to_gate(label="Adder MOD")
