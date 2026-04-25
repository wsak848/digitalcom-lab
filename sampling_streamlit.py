import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

def run():
    st.title("📡 Sampling, Quantization & Aliasing Lab (Advanced)")

    # =========================
    # CONTROL
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        f_signal = st.slider("Signal Frequency (Hz)", 1, 20, 7)

    with col2:
        fs_sample = st.slider("Sampling Rate fs (Hz)", 5, 50, 30)

    with col3:
        n_bits = st.slider("Bit Depth (bits)", 1, 8, 8)

    animate = st.checkbox("🎬 Show Aliasing Animation")

    duration = 1.0

    # =========================
    # TIME BASE
    # =========================
    t = np.linspace(0, duration, 1000)
    x = np.sin(2*np.pi*f_signal*t)

    # ✅ FIX sampling
    t_sample = np.arange(0, duration, 1/fs_sample)
    x_sample = np.sin(2*np.pi*f_signal*t_sample)

    # =========================
    # QUANTIZATION
    # =========================
    L = 2**n_bits
    x_norm = (x_sample + 1) / 2
    xq = np.round(x_norm * (L - 1)) / (L - 1)
    xq = xq * 2 - 1

    error = x_sample - xq

    # =========================
    # ALIAS
    # =========================
    f_alias = abs((f_signal + fs_sample/2) % fs_sample - fs_sample/2)

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
    nyquist = 2 * f_signal

    if fs_sample < nyquist:
        status = "⚠️ ALIASING"
        color = 'red'
    else:
        status = "✅ OK (Nyquist satisfied)"
        color = 'green'

    title_text = f"f={f_signal}Hz | fs={fs_sample}Hz | alias={f_alias:.2f}Hz"

    # =========================
    # PLOT
    # =========================
    def plot_all(highlight=False):
        fig, axs = plt.subplots(4, 1, figsize=(8, 10))
        plt.subplots_adjust(hspace=0.5)

        # 1. ADC Output
        axs[0].plot(t, x, label="Original")
        axs[0].stem(t_sample, x_sample,
                    linefmt='r-', markerfmt='ro', basefmt=" ")
        axs[0].set_title("ADC Output\n" + title_text, color=color)
        axs[0].legend()

        # 2. Overlay
        x_interp = np.interp(t, t_sample, x_sample)

        axs[1].plot(t, x_interp, color='blue', linewidth=3,
                    label="Sampled (Interpolated)", zorder=3)

        axs[1].scatter(t_sample, x_sample,
                       color='blue', s=30, label="Sample Points", zorder=4)

        axs[1].step(t_sample, xq,
                    where='mid', color='orange', linewidth=2,
                    label="Quantized (Step)", zorder=2)

        axs[1].set_title("Sampling vs Quantization (Overlay Comparison)")
        axs[1].legend()

        # 3. Error
        axs[2].plot(t_sample, error, label="Error")
        axs[2].set_title("Quantization Error")
        axs[2].legend()

        # 4. FFT
        axs[3].plot(freq_orig, fft_orig, label="Original Spectrum")
        axs[3].plot(freq_sample, fft_sample, label="Sampled Spectrum")

        axs[3].axvline(f_signal, color='green', linestyle='--', label='True f')
        axs[3].axvline(f_alias, color='red', linestyle='--', label='Alias f')

        axs[3].set_xlim(0, max(20, f_signal*3))
        axs[3].set_title("Frequency Spectrum (FFT)")
        axs[3].legend()

        return fig

    # =========================
    # DISPLAY
    # =========================
    if not animate:
        st.pyplot(plot_all())
    else:
        placeholder = st.empty()
        for i in range(6):
            fig = plot_all(highlight=(i % 2 == 0))
            placeholder.pyplot(fig)
            time.sleep(0.5)

    # =========================
    # 📐 FORMULAS (กลับมาแล้ว)
    # =========================
    st.markdown("---")
    st.header("📐 สมการที่ใช้")

    st.latex(r"f_s \geq 2f \quad (Nyquist\ Criterion)")
    st.latex(r"f_{alias} = \left| (f + \frac{f_s}{2}) \bmod f_s - \frac{f_s}{2} \right|")
    st.latex(r"L = 2^n")
    st.latex(r"x_q = \frac{\text{round}(x_{norm}(L-1))}{L-1}")

    # =========================
    # 🔍 STEP-BY-STEP (กลับมาแล้ว)
    # =========================
    st.markdown("---")
    if st.checkbox("🔍 แสดงวิธีคำนวณ"):

        st.write(f"1. Signal Frequency f = {f_signal} Hz")
        st.write(f"2. Sampling Rate fs = {fs_sample} Hz")
        st.write(f"3. Nyquist = 2f = {nyquist} Hz")

        if fs_sample < nyquist:
            st.error("→ fs < 2f → เกิด Aliasing")
        else:
            st.success("→ fs ≥ 2f → ไม่เกิด Aliasing")

        st.write(f"4. Quantization Levels = 2^{n_bits} = {L}")
        st.write(f"5. Alias Frequency = {f_alias:.2f} Hz")

    # =========================
    # INSIGHT
    # =========================
    st.markdown("---")
    st.info("💡 fs < 2f → aliasing (ความถี่เพี้ยน)")
    st.info("💡 fs สูง → sample หนาแน่นขึ้น")
    st.info("💡 n สูง → quantization ดีขึ้น")
    st.info("💡 FFT ใช้ตรวจ alias ได้ดีที่สุด")
