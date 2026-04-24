import numpy as np
import matplotlib.pyplot as plt

def run():
    # =========================
    # PARAMETERS (ตั้งค่าพื้นฐาน)
    # =========================
    f_signal = 10     # Hz
    fs_sample = 15    # Hz (ลองเปลี่ยนเพื่อดู aliasing)
    n_bits = 4

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
    # ALIAS CALCULATION
    # =========================
    k = int(round(f_signal / fs_sample))
    f_alias = abs(f_signal - k * fs_sample)

    # =========================
    # FFT FUNCTION
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
        status = "✅ OK"
        color = 'green'

    title_text = f"f={f_signal}Hz | fs={fs_sample}Hz | alias={f_alias:.2f}Hz | {status}"

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

    return fig