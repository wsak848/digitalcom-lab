import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("🎛️ Quantization → PCM → Line Coding Lab")

    # =========================
    # INPUT
    # =========================
    fs = st.slider("Sampling Rate (Hz)", 100, 2000, 500)
    n = st.slider("Bit Depth (bits)", 1, 8, 3)
    freq = st.slider("Signal Frequency (Hz)", 1, 10, 2)
    noise = st.slider("Noise Level", 0.0, 0.5, 0.0)

    duration = 1.0

    # =========================
    # ANALOG SIGNAL
    # =========================
    t = np.linspace(0, duration, fs)
    y = 0.8 * np.sin(2 * np.pi * freq * t)

    # =========================
    # QUANTIZATION
    # =========================
    levels = 2**n
    y_scaled = (y + 1) / 2 * (levels - 1)
    indices = np.round(y_scaled).astype(int)

    yq = (indices / (levels - 1)) * 2 - 1
    yq_noisy = yq + noise * np.random.randn(len(yq))

    # =========================
    # PCM MODE
    # =========================
    st.markdown("## 🔢 PCM Bitstream Control")

    mode = st.radio("เลือกโหมด", ["Auto (จาก Quantization)", "Manual Input"])

    num_samples = st.slider("จำนวน Sample ที่ encode", 5, 50, 20)

    if mode == "Auto (จาก Quantization)":
        bitstream = ''.join([format(i, f'0{n}b') for i in indices[:num_samples]])
    else:
        bitstream = st.text_input("ใส่ Bitstream เอง", "1011001110")

    st.code(bitstream)

    # =========================
    # DIGITAL SIGNAL
    # =========================
    samples_per_bit = st.slider("Samples per bit (resolution)", 5, 50, 20)

    digital_signal = np.repeat([1 if b == '1' else 0 for b in bitstream], samples_per_bit)

    # =========================
    # LINE CODING
    # =========================
    def nrz_l(bits):
        return np.repeat([1 if b == "1" else -1 for b in bits], samples_per_bit)

    def nrz_i(bits):
        signal = []
        level = 1
        for b in bits:
            if b == "1":
                level *= -1
            signal.extend([level]*samples_per_bit)
        return np.array(signal)

    def manchester(bits):
        sig = []
        for b in bits:
            if b == "1":
                sig.extend([1]*(samples_per_bit//2) + [-1]*(samples_per_bit//2))
            else:
                sig.extend([-1]*(samples_per_bit//2) + [1]*(samples_per_bit//2))
        return np.array(sig)

    def rz(bits):
        sig = []
        for b in bits:
            if b == "1":
                sig.extend([1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
            else:
                sig.extend([-1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
        return np.array(sig)

    # =========================
    # OVERLAY PLOT
    # =========================
    st.subheader("📡 Digital vs Line Coding Overlay")

    selected = st.multiselect(
        "เลือกสัญญาณ",
        ["Digital (0/1)", "NRZ-L", "NRZ-I", "Manchester", "RZ"],
        default=["Digital (0/1)", "NRZ-L"]
    )

    fig = go.Figure()

    if "Digital (0/1)" in selected:
        fig.add_trace(go.Scatter(y=digital_signal, name="Digital Bits"))

    if "NRZ-L" in selected:
        fig.add_trace(go.Scatter(y=nrz_l(bitstream), name="NRZ-L"))

    if "NRZ-I" in selected:
        fig.add_trace(go.Scatter(y=nrz_i(bitstream), name="NRZ-I"))

    if "Manchester" in selected:
        fig.add_trace(go.Scatter(y=manchester(bitstream), name="Manchester"))

    if "RZ" in selected:
        fig.add_trace(go.Scatter(y=rz(bitstream), name="RZ"))

    fig.update_layout(title="Overlay: Digital vs Line Coding")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # QUANTIZATION GRAPH (เดิมยังอยู่)
    # =========================
    st.markdown("---")
    st.subheader("🎚️ Quantization Signal")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t, y=y, name="Analog"))
    fig2.add_trace(go.Scatter(x=t, y=yq, name="Quantized"))
    fig2.add_trace(go.Scatter(x=t, y=yq_noisy, name="Noisy"))

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # INFO PANEL
    # =========================
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sampling Rate", f"{fs} Hz")
        st.metric("Bit Depth", f"{n}")

    with col2:
        st.metric("Bit Rate", f"{fs*n:,} bps")
        st.metric("Levels", f"{levels}")

    # =========================
    # INSIGHT
    # =========================
    st.markdown("---")
    st.info("💡 Auto mode = PCM จริงจาก Quantization")
    st.info("💡 Manual mode = ทดลองส่ง bit เอง")
    st.info("💡 Manchester = sync ดีสุด")
    st.info("💡 NRZ-L = ง่าย แต่มีปัญหา long 0/1")
