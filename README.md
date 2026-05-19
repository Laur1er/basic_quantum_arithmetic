# Quantum Arithmetic
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-Hardware--V2-purple.svg)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python package that implements basic quantum arithmetic algorithms using Qiskit. Each operation is built from scratch using quantum gates and can be used either as a high-level function or as a reusable gate to integrate into larger quantum circuits.

## Installation

### From source (recommended for development)

Clone the repository and install the package in editable mode using [Flit](https://flit.pypa.io/):

```bash
git clone https://github.com/Laur1er/basic_quantum_arithmetic.git
cd basic_quantum_arithmetic
pip install flit
flit install --symlink
```

> **Note:** `flit install --symlink` installs the package in development mode. Any changes you make to the source code will be immediately reflected without needing to reinstall.

Alternatively, you can use pip directly:

```bash
pip install -e .
```

### Install dependencies only

If you just want to install the dependencies without installing the package itself:

```bash
pip install -r requirements.txt
```

### Development dependencies

To install the package with development tools (pytest, flit):

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from basic_quantum_arithmetic import quantum_addition, quantum_subtraction, quantum_addition_modulo, quantum_product_modulo

# Addition: 5 + 10 = 15
result = quantum_addition(5, 10)
print(result)  # 15

# Subtraction: |10 - 5| = 5
result = quantum_subtraction(5, 10)
print(result)  # 5

# Modular addition: (5 + 10) % 12 = 3
result = quantum_addition_modulo(5, 10, 12)
print(result)  # 3

# Modular multiplication: (3 * 5) % 12 = 3
result = quantum_product_modulo(3, 5, 12)
print(result)  # 3
```

## Algorithms

### 1. Addition

The addition algorithm is the building block for all other arithmetic algorithms.
It performs the transformation $\ket{a,b,c} → \ket{a,a+b,c}$ where a,b are the input registers and c is the carry register, initialized to 0 and brought back to 0 after the operation.

It uses two fundamental gates, called the summation gate and the carry gate:

- Summation gate: $\ket{c_n,a_n,b_n} → \ket{c_n,a_n, a_n ⊕ b_n ⊕ c_n}$

- Carry gate: $\ket{c_{n-1},a_n,b_n, 0} → \ket{c_{n-1},a_n,b_n, (a_n ∧ b_n) ∨ (b_n ∧ c_{n-1}) ∨ (a_n ∧ c_{n-1}) ∨ (a_n ∧ b_n ∧ c_{n-1})}$

The algorithm follows the following steps:
1. Encode a into $\ket{a}$ and b into $\ket{b}$. In order to prevent an overflow on the register b, the number of qubits for b must be equal to the number of qubits for a plus 1. The carry register has the same number of qubits as $\ket{a}$ and is initialized to 0.

2. Using a series of carry gates, the qubits of the carry register $\ket{c_i}$ are computed. The carry gate for the n-th qubit is computed using the n-th qubits of $\ket{a}$ and $\ket{b}$ and the (n-1)-th qubit of the carry register until the strongest qubit is computed and stored into $\ket{b_{n+1}}$.

3. A CNOT gate is applied on the qubit $\ket{b_{n}}$, with $\ket{a_{n}}$ as control. This represents a part of the summation.

4. In reverse order from n-1 to 0, we start by applying a reverse carry gate in order to remove the carries from the previous computation. Then, we apply the summation gate on $\ket{a_n}$, $\ket{b_n}$ and $\ket{c_n}$. Using the summation gate, the qubits of $\ket{b}$ are computed using the n-th qubits of $\ket{a}$, $\ket{b}$ and $\ket{c}$.

5. Finally, the circuit is done and we can measure $\ket{b}$. The result will be a + b and the carry register is back to 0.

#### Usage

The function `quantum_addition(x: int, y: int) -> int` performs the sum of x and y using exactly this algorithm, it returns the sum as an integer.

```python
from basic_quantum_arithmetic import quantum_addition
result = quantum_addition(5, 10)  # returns 15
```

The function `build_addition_gate(num_qubits: int) -> Gate` builds the addition gate for a given number of qubits. The gate doesn't include the encoding part, so the user should encode `a` and `b` before applying the gate. The circuit must have three quantum registers in the following order:

| Register | Name | Size |
|---|---|---|
| `add` | The value to add | `num_qubits` |
| `b_to_res` | Input b, becomes b+a | `num_qubits + 1` |
| `ancilla_add` | Ancilla (initialized to 0) | `num_qubits` |

### 2. Subtraction

The subtraction algorithm is exactly the addition algorithm, but reversed. This is due to the fact that if we apply each gate of the network in reversed order, we get |a,b⟩ → |a,b-a⟩. In the case of a > b, the output will be |a, 2^(n+1) - b + a⟩ because there will be an overflow.

#### Usage

The function `quantum_subtraction(x: int, y: int) -> int` performs the absolute difference of x and y, it returns the result as an integer.

```python
from basic_quantum_arithmetic import quantum_subtraction
result = quantum_subtraction(5, 10)  # returns 5
```

The function `build_subtraction_gate(num_qubits: int) -> Gate` builds the subtraction gate for a given number of qubits. The gate doesn't include the encoding part, so the user should encode |a⟩ and |b⟩ before applying the gate. The registers follow the same layout as the addition gate.

### 3. Addition Modulo

The addition modulo algorithm performs the operation $\ket{a,b,N} → \ket{a,b+a \text{ mod } N,N}$ where $a,b$ are the input registers and $N$ is the modulo. The algorithm uses an ancilla register of size $n+1$ ($\ket{\text{ancilla}}$).

The algorithm follows the following steps:

1. Encode $a$ into $\ket{a}$, $b$ into $\ket{b}$ and $N$ into $\ket{N}$. In order to detect an overflow on the register $\ket{b}$, the number of qubits for $\ket{b}$ must be equal to the number of qubits for $\ket{N}$ and $\ket{a}$ plus 1. The ancilla register is initialized to 0.

2. 



#### Usage

The function `quantum_addition_modulo(x: int, y: int, N: int) -> int` performs the modular addition of $x$ and $y$ with modulo $N$ using exactly this algorithm, it returns the result as an integer.

```python
from basic_quantum_arithmetic import quantum_addition_modulo
result = quantum_addition_modulo(5, 10, 12)  # returns 3
```

The function `build_addition_modulo_gate(num_qubits: int, N: int) -> Gate` builds the modular addition gate for a given number of qubits. The gate doesn't include the encoding part, so the user should encode $|a\rangle$, $|b\rangle$, $|N\rangle$ and the ancilla registers before applying the gate. The circuit must have five quantum registers in the following order:

| Register | Name | Size |
|---|---|---|
| `add` | The value to add | `num_qubits` |
| `b_to_res` | Input b, becomes b+a mod N | `num_qubits + 1` |
| `ancilla_add` | Ancilla (initialized to 0) | `num_qubits` |
| `N` | The modulo | `num_qubits` |
| `temp_mod` | Temporary qubit (initialized to 0) | 1 |

### 4. Controlled Multiplication Modulo
*Coming soon — documentation will be added when the algorithm section is ready.*

## Project Structure

```
basic_quantum_arithmetic/
├── basic_quantum_arithmetic/     # Main package
│   ├── __init__.py               # Public API exports
│   ├── addition.py               # Addition circuit & function
│   ├── subtraction.py            # Subtraction circuit & function
│   ├── addition_modulo.py        # Modular addition circuit & function
│   ├── controlled_product_modulo.py  # Modular multiplication
│   ├── exponentiation_modulaire.py   # Modular exponentiation (WIP)
│   └── utils.py                  # Simulation utilities & advanced gates
├── test/                         # Unit tests
│   └── test_operations.py
├── pyproject.toml                # Build configuration (Flit)
├── requirements.txt              # Pinned dependencies
├── LICENSE                       # MIT License
└── README.md
```

## Running Tests

```bash
pytest test/ -v
```

## Building & Publishing with Flit

This project uses [Flit](https://flit.pypa.io/) as its build system. Flit is a simple tool to publish Python packages with minimal configuration.

### How Flit works in this project

Flit reads the configuration from `pyproject.toml` and automatically:
- Reads the **version** from `basic_quantum_arithmetic/__init__.py` (`__version__`)
- Reads the **description** from the docstring in `basic_quantum_arithmetic/__init__.py`
- Packages everything inside the `basic_quantum_arithmetic/` directory

### Build the package

To create a distributable archive (`.tar.gz` and `.whl`) without publishing:

```bash
flit build
```

This creates a `dist/` directory with the built package files.

### Publish to PyPI

1. Create an account on [PyPI](https://pypi.org/) and generate an API token.

2. Publish:
```bash
flit publish
```

Flit will prompt you for your PyPI credentials (username: `__token__`, password: your API token).

### Publish to TestPyPI (recommended first)

To test the publishing process without affecting the real PyPI index:

```bash
flit publish --repository testpypi
```

You can then install your test package with:
```bash
pip install -i https://test.pypi.org/simple/ basic_quantum_arithmetic
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

**Laurier Perron** — [perl2548@usherbrooke.ca](mailto:perl2548@usherbrooke.ca)
