import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("📡 PAM / QAM / OFDM Lab")

    mode = st.selectbox("เลือกการทดลอง", ["PAM", "QAM", "OFDM"])

    # =========================
    # PAM
    # =========================
    if mode == "PAM":
        st.subheader("🔴 PAM")

        M = st.selectbox("M-PAM", [2, 4, 8])
        bits = st.text_input("Input bits", "0101")

        k = int(np.log2(M))

        if len(bits) % k != 0:
            st.warning(f"ต้องใส่บิตหาร {k} ลงตัว")
            return

        symbols = [int(bits[i:i+k], 2) for i in range(0, len(bits), k)]
        levels = np.linspace(-M+1, M-1, M)
        signal = [levels[s] for s in symbols]

        t = np.arange(len(signal))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=signal, mode='lines+markers'))

        fig.update_layout(title="PAM Signal")
        st.plotly_chart(fig)

    # =========================
    # QAM
    # =========================
    elif mode == "QAM":
        st.subheader("🔵 QAM")

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

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=I,
            y=Q,
            mode='markers',
            marker=dict(size=10)
        ))

        fig.update_layout(
            title="QAM Constellation",
            xaxis_title="I",
            yaxis_title="Q"
        )

        st.plotly_chart(fig)

    # =========================
    # OFDM
    # =========================
    elif mode == "OFDM":
        st.subheader("🟣 OFDM")

        N = st.slider("จำนวน Subcarriers", 4, 64, 16)

        symbols = (np.random.randn(N) + 1j*np.random.randn(N))
        ofdm = np.fft.ifft(symbols)

        t = np.arange(len(ofdm))

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t, y=np.real(ofdm)))

        fig1.update_layout(title="OFDM Time Signal")
        st.plotly_chart(fig1)

        fft = np.fft.fft(ofdm)
        freq = np.fft.fftfreq(len(fft))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=freq, y=np.abs(fft)))

        fig2.update_layout(title="OFDM Spectrum")
        st.plotly_chart(fig2)

    st.markdown("---")
    st.markdown("💡 PAM = เปลี่ยน amplitude")
    st.markdown("💡 QAM = amplitude + phase")
    st.markdown("💡 OFDM = multi-carrier")
