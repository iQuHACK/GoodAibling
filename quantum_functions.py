# This contains some useful functions that interface directly with the quantum simulator/computer
from qiskit import QuantumCircuit, execute, Aer
from qiskit.visualization import plot_histogram
import numpy as np
import random as rd

class QState:
    
    def __init__(self, n_qubits, n_ancilla, n_cbits):
        self.n_qubits = n_qubits
        self.n_ancilla = n_ancilla
        self.n_cbits = n_cbits
    
    def setAndChooseGates(self, n_gates, excluded_bits = set(), percentage = 0):
        # Uses a random single qubit gate u3, and the controlled 2 qubit version cu3
        # Makes the actual quantum circuit and goes n_gates deep
        # It also records a set of instructions to create the same state again
        # Percentage is a number from 0 to 1, where 0 is all 0's and 1 is all 1's.
        self.n_gates = n_gates
        self.excluded_bits = excluded_bits
        self.chooseExcludedBits(excluded_bits, percentage)
        bTwoQubitGate = np.random.randint(2, size = n_gates)
        QubitToOperate = []
        all_bits = set(list(range(self.n_qubits)))
        bits_to_consider = all_bits - excluded_bits
        if len(bits_to_consider) != 0:
            for i in range(n_gates):
                if bTwoQubitGate[i]:
                    qubits = rd.sample(bits_to_consider, k = 2)
                else:
                    qubits = rd.sample(bits_to_consider, k = 1)
                QubitToOperate.append(qubits)
        self.bTwoQubitGate = bTwoQubitGate
        self.QubitToOperate = QubitToOperate
    
    def chooseExcludedBits(self, excluded_bits, percentage):
        if percentage != 0:
            n_excluded_bits = len(excluded_bits)
            n_ones = int(np.floor(percentage * n_excluded_bits))
            bits_to_be_one = rd.sample(excluded_bits, k = n_ones)
            self.oneBits = bits_to_be_one
        else:
            self.oneBits = []
        
    def makeRandomState(self, bNew):
        # Make a state using the instructions stored in bTwoQubitGate and QubitToOperate
        qc = QuantumCircuit(self.n_qubits + self.n_ancilla, self.n_cbits)
        bTwoQubitGate = self.bTwoQubitGate
        QubitToOperate = self.QubitToOperate
        if bNew:
            AngleList = []
        for i in range(self.n_gates):
            if bNew:
                angles = np.random.uniform(0, 2 * np.pi, size = 3)
            else:
                angles = self.AngleList[i]
            if bTwoQubitGate[i]:
                # qc.cu3(angles[0], angles[1], angles[2], QubitToOperate[i][0], QubitToOperate[i][1])
                qc.cx(QubitToOperate[i][0], QubitToOperate[i][1])
            else:
                qc.u3(angles[0], angles[1], angles[2], QubitToOperate[i])
            if bNew:
                AngleList.append(angles)
        if bNew:
            self.AngleList = AngleList
        if hasattr(self, 'excluded_bits'):
            for bit in self.oneBits:
                qc.x(bit)
        self.qc = qc

    def measureZ(self, qbit, trials):
        # assumes there are as many classical bits as quantum bits, and puts the measurements in order into the classical bits.
        qstate = self.qc
        nqbits = len(qbit)
        qstate.measure(qbit, list(range(nqbits)))
        counts = execute(qstate, Aer.get_backend('qasm_simulator'), shots = trials).result().get_counts()
        new_counts = dict()
        for key in counts:
            new_key =  key[::-1] # reverses the key since the classical bits are reverse indexed for some reason
            new_key = new_key[0:nqbits]
            new_counts[new_key] = counts[key]
        return new_counts

    def measureParity(self, bits, trials):
        # qstate is the state which you want to measure. 
        # bits is a list of bits on which you want to measure the parity (if the number of mines is odd or even) on. 
        # always measures on classical bit 0.
        qstate = self.qc
        for bit in bits:
            qstate.cx(bit, qstate.n_qubits - 1) # -1 here for 0 indexing. 
        
        qstate.measure(qstate.n_qubits - 1, 0)
        counts = execute(qstate, Aer.get_backend('qasm_simulator'),shots = trials).result().get_counts()
        new_counts = dict()
        for key in counts:
            new_key = key[self.n_cbits - 1]
            new_counts[new_key] = counts[key]
        return new_counts