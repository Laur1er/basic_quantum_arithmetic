# Effectuer l'operation unitaire |a,b> -> |a,b-a>
import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Gate
from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation

from basic_quantum_arithmetic.addition import build_addition_gate


def quantum_subtraction(x: int, y: int):
    """
    Compute the difference between a and b using only a quantum circuit.
    Params:
        a (int):
        b (int):
    Returns:
        int : The result for the substraction.
    """
    a = min(x, y)
    b = max(x, y)

    a_bin = np.array(list(f"{a:b}"[::-1])).astype(np.int8)
    b_bin = np.array(list(f"{b:b}"[::-1])).astype(np.int8)

    num_qubits = max(b_bin.size, a_bin.size)

    reg_a = QuantumRegister(num_qubits, "a")
    reg_b = QuantumRegister(num_qubits + 1, "b")
    reg_c = QuantumRegister(num_qubits, "c")
    reg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(reg_a, reg_b, reg_c, reg_res)

    circuit.x(reg_a[np.nonzero(a_bin)[0].tolist()])
    circuit.x(reg_b[np.nonzero(b_bin)[0].tolist()])

    # Faire la transformation qui effectue la soustraction
    soustraction = build_subtraction_gate(num_qubits)
    circuit.compose(soustraction, inplace=True)

    return run_quantum_arithmetic_operation(circuit, reg_b, reg_res)


def build_subtraction_gate(num_qubits: int) -> Gate:
    """
    The subtraction gate perform the unitary transformation |a,b> -> |a,b-a> using an ancilla register of len(num_qubits).
    The number of qubits is the lenght of the register representing |a> and the ancilla register
    The number of qubits of the register |b> should be num_qubits + 1.
    In order to use this gate, the registers must already be loaded with the right numbers and the order should be |a>, |b> and |ancilla>.

    Params:
        num_qubits (int): Number of qubits in the register |a> and |ancilla>.

    Return:
        Gate: Gate acting on 3 register. Total number of qubits is (3 * num_qubits) + 1, in order |a>,|b> and |0>
    """
    gate = build_addition_gate(num_qubits)
    reversed_gate = gate.reverse_ops()
    reversed_gate.name = "Inv_Adder"
    return reversed_gate
