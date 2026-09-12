import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


# ADC and signal parameters
VREF = 5.0
SIGNAL_FREQUENCY = 2.0
DURATION = 1.0
ANALOG_POINT_COUNT = 2000


def quantize_signal(input_voltage, bit_depth):
    """Return ADC codes, midpoint voltages, and quantization errors."""
    levels = 2**bit_depth
    lsb = VREF / levels

    # Clip the code so an input at VREF stays inside the ADC code range.
    code = np.floor(input_voltage / lsb).astype(int)
    code = np.clip(code, 0, levels - 1)
    quantized_voltage = (code + 0.5) * lsb
    error = input_voltage - quantized_voltage
    return code, quantized_voltage, error


def format_signed_voltage(value):
    """Format an error with its sign for the current-sample panel."""
    return f"{value:+.4f} V"


def main():
    time_fine = np.linspace(0, DURATION, ANALOG_POINT_COUNT)
    analog_signal = 2.5 + 2.2 * np.sin(
        2 * np.pi * SIGNAL_FREQUENCY * time_fine
    )

    figure, axis = plt.subplots(figsize=(12, 8))
    # Reserve a header area for the calculation panels above the graph.
    plt.subplots_adjust(left=0.10, right=0.96, top=0.64, bottom=0.22)

    figure.suptitle(
        "ADC Sampling, Quantization & Encoding Simulation",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    figure.text(
        0.5,
        0.94,
        "Analog -> Sampling -> Quantization -> Binary Encoding",
        ha="center",
        fontsize=11,
    )
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Voltage (V)")
    axis.set_xlim(0, DURATION)
    axis.set_ylim(0, VREF)
    axis.grid(True, alpha=0.25)

    original_line, = axis.plot(
        time_fine,
        analog_signal,
        "--",
        color="gray",
        alpha=0.8,
        label="Original Analog",
    )
    sample_line, = axis.plot(
        [],
        [],
        "o",
        color="tab:blue",
        markersize=6,
        label="Sample Points",
    )
    quantized_line, = axis.step(
        [],
        [],
        where="post",
        color="tab:red",
        linewidth=2,
        label="Quantized Signal",
    )
    axis.legend(loc="lower right")

    calculation_box = figure.text(
        0.10,
        0.89,
        "",
        va="top",
        ha="left",
        fontsize=10,
        family="monospace",
        bbox={"boxstyle": "round", "facecolor": "#fff4cc", "alpha": 0.95},
    )
    sample_box = figure.text(
        0.96,
        0.89,
        "",
        va="top",
        ha="right",
        fontsize=10,
        family="monospace",
        bbox={"boxstyle": "round", "facecolor": "#dff2ff", "alpha": 0.95},
    )

    # Only draw individual level lines for low bit depths to keep the graph readable.
    level_lines = []

    bit_axis = figure.add_axes([0.16, 0.105, 0.68, 0.03])
    sample_axis = figure.add_axes([0.16, 0.055, 0.68, 0.03])
    bit_slider = Slider(bit_axis, "Bit Depth (n)", 2, 12, valinit=3, valstep=1)
    sample_slider = Slider(
        sample_axis, "Sampling Rate (Hz)", 4, 100, valinit=16, valstep=1
    )

    def update(_value):
        bit_depth = int(bit_slider.val)
        sampling_rate = int(sample_slider.val)
        levels = 2**bit_depth
        lsb = VREF / levels
        max_error = lsb / 2

        # Sampling uses integer time indices so the sample count changes clearly.
        sample_count = max(2, int(round(sampling_rate * DURATION)) + 1)
        sample_times = np.linspace(0, DURATION, sample_count)
        sample_signal = 2.5 + 2.2 * np.sin(
            2 * np.pi * SIGNAL_FREQUENCY * sample_times
        )
        sample_codes, sample_quantized, sample_error = quantize_signal(
            sample_signal, bit_depth
        )

        sample_line.set_data(sample_times, sample_signal)
        quantized_line.set_data(sample_times, sample_quantized)

        for line in level_lines:
            line.remove()
        level_lines.clear()
        if bit_depth <= 4:
            for level in range(levels + 1):
                level_lines.append(
                    axis.axhline(
                        level * lsb,
                        color="tab:orange",
                        linewidth=0.7,
                        alpha=0.45,
                        linestyle=":",
                        zorder=0,
                    )
                )

        selected_index = len(sample_times) // 2
        selected_code = int(sample_codes[selected_index])
        binary_code = format(selected_code, f"0{bit_depth}b")
        calculation_box.set_text(
            "[ ADC / Quantization Calculation ]\n"
            f"VREF              = {VREF:.1f} V\n"
            f"Signal Frequency  = {SIGNAL_FREQUENCY:g} Hz\n"
            f"Sampling Rate     = {sampling_rate:d} Hz\n"
            f"Bit Depth (n)     = {bit_depth:d} bits\n"
            "--------------------------------\n"
            f"Levels (2^n)      = {levels:,d} levels\n"
            f"1 LSB             = {lsb:.4f} V\n"
            f"Max Q. Error      = +/-{max_error:.4f} V\n"
            f"Bit Rate          = {sampling_rate * bit_depth:,d} bps"
        )
        sample_box.set_text(
            "[ Current Sample ]\n"
            f"Time           = {sample_times[selected_index]:.3f} s\n"
            f"Analog Input   = {sample_signal[selected_index]:.4f} V\n"
            f"ADC Code       = {selected_code:d}\n"
            f"Binary Code    = {binary_code}\n"
            f"Quantized      = {sample_quantized[selected_index]:.4f} V\n"
            f"Error          = {format_signed_voltage(sample_error[selected_index])}"
        )
        figure.canvas.draw_idle()

    bit_slider.on_changed(update)
    sample_slider.on_changed(update)
    update(None)
    plt.show()


if __name__ == "__main__":
    main()
