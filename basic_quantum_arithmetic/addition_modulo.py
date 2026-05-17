# Effectuer l'operation unitaire |a,b> -> |a,b+a(mod N)>
import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator

from basic_quantum_arithmetic.utils import build_addition_gate, build_substraction_gate


def quantum_addition_modulo(a: int, b: int, mod: int):
    """
    Computes the addition modulo of two numbers smaller than mod.
    Params:
        a (int): Integer smaller than mod
        b (int): Integer smaller than mod
        mod (int): The modulo
    Returns:
        int : The result of a + b (mod mod)
    """

    a_bin = np.array(list(f"{a:b}"[::-1])).astype(np.int8)
    b_bin = np.array(list(f"{b:b}"[::-1])).astype(np.int8)
    mod_bin = np.array(list(f"{mod:b}"[::-1])).astype(np.int8)

    # Initialisation du circuit et des registres
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
