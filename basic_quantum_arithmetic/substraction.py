# Effectuer l'operation unitaire |a,b> -> |a,b-a>
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator

from basic_quantum_arithmetic.utils import build_substraction_gate


def quantum_substraction(x: int, y: int):
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

    # Initialiser le circuit et les registres en binaire
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
    soustraction = build_substraction_gate(num_qubits)
    circuit.compose(soustraction, inplace=True)

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
