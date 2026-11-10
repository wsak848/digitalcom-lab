import streamlit as st
from core import rssi_dualwifi
from core.rssi_map_component import drag_map, coordinate_updates


def coordinate_input(column, label, default, key):
    if key not in st.session_state:
        st.session_state[key] = default
    return column.number_input(label, 0., 100., value=None, step=1., key=key)


def run():
    # Apply drag results before creating the coordinate widgets.
    pending = st.session_state.pop('rssi_pending_coordinates', {})
    for key, value in pending.items():
        st.session_state[key] = value
    st.title('Dual WiFi RSSI - Walls & Heatmap')
    st.caption('Drag AP / Device on the map. Drag wall centers to move, square ends to resize / rotate. Coordinates below also work.')
    objects = []
    with st.expander('AP and Device positions', expanded=True):
        for name, default in [('AP1', (20., 80.)), ('AP2', (80., 20.)), ('Device', (50., 50.))]:
            cols = st.columns(2)
            objects.append([coordinate_input(cols[j], f'{name} {axis} (m)', default[j],
                            key=f'rssi_{name}_{axis}') for j, axis in enumerate(['X', 'Y'])])
    walls = []
    for i, default in enumerate([(35., 20., 35., 75.), (50., 65., 90., 65.)]):
        with st.expander(f'Wall {i+1}: position, length and loss', expanded=True):
            enabled = st.checkbox('Enabled', value=True, key=f'rssi_w{i}_enabled')
            cols = st.columns(4)
            coords = [coordinate_input(cols[j], label, default[j], key=f'rssi_w{i}_{j}')
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
    event = drag_map(objects, walls, show)
    if isinstance(event, dict) and event.get('id') != st.session_state.get('rssi_last_drag'):
        st.session_state.rssi_last_drag = event.get('id')
        updates = coordinate_updates(event)
        if updates:
            st.session_state.rssi_pending_coordinates = updates
            st.rerun()
    st.caption('RSSI and heatmap update after you release the mouse.')
    st.caption('Map color range: -100 to -30 dBm. Values below -100 retain their actual calculated RSSI.')
    st.code('RSSI = -30 - 25*log10(max(distance_m, 1)) - sum(crossed_wall_loss_dB)')
    st.info('2D full-height walls; no reflection or diffraction. 8 dB is an example: calibrate for material, thickness and frequency.')


if __name__ == '__main__':
    run()
