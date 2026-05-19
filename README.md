# Quantum Arithmetic
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-Hardware--V2-purple.svg)](https://qiskit.org/)
This package implements quantum arithmetic algorithms using Qiskit.

## Installation

```bash
pip install -r requirements.txt
```
Flit???    

## Algorithms

### 1. Addition
The addition algorithm is the building block for all other arithmetic algorithms.
It performs the transformation |a,b,c> -> |a,a+b,c> where a,b are the input registers and c is the carry register, initialized to 0 and brought back to 0 after the operation.

It uses two fundamental gates, called the summation gate and the carry gate:

- Summation gate: |c_n,a_n,b_n> -> |c_n,a_n, a_n xor b_n xor c_n>

- Carry gate: |c_(n-1),a_n,b_n, 0> -> |c_(n-1),a_n,b_n, (a_n ^ b_n) or (b_n ^c_(n-1)) or (a_n ^c_(n-1)) or (a_n ^b_n ^c_(n-1))>

The algorithm follows the following steps:
1. Encode a into |a> and b into |b>. In order to prevent an overflow on the register b, the number of qubits for b must be equal to the number of qubits for a plus 1. The carry register has the same number of qubits as a and is initialized to 0.

2. Using a serie of carry gates, the bits of the carry register are computed. The carry gate for the n-th bit is computed using the n-th bits of a and b and the (n-1)-th bit of the carry register until the strongest bit is computed and stocked into b_{n+1}

3. A CNOT gate is applied on the bit b_{n}, with a_{n} as control. This represents a part of the summation.

4. In reverse order from n-1 to 0, we start by applying a reverse carry gate in order to remove the carries from the previous computation. Then, we apply the summation gate on a_n, b_n and c_n. Using the summation gate, the bits of the register b are computed using the n-th bits of a, b and c. 

5. Finally, the circuit is done and we can measure the register b. The result will be a + b and the carry register is back to 0.

#### Usage
The fonction `basic_quantum_arithmetic.quantum_addition(x: int, y: int) -> int` performs the sum of x and y using exactly this algorithm, it returns the sum as an integer.

The fonction `basic_quantum_arithmetic.build_addition_gate(num_qubits: int) -> Gate` makes the addition gate for a given number of qubits. The gate doesn't include the encoding part, so the user should encode 'a' and 'b' before using the gate. When applying it on a circuit, the user should make sure that there are three quantum registers with the correct sizes.

The qubits should be ordered in the following way: 'add' register, then 'b_to_res' register and finally 'ancilla' register. The 'add' register should have 'num_qubits' qubits and the 'b_to_res' register should have 'num_qubits + 1' qubits, while the 'ancilla_add' register should have 'num_qubits' qubits.

### 2. Subtraction
The subtraction algorithm is exactly the addition algorithm, but reversed. This is due to the fact that if we apply each gate of the network in reversed order, we get |a,b> -> |a,b-a>. In the case of a > b, then the output will be |a,2^(n+1) - b + a> because there will be an overflow.

#### Usage
The fonction `basic_quantum_arithmetic.quantum_subtraction(x: int, y: int) -> int` performs the absolute difference of x and y using exactly this algorithm, it returns the result as an integer.

The fonction `basic_quantum_arithmetic.build_subtraction_gate(num_qubits: int) -> Gate` makes the subtraction gate for a given number of qubits. The gate doesn't include the encoding part, so the user should encode \ket{b} and \ket{b} before using the gate. When applying it on a circuit, the user should make sure that there are three quantum registers with the correct sizes.

The qubits should be ordered in the following way: 'add' register, then 'b_to_res' register and finally 'ancilla' register. The 'add' register should have 'num_qubits' qubits and the 'b_to_res' register should have 'num_qubits + 1' qubits, while the 'ancilla_add' register should have 'num_qubits' qubits.


