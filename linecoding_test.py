import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("🎛️ Quantization + Line Coding Lab")

    # =========================
    # INPUT
    # =========================
    fs = st.slider("Sampling Rate (Hz)", 100, 2000, 500)
    n = st.slider("Bit Depth (bits)", 1, 8, 3)
    freq = st.slider("Signal Frequency (Hz)", 1, 10, 2)
    noise = st.slider("Noise Level", 0.0, 0.5, 0.0)

    bits = st.text_input("Input Bits", "1011001")

    duration = 1.0

    # =========================
    # SIGNAL
    # =========================
    t = np.linspace(0, duration, fs)
    y = 0.8 * np.sin(2 * np.pi * freq * t)

    levels = 2**n
    y_scaled = (y + 1) / 2 * (levels - 1)
    yq = (np.round(y_scaled) / (levels - 1)) * 2 - 1
    yq_noisy = yq + noise * np.random.randn(len(yq))

    bitrate = fs * n

    # =========================
    # QUANTIZATION PLOT
    # =========================
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(x=t, y=y, name="Analog"))
    fig1.add_trace(go.Scatter(x=t, y=yq, name="Quantized"))
    fig1.add_trace(go.Scatter(x=t, y=yq_noisy, name="Noisy"))

    fig1.update_layout(title="Quantization Signal")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # =========================
    # LINE CODING
    # =========================
    st.subheader("📡 Line Coding Overlay")

    coding_types = st.multiselect(
        "เลือก Line Coding",
        ["NRZ-L", "NRZ-I", "Manchester", "RZ"],
        default=["NRZ-L", "Manchester"]
    )

    samples_per_bit = 50
    t_bits = np.arange(len(bits) * samples_per_bit)

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
        signal = []
        for b in bits:
            if b == "1":
                signal.extend([1]* (samples_per_bit//2) + [-1]* (samples_per_bit//2))
            else:
                signal.extend([-1]* (samples_per_bit//2) + [1]* (samples_per_bit//2))
        return np.array(signal)

    def rz(bits):
        signal = []
        for b in bits:
            if b == "1":
                signal.extend([1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
            else:
                signal.extend([-1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
        return np.array(signal)

    fig2 = go.Figure()

    if "NRZ-L" in coding_types:
        fig2.add_trace(go.Scatter(y=nrz_l(bits), name="NRZ-L"))

    if "NRZ-I" in coding_types:
        fig2.add_trace(go.Scatter(y=nrz_i(bits), name="NRZ-I"))

    if "Manchester" in coding_types:
        fig2.add_trace(go.Scatter(y=manchester(bits), name="Manchester"))

    if "RZ" in coding_types:
        fig2.add_trace(go.Scatter(y=rz(bits), name="RZ"))

    fig2.update_layout(title="Line Coding Comparison (Overlay)")
    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # INFO
    # =========================
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sampling Rate", f"{fs} Hz")
        st.metric("Bit Depth", f"{n}")

    with col2:
        st.metric("Bit Rate", f"{bitrate:,} bps")
        st.metric("Levels", f"{levels}")

    # =========================
    # INSIGHT
    # =========================
    st.info("💡 NRZ-L: ง่าย แต่ sync ยาก")
    st.info("💡 Manchester: sync ดี แต่ bandwidth สูง")
    st.info("💡 NRZ-I: ใช้ transition แทนข้อมูล")
    st.info("💡 RZ: กลับศูนย์ทุกบิต")
