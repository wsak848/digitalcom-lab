import numpy as np
import plotly.graph_objects as go

# 🔥 เพิ่มฟังก์ชันนี้
def calculate_rssi(x_ap, y_ap, x, y):
    d = np.sqrt((x - x_ap)**2 + (y - y_ap)**2)

    # ป้องกันหาร 0
    d = np.maximum(d, 1)

    # Path loss model แบบง่าย
    rssi = -30 - 20 * np.log10(d)

    return rssi
    
def best_rssi(ap1, ap2, dev):
    r1 = calculate_rssi(ap1[0], ap1[1], dev[0], dev[1])
    r2 = calculate_rssi(ap2[0], ap2[1], dev[0], dev[1])
    return max(r1, r2)

def generate_plotly_map(ap1, ap2, dev):

    size = 100
    x = np.linspace(0, size, 80)
    y = np.linspace(0, size, 80)
    X, Y = np.meshgrid(x, y)

    v_calc = np.vectorize(calculate_rssi)

    Z = np.maximum(
        v_calc(ap1[0], ap1[1], X, Y),
        v_calc(ap2[0], ap2[1], X, Y)
    )

    fig = go.Figure()

    # 🔥 FIX 1: Heatmap ต้องไม่บัง click
    fig.add_trace(go.Heatmap(
        x=x,
        y=y,
        z=Z,
        colorscale="RdYlGn",
        zmin=-100,
        zmax=-30,
        colorbar=dict(title="dBm"),
        opacity=0.6,
        hoverinfo='skip'   # ⭐ สำคัญมาก
    ))

    # AP1
    fig.add_trace(go.Scatter(
        x=[ap1[0]],
        y=[ap1[1]],
        mode="markers+text",
        marker=dict(size=15, color="black"),
        text=["AP1"],
        textposition="top center",
        name="AP1"
    ))

    # AP2
    fig.add_trace(go.Scatter(
        x=[ap2[0]],
        y=[ap2[1]],
        mode="markers+text",
        marker=dict(size=15, color="blue"),
        text=["AP2"],
        textposition="top center",
        name="AP2"
    ))

    # Device
    fig.add_trace(go.Scatter(
        x=[dev[0]],
        y=[dev[1]],
        mode="markers+text",
        marker=dict(size=12, color="red"),
        text=["Device"],
        textposition="bottom center",
        name="Device"
    ))

    # 🔥 FIX 2: enable click event
    fig.update_layout(
        title="Interactive WiFi Coverage Map",
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100]),
        dragmode="pan",
        clickmode='event+select'   # ⭐ สำคัญ
    )

    return fig
