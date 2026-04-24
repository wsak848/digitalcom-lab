import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

from core import tdm

def run():
    st.title("🎬 TDM Animation Lab")

    # =========================
    # Controls
    # =========================
    num = st.slider("จำนวนสัญญาณ", 2, 4, 2)
    fs = st.slider("Sampling Rate", 20, 200, 50)
    duration = st.slider("Duration", 1, 3, 1)

    speed = st.slider("Animation Speed", 1, 10, 5)

    t = np.linspace(0, duration, fs * duration)

    # frequencies
    freqs = []
    for i in range(num):
        f = st.slider(f"Frequency Signal {i+1}", 1, 10, i+2)
        freqs.append(f)

    # =========================
    # Generate
    # =========================
    signals = tdm.generate_signals(freqs, t)
    mux = tdm.tdm_mux(signals)
    slots = tdm.get_slot_indices(num, len(t))

    colors = ["red", "blue", "green", "orange"]

    # =========================
    # Plot Original
    # =========================
    st.subheader("📊 Original Signals")

    fig1 = go.Figure()
    for i in range(num):
        fig1.add_trace(go.Scatter(
            x=t,
            y=signals[i],
            name=f"S{i+1}"
        ))
    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # Animation
    # =========================
    st.subheader("🎬 TDM Slot Animation")

    play = st.button("▶️ Start Animation")

    chart = st.empty()

    if play:
        x_data = []
        y_data = []
        color_data = []

        for i in range(len(mux)):
            x_data.append(i)
            y_data.append(mux[i])
            color_data.append(colors[slots[i]])

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                marker=dict(color=color_data, size=8),
                line=dict(color="black"),
                name="TDM"
            ))

            fig.update_layout(
                title="TDM Signal (Animated)",
                xaxis_title="Time Slot",
                yaxis_title="Amplitude"
            )

            chart.plotly_chart(fig, use_container_width=True)

            time.sleep(0.1 / speed)

    # =========================
    # Demux
    # =========================
    demux = tdm.tdm_demux(mux, num)

    st.subheader("📥 Demultiplexed Signals")

    fig3 = go.Figure()
    for i in range(num):
        fig3.add_trace(go.Scatter(
            y=demux[i],
            name=f"Recovered {i+1}"
        ))

    st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # Insight
    # =========================
    st.markdown("## 🎯 Insight")

    st.markdown("""
    🔴 สีแดง = Signal 1  
    🔵 สีน้ำเงิน = Signal 2  
    🟢 สีเขียว = Signal 3  

    TDM = สลับ sample ทีละช่อง  
    ยิ่งช่องเยอะ → สลับเร็วขึ้น  
    """)