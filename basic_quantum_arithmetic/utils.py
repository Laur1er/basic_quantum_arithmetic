import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager


def run_quantum_arithmetic_operation(
    circuit: QuantumCircuit, q_reg: QuantumRegister, c_reg: ClassicalRegister
) -> int:
    """
    Runs the quantum circuit representing an arithmetic operation using Qiskit Aer's AerSimulator.
    The bitstring of the most probable result is converted to an integer using little endian ordering
    and the integer value is returned. Due to the complexity of the circuit, the circuit is optimized using qiskit's
    optimization passes (level 3) and run with the AerSimulator.

    Params:
        circuit: The quantum circuit representing an arithmetic operation to run.
        q_reg: The quantum register to measure.
        c_reg: The classical register to store the result.
    Returns:
        int : The result of the arithmetic operation.
    """
    assert (
        c_reg.size == q_reg.size
    ), "The classical register must have the same size as the quantum register"

    circuit.measure(q_reg, c_reg)

    # Simulons afin de voir le bitstring résultant
    simulator = AerSimulator()
    pass_manager = generate_preset_pass_manager(3, simulator)
    isa_circuit = pass_manager.run(circuit)
    job = simulator.run(isa_circuit)
    result = list(list(job.result().get_counts().keys())[0])

    # Transformer le bitstring
    resultat = int("".join(map(str, result)), 2)

    return resultat
