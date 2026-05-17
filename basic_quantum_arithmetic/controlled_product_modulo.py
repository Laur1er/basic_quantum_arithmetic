# Effectuer l'opération unitaire |c,x,0> -> |c,x,ax (mod N)>
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator

from basic_quantum_arithmetic.utils import build_controlled_multiplication_modulo_gate


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

    reg_add = QuantumRegister(num_qubits, "add")  # reviens 0
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")  # reviens 0
    reg_N = QuantumRegister(num_qubits, "N")
    reg_temp_mod = QuantumRegister(1, "temp_mod")  # reviens 0
    reg_x = QuantumRegister(num_qubits, "x")  # initialement a x (on multiplie par a)
    reg_ctrl = QuantumRegister(1, "ctrl")

    creg_res = ClassicalRegister(num_qubits + 1, "res")

    circuit = QuantumCircuit(
        reg_add,
        reg_b_to_res,
        reg_ancilla_add,
        reg_N,
        reg_temp_mod,
        reg_x,
        reg_ctrl,
        creg_res,
    )

    # On charge le registre |x> et |N>
    circuit.x(reg_x[np.nonzero(x_bin)[0].tolist()])
    circuit.x(reg_N[np.nonzero(N_bin)[0].tolist()])

    # Activons le registre de control
    circuit.x(reg_ctrl)

    multiplication_mod_gate = build_controlled_multiplication_modulo_gate(
        num_qubits, N, a
    )
    circuit.compose(
        multiplication_mod_gate,
        reg_add[:]
        + reg_b_to_res[:]
        + reg_ancilla_add[:]
        + reg_N[:]
        + reg_temp_mod[:]
        + reg_x[:]
        + reg_ctrl[:],
        inplace=True,
    )

    circuit.measure(reg_b_to_res, creg_res)

    # Simulons afin de voir le bitstring résultant
    simulator = AerSimulator()
    pass_manager = generate_preset_pass_manager(3, simulator)
    isa_circuit = pass_manager.run(circuit)
    job = simulator.run(isa_circuit)
    result = list(list(job.result().get_counts().keys())[0])

    # Transformer le bitstring
    resultat = int("".join(map(str, result)), 2)

    return resultat
