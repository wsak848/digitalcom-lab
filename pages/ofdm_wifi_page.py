import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

from core import ofdm_wifi as w

def run():
    st.title("📶 WiFi OFDM Simulation (802.11-like)")

    # =========================
    # Controls
    # =========================
    n_sym = st.slider("Number of OFDM Symbols", 1, 5, 1)
    snr_db = st.slider("SNR (dB)", 0, 40, 20)
    speed = st.slider("Animation Speed", 1, 10, 5)
    show_spectrum = st.checkbox("Show Spectrum (FFT)", True)
    show_const = st.checkbox("Show Constellation", True)

    # =========================
    # TX
    # =========================
    tx, bits_tx, freq_syms = w.wifi_ofdm_tx(n_sym=n_sym)

    # =========================
    # Channel
    # =========================
    rx, taps = w.apply_channel(tx, snr_db=snr_db)

    # =========================
    # RX
    # =========================
    bits_rx, const_rec, H_est = w.wifi_ofdm_rx(rx, n_sym=n_sym, eq=True)

    # BER
    ber = np.mean(bits_tx.reshape(-1) != bits_rx.reshape(-1))

    # =========================
    # Time Domain
    # =========================
    st.subheader("📊 Time Domain (TX vs RX)")
    t = np.arange(len(tx))

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=t, y=np.real(tx), name="TX (real)"))
    fig_t.add_trace(go.Scatter(x=t, y=np.real(rx), name="RX (real)"))
    st.plotly_chart(fig_t, use_container_width=True)

    # =========================
    # Animation: build one symbol from subcarriers
    # =========================
    st.subheader("🎬 Subcarrier Build Animation (1 symbol)")

    play = st.button("▶️ Start Animation")
    chart = st.empty()

    if play:
        X0 = freq_syms[0]  # first symbol in freq domain
        for k in range(1, w.N_FFT+1):
            X_partial = np.zeros_like(X0)
            X_partial[:k] = X0[:k]

            x_partial = np.fft.ifft(np.fft.ifftshift(X_partial))

            fig = go.Figure()
            fig.add_trace(go.Scatter(y=np.real(x_partial), name=f"{k} subcarriers"))
            fig.update_layout(title=f"Building OFDM symbol ({k}/{w.N_FFT})")
            chart.plotly_chart(fig, use_container_width=True)
            time.sleep(0.15 / speed)

    # =========================
    # Spectrum
    # =========================
    if show_spectrum:
        st.subheader("📊 Spectrum (FFT)")

        f_tx, s_tx = w.spectrum(tx)
        f_rx, s_rx = w.spectrum(rx)

        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=f_tx, y=s_tx, name="TX"))
        fig_s.add_trace(go.Scatter(x=f_rx, y=s_rx, name="RX"))

        st.plotly_chart(fig_s, use_container_width=True)

    # =========================
    # Constellation
    # =========================
    if show_const:
        st.subheader("⭐ Constellation (After Equalization)")

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=np.real(const_rec.flatten()),
            y=np.imag(const_rec.flatten()),
            mode='markers',
            name="QPSK"
        ))
        st.plotly_chart(fig_c, use_container_width=True)

    # =========================
    # Metrics
    # =========================
    st.markdown(f"### 📈 BER ≈ {ber:.4f}")

    st.markdown("## 🎯 Insight")
    st.markdown(f"""
- ใช้ **64 subcarriers** + **Cyclic Prefix ({w.CP_LEN})**
- มี **multipath channel** → ต้อง equalize
- **SNR ต่ำ → constellation กระจาย → BER สูง**
- OFDM ทำให้หลายช่อง “ซ้อนกันได้แต่ไม่ชน (orthogonal)”
""")