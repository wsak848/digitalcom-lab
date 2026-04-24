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

# --- 2. Engineering Calculation Engine ---
def calculate_rssi(ax, ay, dx, dy):
    """คำนวณ RSSI โดยใช้ Path Loss Model (n=2.5 สำหรับพื้นที่วิทยาลัย)"""
    dist = np.sqrt((ax - dx)**2 + (ay - dy)**2)
    tx_power = -30 # RSSI ที่ระยะ 1 เมตร
    if dist <= 1.0: return float(tx_power)
    # สูตร: RSSI = Pt - 10*n*log10(d)
    val = tx_power - 10 * 2.5 * np.log10(dist)
    return float(np.clip(val, -100, -30))

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
    if not measured_points:
        messagebox.showwarning("แจ้งเตือน", "กรุณากด CAPTURE ข้อมูลก่อนทำการวิเคราะห์ครับ")
        return

    analysis_window = tk.Toplevel(root)
    analysis_window.title("Hatyai Tech - Interference & Coverage Analysis")
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    
    # สร้าง Meshgrid เพื่อคำนวณ Heatmap ทั่วพื้นที่ 100x100 เมตร
    res = 2 
    x = np.arange(0, 101, res)
    y = np.arange(0, 101, res)
    X, Y = np.meshgrid(x, y)
    v_calc = np.vectorize(calculate_rssi)
    # วิเคราะห์การซ้อนทับโดยเลือกค่า Max RSSI ในแต่ละพิกัด
    Z = np.maximum(v_calc(ap1_x, ap1_y, X, Y), v_calc(ap2_x, ap2_y, X, Y))
    
    # วาดแผนภาพ Heatmap พื้นหลัง (Interference Map)
    cp = ax.contourf(X, Y, Z, levels=np.linspace(-100, -30, 20), cmap='RdYlGn', alpha=0.7)
    fig.colorbar(cp, label='Best Signal Strength (dBm)')
    
    # วาดจุด Log และแปะตัวเลข dBm กำกับทุกจุด
    for pt in measured_points:
        px, py, prssi = pt
        ax.scatter(px, py, c='black', s=40, zorder=10)
        ax.text(px, py+2.5, f"{int(prssi)}dBm", fontsize=8, ha='center', weight='bold', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

    ax.scatter(ap1_x, ap1_y, c='black', marker='^', s=300, label='AP 1', edgecolors='white', linewidth=2)
    ax.scatter(ap2_x, ap2_y, c='blue', marker='^', s=300, label='AP 2', edgecolors='white', linewidth=2)
    ax.set_title("Signal Overlapping & Interference Map", fontweight='bold', pad=15)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.set_xlabel("Meters (X)"); ax.set_ylabel("Meters (Y)")
    ax.legend(loc='upper right')
    
    FigureCanvasTkAgg(fig, master=analysis_window).get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- 4. UI Rendering & Interaction ---
def update_main_view():
    ax_hm.clear()
    ax_hm.set_xlim(0, 100); ax_hm.set_ylim(0, 100)
    ax_hm.set_title(f"Live Simulation: Path Loss Model (Scale: 100x100m)")
    ax_hm.grid(True, alpha=0.15, linestyle='--')
    
    # วาดประวัติข้อมูลที่บันทึกไว้
    if measured_points:
        data = np.array(measured_points)
        ax_hm.scatter(data[:, 0], data[:, 1], c=data[:, 2], cmap='RdYlGn_r', vmin=-100, vmax=-30, s=100, alpha=0.5)

    # วาดอุปกรณ์ AP และ Device
    ax_hm.scatter(ap1_x, ap1_y, c='black', marker='^', s=400, label='Access Point 1', zorder=15)
    ax_hm.scatter(ap2_x, ap2_y, c='darkblue', marker='^', s=400, label='Access Point 2', zorder=15)
    ax_hm.scatter(dev_x, dev_y, c='#007bff', marker='o', s=300, edgecolors='white', linewidth=2, zorder=25)
    
    # ระบบเชื่อมต่ออัตโนมัติ (Auto Connection Line)
    d1 = np.sqrt((ap1_x-dev_x)**2 + (ap1_y-dev_y)**2)
    d2 = np.sqrt((ap2_x-dev_x)**2 + (ap2_y-dev_y)**2)
    
    # เลือก AP ที่ใกล้และแรงที่สุด
    if d1 <= d2:
        target, dist, label = (ap1_x, ap1_y), d1, "Connected: AP 1"
    else:
        target, dist, label = (ap2_x, ap2_y), d2, "Connected: AP 2"
        
    ax_hm.plot([target[0], dev_x], [target[1], dev_y], color='gray', linestyle='--', alpha=0.6, zorder=5)
    ax_hm.text((target[0]+dev_x)/2, (target[1]+dev_y)/2, f"{dist:.1f}m", 
               ha='center', fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    ax_hm.text(dev_x, dev_y-6, label, ha='center', fontsize=9, fontweight='bold', color='#1A5276')
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
    if not event.inaxes or not dragging_target: return
    
    new_x, new_y = np.clip(event.xdata, 0, 100), np.clip(event.ydata, 0, 100)
    
    if dragging_target == 'AP1': ap1_x, ap1_y = new_x, new_y
    elif dragging_target == 'AP2': ap2_x, ap2_y = new_x, new_y
    elif dragging_target == 'DEV': 
        dev_x, dev_y = new_x, new_y
        entry_x.delete(0, tk.END); entry_x.insert(0, f"{dev_x:.1f}")
        entry_y.delete(0, tk.END); entry_y.insert(0, f"{dev_y:.1f}")
    
    update_main_view()

def on_click(event):
    global dragging_target
    if not event.inaxes: return
    # ตรวจสอบการคลิกโดนวัตถุ (รัศมี 7 เมตร)
    if np.hypot(event.xdata-dev_x, event.ydata-dev_y) < 7: dragging_target = 'DEV'
    elif np.hypot(event.xdata-ap1_x, event.ydata-ap1_y) < 7: dragging_target = 'AP1'
    elif np.hypot(event.xdata-ap2_x, event.ydata-ap2_y) < 7: dragging_target = 'AP2'

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
rssi_disp = tk.Label(ctrl, text="-30", font=("Arial", 80, "bold"), fg="#1A9641")
rssi_disp.pack()

# Input: Coordinates
pos_f = ttk.LabelFrame(ctrl, text=" Device (Target) Position ", padding=10)
pos_f.pack(fill=tk.X, pady=10)
entry_x = ttk.Entry(pos_f, width=8); entry_y = ttk.Entry(pos_f, width=8)
ttk.Label(pos_f, text="X:").grid(row=0, column=0); entry_x.grid(row=0, column=1)
ttk.Label(pos_f, text="Y:").grid(row=0, column=2); entry_y.grid(row=0, column=3)
entry_x.insert(0, "50.0"); entry_y.insert(0, "50.0")
ttk.Button(pos_f, text="CAPTURE DATA POINT", command=log_point).grid(row=1, columnspan=4, pady=12, sticky='ew')

# Data Logging Table
log_table = ttk.Treeview(ctrl, columns=("#","X","Y","RSSI"), show="headings", height=18)
for c in ("#","X","Y","RSSI"): 
    log_table.heading(c, text=c); log_table.column(c, width=60, anchor="center")
log_table.pack(fill=tk.BOTH, expand=True)

ttk.Button(ctrl, text="SHOW COMBINED HEATMAP", command=show_combined_analysis).pack(fill=tk.X, pady=8)
ttk.Button(ctrl, text="CLEAR ALL SIMULATION", command=lambda: [measured_points.clear(), [log_table.delete(i) for i in log_table.get_children()], update_main_view()]).pack(fill=tk.X)

# Right Panel: Visualization & Monitoring
graph_frame = ttk.Frame(root); graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Graph 1: Live Monitor
mon_fig, ax_mon = plt.subplots(figsize=(5, 2), dpi=100); plt.subplots_adjust(bottom=0.3)
line, = ax_mon.plot([], [], lw=2.5, color='#8E44AD')
ax_mon.set_ylim(-105, -25); ax_mon.set_title("Live RSSI Monitor Stream (dBm)")
canvas_mon = FigureCanvasTkAgg(mon_fig, master=graph_frame); canvas_mon.get_tk_widget().pack(fill=tk.X)

# Graph 2: Main Simulation Map
hm_fig, ax_hm = plt.subplots(figsize=(6, 6), dpi=100)
canvas_hm = FigureCanvasTkAgg(hm_fig, master=graph_frame); canvas_hm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Animation Setup
x_stream, y_stream = [], []
def animate(i):
    global manual_rssi
    manual_rssi = get_current_best_rssi()
    y_stream.append(manual_rssi); x_stream.append(i)
    if len(x_stream) > 50: x_stream.pop(0); y_stream.pop(0)
    line.set_data(x_stream, y_stream); ax_mon.set_xlim(min(x_stream), max(x_stream)+1)
    rssi_disp.config(text=f"{int(manual_rssi)}", fg=get_color_smooth(manual_rssi))
    return line,

dragging_target = None
hm_fig.canvas.mpl_connect('button_press_event', on_click)
hm_fig.canvas.mpl_connect('button_release_event', on_release)
hm_fig.canvas.mpl_connect('motion_notify_event', on_drag)

ani = animation.FuncAnimation(mon_fig, animate, interval=200, cache_frame_data=False)
update_main_view()
root.mainloop()