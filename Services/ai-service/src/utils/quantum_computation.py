from qiskit import QuantumCircuit, Aer, transpile, assemble, execute
from qiskit.visualization import plot_histogram
from qiskit.providers.aer import AerSimulator

class QuantumComputation:
    """ Implementação de circuitos quânticos """

    def __init__(self, num_qubits=2):
        """
        Inicializa a classe QuantumComputation.

        Args:
            num_qubits (int): Número de qubits no circuito.
        """
        self.num_qubits = num_qubits
        self.circuit = QuantumCircuit(num_qubits)

    def create_entanglement(self):
        """
        Cria um circuito quântico com entrelaçamento (entanglement).

        Returns:
            QuantumCircuit: O circuito quântico criado.
        """
        try:
            self.circuit.h(0)
            self.circuit.cx(0, 1)
            return self.circuit
        except Exception as e:
            print(f"Erro ao criar o circuito: {e}")
            raise

    def simulate_circuit(self):
        """
        Simula o circuito quântico e retorna os resultados.

        Returns:
            dict: Resultados da simulação.
        """
        try:
            simulator = AerSimulator()
            compiled_circuit = transpile(self.circuit, simulator)
            qobj = assemble(compiled_circuit)
            result = simulator.run(qobj).result()
            counts = result.get_counts(self.circuit)
            return counts
        except Exception as e:
            print(f"Erro ao simular o circuito: {e}")
            raise

    def plot_results(self, counts):
        """
        Plota os resultados da simulação.

        Args:
            counts (dict): Resultados da simulação.
        """
        try:
            plot_histogram(counts)
        except Exception as e:
            print(f"Erro ao plotar os resultados: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    quantum_computation = QuantumComputation()
    circuit = quantum_computation.create_entanglement()
    print("Circuito criado:")
    print(circuit)

    results = quantum_computation.simulate_circuit()
    print("Resultados da simulação:")
    print(results)

    quantum_computation.plot_results(results)
