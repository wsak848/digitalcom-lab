import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("🎛️ Quantization → Digital → Line Coding Lab")

    # =========================
    # INPUT
    # =========================
    fs = st.slider("Sampling Rate (Hz)", 100, 2000, 500)
    n = st.slider("Bit Depth (bits)", 1, 8, 3)
    freq = st.slider("Signal Frequency (Hz)", 1, 10, 2)
    noise = st.slider("Noise Level", 0.0, 0.5, 0.0)

    duration = 1.0

    # =========================
    # ANALOG SIGNAL
    # =========================
    t = np.linspace(0, duration, fs)
    y = 0.8 * np.sin(2 * np.pi * freq * t)

    # =========================
    # QUANTIZATION
    # =========================
    levels = 2**n
    y_scaled = (y + 1) / 2 * (levels - 1)
    indices = np.round(y_scaled).astype(int)

    yq = (indices / (levels - 1)) * 2 - 1
    yq_noisy = yq + noise * np.random.randn(len(yq))

    # =========================
    # PCM ENCODING (สำคัญ🔥)
    # =========================
    bitstream = ''.join([format(i, f'0{n}b') for i in indices[:20]])  # เอา 20 sample แรก

    st.markdown(f"### 🔢 PCM Bitstream (ตัวอย่าง)")
    st.code(bitstream)

    # =========================
    # DIGITAL SIGNAL (0/1)
    # =========================
    samples_per_bit = 20
    digital_signal = np.repeat([1 if b == '1' else 0 for b in bitstream], samples_per_bit)

    # =========================
    # LINE CODING FUNCTIONS
    # =========================
    def nrz_l(bits):
        return np.repeat([1 if b == "1" else -1 for b in bits], samples_per_bit)

    def manchester(bits):
        sig = []
        for b in bits:
            if b == "1":
                sig.extend([1]*(samples_per_bit//2) + [-1]*(samples_per_bit//2))
            else:
                sig.extend([-1]*(samples_per_bit//2) + [1]*(samples_per_bit//2))
        return np.array(sig)

    def rz(bits):
        sig = []
        for b in bits:
            if b == "1":
                sig.extend([1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
            else:
                sig.extend([-1]*(samples_per_bit//2) + [0]*(samples_per_bit//2))
        return np.array(sig)

    # =========================
    # PLOT OVERLAY
    # =========================
    st.subheader("📡 Digital vs Line Coding Overlay")

    selected = st.multiselect(
        "เลือกสัญญาณ",
        ["Digital (0/1)", "NRZ-L", "Manchester", "RZ"],
        default=["Digital (0/1)", "NRZ-L"]
    )

    fig = go.Figure()

    if "Digital (0/1)" in selected:
        fig.add_trace(go.Scatter(y=digital_signal, name="Digital Bits"))

    if "NRZ-L" in selected:
        fig.add_trace(go.Scatter(y=nrz_l(bitstream), name="NRZ-L"))

    if "Manchester" in selected:
        fig.add_trace(go.Scatter(y=manchester(bitstream), name="Manchester"))

    if "RZ" in selected:
        fig.add_trace(go.Scatter(y=rz(bitstream), name="RZ"))

    fig.update_layout(title="Overlay: Digital vs Line Coding")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INSIGHT
    # =========================
    st.markdown("---")
    st.info("💡 Digital = 0/1 ดิบ (ยังไม่เหมาะส่งจริง)")
    st.info("💡 Line Coding = แปลงเพื่อส่งผ่าน channel")
    st.info("💡 Manchester มี transition → sync ดีมาก")
