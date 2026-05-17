# Effectuer l'opération unitaire |exp,0> -> |exp,a**exp (mod N)>
import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.circuit import Gate

from qiskit_aer import AerSimulator

from basic_quantum_arithmetic.utils import (
    build_controlled_multiplication_modulo_gate,
)

a, exp, N = 3, 7, 7

exp_bin = np.array(list(f"{exp:b}"[::-1])).astype(np.int8)
N_bin = np.array(list(f"{N:b}"[::-1])).astype(np.int8)

# Initialisation du circuit et des registres
num_qubits = N_bin.size

reg_add = QuantumRegister(num_qubits, "add")
reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")
reg_N = QuantumRegister(num_qubits, "N")
reg_temp_mod = QuantumRegister(1, "temp_mod")
reg_x = QuantumRegister(num_qubits, "x")
reg_exp = QuantumRegister(num_qubits, "exp")

creg_res = ClassicalRegister(num_qubits, "resu")

circuit = QuantumCircuit(
    reg_add,
    reg_b_to_res,
    reg_ancilla_add,
    reg_N,
    reg_temp_mod,
    reg_x,
    reg_exp,
    creg_res,
)

# On charge le registre |exp> et |N>
circuit.x(reg_exp[np.nonzero(exp_bin)[0].tolist()])
circuit.x(reg_N[np.nonzero(N_bin)[0].tolist()])

# On prepare |x> a |1>
circuit.x(reg_x[0])

for i, x_i in enumerate(reg_exp):
    print(x_i)
    a2i = pow(a, 2**i, N)
    inv_a2i = pow(a2i, -1, N)
    print(f"{a2i}*{inv_a2i} (mod {N}) = {(a2i*inv_a2i)%N}")

    # Étape 1 :
    multiplication_mod_gate = build_controlled_multiplication_modulo_gate(
        num_qubits, N, a2i
    )
    circuit.compose(
        multiplication_mod_gate,
        reg_add[:]
        + reg_b_to_res[:]
        + reg_ancilla_add[:]
        + reg_N[:]
        + reg_temp_mod[:]
        + reg_x[:]
        + [x_i],
        inplace=True,
    )

    # Étape 2 : SWAP reg_b_to_res avec res_x (bit par bit)
    for j in range(num_qubits):
        circuit.swap(reg_b_to_res[j], reg_x[j])

    # Étape 3 : Faire la multiplication inverse
    inv_multiplication_mod_gate = build_controlled_multiplication_modulo_gate(
        num_qubits, N, inv_a2i
    ).inverse()
    circuit.compose(
        inv_multiplication_mod_gate,
        reg_add[:]
        + reg_b_to_res[:]
        + reg_ancilla_add[:]
        + reg_N[:]
        + reg_temp_mod[:]
        + reg_x[:]
        + [x_i],
        inplace=True,
    )

circuit.measure(reg_x, creg_res)

# Simulons afin de voir le bitstring résultant
simulator = AerSimulator()
pass_manager = generate_preset_pass_manager(3, simulator)
isa_circuit = pass_manager.run(circuit)
job = simulator.run(isa_circuit)
result = list(list(job.result().get_counts().keys())[0])

# Transformer le bitstring
resultat = int("".join(map(str, result)), 2)

print(f"Grâce à l'ordinateur quantique: ({a}^{exp}) % {N} = {resultat}")
print(f"Grâce à l'ordinateur classique: ({a}^{exp}) % {N} = {(a**exp) %N}")
