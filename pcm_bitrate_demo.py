import numpy as np
import matplotlib.pyplot as plt

def run():
    # =========================
    # PARAMETERS
    # =========================
    f_signal = 2       # Hz
    duration = 1.0     # seconds

    # time base (analog)
    t_fine = np.linspace(0, duration, 1000)
    y_analog = np.sin(2 * np.pi * f_signal * t_fine)

    # =========================
    # PCM FUNCTION
    # =========================
    def generate_pcm(fs, bit_depth):
        t_sample = np.arange(0, duration, 1/fs)
        y_sample = np.sin(2 * np.pi * f_signal * t_sample)

        levels = 2**bit_depth

        # quantization
        y_quantized = np.round(((y_sample + 1) / 2) * (levels - 1))
        y_normalized = (y_quantized / (levels - 1)) * 2 - 1

        bitrate = fs * bit_depth
        return t_sample, y_normalized, bitrate

    # =========================
    # CASE A (Low bitrate)
    # =========================
    fs1, depth1 = 12, 3
    t1, y1, br1 = generate_pcm(fs1, depth1)

    # =========================
    # CASE B (High bitrate)
    # =========================
    fs2, depth2 = 60, 8
    t2, y2, br2 = generate_pcm(fs2, depth2)

    # =========================
    # PLOT
    # =========================
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(hspace=0.4)

    # --- Low Bitrate ---
    ax1.plot(t_fine, y_analog, 'k--', alpha=0.3, label='Original Analog')
    ax1.step(t1, y1, where='mid', color='red', label=f'{depth1}-bit PCM')
    ax1.stem(t1, y1, linefmt='r-', markerfmt='ro', basefmt=" ")
    ax1.set_title(f"Low Bitrate = {br1} bps (fs={fs1}, bits={depth1})")
    ax1.legend()
    ax1.grid(True)

    # --- High Bitrate ---
    ax2.plot(t_fine, y_analog, 'k--', alpha=0.3, label='Original Analog')
    ax2.step(t2, y2, where='mid', color='blue', label=f'{depth2}-bit PCM')
    ax2.stem(t2, y2, linefmt='b-', markerfmt='bo', basefmt=" ")
    ax2.set_title(f"High Bitrate = {br2} bps (fs={fs2}, bits={depth2})")
    ax2.legend()
    ax2.grid(True)

    return fig