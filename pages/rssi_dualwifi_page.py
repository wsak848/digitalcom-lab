import streamlit as st
from core import rssi_dualwifi
from streamlit_plotly_events import plotly_events

def run():
    st.title("📡 WiFi Planner (Click to Move AP)")

    # =========================
    # SESSION STATE
    # =========================
    if "ap1" not in st.session_state:
        st.session_state.ap1 = [20, 80]
        st.session_state.ap2 = [80, 20]
        st.session_state.dev = [50, 50]

    # =========================
    # MODE
    # =========================
    mode = st.radio(
        "เลือกสิ่งที่จะย้าย",
        ["AP1", "AP2", "Device"]
    )

    st.info("👉 คลิกบนแผนที่เพื่อย้ายตำแหน่ง")

    # =========================
    # DRAW MAP
    # =========================
    fig = rssi_dualwifi.generate_plotly_map(
        st.session_state.ap1,
        st.session_state.ap2,
        st.session_state.dev
    )

    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False
    )

    # =========================
    # HANDLE CLICK
    # =========================
    if selected_points:
        x = int(selected_points[0]["x"])
        y = int(selected_points[0]["y"])

        if mode == "AP1":
            st.session_state.ap1 = [x, y]

        elif mode == "AP2":
            st.session_state.ap2 = [x, y]

        elif mode == "Device":
            st.session_state.dev = [x, y]

        st.rerun()

    # =========================
    # SHOW VALUE
    # =========================
    rssi = rssi_dualwifi.best_rssi(
        st.session_state.ap1,
        st.session_state.ap2,
        st.session_state.dev
    )

    st.metric("📶 Best RSSI", f"{rssi:.2f} dBm")

    # =========================
    # DEBUG (optional)
    # =========================
    with st.expander("📍 Current Position"):
        st.write("AP1:", st.session_state.ap1)
        st.write("AP2:", st.session_state.ap2)
        st.write("Device:", st.session_state.dev)
