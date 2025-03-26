import time
import numpy as np
# Tente importar AerSimulator da nova localização
try:
    from qiskit_aer import AerSimulator
except ImportError:
    # Se a nova localização falhar, tente a localização antiga
    from qiskit.providers.aer import AerSimulator
from qiskit.circuit.random import random_circuit
# Tente importar Aer da nova localização
try:
    from qiskit_aer import Aer
except ImportError:
    # Se a nova localização falhar, tente a localização antiga
    from qiskit import Aer
from qiskit.quantum_info import state_fidelity
from qiskit import transpile, assemble

def generate_random_circuit(num_qubits, depth):
    """Generate a random quantum circuit."""
    return random_circuit(num_qubits, depth, max_operands=2)

def benchmark_circuit_execution(circuit, backend):
    """Benchmark the execution time of a quantum circuit on a given backend."""
    transpiled_circuit = transpile(circuit, backend)
    qobj = assemble(transpiled_circuit)
    start_time = time.time()
    result = backend.run(qobj).result()
    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time, result

def calculate_fidelity(circuit, backend):
    """Calculate the fidelity of the quantum circuit execution."""
    transpiled_circuit = transpile(circuit, backend)
    qobj = assemble(transpiled_circuit)
    result = backend.run(qobj).result()
    statevector = result.get_statevector()
    ideal_statevector = AerSimulator().run(qobj).result().get_statevector()
    fidelity = state_fidelity(statevector, ideal_statevector)
    return fidelity

def run_benchmarks(num_qubits_list, depth_list, num_trials=10):
    """Run benchmarks for various circuit sizes and depths."""
    backend = Aer.get_backend('qasm_simulator')
    results = []

    for num_qubits in num_qubits_list:
        for depth in depth_list:
            execution_times = []
            fidelities = []
            for _ in range(num_trials):
                circuit = generate_random_circuit(num_qubits, depth)
                execution_time, _ = benchmark_circuit_execution(circuit, backend)
                fidelity = calculate_fidelity(circuit, backend)
                execution_times.append(execution_time)
                fidelities.append(fidelity)
            
            avg_execution_time = np.mean(execution_times)
            avg_fidelity = np.mean(fidelities)
            results.append({
                'num_qubits': num_qubits,
                'depth': depth,
                'avg_execution_time': avg_execution_time,
                'avg_fidelity': avg_fidelity
            })
    
    return results

if __name__ == "__main__":
    num_qubits_list = [2, 4, 6, 8, 10]
    depth_list = [10, 20, 30, 40, 50]
    results = run_benchmarks(num_qubits_list, depth_list)

    for result in results:
        print(f"Qubits: {result['num_qubits']}, Depth: {result['depth']}, "
              f"Avg Execution Time: {result['avg_execution_time']:.4f}s, "
              f"Avg Fidelity: {result['avg_fidelity']:.4f}")