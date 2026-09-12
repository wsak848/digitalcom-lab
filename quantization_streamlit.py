"""Run with: streamlit run quantization_streamlit.py."""

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from quantization2 import DURATION, SIGNAL_FREQUENCY, VREF, quantize_signal


def run():
    st.header("ADC Sampling, Quantization & Encoding")
    st.caption("Analog → Sampling → Quantization → Binary Encoding")
    # Reserve display positions so the graph uses this run's slider values
    # while the controls remain immediately below it.
    summary = st.container()
    with st.container():
        graph = st.container()
        bit_depth = st.slider("Bit Depth (bits)", 2, 12, 3)
        sampling_rate = st.slider("Sampling Rate (Hz)", 4, 100, 16)

    time_fine = np.linspace(0, DURATION, 2000)
    analog = 2.5 + 2.2 * np.sin(2 * np.pi * SIGNAL_FREQUENCY * time_fine)
    times = np.linspace(0, DURATION, int(round(sampling_rate * DURATION)) + 1)
    samples = 2.5 + 2.2 * np.sin(2 * np.pi * SIGNAL_FREQUENCY * times)
    codes, quantized, errors = quantize_signal(samples, bit_depth)
    levels = 2**bit_depth
    lsb = VREF / levels
    selected = len(times) // 2

    with summary:
        st.markdown(
            f"**VREF:** {VREF:.1f} V · **Signal:** {SIGNAL_FREQUENCY:g} Hz  \n"
            f"**Sampling:** {sampling_rate} Hz · **Bit depth:** {bit_depth} bits  \n"
            f"**Levels:** {levels:,} · **1 LSB:** {lsb:.4f} V  \n"
            f"**Max Q. Error:** ±{lsb / 2:.4f} V · "
            f"**Bit Rate:** {sampling_rate * bit_depth:,} bps"
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
    with graph:
        st.pyplot(figure, width="stretch")

    with st.container():
        st.subheader("Current sample")
        st.markdown(
            f"**Time:** {times[selected]:.3f} s  \n"
            f"**Analog Input:** {samples[selected]:.4f} V  \n"
            f"**ADC Code:** {codes[selected]} · "
            f"**Binary Code:** `{int(codes[selected]):0{bit_depth}b}`  \n"
            f"**Quantized:** {quantized[selected]:.4f} V  \n"
            f"**Error:** {errors[selected]:+.4f} V"
        )


if __name__ == "__main__":
    st.set_page_config(page_title="ADC Quantization Lab", layout="wide")
    run()
