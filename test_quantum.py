from qiskit import QuantumCircuit, execute, Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

#n = 8 
#n_q = 8 # number of quantum bits
#n_b = 8 # number of classical bits. These are where the measurements go.
#qc_output = QuantumCircuit(n_q,n_b)
#
#for j in range(n):
#	print(j)
#	qc_output.measure(j,j)
#	
#qc_output.draw(output='mpl')

# counts = execute(qc_output,Aer.get_backend('qasm_simulator')).result().get_counts()
# plot_histogram(counts)

state = QuantumCircuit(4,4)
state.h(2)
state.h(1)
state.cx(0,2)
state.measure(1,1)

counts = execute(state, Aer.get_backend('qasm_simulator'),shots = 1024).result().get_counts()

