"""Offline teaching lab. Run: python -m streamlit run digital_transmission_lab.py."""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


LEVELS = (2, 4, 8, 16)
PRESETS = ("10110010", "11111111", "00000000", "10101010", "11001100")


def show_figure(fig):
    """Fit plots to the screen and release the figure after each rerun."""
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def set_bit_stream(value):
    st.session_state["bit_stream"] = value


def waveform(bits, bit_rate, encoding):
    """Draw at most eight bits per row, preserving absolute time on each row."""
    tb = 1.0 / bit_rate
    row_count = (len(bits) + 7) // 8
    fig, axes = plt.subplots(row_count, 1, figsize=(7, 2.5 * row_count),
                             squeeze=False, constrained_layout=True)
    for row, ax in enumerate(axes[:, 0]):
        start = row * 8
        chunk = bits[start:start + 8]
        values = np.array([int(bit) for bit in chunk])
        if encoding == "Manchester":
            # Convention: 1 = LOW -> HIGH; 0 = HIGH -> LOW.
            values = np.column_stack((1 - values, values)).ravel()
            step = tb / 2
        else:
            step = tb
        edges = start * tb + np.arange(len(values) + 1) * step
        ax.step(edges, np.append(values, values[-1]), where="post",
                linewidth=2.5, color="#0072B2")
        boundaries = np.arange(start, start + len(chunk) + 1) * tb
        for boundary in boundaries:
            ax.axvline(boundary, color="gray", linestyle=":", alpha=0.6)
        for index, bit in enumerate(chunk):
            ax.text((start + index + 0.5) * tb, 1.23, bit,
                    ha="center", fontsize=13, weight="bold")
        ax.set(xlim=(boundaries[0], boundaries[-1]), ylim=(-0.25, 1.55),
               xlabel="Time (seconds)", ylabel="Signal Level")
        ax.set_xticks(boundaries)
        ax.set_xticklabels([f"{time:.3g}" for time in boundaries], fontsize=9)
        ax.set_yticks([0, 1], ["LOW (0)", "HIGH (1)"])
        ax.spines[["top", "right"]].set_visible(False)
    return fig


def adc_experiment():
    st.subheader("ADC → Bit Rate")
    st.write("ADC แปลงสัญญาณ Analog เป็นข้อมูล Digital โดยสุ่มตัวอย่างและแทนแต่ละตัวอย่างด้วยบิต")
    mode = st.selectbox("Sampling Rate — เลือกค่าหรือกำหนดเอง",
                        [8000, 16000, 44100, 48000, "กำหนดเอง"])
    fs = (st.slider("Sampling Rate (samples/s)", 1000, 48000, 8000, 1)
          if mode == "กำหนดเอง" else mode)
    resolution = st.selectbox("ADC Resolution (bits/sample)", [4, 8, 12, 16, 24], index=1)
    # One channel of uncompressed samples; framing overhead is excluded.
    rate = fs * resolution
    st.latex(r"R_b = f_s \times n")
    st.metric("Bit Rate (bps)", f"{rate:,}")
    st.metric("Bit Rate (kbps)", f"{rate / 1000:,.3f}")
    st.write(f"Sampling Rate: **{fs:,} samples/s** · ADC Resolution: **{resolution} bits/sample**")
    st.write(f"Quantization levels = 2^{resolution} = **{2 ** resolution:,} ระดับ**")
    st.write(f"Bit period = 1/Rb = **{1e6 / rate:,.3f} µs**")
    st.info("เพิ่ม Sampling Rate จะได้ตัวอย่างต่อวินาทีมากขึ้น และเพิ่ม Resolution จะได้ระดับ Quantization "
            "ละเอียดขึ้น ทั้งสองอย่างทำให้ Bit Rate เพิ่มขึ้น ตัวอย่าง 8,000 × 8 = 64,000 bps = 64 kbps "
            "คำนวณสำหรับ 1 ช่องสัญญาณ ไม่บีบอัดและไม่รวมบิตส่วนเกิน โดย 1 kbps = 1,000 bps")
    st.markdown("### โจทย์ทดลอง")
    st.write("เปรียบเทียบ 8,000 Hz / 8 bit, 8,000 Hz / 16 bit และ 44,100 Hz / 16 bit "
             "แล้วอธิบายว่า ADC Resolution และ Sampling Rate ส่งผลต่อ Bit Rate อย่างไร")


def line_coding_experiment():
    st.subheader("Bit Stream → Digital Signal")
    st.write("เลือกชุดบิตและวิธี Line Coding เพื่อดูรูปคลื่นตามเวลา")
    st.caption("ชุดบิตตัวอย่าง — กดเพื่อแทนที่ข้อความด้านล่าง")
    for preset in PRESETS:
        st.button(preset, key=f"preset_{preset}", on_click=set_bit_stream, args=(preset,))
    if "bit_stream" not in st.session_state:
        st.session_state["bit_stream"] = "10110010"
    bits = st.text_input("Bit Stream — ใส่เฉพาะ 0 และ 1 (สูงสุด 64 บิต)",
                         max_chars=64, key="bit_stream")
    encoding = st.selectbox("Line Coding", ["NRZ-L", "Manchester"])
    rate = st.slider("Bit Rate (bps)", 1, 20, 4)
    st.caption("NRZ-L: 1 = HIGH, 0 = LOW · Manchester: 1 = LOW → HIGH, "
               "0 = HIGH → LOW โดยเปลี่ยนระดับที่กึ่งกลางทุกบิต")
    valid = bool(bits) and len(bits) <= 64 and all(bit in "01" for bit in bits)
    if not valid:
        st.error("กรุณาใส่บิต 0 และ 1 จำนวน 1–64 บิตเท่านั้น ไม่ใส่ช่องว่างหรือตัวอักษรอื่น")
    else:
        show_figure(waveform(bits, rate, encoding))
        st.caption("แบ่งกราฟทุก 8 บิตเพื่อให้อ่านง่ายบนมือถือ แกนเวลาแสดงเวลาต่อเนื่องของข้อมูลชุดเดียวกัน")
        st.write("Bit Stream:")
        st.code(bits, language=None, wrap_lines=True)
        st.write(f"Bit Rate: **{rate} bps** · Bit Period Tb = 1/Rb: **{1 / rate:.4f} s**")
        st.write(f"จำนวนบิต: **{len(bits)}** · เวลาส่งทั้งหมด: **{len(bits) / rate:.4f} s**")
    st.info("ลองชุด 11111111: NRZ-L คงระดับเดิมตลอดชุด แต่ Manchester เปลี่ยนระดับกลางทุกบิต "
            "จึงมีจุดอ้างอิงช่วยให้ตัวรับทำ Synchronization ได้ การเปลี่ยนระดับไม่ใช่จำนวนบิตข้อมูลที่เพิ่มขึ้น")
    st.markdown("### โจทย์ทดลอง")
    st.write("เปรียบเทียบ 11111111 และ 10101010 ด้วย NRZ-L และ Manchester ที่ Bit Rate เท่ากัน "
             "รูปคลื่นใดมีการเปลี่ยนระดับมากกว่า? การไม่มี Transition เป็นเวลานานส่งผลต่อการจับจังหวะอย่างไร?")


def baud_experiment():
    st.subheader("Baud Rate & Signal Levels")
    baud = st.slider("Baud Rate (symbols/s)", 100, 10000, 1000, 100)
    levels = st.selectbox("Signal Levels M", LEVELS, key="baud_levels")
    bits_per_symbol = int(np.log2(levels))
    st.latex(r"k = \log_2(M), \qquad R_b = R_s \log_2(M)")
    st.metric("Bits per Symbol", bits_per_symbol)
    st.metric("Bit Rate (bps)", f"{baud * bits_per_symbol:,}")
    st.write(f"Baud Rate = **{baud:,} baud** · M = **{levels}**")
    st.table({"M": list(LEVELS), "bits/symbol": [int(np.log2(m)) for m in LEVELS],
              "Bit Rate (bps)": [baud * int(np.log2(m)) for m in LEVELS]})
    st.info("Bit Rate คือปริมาณข้อมูลเป็นบิตต่อวินาที ส่วน Baud Rate คือจำนวน Symbol ต่อวินาที "
            "เมื่อ M = 2 หนึ่ง Symbol แทน 1 บิต จึงมีค่าตัวเลขเท่ากัน เมื่อ M มากขึ้นหนึ่ง Symbol "
            "แทนได้หลายบิต เช่น M = 4 แทนได้ 2 bits/symbol โดย Symbol ที่ติดกันอาจมีระดับเท่ากันได้")
    st.markdown("### โจทย์ทดลอง")
    st.write("ตั้ง Baud Rate = 1,000 baud ทดลอง M = 2, 4, 8, 16 และบันทึก Bit Rate "
             "อธิบายว่าทำไมจำนวน Symbol ต่อวินาทีเท่าเดิม แต่จำนวนบิตต่อวินาทีเพิ่มขึ้น")


def nyquist_experiment():
    st.subheader("Bandwidth & Nyquist")
    bandwidth = st.slider("Bandwidth B (Hz)", 100, 20000, 3000, 100)
    levels = st.selectbox("Signal Levels M", LEVELS, key="nyquist_levels")
    bits_per_symbol = int(np.log2(levels))
    # Nyquist limit for an ideal noiseless channel (not the ADC sampling rule).
    maximum = 2 * bandwidth * bits_per_symbol
    st.latex(r"R_{\max} = 2 B \log_2(M)")
    rates = 2 * bandwidth * np.log2(np.array(LEVELS))
    fig, ax = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
    ax.plot(LEVELS, rates, "o-", color="#0072B2", linewidth=2)
    ax.scatter([levels], [maximum], color="#D55E00", s=100, zorder=3, label="Selected M")
    ax.set(xlabel="Signal Levels M", ylabel="Maximum Bit Rate (bps)",
           xticks=LEVELS, ylim=(0, rates[-1] * 1.15))
    ax.ticklabel_format(axis="y", style="plain")
    ax.grid(alpha=0.25)
    ax.legend()
    show_figure(fig)
    st.write(f"Bandwidth: **{bandwidth:,} Hz** · Signal Levels: **{levels}** · "
             f"Bits per Symbol: **{bits_per_symbol}**")
    st.metric("Maximum Bit Rate (bps)", f"{maximum:,}")
    st.metric("Maximum Bit Rate (kbps)", f"{maximum / 1000:,.3f}")
    st.info("สูตร Nyquist ในการทดลองนี้ใช้กับช่องสัญญาณอุดมคติที่ไม่มี Noise "
            "ระบบจริงมี Noise และข้อจำกัดอื่น ๆ ดังนั้นอัตราข้อมูลจริงอาจต่ำกว่าค่าทฤษฎี")
    st.write("เมื่อ B = 3,000 Hz: M = 2 ให้ Rmax = 6,000 bps และ M = 4 ให้ Rmax = 12,000 bps "
             "การเพิ่ม M ทำให้แต่ละ Symbol แทนบิตได้มากขึ้น แต่ในระบบจริงต้องแยกระดับสัญญาณให้ได้ด้วย")
    st.markdown("### โจทย์ทดลอง")
    st.write("ตั้ง Bandwidth = 3,000 Hz ทดลอง M = 2, 4, 8, 16 และบันทึก Rmax "
             "เมื่อเพิ่ม M เป็นสองเท่า Rmax เพิ่มขึ้นเท่าไร? แล้วลองเพิ่ม Bandwidth เป็นสองเท่าและเปรียบเทียบผล")


def render_digital_transmission_lab():
    """Render all four experiments; the calling app owns page configuration."""
    st.title("Digital Transmission Lab")
    st.subheader("Broadband Communication")
    st.write("ห้องทดลองการส่งข้อมูลดิจิทัล: ปรับค่า สังเกตผล และอธิบายความสัมพันธ์ด้วยตนเอง")
    with st.expander("เส้นทางจากสัญญาณ Analog สู่เครือข่าย Broadband", expanded=True):
        st.markdown("**Analog Signal**  \n↓  \n**ADC**  \n↓  \n**Digital Data**  \n↓  \n"
                    "**Line Coding**  \n↓  \n**Transmission Channel**  \n↓  \n**Broadband Network**")
    tabs = st.tabs(["ADC → Bit Rate", "Line Coding", "Baud Rate", "Nyquist"])
    for tab, experiment in zip(tabs, (adc_experiment, line_coding_experiment,
                                     baud_experiment, nyquist_experiment)):
        with tab:
            experiment()


def main():
    """Configure the page only when running this lab as a standalone app."""
    st.set_page_config(page_title="Digital Transmission Lab", page_icon="📡", layout="centered")
    render_digital_transmission_lab()


if __name__ == "__main__":
    main()
