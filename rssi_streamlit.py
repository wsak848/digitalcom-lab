"""Standalone Streamlit entry point for the interactive dual-AP RSSI lab.

Run: python -m streamlit run rssi_streamlit.py
"""
import streamlit as st
from pages.rssi_dualwifi_page import run

st.set_page_config(page_title='WiFi RSSI Lab', layout='wide')
run()
