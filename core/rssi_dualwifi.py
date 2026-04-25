import plotly.graph_objects as go

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

    # Heatmap
    fig.add_trace(go.Heatmap(
        x=x,
        y=y,
        z=Z,
        colorscale="RdYlGn",
        zmin=-100,
        zmax=-30,
        colorbar=dict(title="dBm"),
        opacity=0.7
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

    fig.update_layout(
        title="Interactive WiFi Coverage Map",
        xaxis=dict(range=[0,100]),
        yaxis=dict(range=[0,100]),
        dragmode="pan"
    )

    return fig
