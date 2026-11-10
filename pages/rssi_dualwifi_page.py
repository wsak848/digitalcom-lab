import streamlit as st
from core import rssi_dualwifi


def run():
    st.title('Dual WiFi RSSI - Walls & Heatmap')
    st.caption('100 x 100 meters. Change coordinates to move radios and resize or rotate walls.')
    objects = []
    with st.expander('AP and Device positions', expanded=True):
        for name, default in [('AP1', (20., 80.)), ('AP2', (80., 20.)), ('Device', (50., 50.))]:
            cols = st.columns(2)
            objects.append([cols[j].number_input(f'{name} {axis} (m)', 0., 100., default[j],
                            step=1., key=f'rssi_{name}_{axis}') for j, axis in enumerate(['X', 'Y'])])
    walls = []
    for i, default in enumerate([(35., 20., 35., 75.), (50., 65., 90., 65.)]):
        with st.expander(f'Wall {i+1}: position, length and loss', expanded=True):
            enabled = st.checkbox('Enabled', value=True, key=f'rssi_w{i}_enabled')
            cols = st.columns(4)
            coords = [cols[j].number_input(label, 0., 100., default[j], step=1., key=f'rssi_w{i}_{j}')
                      for j, label in enumerate(['Start X', 'Start Y', 'End X', 'End Y'])]
            loss = st.number_input('Penetration loss (dB)', 0., 100., 8., step=.5, key=f'rssi_w{i}_loss')
            if coords[:2] == coords[2:]:
                st.warning('Zero-length wall does not block the signal.')
            walls.append(dict(start=coords[:2], end=coords[2:], loss=loss, enabled=enabled))
    show = st.checkbox('SHOW HEATMAP', value=True, key='rssi_heatmap')
    ap1, ap2, dev = objects
    r1 = float(rssi_dualwifi.calculate_rssi(*ap1, *dev, walls))
    r2 = float(rssi_dualwifi.calculate_rssi(*ap2, *dev, walls))
    cols = st.columns(3)
    for col, name, value in zip(cols, ['AP1', 'AP2', 'Best RSSI'], [r1, r2, max(r1, r2)]):
        col.metric(name, f'{value:.1f} dBm')
    st.write('Connected: ' + ('AP1' if r1 >= r2 else 'AP2'))
    st.plotly_chart(rssi_dualwifi.generate_plotly_map(ap1, ap2, dev, walls, show), width='stretch', key='rssi_map')
    st.caption('Map color range: -100 to -30 dBm. Values below -100 retain their actual calculated RSSI.')
    st.code('RSSI = -30 - 25*log10(max(distance_m, 1)) - sum(crossed_wall_loss_dB)')
    st.info('2D full-height walls; no reflection or diffraction. 8 dB is an example: calibrate for material, thickness and frequency.')


if __name__ == '__main__':
    run()
