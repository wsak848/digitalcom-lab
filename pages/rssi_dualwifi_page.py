import streamlit as st
from core import rssi_dualwifi
from streamlit_plotly_events import plotly_events

def run():
    st.title("📡 WiFi Planner (Drag AP freely)")

    # =========================
    # SESSION
    # =========================
    if "ap1" not in st.session_state:
        st.session_state.ap1 = [20, 80]
        st.session_state.ap2 = [80, 20]
        st.session_state.dev = [50, 50]
        st.session_state.drag_target = "AP1"

    # =========================
    # SELECT TARGET
    # =========================
    target = st.radio(
        "เลือกสิ่งที่จะลาก",
        ["AP1", "AP2", "Device"],
        key="drag_target"
    )

    st.info("🖱️ คลิกค้าง + ขยับเมาส์ = ลาก (Drag Simulation)")

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
    # GET EVENTS
    # =========================
    events = plotly_events(
        fig,
        click_event=True,
        hover_event=True,   # 🔥 ใช้ hover เป็น drag
        select_event=False
    )

    # =========================
    # DRAG LOGIC
    # =========================
    if events:
        x = max(0, min(100, int(events[-1]["x"])))
        y = max(0, min(100, int(events[-1]["y"])))

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

    # =========================
    # DEBUG
    # =========================
    with st.expander("📍 Current Position"):
        st.write("AP1:", st.session_state.ap1)
        st.write("AP2:", st.session_state.ap2)
        st.write("Device:", st.session_state.dev)
