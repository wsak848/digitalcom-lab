import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("🎛️ Quantization Lab (Interactive)")

    # =========================
    # INPUT CONTROL
    # =========================
    fs = st.slider("Sampling Rate (Hz)", 100, 5000, 1000)
    n = st.slider("Bit Depth (bits)", 1, 12, 3)
    freq = st.slider("Signal Frequency (Hz)", 1, 10, 2)
    noise = st.slider("Noise Level", 0.0, 1.0, 0.0)

    duration = 1.0

    # =========================
    # SIGNAL GENERATION
    # =========================
    t = np.linspace(0, duration, fs)
    y = 0.8 * np.sin(2 * np.pi * freq * t)

    # =========================
    # QUANTIZATION
    # =========================
    levels = 2**n
    y_scaled = (y + 1) / 2 * (levels - 1)
    yq = (np.round(y_scaled) / (levels - 1)) * 2 - 1

    # noise
    yq_noisy = yq + noise * np.random.randn(len(yq))

    # =========================
    # BIT RATE
    # =========================
    bitrate = fs * n

    # =========================
    # PLOT
    # =========================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t,
        y=y,
        name="Analog",
        line=dict(dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=t,
        y=yq,
        name="Quantized",
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=t,
        y=yq_noisy,
        name="Quantized + Noise",
        mode='lines'
    ))

    fig.update_layout(
        title="Quantization Signal",
        xaxis_title="Time",
        yaxis_title="Amplitude"
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INFO PANEL
    # =========================
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sampling Rate (fs)", f"{fs} Hz")
        st.metric("Bit Depth (n)", f"{n} bits")

    with col2:
        st.metric("Bit Rate (fs × n)", f"{bitrate:,} bps")
        st.metric("Levels (2^n)", f"{levels}")

    # =========================
    # INSIGHT
    # =========================
    st.info("💡 n เพิ่ม → สัญญาณละเอียดขึ้น")
    st.info("💡 fs เพิ่ม → Bitrate เพิ่ม")
    st.info("💡 Noise เพิ่ม → distortion เพิ่ม")
