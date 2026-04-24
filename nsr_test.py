import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("📡 SNR Interactive Lab")

    # =========================
    # CONTROL
    # =========================
    freq = st.slider("Signal Frequency (Hz)", 1, 20, 5)
    noise_amp = st.slider("Noise Amplitude", 0.0, 2.0, 0.3)
    duration = st.slider("Duration (s)", 0.5, 2.0, 1.0)

    fs = 500
    t = np.linspace(0, duration, int(fs * duration))

    # =========================
    # SIGNAL
    # =========================
    signal = np.sin(2 * np.pi * freq * t)
    noise = noise_amp * np.random.randn(len(t))
    noisy = signal + noise

    # =========================
    # SNR CALCULATION
    # =========================
    signal_power = np.mean(signal**2)
    noise_power = np.mean(noise**2)

    if noise_power == 0:
        snr_db = float("inf")
    else:
        snr_db = 10 * np.log10(signal_power / noise_power)

    # =========================
    # PLOT (Overlay)
    # =========================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t, y=signal,
        name="Signal",
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=t, y=noisy,
        name="Noisy Signal",
        line=dict(width=2)
    ))

    fig.add_trace(go.Scatter(
        x=t, y=noise,
        name="Noise",
        line=dict(dash='dot')
    ))

    fig.update_layout(
        title=f"SNR = {snr_db:.2f} dB",
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
        st.metric("Signal Power", f"{signal_power:.4f}")
        st.metric("Noise Power", f"{noise_power:.4f}")

    with col2:
        st.metric("SNR (dB)", f"{snr_db:.2f} dB")

    # =========================
    # CALCULATION DETAIL
    # =========================
    st.markdown("---")
    if st.checkbox("🔍 แสดงวิธีคำนวณ (Show Calculation Steps)"):

        st.markdown("### 📐 สูตรที่ใช้")

        st.latex(r"SNR = \frac{P_{signal}}{P_{noise}}")
        st.latex(r"SNR_{dB} = 10 \log_{10}\left(\frac{P_{signal}}{P_{noise}}\right)")

        st.markdown("### 🧮 คำนวณจากค่าจริง")

        st.write(f"Signal Power = mean(signal²) = {signal_power:.4f}")
        st.write(f"Noise Power = mean(noise²) = {noise_power:.4f}")

        if noise_power != 0:
            ratio = signal_power / noise_power
            st.write(f"SNR (linear) = {signal_power:.4f} / {noise_power:.4f} = {ratio:.4f}")
            st.write(f"SNR (dB) = 10 log10({ratio:.4f}) = {snr_db:.2f} dB")
        else:
            st.write("Noise = 0 → SNR = ∞")

        st.info("💡 SNR คืออัตราส่วนกำลังของสัญญาณต่อ Noise")

    # =========================
    # INSIGHT
    # =========================
    st.markdown("---")
    st.info("💡 Noise เพิ่ม → SNR ลด")
    st.info("💡 SNR สูง → สัญญาณชัด")
    st.info("💡 SNR ต่ำ → สัญญาณเพี้ยน")
