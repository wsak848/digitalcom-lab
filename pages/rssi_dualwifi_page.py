import streamlit as st
from core import rssi_dualwifi
from streamlit_plotly_events import plotly_events

def run():
    st.title("📡 WiFi Planner (Click to Move AP)")

    # =========================
    # STATE
    # =========================
    if "ap1" not in st.session_state:
        st.session_state.ap1 = [20, 80]
        st.session_state.ap2 = [80, 20]
        st.session_state.dev = [50, 50]

    # =========================
    # SELECT OBJECT
    # =========================
    target = st.radio(
        "เลือกสิ่งที่จะย้าย",
        ["AP1", "AP2", "Device"]
    )

    st.info("👉 คลิกตำแหน่งใหม่บนแผนที่เพื่อย้าย")

    # =========================
    # DRAW MAP
    # =========================
    fig = rssi_dualwifi.generate_plotly_map(
        st.session_state.ap1,
        st.session_state.ap2,
        st.session_state.dev
    )

    fig.update_layout(
        clickmode='event+select',
        dragmode='pan'
    )

    # =========================
    # CLICK EVENT
    # =========================
    events = plotly_events(
        fig,
        click_event=True,
        hover_event=False
    )

    # =========================
    # MOVE OBJECT
    # =========================
    if events:
        x = int(events[0]["x"])
        y = int(events[0]["y"])

        if target == "AP1":
            st.session_state.ap1 = [x, y]

        elif target == "AP2":
            st.session_state.ap2 = [x, y]

        elif target == "Device":
            st.session_state.dev = [x, y]

        st.rerun()

    # =========================
    # RSSI
    # =========================
    rssi = rssi_dualwifi.best_rssi(
        st.session_state.ap1,
        st.session_state.ap2,
        st.session_state.dev
    )

    st.metric("📶 Best RSSI", f"{rssi:.2f} dBm")

    with st.expander("📍 Current Position"):
        st.write("AP1:", st.session_state.ap1)
        st.write("AP2:", st.session_state.ap2)
        st.write("Device:", st.session_state.dev)
