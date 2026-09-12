"""Run with: streamlit run quantization_streamlit.py."""

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from quantization2 import DURATION, SIGNAL_FREQUENCY, VREF, quantize_signal


def run():
    st.header("ADC Sampling, Quantization & Encoding")
    st.caption("Analog → Sampling → Quantization → Binary Encoding")
    controls = st.columns(2)
    bit_depth = controls[0].slider("Bit Depth (n)", 2, 12, 3)
    sampling_rate = controls[1].slider("Sampling Rate (Hz)", 4, 100, 16)

    time_fine = np.linspace(0, DURATION, 2000)
    analog = 2.5 + 2.2 * np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_fine)
    times = np.linspace(0, DURATION, int(round(sampling_rate * DURATION)) + 1)
    samples = 2.5 + 2.2 * np.sin(2 * np.pi * SIGNAL_FREQUENCY * times)
    codes, quantized, errors = quantize_signal(samples, bit_depth)
    levels = 2**bit_depth
    lsb = VREF / levels
    selected = len(times) // 2

    left, right = st.columns(2)
    with left:
        st.subheader("Quantization calculation")
        st.code(
            f"VREF             = {VREF:.1f} V\n"
            f"Signal Frequency = {SIGNAL_FREQUENCY:g} Hz\n"
            f"Sampling Rate    = {sampling_rate} Hz\n"
            f"Bit Depth        = {bit_depth} bits\n"
            f"Levels (2^n)     = {levels:,}\n"
            f"1 LSB            = {lsb:.4f} V\n"
            f"Max Q. Error     = +/-{lsb / 2:.4f} V\n"
            f"Bit Rate         = {sampling_rate * bit_depth:,} bps",
            language=None,
        )
    with right:
        st.subheader("Current sample")
        st.code(
            f"Time         = {times[selected]:.3f} s\n"
            f"Analog Input = {samples[selected]:.4f} V\n"
            f"ADC Code     = {codes[selected]}\n"
            f"Binary Code  = {int(codes[selected]):0{bit_depth}b}\n"
            f"Quantized    = {quantized[selected]:.4f} V\n"
            f"Error        = {errors[selected]:+.4f} V",
            language=None,
        )

    figure = Figure(figsize=(10, 4), layout="constrained")
    axis = figure.subplots()
    axis.plot(time_fine, analog, "--", color="gray", label="Original Analog")
    axis.plot(times, samples, "o", color="tab:blue", label="Sample Points")
    axis.step(times, quantized, where="post", color="tab:red", label="Quantized Signal")
    if bit_depth <= 4:
        for level in range(levels + 1):
            axis.axhline(level * lsb, color="tab:orange", linewidth=0.7,
                         alpha=0.45, linestyle=":", zorder=0)
    axis.set(xlim=(0, DURATION), ylim=(0, VREF), xlabel="Time (s)", ylabel="Voltage (V)")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="lower right")
    st.pyplot(figure)


if __name__ == "__main__":
    st.set_page_config(page_title="ADC Quantization Lab", layout="wide")
    run()
