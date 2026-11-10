import numpy as np
import plotly.graph_objects as go


def calculate_rssi(x_ap, y_ap, x, y, walls=None):
    """n=2.5 log-distance plus calibrated full-height thin-wall losses.

    No reflection/diffraction. Calibrate n without explicit walls to avoid
    counting wall loss twice. Collinear travel and on-wall radios excluded.
    """
    rx, ry = np.asarray(x)-x_ap, np.asarray(y)-y_ap
    result = -30 - 25*np.log10(np.maximum(np.hypot(rx, ry), 1))
    for w in walls or []:
        if not w.get('enabled', True):
            continue
        qx, qy = w['start']
        sx, sy = np.subtract(w['end'], w['start'])
        denom = rx*sy-ry*sx
        valid = np.abs(denom) > 1e-9
        t = np.divide((qx-x_ap)*sy-(qy-y_ap)*sx, denom,
                      out=np.zeros_like(denom, dtype=float), where=valid)
        u = np.divide((qx-x_ap)*ry-(qy-y_ap)*rx, denom,
                      out=np.zeros_like(denom, dtype=float), where=valid)
        crossed = valid & (t > 1e-9) & (t < 1-1e-9) & (u >= -1e-9) & (u <= 1+1e-9)
        result = result - crossed*w['loss']
    return result


def best_rssi(ap1, ap2, dev, walls=None):
    return max(calculate_rssi(*ap1, *dev, walls), calculate_rssi(*ap2, *dev, walls))


def generate_plotly_map(ap1, ap2, dev, walls=None, show_heatmap=True):
    fig = go.Figure()
    if show_heatmap:
        x = np.linspace(0, 100, 101)
        X, Y = np.meshgrid(x, x)
        z = np.maximum(calculate_rssi(*ap1, X, Y, walls), calculate_rssi(*ap2, X, Y, walls))
        fig.add_trace(go.Heatmap(x=x, y=x, z=z, zmin=-100, zmax=-30,
                      colorscale='RdYlGn', colorbar=dict(title='dBm'), opacity=.75))
    for i, w in enumerate(walls or []):
        a, b = w['start'], w['end']
        fig.add_trace(go.Scatter(x=[a[0], b[0]], y=[a[1], b[1]], mode='lines+markers',
                      line=dict(color=['saddlebrown', 'purple'][i % 2], width=7),
                      marker=dict(symbol='square', size=10),
                      opacity=1 if w.get('enabled', True) else .25,
                      name=f"Wall {i+1}: {w['loss']:g} dB"))
    r1 = calculate_rssi(*ap1, *dev, walls)
    r2 = calculate_rssi(*ap2, *dev, walls)
    target = ap1 if r1 >= r2 else ap2
    fig.add_trace(go.Scatter(x=[target[0], dev[0]], y=[target[1], dev[1]],
                  mode='lines', line=dict(color='gray', dash='dash'), name='Connected AP'))
    for name, point, color in [('AP1', ap1, 'black'), ('AP2', ap2, 'blue'), ('Device', dev, 'red')]:
        fig.add_trace(go.Scatter(x=[point[0]], y=[point[1]], mode='markers+text',
                      marker=dict(size=15, color=color), text=[name], textposition='top center', name=name))
    fig.update_layout(title='WiFi coverage with wall loss', height=750,
                      xaxis=dict(range=[0, 100], title='X (m)'),
                      yaxis=dict(range=[0, 100], title='Y (m)', scaleanchor='x', scaleratio=1),
                      margin=dict(l=30, r=30, t=60, b=30), dragmode='pan')
    return fig
