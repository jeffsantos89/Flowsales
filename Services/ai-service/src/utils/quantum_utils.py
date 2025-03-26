import numpy as np
from scipy.linalg import expm

class QuantumUtils:
    @staticmethod
    def create_basis_states(num_qubits):
        """Create basis states for a given number of qubits."""
        basis_states = []
        for i in range(2**num_qubits):
            state = np.zeros(2**num_qubits)
            state[i] = 1
            basis_states.append(state)
        return np.array(basis_states)

    @staticmethod
    def apply_gate(state, gate, qubit_index, num_qubits):
        """Apply a quantum gate to a specific qubit in the state."""
        identity = np.eye(2)
        gate_matrix = 1
        for i in range(num_qubits):
            if i == qubit_index:
                gate_matrix = np.kron(gate_matrix, gate)
            else:
                gate_matrix = np.kron(gate_matrix, identity)
        return np.dot(gate_matrix, state)

    @staticmethod
    def tensor_product(*states):
        """Compute the tensor product of multiple quantum states."""
        result = states[0]
        for state in states[1:]:
            result = np.kron(result, state)
        return result

    @staticmethod
    def measure_state(state):
        """Measure a quantum state and return the probability distribution."""
        probabilities = np.abs(state)**2
        return probabilities / np.sum(probabilities)

    @staticmethod
    def evolve_state(state, hamiltonian, time):
        """Evolve a quantum state under a given Hamiltonian for a specified time."""
        unitary = expm(-1j * hamiltonian * time)
        return np.dot(unitary, state)

    @staticmethod
    def create_hadamard_gate():
        """Create a Hadamard gate."""
        return np.array([[1, 1], [1, -1]]) / np.sqrt(2)

    @staticmethod
    def create_pauli_x_gate():
        """Create a Pauli-X (NOT) gate."""
        return np.array([[0, 1], [1, 0]])

    @staticmethod
    def create_pauli_y_gate():
        """Create a Pauli-Y gate."""
        return np.array([[0, -1j], [1j, 0]])

    @staticmethod
    def create_pauli_z_gate():
        """Create a Pauli-Z gate."""
        return np.array([[1, 0], [0, -1]])

    @staticmethod
    def create_cnot_gate():
        """Create a CNOT gate."""
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1],
                         [0, 0, 1, 0]])

    @staticmethod
    def create_identity_gate():
        """Create an identity gate."""
        return np.eye(2)

    @staticmethod
    def create_swap_gate():
        """Create a SWAP gate."""
        return np.array([[1, 0, 0, 0],
                         [0, 0, 1, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1]])