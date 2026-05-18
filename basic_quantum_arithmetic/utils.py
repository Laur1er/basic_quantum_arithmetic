import numpy as np

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager


def build_addition_gate(num_qubits: int) -> Gate:
    """
    The adder circuit perform the transformation |a,b> -> |a,a+b>, given a number of qubits.
    The number of qubits is the lenght of the register representing |a>.
    The number of qubits of the register |b> should be num_qubits + 1.
    This circuit utilises an ancilla register |c> of lenght num_qubits.

    Return:
        QuantumCircuit making the transformation, the circuit has 3 registers |a>:num_qubits |b>:num_qubits + 1 and |c>:num_qubits
    """

    def build_retenue_gate() -> Gate:
        """
        Porte utile afin de faire les portes arithmetiques.
        """
        qc = QuantumCircuit(4)
        qc.ccx(1, 2, 3)
        qc.cx(1, 2)
        qc.ccx(0, 2, 3)

        return qc.to_gate(label="Retenue")

    def build_summation_gate() -> Gate:
        """
        Porte utile afin de faire les portes arithmetiques.
        """
        qc = QuantumCircuit(3)
        qc.cx(1, 2)
        qc.cx(0, 2)

        return qc.to_gate(label="Somme")

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


def build_substraction_gate(num_qubits: int) -> Gate:
    """
    The adder circuit perform the transformation |a,b> -> |a,a+b>, given a number of qubits.
    The number of qubits is the lenght of the register representing |a>.
    The number of qubits of the register |b> should be num_qubits + 1.
    This circuit utilises an ancilla register |c> of lenght num_qubits.

    Return:
        QuantumCircuit making the transformation, the circuit has 3 registers |a>:num_qubits |b>:num_qubits + 1 and |c>:num_qubits
    """
    gate = build_addition_gate(num_qubits)
    reversed_gate = gate.reverse_ops()
    reversed_gate.name = "Inv_Adder"
    return reversed_gate


def build_addition_modulo_gate(num_qubits: int, N: int) -> Gate:
    """
    Construct a gate, N must already be loaded by itself.
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
    soustraction = build_substraction_gate(num_qubits)
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


def build_controlled_multiplication_modulo_gate(
    num_qubits: int, N: int, multiplier: int
):
    """
    This does the trick, |x> et |N> doivent etre loader, le resultat est dans |b>
    """
    reg_add = QuantumRegister(num_qubits, "add")
    reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
    reg_ancilla_add = QuantumRegister(num_qubits, "ancilla_add")
    reg_N = QuantumRegister(num_qubits, "N")
    reg_temp_mod = QuantumRegister(1, "temp_mod")
    reg_x = QuantumRegister(num_qubits, "x")
    reg_ctrl = QuantumRegister(1, "ctrl")

    circuit = QuantumCircuit(
        reg_add, reg_b_to_res, reg_ancilla_add, reg_N, reg_temp_mod, reg_x, reg_ctrl
    )

    adder_mod = build_addition_modulo_gate(num_qubits, N)

    # Boucle d'addition modulaires itératives
    for i, x_i in enumerate(reg_x):

        # On doit utiliser des portes Toffoli afin d'écrire 2**i * a (mod N) dans le registre |a> afin de l'additionner dans |b>
        a2i = ((2**i) * multiplier) % N
        a2i_bin = np.array(list(f"{a2i:b}"[::-1])).astype(np.int8)
        for pos in np.nonzero(a2i_bin)[0].tolist():
            circuit.ccx(x_i, reg_ctrl[0], reg_add[pos])

        # On fait l'addition modulo N pour ajouter le contenu de |a> dans |res>
        circuit.compose(
            adder_mod,
            reg_add[:]
            + reg_b_to_res[:]
            + reg_ancilla_add[:]
            + reg_N[:]
            + reg_temp_mod[:],
            inplace=True,
        )

        # Remettre a letat initial
        for pos in np.nonzero(a2i_bin)[0].tolist():
            circuit.ccx(x_i, reg_ctrl[0], reg_add[pos])

    # Si le control est a zero, alors aucune addition n'a été faite. On veux copier |x> dans |res> grace à une copie conditionnelle.
    circuit.x(reg_ctrl)
    for i, x_i in enumerate(reg_x):
        circuit.ccx(reg_ctrl[0], x_i, reg_b_to_res[i])
    circuit.x(reg_ctrl)

    return circuit.to_gate(label="Ctrl_Mult_mod")


def build_inv_controlled_multiplication_modulo_gate(
    num_qubits: int, N: int, multiplier: int
):
    """
    This does the trick |x> et |N> doivent etre loader
    """
    ctrl_mult_mod_gate = build_controlled_multiplication_modulo_gate(
        num_qubits, N, multiplier
    )
    inv_ctrl_mult_mod_gate = ctrl_mult_mod_gate.reverse_ops()
    inv_ctrl_mult_mod_gate.label = "inv_Ctrl_Mult_mod"
    return inv_ctrl_mult_mod_gate


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
