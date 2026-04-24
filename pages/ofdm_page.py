import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

from core import ofdm

def run():
    st.title("📡 OFDM Lab (Animation + Spectrum)")

    # =========================
    # Controls
    # =========================
    N = st.slider("Number of Subcarriers", 4, 64, 16)
    noise_level = st.slider("Noise Level", 0.0, 0.5, 0.0)
    speed = st.slider("Animation Speed", 1, 10, 5)

    show_spectrum = st.checkbox("Show Spectrum", True)

    # =========================
    # Generate symbols
    # =========================
    symbols = ofdm.generate_symbols(N)

    # =========================
    # OFDM TX
    # =========================
    tx_signal = ofdm.ofdm_tx(symbols)

    # Add noise
    rx_signal = ofdm.add_noise(tx_signal, noise_level)

    # RX
    recovered = ofdm.ofdm_rx(rx_signal)

    # =========================
    # Time domain
    # =========================
    st.subheader("📊 OFDM Time Signal")

    t = np.arange(len(tx_signal))

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=t,
        y=np.real(tx_signal),
        name="Real"
    ))
    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # Animation (Subcarriers 🔥)
    # =========================
    st.subheader("🎬 Subcarrier Animation")

    play = st.button("▶️ Start OFDM Animation")
    chart = st.empty()

    if play:
        for i in range(1, N+1):

            partial = np.zeros(N, dtype=complex)
            partial[:i] = symbols[:i]

            partial_signal = np.fft.ifft(partial)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                y=np.real(partial_signal),
                name=f"{i} Subcarriers"
            ))

            fig.update_layout(
                title=f"Building OFDM Signal ({i}/{N})"
            )

            chart.plotly_chart(fig, use_container_width=True)
            time.sleep(0.2 / speed)

    # =========================
    # Spectrum
    # =========================
    if show_spectrum:
        st.subheader("📊 Spectrum (FFT)")

        fft = np.fft.fft(tx_signal)
        freq = np.fft.fftfreq(len(fft))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=freq,
            y=np.abs(fft),
            name="Spectrum"
        ))

        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # Constellation
    # =========================
    st.subheader("⭐ Constellation (Recovered)")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=np.real(recovered),
        y=np.imag(recovered),
        mode='markers',
        name="Recovered Symbols"
    ))

    st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # Insight
    # =========================
    st.markdown("## 🎯 Insight")

    st.markdown("""
    🔥 OFDM = หลาย subcarriers + orthogonal

    ✔ ซ้อนกันได้ (ไม่ชน)
    ✔ ใช้ FFT แยกออก
    ✔ ใช้ใน WiFi / 4G / 5G

    Noise ↑ → จุด constellation กระจาย
    """)