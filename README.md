# Quantum Arithmetic

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-Hardware--V2-purple.svg)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python package implementing basic quantum arithmetic algorithms using Qiskit. Every operation is built from scratch using elementary quantum gates and can be used either as a standalone high-level function or as a composable gate inside a larger quantum circuit.

The algorithms are a direct implementation of the quantum networks described in:

> **Vedral, V., Barenco, A., & Ekert, A.** (1996). *Quantum Networks for Elementary Arithmetic Operations*. Physical Review A, 54(1), 147–153. [arXiv:quant-ph/9511018](https://arxiv.org/abs/quant-ph/9511018)

---

## Table of Contents

- [Installation](#installation)
- [Algorithms](#algorithms)
  - [1. Addition](#1-addition)
  - [2. Subtraction](#2-subtraction)
  - [3. Addition Modulo](#3-addition-modulo)
  - [4. Controlled Multiplication Modulo](#4-controlled-multiplication-modulo)
  - [5. Exponentiation Modulo](#5-exponentiation-modulo)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Building & Publishing](#building--publishing-with-flit)
- [License](#license)

---

## Installation

### From source (recommended for development)

Clone the repository and install the package in editable mode using [Flit](https://flit.pypa.io/):

```bash
git clone https://github.com/Laur1er/basic_quantum_arithmetic.git
cd basic_quantum_arithmetic
pip install flit
flit install --symlink
```

> `flit install --symlink` installs the package in development mode — any changes to the source are immediately reflected without reinstalling.

Alternatively, with pip directly:

```bash
pip install -e .
```

### Install dependencies only

```bash
pip install -r requirements.txt
```

### Development dependencies

```bash
pip install -e ".[dev]"
```

---

## Algorithms

All algorithms rely on a ripple-carry architecture and are fully reversible, ensuring that ancilla registers are returned to their initial state after each operation.

---

### 1. Addition

The addition algorithm is the foundational building block for every other operation in this package. It performs the transformation:

$$|a, b, 0\rangle \;\rightarrow\; |a,\; a+b,\; 0\rangle$$

where $a$ and $b$ are the input registers and the carry register is initialized to $|0\rangle$ and uncomputed back to $|0\rangle$ at the end.

Two primitive gates drive the algorithm:

**Carry gate** — computes the carry bit for position $n$:

$$|c_{n-1}, a_n, b_n, 0\rangle \;\rightarrow\; |c_{n-1}, a_n, b_n,\; (a_n \land b_n) \lor (b_n \land c_{n-1}) \lor (a_n \land c_{n-1})\rangle$$

**Summation gate** — computes the sum bit at position $n$:

$$|c_n, a_n, b_n\rangle \;\rightarrow\; |c_n, a_n,\; a_n \oplus b_n \oplus c_n\rangle$$

**Steps:**

1. Encode $a$ into $|a\rangle$ and $b$ into $|b\rangle$. The register $|b\rangle$ is allocated with one extra qubit to accommodate a potential overflow. The carry register has the same width as $|a\rangle$ and is initialized to $|0\rangle$.
2. Sweep forward with carry gates to propagate the carry bits from LSB to MSB, storing the final carry directly into the overflow qubit of $|b\rangle$.
3. Apply a CNOT with $|a_n\rangle$ as control and $|b_n\rangle$ as target to handle the MSB summation.
4. Sweep backward from $n-1$ to $0$: apply the inverse carry gate to uncompute each carry, then apply the summation gate to write the sum into $|b\rangle$.
5. Measure $|b\rangle$ — the result is $a + b$. The carry register is back to $|0\rangle$.

#### 1.1 Usage

```python
from basic_quantum_arithmetic import quantum_addition

result = quantum_addition(5, 10)  # returns 15
```

To embed the addition as a reusable gate in a larger circuit:

```python
from basic_quantum_arithmetic import build_addition_gate
from qiskit import QuantumCircuit, QuantumRegister

num_qubits = n  # bit-width of a
a       = QuantumRegister(num_qubits,     name="a")
b       = QuantumRegister(num_qubits + 1, name="b")
ancilla = QuantumRegister(num_qubits,     name="carry")

qc = QuantumCircuit(a, b, ancilla)
# Encode a and b in binary, little-endian ...
qc.compose(build_addition_gate(num_qubits), a[:] + b[:] + ancilla[:], inplace=True)
```

---

### 2. Subtraction

Subtraction is the time-reversal of addition. Because every gate in the addition network is its own inverse (up to conjugation), reversing the gate sequence yields:

$$|a, b\rangle \;\rightarrow\; |a,\; b - a\rangle$$

When $a > b$, the result wraps modulo $2^{n+1}$, i.e. the output is $|a,\; 2^{n+1} - (a - b)\rangle$.

#### 2.1 Usage

```python
from basic_quantum_arithmetic import quantum_subtraction

result = quantum_subtraction(10, 5)  # returns 5
result = quantum_subtraction(5, 10)  # returns 5 (absolute difference)
```

To embed the subtraction as a reusable gate:

```python
from basic_quantum_arithmetic import build_subtraction_gate
from qiskit import QuantumCircuit, QuantumRegister

num_qubits = n
a       = QuantumRegister(num_qubits,     name="a")
b       = QuantumRegister(num_qubits + 1, name="b")
ancilla = QuantumRegister(num_qubits,     name="carry")

qc = QuantumCircuit(a, b, ancilla)
# Encode a and b in binary, little-endian ...
qc.compose(build_subtraction_gate(num_qubits), a[:] + b[:] + ancilla[:], inplace=True)
```

---

### 3. Addition Modulo

Modular addition performs:

$$|a, b, N\rangle \;\rightarrow\; |a,\; (a + b) \bmod N,\; N\rangle$$

A single ancilla qubit is used as a temporary flag and is uncomputed at the end of the procedure.

**Steps:**

1. Encode $a$ into $|a\rangle$, $b$ into $|b\rangle$ (width $n+1$ to detect overflow), and $N$ into $|N\rangle$. Initialize the ancilla register to $|0\rangle$.
2. Apply an addition gate: $|a, b\rangle \rightarrow |a, a+b\rangle$.
3. Apply a subtraction gate using $|N\rangle$ as the subtrahend: $|N, a+b\rangle \rightarrow |N, a+b-N\rangle$.
4. Use the overflow qubit of $|b\rangle$ (which is $|0\rangle$ when $a+b \geq N$, i.e. when the subtraction did not underflow) to copy the overflow flag into the ancilla qubit via a CNOT.
5. Controlled on the ancilla, restore $|N\rangle$ using CNOTs — effectively adding $N$ back when the sum was below $N$.
6. Add $N$ back into $|b\rangle$. If $N$ was zeroed out in the previous step, this adds nothing.
7. Re-encode $N$ into $|N\rangle$ (mirror of step 5).
8. Subtract $a$ from $|b\rangle$ to expose whether the modular reduction was applied.
9. Use the resulting overflow qubit to uncompute the ancilla via a CNOT.
10. Add $a$ back into $|b\rangle$. The modular addition is complete.

#### 3.1 Usage

```python
from basic_quantum_arithmetic import quantum_addition_modulo

result = quantum_addition_modulo(5, 10, 12)  # returns 3
```

To embed the modular addition as a reusable gate:

```python
from basic_quantum_arithmetic import build_addition_modulo_gate
from qiskit import QuantumCircuit, QuantumRegister

num_qubits = N.bit_length()  # bit-width of N

a       = QuantumRegister(num_qubits,     name="a")
b       = QuantumRegister(num_qubits + 1, name="b")
n_reg   = QuantumRegister(num_qubits,     name="N")
ancilla = QuantumRegister(num_qubits + 1, name="ancilla")

qc = QuantumCircuit(a, b, n_reg, ancilla)
# Encode a, b and N in binary, little-endian ...
qc.compose(
    build_addition_modulo_gate(num_qubits, N),
    a[:] + b[:] + n_reg[:] + ancilla[:],
    inplace=True
)
```

---

### 4. Controlled Multiplication Modulo

Controlled modular multiplication performs:

$$|c\rangle|x\rangle|b\rangle \;\rightarrow\; |c\rangle|x\rangle|\,b + c \cdot x \cdot a \bmod N\rangle$$

where $a$ and $N$ are classical parameters known at circuit-construction time, $x$ is an $n$-qubit quantum register, $b$ is initialized to $|0\rangle$, and $c$ is the single control qubit. When $c = |0\rangle$ the register $|b\rangle$ is left unchanged.

The key insight from Vedral et al. is that multiplying by $a$ can be decomposed into $n$ **controlled modular additions**. For each bit $x_i$ of $|x\rangle$, the classical value $2^i \cdot a \bmod N$ is precomputed and a controlled-addition-modulo gate is applied, controlled jointly on $c$ and $x_i$:

$$|b\rangle \;\xrightarrow{x_i = 1}\; |b + 2^i a \bmod N\rangle$$

Iterating over all $n$ bits accumulates $\sum_{i} x_i \cdot 2^i \cdot a = x \cdot a$ into $|b\rangle$, modulo $N$ throughout.

**Steps:**

1. Initialize $|b\rangle$ to $|0\rangle$ (the accumulator register, width $n+1$).
2. For each bit $i$ from $0$ to $n-1$, precompute the classical constant $\tilde{a}_i = (2^i \cdot a) \bmod N$.
3. Apply a doubly-controlled addition modulo gate — controlled on $c$ and $x_i$ — adding $\tilde{a}_i$ into $|b\rangle$ modulo $N$.
4. After all $n$ steps, $|b\rangle = c \cdot x \cdot a \bmod N$.

#### 4.1 Usage

```python
from basic_quantum_arithmetic import quantum_product_modulo

result = quantum_product_modulo(x=3, a=5, N=7)  # returns (3 * 5) % 7 = 1
```

To embed the controlled multiplication as a reusable gate:

```python
from basic_quantum_arithmetic import build_controlled_product_modulo_gate
from qiskit import QuantumCircuit, QuantumRegister

num_qubits = N.bit_length()

b = QuantumRegister(num_qubits + 1, "b_to_res")
N = QuantumRegister(num_qubits, "N")
x = QuantumRegister(num_qubits, "x")
ancilla = QuantumRegister(2 * num_qubits + 1, "ancilla_add")
reg_ctrl = QuantumRegister(1, "ctrl")

qc = QuantumCircuit(b, N, x, ancilla, reg_ctrl)

# Encode N, x in binary, little-endian; b initialized to |0⟩ ...
circuit.compose(
        build_controlled_product_modulo_gate(num_qubits, N, a),
        b[:] + N[:] + x[:] + ancilla[:] + reg_ctrl[:],
        inplace=True,
    )
```

---

### 5. Exponentiation Modulo

Modular exponentiation performs:

$$|x\rangle|1\rangle \;\rightarrow\; |x\rangle|\,a^x \bmod N\rangle$$

where $a$ and $N$ are classical parameters. This is the most resource-intensive primitive in this package and constitutes the core quantum subroutine of **Shor's factoring algorithm**.

The algorithm decomposes the exponent $x$ in binary as $x = \sum_{i=0}^{n-1} x_i \cdot 2^i$ and uses the identity:

$$a^x = a^{\sum_i x_i 2^i} = \prod_i \left(a^{2^i}\right)^{x_i}$$

Each factor $a^{2^i} \bmod N$ is a classical constant precomputable by repeated squaring. The quantum circuit applies, for each bit $x_i$, a **controlled multiplication modulo** gate that conditionally multiplies the accumulator by $a^{2^i} \bmod N$. The accumulator is initialized to $|1\rangle$ so that uncontrolled steps contribute a factor of $1$.

**Steps:**

1. Initialize the output register $|y\rangle$ to $|1\rangle$ (width $n+1$).
2. Precompute the classical sequence $A_i = a^{2^i} \bmod N$ for $i = 0, \ldots, n-1$ via repeated squaring.
3. For each bit $i$ from $0$ to $n-1$, apply a controlled-multiplication-modulo gate — controlled on qubit $x_i$ — that maps $|y\rangle \rightarrow |y \cdot A_i \bmod N\rangle$.
4. After all $n$ steps, the output register holds $a^x \bmod N$.

> **Complexity note:** Vedral et al. show that the total auxiliary memory required grows only *linearly* in $n = \lceil \log_2 N \rceil$, making this approach practical for integration into larger quantum algorithms.

#### 5.1 Usage

```python
from basic_quantum_arithmetic import quantum_exponential

result = quantum_exponential(x=3, a=2, N=7)  # returns 2**3 % 7 = 1
```

To embed the modular exponentiation as a reusable gate:

```python
from basic_quantum_arithmetic import build_exponential_modulo_gate
from qiskit import QuantumCircuit, QuantumRegister

num_qubits = N.bit_length()

reg_b_to_res = QuantumRegister(num_qubits + 1, "b_to_res")
reg_N = QuantumRegister(num_qubits, "N")
reg_x = QuantumRegister(num_qubits, "x")
reg_ancilla = QuantumRegister(2 * num_qubits + 1, "ancilla")
reg_exp = QuantumRegister(num_qubits, "exp")

circuit = QuantumCircuit(
    reg_b_to_res,
    reg_N,
    reg_x,
    reg_ancilla,
    reg_exp,
)
# On charge le registre |exp> et |N> ...

circuit.compose(
    build_controlled_product_modulo_gate(num_qubits, N, a),
    reg_b_to_res[:] + reg_N[:] + reg_x[:] + reg_ancilla[:] + reg_ctrl[:],
    inplace=True,
)
```

---

## Project Structure

```
basic_quantum_arithmetic/
├── basic_quantum_arithmetic/
│   ├── __init__.py                   # Public API exports
│   ├── addition.py                   # Addition circuit & function
│   ├── subtraction.py                # Subtraction circuit & function
│   ├── addition_modulo.py            # Modular addition circuit & function
│   ├── controlled_product_modulo.py  # Controlled modular multiplication
│   ├── exponentiation_modulaire.py   # Modular exponentiation
│   └── utils.py                      # Simulation utilities & composite gates
├── test/
│   └── test_operations.py            # Unit tests
├── pyproject.toml                    # Build configuration (Flit)
├── requirements.txt                  # Pinned dependencies
├── LICENSE                           # MIT License
└── README.md
```

---

## Running Tests

```bash
pytest test/ -v
```

---

## Building & Publishing with Flit

This project uses [Flit](https://flit.pypa.io/) as its build system. Flit reads configuration from `pyproject.toml` and automatically:

- reads the **version** from `basic_quantum_arithmetic/__init__.py` (`__version__`)
- reads the **description** from the module docstring in `__init__.py`
- packages everything inside the `basic_quantum_arithmetic/` directory

### Build the package

```bash
flit build
```

This creates a `dist/` directory containing the `.tar.gz` and `.whl` distribution files.

### Publish to PyPI

1. Create an account on [PyPI](https://pypi.org/) and generate an API token.
2. Run:

```bash
flit publish
```

Flit will prompt for credentials (username: `__token__`, password: your API token).

### Publish to TestPyPI first (recommended)

```bash
flit publish --repository testpypi
```

Then install and verify:

```bash
pip install -i https://test.pypi.org/simple/ basic_quantum_arithmetic
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Author

**Laurier Perron** — [perl2548@usherbrooke.ca](mailto:perl2548@usherbrooke.ca)

---

## Reference

Vedral, V., Barenco, A., & Ekert, A. (1996). *Quantum Networks for Elementary Arithmetic Operations*. Physical Review A, 54(1), 147–153.
[https://doi.org/10.1103/PhysRevA.54.147](https://doi.org/10.1103/PhysRevA.54.147) · [arXiv:quant-ph/9511018](https://arxiv.org/abs/quant-ph/9511018)