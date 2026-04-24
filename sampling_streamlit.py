import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def run():
    st.title("📡 Sampling, Quantization & Aliasing Lab")

    # =========================
    # CONTROL PANEL
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        f_signal = st.slider("Signal Frequency (Hz)", 1, 20, 10)

    with col2:
        fs_sample = st.slider("Sampling Rate fs (Hz)", 5, 50, 15)

    with col3:
        n_bits = st.slider("Bit Depth (bits)", 1, 8, 4)

    # =========================
    # TIME BASE
    # =========================
    t = np.linspace(0, 1, 1000)
    x = np.sin(2*np.pi*f_signal*t)

    t_sample = np.linspace(0, 1, fs_sample)
    x_sample = np.sin(2*np.pi*f_signal*t_sample)

    # =========================
    # QUANTIZATION
    # =========================
    L = 2**n_bits
    delta = 2 / L
    xq = np.round((x_sample + 1)/delta)*delta - 1

    error = x_sample - xq

    # =========================
    # ALIASING
    # =========================
    k = int(round(f_signal / fs_sample))
    f_alias = abs(f_signal - k * fs_sample)

    # =========================
    # FFT
    # =========================
    def compute_fft(signal, fs):
        N = len(signal)
        fft = np.fft.fft(signal)
        freq = np.fft.fftfreq(N, d=1/fs)
        mask = freq >= 0
        return freq[mask], np.abs(fft[mask])

    freq_orig, fft_orig = compute_fft(x, 1000)
    freq_sample, fft_sample = compute_fft(x_sample, fs_sample)

    # =========================
    # STATUS
    # =========================
    if fs_sample < 2 * f_signal:
        status = "⚠️ ALIASING"
        color = 'red'
    else:
        status = "✅ OK (Nyquist satisfied)"
        color = 'green'

    title_text = f"f={f_signal}Hz | fs={fs_sample}Hz | alias={f_alias:.2f}Hz"

    # =========================
    # PLOT
    # =========================
    fig, axs = plt.subplots(4, 1, figsize=(8, 10))
    plt.subplots_adjust(hspace=0.5)

    # ADC Output
    axs[0].plot(t, x, label="Original")
    axs[0].stem(t_sample, xq, linefmt='r-', markerfmt='ro', basefmt=" ")
    axs[0].set_title("ADC Output\n" + title_text, color=color)
    axs[0].legend()

    # Sampling vs Quantization
    axs[1].plot(t_sample, x_sample, label="Sampled")
    axs[1].plot(t_sample, xq, label="Quantized")
    axs[1].set_title("Sampling vs Quantization")
    axs[1].legend()

    # Error
    axs[2].plot(t_sample, error, label="Error")
    axs[2].set_title("Quantization Error")
    axs[2].legend()

    # FFT
    axs[3].plot(freq_orig, fft_orig, label="Original Spectrum")
    axs[3].plot(freq_sample, fft_sample, label="Sampled Spectrum")
    axs[3].axvline(f_signal, color='green', linestyle='--', label='True f')
    axs[3].axvline(f_alias, color='red', linestyle='--', label='Alias f')
    axs[3].set_xlim(0, max(20, f_signal*3))
    axs[3].set_title("Frequency Spectrum (FFT)")
    axs[3].legend()

    st.pyplot(fig)

    # =========================
    # FORMULAS (🔥 เพิ่มใหม่)
    # =========================
    st.markdown("---")
    st.header("📐 สมการที่ใช้")

    st.latex(r"f_s \geq 2f \quad \text{(Nyquist Criterion)}")
    st.latex(r"f_{alias} = |f - kf_s|")
    st.latex(r"L = 2^n")
    st.latex(r"\Delta = \frac{2}{L}")
    st.latex(r"x_q = \text{round}\left(\frac{x+1}{\Delta}\right)\Delta - 1")

    # =========================
    # CALCULATION STEP
    # =========================
    st.markdown("---")
    if st.checkbox("🔍 แสดงวิธีคำนวณ"):

        st.subheader("Step-by-step")

        st.write(f"1. Sampling Rate (fs) = {fs_sample} Hz")
        st.write(f"2. Signal Frequency (f) = {f_signal} Hz")
        st.write(f"3. Nyquist = 2f = {2*f_signal} Hz")

        if fs_sample < 2*f_signal:
            st.error("→ fs < 2f → เกิด Aliasing")
        else:
            st.success("→ fs ≥ 2f → ไม่เกิด Aliasing")

        st.write(f"4. Quantization Levels = 2^{n_bits} = {L}")
        st.write(f"5. Step size Δ = {delta:.4f}")
        st.write(f"6. Alias frequency = {f_alias:.2f} Hz")

    # =========================
    # INSIGHT
    # =========================
    st.markdown("---")
    st.info("💡 fs < 2f → เกิด aliasing (ความถี่เพี้ยน)")
    st.info("💡 n เพิ่ม → quantization ดีขึ้น")
    st.info("💡 FFT ใช้ดู frequency จริง vs alias")
