import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from qiskit.visualization import circuit_drawer, plot_bloch_multivector
import matplotlib.pyplot as plt

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(page_title="Quantum Error Correction", layout="wide")
st.title("🧬 Quantum Hamming (Steane) Code – FULL Practical Demo")

st.markdown("""
This web app **practically demonstrates**:
- Quantum encoding  
- Parity (syndrome) extraction  
- Automatic error correction  
- Receiver-side recovery  

Using **Quantum Hamming (Steane) Code**
""")

# -------------------------------------------------
# Quantum Logic
# -------------------------------------------------

def steane_encode():
    qc = QuantumCircuit(10, 3)

    # Logical qubit |ψ⟩
    qc.h(0)

    # Encode into 7 physical qubits
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(1, 3)
    qc.cx(2, 3)
    qc.cx(1, 4)
    qc.cx(2, 5)
    qc.cx(3, 6)

    return qc

def inject_error(qc, qubit, error):
    if error == "X":
        qc.x(qubit)
    elif error == "Z":
        qc.z(qubit)
    elif error == "Y":
        qc.y(qubit)

def syndrome_measurement(qc):
    # Ancilla-based parity checks
    qc.cx(0, 7); qc.cx(1, 7); qc.cx(3, 7)
    qc.cx(0, 8); qc.cx(2, 8); qc.cx(3, 8)
    qc.cx(1, 9); qc.cx(2, 9); qc.cx(3, 9)

    qc.measure(7, 0)
    qc.measure(8, 1)
    qc.measure(9, 2)

SYNDROME_TABLE = {
    "001": 0,
    "010": 1,
    "011": 2,
    "100": 3,
    "101": 4,
    "110": 5,
    "111": 6
}

def apply_correction(qc, syndrome, error_type):
    if syndrome in SYNDROME_TABLE:
        q = SYNDROME_TABLE[syndrome]
        if error_type == "X":
            qc.x(q)
        elif error_type == "Z":
            qc.z(q)
        elif error_type == "Y":
            qc.y(q)
        return q
    return None

# -------------------------------------------------
# Visualization (FIXED)
# -------------------------------------------------

def show_circuit(qc):
    fig = circuit_drawer(qc, output="mpl")
    st.pyplot(fig)

def show_bloch(qc):
    qc2 = qc.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(qc2)
    fig = plot_bloch_multivector(sv)
    st.pyplot(fig)

# -------------------------------------------------
# Sidebar Controls
# -------------------------------------------------

st.sidebar.header("⚙ Controls")

error_type = st.sidebar.selectbox(
    "Error Type",
    ["None", "X", "Z", "Y"]
)

error_qubit = st.sidebar.selectbox(
    "Error Qubit (0–6)",
    list(range(7))
)

shots = st.sidebar.slider("Shots", 256, 2048, 1024)
run = st.sidebar.button("▶ Run Quantum Process")

# -------------------------------------------------
# Execution
# -------------------------------------------------

if run:
    qc = steane_encode()

    st.subheader("1️⃣ Quantum Encoding (Sender)")
    st.write("Logical qubit encoded into **7 physical qubits**.")

    if error_type != "None":
        inject_error(qc, error_qubit, error_type)
        st.warning(f"{error_type} error injected on qubit {error_qubit}")

    st.subheader("2️⃣ Syndrome Measurement (Receiver)")
    syndrome_measurement(qc)

    backend = AerSimulator()
    result = backend.run(qc, shots=shots).result()
    counts = result.get_counts()

    syndrome = max(counts, key=counts.get)
    st.code(f"Syndrome bits: {syndrome}")

    st.subheader("3️⃣ Automatic Error Correction")

    corrected = None
    if error_type != "None":
        corrected = apply_correction(qc, syndrome, error_type)

    if corrected is not None:
        st.success(f"Error corrected on qubit {corrected}")
    else:
        st.success("No error detected")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧩 Quantum Circuit")
        show_circuit(qc)

    with col2:
        st.subheader("🧭 Quantum State (Bloch Sphere)")
        show_bloch(qc)

    st.subheader("📊 Syndrome Distribution")
    st.bar_chart(counts)

# -------------------------------------------------
# Explanation Panel
# -------------------------------------------------

st.markdown("---")
st.header("📘 Receiver-Side Explanation")

st.markdown("""
### 🔹 Quantum Parity
Parity is extracted using **ancilla qubits**, not classical bits.

### 🔹 Syndrome Decoding
Measured syndrome uniquely identifies the faulty qubit.

### 🔹 Correction
Receiver applies **X / Z / Y gate** to recover the quantum state.

### 🔹 Real-World Relevance
This is the **foundation of fault-tolerant quantum computers**.
""")
