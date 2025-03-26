import numpy as np
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
from qiskit.providers.aer import AerSimulator

class QuantumSecurityAnalysis:
    def __init__(self, num_qubits=2):
        self.num_qubits = num_qubits
        self.simulator = AerSimulator()
        self.circuit = QuantumCircuit(self.num_qubits)

    def apply_hadamard(self):
        for qubit in range(self.num_qubits):
            self.circuit.h(qubit)
        return self

    def apply_cnot(self, control_qubit, target_qubit):
        self.circuit.cx(control_qubit, target_qubit)
        return self

    def measure_all(self):
        self.circuit.measure_all()
        return self

    def run_simulation(self, shots=1024):
        compiled_circuit = transpile(self.circuit, self.simulator)
        qobj = assemble(compiled_circuit, shots=shots)
        result = self.simulator.run(qobj).result()
        counts = result.get_counts(self.circuit)
        return counts

    def plot_results(self, counts):
        plot_histogram(counts).show()

    def reset_circuit(self):
        self.circuit = QuantumCircuit(self.num_qubits)
        return self

if __name__ == "__main__":
    qsa = QuantumSecurityAnalysis(num_qubits=2)
    qsa.apply_hadamard().apply_cnot(0, 1).measure_all()
    counts = qsa.run_simulation()
    print("Simulation results:", counts)
    qsa.plot_results(counts)