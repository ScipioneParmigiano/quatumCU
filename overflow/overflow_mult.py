"""
if x*2/3 >= 7:
    return x+1
else:
    return x+5
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator, Aer
from fpqs6 import fpqs_circ
import matplotlib.pyplot as plt
from QArithmetic import mult, add, cadd

# Registers and circuit.
a = QuantumRegister(4)
b = QuantumRegister(4)
x = QuantumRegister(4)
m = QuantumRegister(8)
anc = QuantumRegister(2)
cm = ClassicalRegister(4)
canc = ClassicalRegister(2)
qc = QuantumCircuit(a, b, x, m, anc, cm)
qc_new = QuantumCircuit(a, b, x, m, anc, cm)

# Numbers to multiply.
qc_new.x(a[1]) # a = 0010 / 0011
qc_new.h(a[0])

qc_new.h(x[0]) # x = from 0000 to 0111
qc_new.h(x[1])
qc_new.h(x[2])

# Multiply the numbers, so |a>|x>|m=0> to |a>|x>|a*x>.
qc.barrier()
mult(qc, a, x, m, 3)
qc.barrier()


# # Encode |1> in b register
qc_new.x(b[0]) # 0001

qc.barrier()

# # m+1
add(qc, b, m, 4)
qc_inv = qc.inverse()
qc_new.append(qc, range(0, len(qc.qubits)), range(0, len(qc.clbits)))

# first ancilla qubit indicates if 2/3*x >= 7
qc_new.barrier()
qc_new.ccx(m[4], m[3], anc[0])
qc_new.cx(m[3], anc[0])
qc_new.cx(m[4], anc[0])


# revert the *2/3 and +1
qc_new.append(qc_inv, range(0, len(qc.qubits)), range(0, len(qc.clbits)))

# controlled x+1
cadd(qc_new, anc[0], b, x, 3)

# x gate to the first ancilla to act on the other qubits
qc_new.x(anc[0])

# # encode |7> in b register
qc_new.x(b[0]) # 0101
qc_new.x(b[0])
qc_new.x(b[1])
qc_new.x(b[2])


# controlled x+7
cadd(qc_new, anc[0], b, x, 3)

# qc_new.barrier()
# qc_new.cx(x[3], 21)
# qc_new.barrier()
# print(qc_new)
# qc_new.measure(x, cm)
# qc_new.measure(anc, canc)

# fpqs
def oracle(qc, num_qubits):
    # oracle to observe if an overflow happened
    qc.cx(11, 21)

A = qc_new

# Perform fixed-point quantum search
fpqs_qc = fpqs_circ(oracle, .5, 4, A)
qc_new.append(fpqs_qc, range(0, 22), range(0,4))

# Measure the result
qc_new.barrier()
qc_new.measure(x, cm)
# qc_new.measure(anc, canc)

# Simulate the circuit.
simulator = AerSimulator()
qct = transpile(qc_new, simulator)
# print(qct)

result = Aer.get_backend('statevector_simulator').run(qct, shots=100).result()
counts = result.get_counts()
print(counts)
# decimal_dict = {int(key, 2): value for key, value in counts.items()}

# sorted_dict = dict(sorted(decimal_dict.items()))

# print(sorted_dict)

plt.figure(figsize=(10, 5))
plt.bar(counts.keys(), counts.values())
plt.xlabel('States')
plt.ylabel('Frequency')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()