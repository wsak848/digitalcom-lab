import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

# --- 1. Settings & Initial State ---
ap1_x, ap1_y = 20.0, 80.0
ap2_x, ap2_y = 80.0, 20.0
dev_x, dev_y = 50.0, 50.0
measured_points = []
manual_rssi = -30.0
room_size = 100

# Site-specific multi-wall model. Loss values are experimental parameters,
# not universal material constants. n describes the background environment;
# calibrate it without these explicit walls to avoid counting wall loss twice.
walls = [
    dict(start=np.array([35., 20.]), end=np.array([35., 75.]), loss=8., enabled=True),
    dict(start=np.array([50., 65.]), end=np.array([90., 65.]), loss=8., enabled=True),
]
wall_colors = ['#8B4513', '#6A3D9A']


def crosses_wall(ax, ay, dx, dy, wall):
    """Thin-wall crossing: endpoint touch counts; collinear travel does not.

    AP/device exactly on the wall is excluded (no well-defined penetration).
    Walls represent full-height partitions in this 2D floor plan.
    """
    p = np.array([ax, ay], dtype=float)
    r = np.array([dx, dy], dtype=float) - p
    q = wall['start']
    s = wall['end'] - q
    cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
    denom = cross(r, s)
    if abs(denom) < 1e-9:
        return False
    t = cross(q - p, s) / denom
    u = cross(q - p, r) / denom
    return 1e-9 < t < 1 - 1e-9 and -1e-9 <= u <= 1 + 1e-9


def wall_loss(ax, ay, dx, dy):
    return sum(w['loss'] for w in walls
               if w['enabled'] and crosses_wall(ax, ay, dx, dy, w))


def draw_walls(axes):
    for i, wall in enumerate(walls):
        a, b = wall['start'], wall['end']
        axes.plot([a[0], b[0]], [a[1], b[1]], color=wall_colors[i],
                  linewidth=5, alpha=1 if wall['enabled'] else .25,
                  marker='s', markersize=8, zorder=12,
                  label=f"Wall {i+1}: {wall['loss']:g} dB" +
                        ('' if wall['enabled'] else ' (off)'))


def apply_wall_settings():
    try:
        losses = [float(v.get()) for v in wall_loss_vars]
        if not all(np.isfinite(v) and 0 <= v <= 100 for v in losses):
            raise ValueError
    except ValueError:
        messagebox.showerror('Wall loss', 'Enter a finite loss from 0 to 100 dB.')
        return
    for i, wall in enumerate(walls):
        wall['loss'] = losses[i]
        wall['enabled'] = wall_enabled_vars[i].get()
    update_main_view()

# --- 2. Engineering Calculation Engine ---
def calculate_rssi(ax, ay, dx, dy):
    """คำนวณ RSSI โดยใช้ Path Loss Model (n=2.5 สำหรับพื้นที่วิทยาลัย)"""
    dist = np.sqrt((ax - dx)**2 + (ay - dy)**2)
    tx_power = -30 # RSSI ที่ระยะ 1 เมตร
    dist = max(float(dist), 1.0)
    # สูตร: RSSI = Pt - 10*n*log10(d)
    val = tx_power - 10 * 2.5 * np.log10(dist) - wall_loss(ax, ay, dx, dy)
    # Preserve physical loss below the plot's display range.
    return float(val)

def get_current_best_rssi():
    """ระบบเลือกสัญญาณจาก AP ที่แรงที่สุด (Best Server Selection)"""
    r1 = calculate_rssi(ap1_x, ap1_y, dev_x, dev_y)
    r2 = calculate_rssi(ap2_x, ap2_y, dev_x, dev_y)
    return int(max(r1, r2))

def get_color_smooth(val):
    """Deep Red Color Scale: เน้นสีแดงเข้มพิเศษเมื่อสัญญาณวิกฤต"""
    if val >= -45: return "#1A9641"   # เขียวเข้ม (Excellent)
    elif val >= -60: return "#A6D96A" # เขียวอ่อน (Good)
    elif val >= -75: return "#FDAE61" # ส้ม (Fair)
    elif val >= -85: return "#D73027" # แดง (Poor)
    else: return "#7B0000"            # แดงเข้ม/Deep Red (Critical)

# --- 3. Advanced Analysis Window ---
def show_combined_analysis():
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Hatyai Tech - Interference & Coverage Analysis")
    analysis_window.geometry('1000x900')
    fig, ax = plt.subplots(figsize=(9, 8), dpi=100, layout='constrained')
    
    # สร้าง Meshgrid เพื่อคำนวณ Heatmap ทั่วพื้นที่ 100x100 เมตร
    res = 2 
    x = np.arange(0, 101, res)
    y = np.arange(0, 101, res)
    X, Y = np.meshgrid(x, y)
    v_calc = np.vectorize(calculate_rssi)
    # วิเคราะห์การซ้อนทับโดยเลือกค่า Max RSSI ในแต่ละพิกัด
    Z = np.maximum(v_calc(ap1_x, ap1_y, X, Y), v_calc(ap2_x, ap2_y, X, Y))
    
    # วาดแผนภาพ Heatmap พื้นหลัง (Interference Map)
    cp = ax.contourf(X, Y, Z, levels=np.linspace(-100, -30, 20), cmap='RdYlGn', alpha=0.7, extend='min')
    draw_walls(ax)
    fig.colorbar(cp, label='Best Signal Strength (dBm)')
    
    # วาดจุด Log และแปะตัวเลข dBm กำกับทุกจุด
    for pt in measured_points:
        px, py, prssi = pt
        ax.scatter(px, py, c='black', s=40, zorder=10)
        ax.text(px, py+2.5, f"{int(prssi)}dBm", fontsize=8, ha='center', weight='bold', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

    ax.scatter(ap1_x, ap1_y, c='black', marker='^', s=300, label='AP 1', edgecolors='white', linewidth=2)
    ax.scatter(ap2_x, ap2_y, c='blue', marker='^', s=300, label='AP 2', edgecolors='white', linewidth=2)
    ax.set_title("Best-server Coverage with Wall Loss (current layout)", fontweight='bold', pad=15)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.set_xlabel("Meters (X)"); ax.set_ylabel("Meters (Y)")
    ax.legend(loc='upper right')
    
    heatmap_canvas = FigureCanvasTkAgg(fig, master=analysis_window)
    heatmap_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    heatmap_canvas.draw()

    def close_analysis():
        plt.close(fig)
        analysis_window.destroy()

    analysis_window.protocol('WM_DELETE_WINDOW', close_analysis)

# --- 4. UI Rendering & Interaction ---
def update_main_view():
    ax_hm.clear()
    ax_hm.set_xlim(0, 100); ax_hm.set_ylim(0, 100)
    ax_hm.set_title(f"Live Simulation: Path Loss Model (Scale: 100x100m)")
    ax_hm.grid(True, alpha=0.15, linestyle='--')
    ax_hm.set_aspect('equal', adjustable='box')
    draw_walls(ax_hm)
    
    # วาดประวัติข้อมูลที่บันทึกไว้
    if measured_points:
        data = np.array(measured_points)
        ax_hm.scatter(data[:, 0], data[:, 1], c=data[:, 2], cmap='RdYlGn', vmin=-100, vmax=-30, s=100, alpha=0.5)

    # วาดอุปกรณ์ AP และ Device
    ax_hm.scatter(ap1_x, ap1_y, c='black', marker='^', s=400, label='Access Point 1', zorder=15)
    ax_hm.scatter(ap2_x, ap2_y, c='darkblue', marker='^', s=400, label='Access Point 2', zorder=15)
    ax_hm.scatter(dev_x, dev_y, c='#007bff', marker='o', s=300, edgecolors='white', linewidth=2, zorder=25)
    
    # ระบบเชื่อมต่ออัตโนมัติ (Auto Connection Line)
    d1 = np.sqrt((ap1_x-dev_x)**2 + (ap1_y-dev_y)**2)
    d2 = np.sqrt((ap2_x-dev_x)**2 + (ap2_y-dev_y)**2)
    
    # เลือก AP ที่ใกล้และแรงที่สุด
    r1 = calculate_rssi(ap1_x, ap1_y, dev_x, dev_y)
    r2 = calculate_rssi(ap2_x, ap2_y, dev_x, dev_y)
    if r1 >= r2:
        target, dist, label = (ap1_x, ap1_y), d1, "Connected: AP 1"
    else:
        target, dist, label = (ap2_x, ap2_y), d2, "Connected: AP 2"
        
    ax_hm.plot([target[0], dev_x], [target[1], dev_y], color='gray', linestyle='--', alpha=0.6, zorder=5)
    ax_hm.text((target[0]+dev_x)/2, (target[1]+dev_y)/2, f"{dist:.1f}m", 
               ha='center', fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    ax_hm.text(dev_x, dev_y-6, label, ha='center', fontsize=9, fontweight='bold', color='#1A5276')
    ax_hm.text(.01, .01,
               f'AP1: {r1:.1f} dBm (walls -{wall_loss(ap1_x, ap1_y, dev_x, dev_y):g} dB)\n'
               f'AP2: {r2:.1f} dBm (walls -{wall_loss(ap2_x, ap2_y, dev_x, dev_y):g} dB)',
               transform=ax_hm.transAxes, fontsize=9,
               bbox=dict(facecolor='white', alpha=.85, edgecolor='none'))
    rssi_disp.config(text=f'{int(max(r1, r2))}', fg=get_color_smooth(max(r1, r2)))
    ax_hm.legend(loc='upper right', frameon=True, shadow=True)
    canvas_hm.draw()

def log_point():
    global manual_rssi
    manual_rssi = get_current_best_rssi()
    measured_points.append([dev_x, dev_y, manual_rssi])
    log_table.insert("", "end", values=(len(measured_points), f"{dev_x:.1f}", f"{dev_y:.1f}", f"{int(manual_rssi)}"))
    log_table.yview_moveto(1)
    update_main_view()

# --- 5. Event Handlers (Drag & Drop) ---
def on_drag(event):
    global ap1_x, ap1_y, ap2_x, ap2_y, dev_x, dev_y, dragging_target
    if event.inaxes is not ax_hm or not dragging_target: return
    
    new_x, new_y = np.clip(event.xdata, 0, 100), np.clip(event.ydata, 0, 100)
    
    if isinstance(dragging_target, tuple):
        index, handle, anchor, original_start, original_end = dragging_target
        wall = walls[index]
        point = np.array([new_x, new_y])
        if handle == 'body':
            delta = point - anchor
            delta = np.clip(delta, -np.minimum(original_start, original_end),
                            room_size - np.maximum(original_start, original_end))
            wall['start'], wall['end'] = original_start + delta, original_end + delta
        else:
            other = wall['end' if handle == 'start' else 'start']
            if np.linalg.norm(point - other) >= 1.0:
                wall[handle] = point
    elif dragging_target == 'AP1': ap1_x, ap1_y = new_x, new_y
    elif dragging_target == 'AP2': ap2_x, ap2_y = new_x, new_y
    elif dragging_target == 'DEV': 
        dev_x, dev_y = new_x, new_y
        entry_x.delete(0, tk.END); entry_x.insert(0, f"{dev_x:.1f}")
        entry_y.delete(0, tk.END); entry_y.insert(0, f"{dev_y:.1f}")
    
    update_main_view()

def on_click(event):
    global dragging_target
    dragging_target = None
    if event.inaxes is not ax_hm or event.button != 1: return
    point = np.array([event.xdata, event.ydata])
    # Square endpoint handles take priority so short walls remain resizable.
    for i, wall in enumerate(walls):
        for handle in ('start', 'end'):
            if np.linalg.norm(point - wall[handle]) < 2.5:
                dragging_target = (i, handle, point, wall['start'].copy(), wall['end'].copy())
                return
    # ตรวจสอบการคลิกโดนวัตถุ (รัศมี 7 เมตร)
    if np.hypot(event.xdata-dev_x, event.ydata-dev_y) < 7: dragging_target = 'DEV'
    elif np.hypot(event.xdata-ap1_x, event.ydata-ap1_y) < 7: dragging_target = 'AP1'
    elif np.hypot(event.xdata-ap2_x, event.ydata-ap2_y) < 7: dragging_target = 'AP2'
    else:
        for i, wall in enumerate(walls):
            segment = wall['end'] - wall['start']
            t = np.clip(np.dot(point - wall['start'], segment) / np.dot(segment, segment), 0, 1)
            if np.linalg.norm(point - (wall['start'] + t * segment)) < 2.5:
                dragging_target = (i, 'body', point, wall['start'].copy(), wall['end'].copy())
                return

def on_release(event):
    global dragging_target
    dragging_target = None

# --- 6. Main Interface Layout ---
root = tk.Tk()
root.title("Advanced Wireless propagation Lab - Hatyai Technical College")
root.geometry("1400x950")

# Left Panel: Controls & Data Log
ctrl = ttk.Frame(root, padding=15); ctrl.pack(side=tk.LEFT, fill=tk.Y)
ttk.Label(ctrl, text="SIGNAL SIMULATOR (100m)", font=("Arial", 14, "bold")).pack(pady=5)

# Real-time RSSI Display
rssi_disp = tk.Label(ctrl, text="-30", font=("Arial", 64, "bold"), fg="#1A9641")
rssi_disp.pack()

# Keep actions above the expanding data log.
ttk.Button(ctrl, text="SHOW HEATMAP (100 x 100 m)",
           command=show_combined_analysis).pack(fill=tk.X, pady=5)
ttk.Button(ctrl, text="CLEAR CAPTURED POINTS",
           command=lambda: [measured_points.clear(),
                            [log_table.delete(i) for i in log_table.get_children()],
                            update_main_view()]).pack(fill=tk.X)

# Input: Coordinates
pos_f = ttk.LabelFrame(ctrl, text=" Device (Target) Position ", padding=10)
pos_f.pack(fill=tk.X, pady=10)
entry_x = ttk.Entry(pos_f, width=8); entry_y = ttk.Entry(pos_f, width=8)
ttk.Label(pos_f, text="X:").grid(row=0, column=0); entry_x.grid(row=0, column=1)
ttk.Label(pos_f, text="Y:").grid(row=0, column=2); entry_y.grid(row=0, column=3)
entry_x.insert(0, "50.0"); entry_y.insert(0, "50.0")
ttk.Button(pos_f, text="CAPTURE DATA POINT", command=log_point).grid(row=1, columnspan=4, pady=12, sticky='ew')

# Data Logging Table
wall_frame = ttk.LabelFrame(ctrl, text='Walls / penetration loss', padding=8)
wall_frame.pack(fill=tk.X, pady=5)
wall_loss_vars, wall_enabled_vars = [], []
for i, wall in enumerate(walls):
    enabled = tk.BooleanVar(value=wall['enabled'])
    loss = tk.StringVar(value=str(wall['loss']))
    wall_enabled_vars.append(enabled)
    wall_loss_vars.append(loss)
    ttk.Checkbutton(wall_frame, text=f'Wall {i+1}', variable=enabled,
                    command=apply_wall_settings).grid(row=i, column=0)
    ttk.Entry(wall_frame, textvariable=loss, width=7).grid(row=i, column=1)
    ttk.Label(wall_frame, text='dB').grid(row=i, column=2)
ttk.Button(wall_frame, text='Apply wall loss', command=apply_wall_settings).grid(row=2, columnspan=3, sticky='ew')
ttk.Label(wall_frame, text='Drag wall: move | Drag square end: resize / rotate\n'
          'RSSI = -30 - 25 log10(max(d, 1)) - sum(wall loss)\n'
          'd in meters; 8 dB is an example, calibrate for material.\n'
          '2D full-height walls; no reflection / diffraction.\n'
          'Captured points retain their original readings.',
          wraplength=310, justify=tk.LEFT).grid(row=3, columnspan=3, pady=5)
log_table = ttk.Treeview(ctrl, columns=("#","X","Y","RSSI"), show="headings", height=6)
for c in ("#","X","Y","RSSI"): 
    log_table.heading(c, text=c); log_table.column(c, width=60, anchor="center")
log_table.pack(fill=tk.BOTH, expand=True)

# Right Panel: Visualization & Monitoring
graph_frame = ttk.Frame(root); graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Graph 1: Live Monitor
mon_fig, ax_mon = plt.subplots(figsize=(5, 1.35), dpi=100)
mon_fig.subplots_adjust(left=.08, right=.98, bottom=.25, top=.78)
line, = ax_mon.plot([], [], lw=2.5, color='#8E44AD')
ax_mon.set_ylim(-105, -25); ax_mon.set_title("Live RSSI Monitor Stream (dBm)")
canvas_mon = FigureCanvasTkAgg(mon_fig, master=graph_frame); canvas_mon.get_tk_widget().pack(fill=tk.X)

# Graph 2: Main Simulation Map
hm_fig, ax_hm = plt.subplots(figsize=(8, 8), dpi=100)
hm_fig.subplots_adjust(left=.06, right=.98, bottom=.06, top=.95)
canvas_hm = FigureCanvasTkAgg(hm_fig, master=graph_frame); canvas_hm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Animation Setup
x_stream, y_stream = [], []
def animate(i):
    global manual_rssi
    manual_rssi = get_current_best_rssi()
    y_stream.append(manual_rssi); x_stream.append(i)
    if len(x_stream) > 50: x_stream.pop(0); y_stream.pop(0)
    line.set_data(x_stream, y_stream); ax_mon.set_xlim(min(x_stream), max(x_stream)+1)
    ax_mon.set_ylim(min(-105, min(y_stream) - 5), -25)
    rssi_disp.config(text=f"{int(manual_rssi)}", fg=get_color_smooth(manual_rssi))
    return line,

dragging_target = None
hm_fig.canvas.mpl_connect('button_press_event', on_click)
hm_fig.canvas.mpl_connect('button_release_event', on_release)
hm_fig.canvas.mpl_connect('motion_notify_event', on_drag)

ani = animation.FuncAnimation(mon_fig, animate, interval=200, cache_frame_data=False)
update_main_view()
root.mainloop()
