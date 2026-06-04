import numpy as np
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Gate

from basic_quantum_arithmetic.utils import run_quantum_arithmetic_operation


def quantum_addition(x: int, y: int) -> int:
    """
    Computes the sum of x and y using only a quantum computer.
    Params:
        x: Integer
        y: Integer
    Returns:
        int : The sum of x and y.
    """
    a = min(x, y)
    b = max(x, y)

    a_bin = np.array(list(f"{a:b}"[::-1])).astype(np.int8)
    b_bin = np.array(list(f"{b:b}"[::-1])).astype(np.int8)

    num_qubits = max(a_bin.size, b_bin.size)

    reg_a = QuantumRegister(num_qubits, "a")
    reg_b = QuantumRegister(num_qubits + 1, "b")
    reg_c = QuantumRegister(num_qubits, "c")
    reg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(reg_a, reg_b, reg_c, reg_res)

    addition = build_addition_gate(num_qubits)

    circuit.x(reg_a[np.nonzero(a_bin)[0].tolist()])
    circuit.x(reg_b[np.nonzero(b_bin)[0].tolist()])
    circuit.compose(addition, inplace=True)

    return run_quantum_arithmetic_operation(circuit, reg_b, reg_res)


def build_addition_gate(num_qubits: int) -> Gate:
    """
    The addition gate perform the unitary transformation |a,b> -> |a,b+a> using an ancilla register of len(num_qubits).
    The number of qubits is the lenght of the register representing |a> and the ancilla register
    The number of qubits of the register |b> should be num_qubits + 1.
    In order to use this gate, the registers must already be loaded with the right numbers and the order should be |a>, |b> and |ancilla>.

    Params:
        num_qubits (int): Number of qubits in the register |a> and |ancilla>.

    Return:
        Gate: Gate acting on 3 register. Total number of qubits is (3 * num_qubits) + 1, in order |a>,|b> and |0>
    """

    def build_retenue_gate() -> Gate:
        """
        Gate useful for calculating the carry bit of the sum of qubits a,b and c. Stores the carry bit in c.
        """
        qc = QuantumCircuit(4)
        qc.ccx(1, 2, 3)
        qc.cx(1, 2)
        qc.ccx(0, 2, 3)

        return qc.to_gate(label="Carry")

    def build_summation_gate() -> Gate:
        """
        Gate useful for summing qubits a,b and c. Stores the result in b.
        """
        qc = QuantumCircuit(3)
        qc.cx(1, 2)
        qc.cx(0, 2)

        return qc.to_gate(label="Sum")

    reg_add = QuantumRegister(num_qubits, "add")
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")

    circuit = QuantumCircuit(reg_add, reg_b_to_res, reg_ancilla_add)
    retenue = build_retenue_gate()
    somme = build_summation_gate()

    for i in range(num_qubits):
        if i == num_qubits - 1:
            circuit.compose(
                retenue,
                [reg_ancilla_add[i], reg_add[i], reg_b_to_res[i], reg_b_to_res[i + 1]],
                inplace=True,
            )
        else:
            circuit.compose(
                retenue,
                [
                    reg_ancilla_add[i],
                    reg_add[i],
                    reg_b_to_res[i],
                    reg_ancilla_add[i + 1],
                ],
                inplace=True,
            )

    circuit.cx(reg_add[-1], reg_b_to_res[-2])

    inv_retenue = retenue.reverse_ops()
    inv_retenue.label = "inv_Carry"

    for i in range(num_qubits - 1, -1, -1):

        if i != num_qubits - 1:
            circuit.compose(
                inv_retenue,
                [
                    reg_ancilla_add[i],
                    reg_add[i],
                    reg_b_to_res[i],
                    reg_ancilla_add[i + 1],
                ],
                inplace=True,
            )
        circuit.compose(
            somme, [reg_ancilla_add[i], reg_add[i], reg_b_to_res[i]], inplace=True
        )

    return circuit.to_gate(label="Adder")
