"""Bidirectional canvas map: send completed drags back to Streamlit."""
from pathlib import Path
import math
import numpy as np
import streamlit.components.v1 as components
from core.rssi_dualwifi import calculate_rssi

_map = components.declare_component(
    'rssi_drag_map', path=str(Path(__file__).with_name('rssi_map_frontend')))


def coordinate_updates(payload):
    """Validate the entire browser message before changing widget state."""
    updates = {}
    try:
        points, walls = payload['points'], payload['walls']
        if len(points) != 3 or len(walls) != 2:
            return {}
        groups = [(f'rssi_{name}_', point, ['X', 'Y'])
                  for name, point in zip(['AP1', 'AP2', 'Device'], points)]
        groups += [(f'rssi_w{i}_', wall, ['0', '1', '2', '3'])
                   for i, wall in enumerate(walls)]
        for prefix, values, suffixes in groups:
            if len(values) != len(suffixes):
                return {}
            for suffix, value in zip(suffixes, values):
                value = float(value)
                if not math.isfinite(value):
                    return {}
                updates[prefix + suffix] = round(max(0., min(100., value)), 2)
    except (KeyError, TypeError, ValueError, OverflowError):
        return {}
    return updates


def drag_map(points, walls, show_heatmap):
    grid = None
    if show_heatmap:
        axis = np.linspace(0, 100, 101)
        x, y = np.meshgrid(axis, axis)
        grid = np.maximum(calculate_rssi(*points[0], x, y, walls),
                          calculate_rssi(*points[1], x, y, walls)).tolist()
    best = int(calculate_rssi(*points[1], *points[2], walls) >
               calculate_rssi(*points[0], *points[2], walls))
    return _map(points=points, walls=walls, grid=grid, best=best,
                key='rssi_drag_canvas', default=None)
