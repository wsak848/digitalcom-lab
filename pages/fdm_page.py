import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

from core import fdm

# =========================
# Low-pass filter (FFT)
# =========================
def lowpass_filter(signal, cutoff, fs):
    fft = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), d=1/fs)

    mask = np.abs(freqs) < cutoff
    fft_filtered = fft * mask

    return np.real(np.fft.ifft(fft_filtered))


# =========================
# Spectrum (FFT)
# =========================
def compute_spectrum(signal, fs):
    N = len(signal)
    fft = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, d=1/fs)

    # ใช้เฉพาะฝั่งบวก
    mask = freqs >= 0
    return freqs[mask], np.abs(fft[mask]) / N


def run():
    st.title("📡 FDM Lab + Animation + Spectrum")

    # =========================
    # Controls
    # =========================
    num = st.slider("จำนวนสัญญาณ", 2, 4, 2)
    fs = st.slider("Sampling Rate", 200, 1000, 500)
    duration = 1

    speed = st.slider("Animation Speed", 1, 10, 5)

    show_spectrum = st.checkbox("📊 Show Spectrum (FFT)", True)

    t = np.linspace(0, duration, fs)

    # baseband
    base_freqs = []
    for i in range(num):
        f = st.slider(f"Base Signal {i+1}", 1, 5, i+1)
        base_freqs.append(f)

    # carriers
    st.subheader("Carrier Frequencies")

    carriers = []
    for i in range(num):
        fc = st.slider(f"Carrier {i+1}", 20, 120, 20 + i*30)
        carriers.append(fc)

    # =========================
    # Generate
    # =========================
    signals = fdm.generate_signals(base_freqs, t)
    modulated = fdm.fdm_modulate(signals, carriers, t)
    combined = fdm.fdm_combine(modulated)

    colors = ["red", "blue", "green", "orange"]

    # =========================
    # Original
    # =========================
    st.subheader("📊 Original Signals")

    fig1 = go.Figure()
    for i in range(num):
        fig1.add_trace(go.Scatter(
            x=t, y=signals[i], name=f"S{i+1}"
        ))
    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # Animation
    # =========================
    st.subheader("🎬 FDM Animation")

    play = st.button("▶️ Start Animation")
    chart = st.empty()

    if play:
        for i in range(20, len(t)):

            fig = go.Figure()

            # Modulated
            for ch in range(num):
                fig.add_trace(go.Scatter(
                    x=t[:i],
                    y=modulated[ch][:i],
                    name=f"Channel {ch+1}",
                    line=dict(color=colors[ch], width=2)
                ))

            # Combined
            fig.add_trace(go.Scatter(
                x=t[:i],
                y=combined[:i],
                name="Combined",
                line=dict(color="black", width=3)
            ))

            chart.plotly_chart(fig, use_container_width=True)

            time.sleep(0.05 / speed)

    # =========================
    # Spectrum (NEW 🔥)
    # =========================
    if show_spectrum:
        st.subheader("📊 Frequency Spectrum (FFT)")

        freqs, spec = compute_spectrum(combined, fs)

        fig_spec = go.Figure()

        fig_spec.add_trace(go.Scatter(
            x=freqs,
            y=spec,
            name="Spectrum",
            line=dict(color="purple")
        ))

        # แสดงตำแหน่ง carrier
        for fc in carriers:
            fig_spec.add_vline(
                x=fc,
                line_dash="dash",
                annotation_text=f"{fc} Hz"
            )

        fig_spec.update_layout(
            xaxis_title="Frequency (Hz)",
            yaxis_title="Magnitude",
            title="FDM Spectrum (Channels separated)"
        )

        st.plotly_chart(fig_spec, use_container_width=True)

    # =========================
    # Demux
    # =========================
    st.subheader("📥 Demultiplexed Signals")

    recovered = []

    for i, fc in enumerate(carriers):
        demod = combined * np.cos(2*np.pi*fc*t)
        rec = lowpass_filter(demod, cutoff=base_freqs[i]*2, fs=fs)
        recovered.append(rec)

    fig2 = go.Figure()
    for i in range(num):
        fig2.add_trace(go.Scatter(
            x=t,
            y=recovered[i],
            name=f"Recovered {i+1}",
            line=dict(color=colors[i])
        ))

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # Insight
    # =========================
    st.markdown("## 🎯 Insight")

    st.markdown("""
    🔥 FDM = แยกกันด้วยความถี่ (Frequency Domain)

    📊 ใน Spectrum:
    - แต่ละ peak = 1 channel
    - ไม่ชนกัน → แยกได้
    - ถ้าใกล้กัน → overlap → error

    🧠 Demux:
    - คูณ carrier
    - low-pass filter
    """)