import streamlit as st
import numpy as np
import plotly.graph_objects as go

def run():
    st.title("📡 Digital Modulation Lab (Interactive)")

    tab1, tab2, tab3 = st.tabs(["PAM", "QAM", "OFDM"])

    # =========================
    # PAM
    # =========================
    with tab1:
        st.subheader("🔴 PAM")

        M = st.selectbox("M-PAM", [2, 4, 8], key="pam_M")
        bits = st.text_input("Input bits", "0101", key="pam_bits")
        noise = st.slider("Noise", 0.0, 1.0, 0.0, key="pam_noise")

        k = int(np.log2(M))

        if len(bits) % k != 0:
            st.warning(f"ต้องหาร {k} ลงตัว")
        else:
            symbols = [int(bits[i:i+k], 2) for i in range(0, len(bits), k)]
            levels = np.linspace(-M+1, M-1, M)
            signal = np.array([levels[s] for s in symbols])

            noisy = signal + noise*np.random.randn(len(signal))

            t = np.arange(len(signal))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=signal, name="Original"))
            fig.add_trace(go.Scatter(x=t, y=noisy, name="Noisy"))

            fig.update_layout(title="PAM Signal")
            st.plotly_chart(fig, use_container_width=True)

            st.info("💡 เพิ่ม Noise → amplitude เพี้ยน")

    # =========================
    # QAM
    # =========================
    with tab2:
        st.subheader("🔵 QAM")

        M = st.selectbox("QAM Order", [4, 16], key="qam_M")
        bits = st.text_input("Input bits", "010011", key="qam_bits")
        noise = st.slider("Noise", 0.0, 1.0, 0.0, key="qam_noise")

        k = int(np.log2(M))

        if len(bits) % k != 0:
            st.warning(f"ต้องหาร {k} ลงตัว")
        else:
            symbols = [int(bits[i:i+k], 2) for i in range(0, len(bits), k)]

            sqrtM = int(np.sqrt(M))
            I = np.array([(s % sqrtM) for s in symbols])
            Q = np.array([(s // sqrtM) for s in symbols])

            # normalize
            I = 2*I - (sqrtM-1)
            Q = 2*Q - (sqrtM-1)

            I_noisy = I + noise*np.random.randn(len(I))
            Q_noisy = Q + noise*np.random.randn(len(Q))

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=I,
                y=Q,
                mode='markers',
                name="Ideal"
            ))

            fig.add_trace(go.Scatter(
                x=I_noisy,
                y=Q_noisy,
                mode='markers',
                name="Noisy"
            ))

            fig.update_layout(
                title="QAM Constellation",
                xaxis_title="I",
                yaxis_title="Q"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.info("💡 Noise มาก → จุดกระจาย → error เพิ่ม")

    # =========================
    # OFDM
    # =========================
    with tab3:
        st.subheader("🟣 OFDM")

        N = st.slider("Subcarriers", 4, 64, 16)
        noise = st.slider("Noise", 0.0, 1.0, 0.1)

        # random QAM-like symbols
        symbols = (np.random.randn(N) + 1j*np.random.randn(N))

        ofdm = np.fft.ifft(symbols)

        noisy = np.real(ofdm) + noise*np.random.randn(len(ofdm))

        t = np.arange(len(ofdm))

        # Time domain
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t, y=np.real(ofdm), name="Original"))
        fig1.add_trace(go.Scatter(x=t, y=noisy, name="Noisy"))

        fig1.update_layout(title="OFDM Signal (Time)")
        st.plotly_chart(fig1, use_container_width=True)

        # Frequency domain
        fft = np.fft.fft(ofdm)
        freq = np.fft.fftfreq(len(fft))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=freq, y=np.abs(fft)))

        fig2.update_layout(title="OFDM Spectrum")
        st.plotly_chart(fig2, use_container_width=True)

        st.info("💡 เพิ่ม subcarrier → bandwidth ถูกแบ่งเป็นหลายช่องเล็ก")

    st.markdown("---")
    st.success("🎓 ใช้ทดลอง: ปรับ Noise / M / Subcarrier แล้วดูผลทันที")
