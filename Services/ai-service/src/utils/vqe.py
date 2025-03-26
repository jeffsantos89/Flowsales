import logging
from qiskit.algorithms import VQE
from qiskit.circuit.library import EfficientSU2
from qiskit.providers.aer import AerSimulator
from qiskit.utils import QuantumInstance

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VQEAlgorithm:
    """ Algoritmo VQE para otimização de problemas quânticos """

    def __init__(self, num_qubits=4, optimizer=None, backend=None):
        """
        Inicializa o algoritmo VQE com os parâmetros fornecidos.

        Args:
            num_qubits (int): Número de qubits para o ansatz.
            optimizer (Optimizer): Otimizador a ser usado no VQE.
            backend (Backend): Backend quântico a ser usado para simulação.
        """
        self.num_qubits = num_qubits
        self.optimizer = optimizer
        self.backend = backend or AerSimulator()
        self.quantum_instance = QuantumInstance(self.backend)

    def run_vqe(self):
        """
        Executa o algoritmo VQE.

        Returns:
            VQE: Instância do algoritmo VQE configurada.
        """
        try:
            ansatz = EfficientSU2(self.num_qubits)
            vqe = VQE(ansatz, optimizer=self.optimizer, quantum_instance=self.quantum_instance)
            logger.info("VQE algorithm initialized successfully.")
            return vqe
        except Exception as e:
            logger.error(f"Failed to initialize VQE algorithm: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    try:
        vqe_algorithm = VQEAlgorithm()
        vqe_instance = vqe_algorithm.run_vqe()
        logger.info("VQE instance created successfully.")
    except Exception as e:
        logger.error(f"Error running VQE algorithm: {e}")
