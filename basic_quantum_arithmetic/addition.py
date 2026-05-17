# Effectuer l'operation unitaire |a,b> -> |a,b+a>
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator

from basic_quantum_arithmetic.utils import build_addition_gate


def quantum_addition(x: int, y: int):
    """
    Computes the sum of x and y using only a quantum computer.
    Params:
        a (int):
        b (int):
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

    circuit.measure(reg_b, reg_res)

    # Simulons afin de voir le bitstring résultant
    simulator = AerSimulator()
    pass_manager = generate_preset_pass_manager(3, simulator)
    isa_circuit = pass_manager.run(circuit)
    job = simulator.run(isa_circuit)
    result = list(list(job.result().get_counts().keys())[0])

    # Transformer le bitstring
    resultat = int("".join(map(str, result)), 2)

    return resultat
