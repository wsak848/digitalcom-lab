# WiFi RSSI lab (interactive map v2)

Run from the repository directory:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run rssi_streamlit.py
```

With the existing Windows environment:

```powershell
.\venv2\Scripts\python.exe -m streamlit run rssi_streamlit.py
```

Open the local URL printed in the terminal. The page shows
`Interactive map v2`. Drag AP1, AP2 or Device to move them. Drag a wall's
center to translate it, or its square endpoints to resize/rotate it.
Release the mouse to update RSSI and the heatmap. Expand the coordinate
panels to enter exact positions or change wall loss. Enable SHOW HEATMAP
to display coverage.

The complete lab menu remains available with `streamlit run app.py`,
under **11. Dual WiFi RSSI**, using the same interactive map.

For Streamlit Community Cloud, use repository `wsak848/digitalcom-lab`,
branch `main`, and entry point `app.py` (all labs) or `rssi_streamlit.py`
(RSSI only). A GitHub push does not itself verify that the hosted app
has loaded the new revision. Check for `Interactive map v2` in the page.

`RSSImap_dual.py` is the desktop Tkinter version; it is not the Streamlit
entry point. The web map needs no external JavaScript CDN or new package.
