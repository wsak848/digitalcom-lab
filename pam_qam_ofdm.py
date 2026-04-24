import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("📡 PAM / QAM / OFDM (Classroom Mode)")

    mode = st.selectbox("เลือกหัวข้อ", ["PAM", "QAM", "OFDM"])

    # =========================
    # PAM
    # =========================
    if mode == "PAM":
        st.header("🔴 PAM (Pulse Amplitude Modulation)")

        st.markdown("👉 แนวคิด: เปลี่ยน 'ระดับความสูงของสัญญาณ' ตามข้อมูล")

        M = st.selectbox("M-PAM", [2, 4, 8])
        bits = st.text_input("Input bits", "0101")

        k = int(np.log2(M))

        if len(bits) % k != 0:
            st.warning(f"ต้องใส่บิตหาร {k} ลงตัว")
            return

        # Mapping
        symbols = [int(bits[i:i+k], 2) for i in range(0, len(bits), k)]
        levels = np.linspace(-M+1, M-1, M)
        signal = [levels[s] for s in symbols]

        st.markdown(f"🔢 Symbols: {symbols}")
        st.markdown(f"📊 Levels: {levels}")

        t = np.arange(len(signal))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t,
            y=signal,
            mode='lines+markers'
        ))

        fig.update_layout(title="PAM Signal (Amplitude changes)")
        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 Insight: PAM ใช้ amplitude อย่างเดียว → noise กระทบง่าย")

    # =========================
    # QAM
    # =========================
    elif mode == "QAM":
        st.header("🔵 QAM (Quadrature Amplitude Modulation)")

        st.markdown("👉 แนวคิด: ใช้ I + Q (2 มิติ) → ส่งข้อมูลได้มากขึ้น")

        M = st.selectbox("QAM Order", [4, 16])
        bits = st.text_input("Input bits", "010011")

        k = int(np.log2(M))

        if len(bits) % k != 0:
            st.warning(f"ต้องใส่บิตหาร {k} ลงตัว")
            return

        symbols = [int(bits[i:i+k], 2) for i in range(0, len(bits), k)]

        sqrtM = int(np.sqrt(M))
        I = [(s % sqrtM) for s in symbols]
        Q = [(s // sqrtM) for s in symbols]

        st.markdown(f"🔢 Symbols: {symbols}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=I,
            y=Q,
            mode='markers',
            marker=dict(size=12)
        ))

        fig.update_layout(
            title="QAM Constellation",
            xaxis_title="In-phase (I)",
            yaxis_title="Quadrature (Q)"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 Insight: QAM ส่งข้อมูลมากขึ้น แต่ต้องใช้ SNR สูง")

    # =========================
    # OFDM
    # =========================
    elif mode == "OFDM":
        st.header("🟣 OFDM (Orthogonal Frequency Division Multiplexing)")

        st.markdown("👉 แนวคิด: ใช้หลาย subcarrier ส่งข้อมูลพร้อมกัน")

        N = st.slider("จำนวน Subcarriers", 4, 64, 16)
        noise_level = st.slider("Noise Level", 0.0, 1.0, 0.1)

        symbols = (np.random.randn(N) + 1j*np.random.randn(N))

        # IFFT
        ofdm = np.fft.ifft(symbols)

        # Add noise
        noise = noise_level * np.random.randn(len(ofdm))
        ofdm_noisy = np.real(ofdm) + noise

        t = np.arange(len(ofdm))

        # Time domain
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t, y=np.real(ofdm), name="Original"))
        fig1.add_trace(go.Scatter(x=t, y=ofdm_noisy, name="With Noise"))

        fig1.update_layout(title="OFDM Signal (Time Domain)")
        st.plotly_chart(fig1, use_container_width=True)

        # Frequency domain
        fft = np.fft.fft(ofdm)
        freq = np.fft.fftfreq(len(fft))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=freq, y=np.abs(fft)))

        fig2.update_layout(title="OFDM Spectrum (Subcarriers)")
        st.plotly_chart(fig2, use_container_width=True)

        st.info("💡 Insight: OFDM ใช้ subcarrier จำนวนมาก → ทน multipath ดีมาก")

    st.markdown("---")
    st.success("🎓 ใช้สอนหน้าห้องได้เลย: PAM → QAM → OFDM = Evolution ของการสื่อสาร")
