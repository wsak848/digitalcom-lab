import streamlit as st

# =========================
# Page Config (ต้องอยู่บนสุด)
# =========================
st.set_page_config(
    page_title="Digital Communication Lab",
    layout="centered"
)

# =========================
# Header
# =========================
st.title("📡 Digital Communication Simulation")
st.subheader("By Sakda Wongadyarin : สถาบันการอาชีวศึกษาภาคใต้3")

st.markdown("---")
st.header("เลือกการทดลอง")

# =========================
# Session State
# =========================
if "menu" not in st.session_state:
    st.session_state.menu = None

# =========================
# Menu Buttons
# =========================
if st.button("1. PCM & Bitrate test"):
    st.session_state.menu = "pcm"

if st.button("2. Sampling & Aliasing"):
    st.session_state.menu = "sampling"

if st.button("3. Quantization test"):
    st.session_state.menu = "quant"

if st.button("4. Line Coding"):
    st.session_state.menu = "line"

if st.button("5. SNR"):
    st.session_state.menu = "snr"

if st.button("6. PAM QAM OFDM"):
    st.session_state.menu = "pam"

# 🔥 เพิ่มใหม่
if st.button("7. TDM Multiplexing"):
    st.session_state.menu = "tdm"

if st.button("8. FDM Multiplexing"):
    st.session_state.menu = "fdm"

if st.button("9. OFDM"):
    st.session_state.menu = "ofdm"

if st.button("10. WiFi OFDM Simulation"):
    st.session_state.menu = "ofdm_wifi"
# =========================
# Routing
# =========================

# ===== OLD MODULES =====
if st.session_state.menu == "pcm":
    import pcm_bitrate_demo as mod2
    fig = mod2.run()
    st.pyplot(fig)

if st.button("11. Dual WiFi RSSI"):
    st.session_state.menu = "rssi"

elif st.session_state.menu == "sampling":
    import sampling_streamlit as mod
    mod.run()

elif st.session_state.menu == "quant":
    import quantizedsim1 as mod3
    fig = mod3.run()
    st.pyplot(fig)

elif st.session_state.menu == "line":
    import linecoding_test as mod3
    fig = mod3.run()
    st.pyplot(fig)

elif st.session_state.menu == "snr":
    import nsr_test as mod4
    fig = mod4.run()
    st.pyplot(fig)

elif st.session_state.menu == "pam":
    import pam_qam_ofdm as mod4
    fig = mod4.run()
    st.pyplot(fig)

# ===== NEW MODULE =====
elif st.session_state.menu == "tdm":
    from pages import tdm_page as mod5
    mod5.run()

elif st.session_state.menu == "fdm":
    from pages import fdm_page
    fdm_page.run()

elif st.session_state.menu == "ofdm":
    from pages import ofdm_page
    ofdm_page.run()
    
elif st.session_state.menu == "ofdm_wifi":
    from pages import ofdm_wifi_page
    ofdm_wifi_page.run()

elif st.session_state.menu == "rssi":
    from pages import rssi_dualwifi_page
    rssi_dualwifi_page.run()
