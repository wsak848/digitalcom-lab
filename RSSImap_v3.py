import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

# --- 1. ตั้งค่าพื้นฐาน ---
manual_rssi = -30.0
measured_points = [] 

# ตำแหน่ง AP และ Device
ap_x, ap_y = 2.0, 8.0
dev_x, dev_y = 5.0, 5.0

dragging_target = None 
drag_press_pos = None

room_width, room_height = 10, 10

# --- 2. ฟังก์ชันคำนวณ RSSI และจัดการสี ---
def calculate_rssi_by_distance(ax, ay, dx, dy):
    # คำนวณระยะห่างแบบ Euclidean
    distance = np.sqrt((ax - dx)**2 + (ay - dy)**2)
    # Path Loss Model: RSSI = P_ref - 10 * n * log10(d)
    # กำหนด n=3.0 (Indoor) และ P_ref=-30 (ที่ 1 เมตร)
    tx_power = -30
    if distance <= 1.0:
        return float(tx_power)
    calculated = tx_power - 10 * 3.0 * np.log10(distance)
    return float(np.clip(calculated, -100, -30))

def get_color(val):
    if val >= -45: return "#1A9641"   # เขียวเข้ม
    elif val >= -60: return "#A6D96A" # เขียวอ่อน
    elif val >= -75: return "#FFFFBF" # เหลือง
    elif val >= -85: return "#FDAE61" # ส้ม
    return "#D7191C"                  # แดง

def update_ui_rssi():
    global manual_rssi
    manual_rssi = int(calculate_rssi_by_distance(ap_x, ap_y, dev_x, dev_y))
    entry_rssi.delete(0, tk.END)
    entry_rssi.insert(0, str(manual_rssi))

def log_point():
    global manual_rssi, dev_x, dev_y
    try:
        measured_points.append([dev_x, dev_y, manual_rssi])
        point_num = len(measured_points)
        log_table.insert("", "end", values=(point_num, f"{dev_x:.1f}", f"{dev_y:.1f}", f"{manual_rssi}"))
        log_table.yview_moveto(1)
        update_heatmap()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- 3. ฟังก์ชันวาดกราฟและหน้าต่างพิเศษ ---
def update_heatmap():
    global ap_x, ap_y, dev_x, dev_y
    ax_hm.clear()
    ax_hm.set_title(f"Live Simulation: Path Loss Model (n=3.0)")
    ax_hm.set_xlim(0, room_width)
    ax_hm.set_ylim(0, room_height)
    ax_hm.grid(True, alpha=0.3)
    
    # วาดจุดประวัติที่ Log ไว้
    if measured_points:
        data = np.array(measured_points)
        ax_hm.scatter(data[:, 0], data[:, 1], c=data[:, 2], cmap='RdYlGn', 
                      vmin=-100, vmax=-30, s=150, edgecolors='black', alpha=0.4)

    # วาด AP และ Device
    ax_hm.scatter(ap_x, ap_y, c='black', marker='^', s=350, label='Access Point', zorder=100)
    ax_hm.scatter(dev_x, dev_y, c='#007bff', marker='o', s=300, edgecolors='white', 
                  linewidth=2, label='Current Device', zorder=101)

    # วาดเส้นบอกระยะห่าง
    dist = np.sqrt((ap_x-dev_x)**2 + (ap_y-dev_y)**2)
    ax_hm.plot([ap_x, dev_x], [ap_y, dev_y], 'k--', alpha=0.2)
    ax_hm.text((ap_x+dev_x)/2, (ap_y+dev_y)/2, f"{dist:.1f}m", fontsize=9, backgroundcolor='white')

    ax_hm.legend(loc='upper right', fontsize='small')
    canvas_hm.draw()

def show_combined_heatmap():
    if not measured_points:
        messagebox.showwarning("Warning", "ยังไม่มีข้อมูลให้แสดง!")
        return
    
    combo_window = tk.Toplevel(root)
    combo_window.title("RSSI Concentric Analysis")
    combo_fig, combo_ax = plt.subplots(figsize=(6, 6), dpi=100)
    combo_ax.set_aspect('equal')
    combo_ax.set_xlim(-12, 12)
    combo_ax.set_ylim(-12, 12)
    combo_ax.set_title("RSSI Range Profiles (Relative to AP)", fontweight='bold')
    
    sorted_points = sorted(measured_points, key=lambda p: -abs(p[2]))
    for point in sorted_points:
        rssi = point[2]
        radius = 2 + (abs(rssi) - 20) * 8 / 80
        color = get_color(rssi)
        circle = plt.Circle((0, 0), radius, color=color, alpha=0.4, ec='black', lw=1)
        combo_ax.add_patch(circle)
        combo_ax.text(0, radius + 0.2, f"{int(rssi)} dBm", ha='center', fontsize=8)
    
    combo_ax.scatter(0, 0, c='black', marker='*', s=450, label=f'AP Center')
    combo_ax.grid(True, alpha=0.2)
    combo_ax.legend()
    FigureCanvasTkAgg(combo_fig, master=combo_window).get_tk_widget().pack(fill=tk.BOTH, expand=True)

def clear_data():
    measured_points.clear()
    for item in log_table.get_children(): log_table.delete(item)
    update_heatmap()

# --- 4. ระบบ Drag & Drop ---
def on_press(event):
    global dragging_target, drag_press_pos
    if event.inaxes != ax_hm or not event.xdata: return
    if np.sqrt((event.xdata - dev_x)**2 + (event.ydata - dev_y)**2) < 0.7:
        dragging_target = 'DEV'
    elif np.sqrt((event.xdata - ap_x)**2 + (event.ydata - ap_y)**2) < 0.7:
        dragging_target = 'AP'
    drag_press_pos = (event.xdata, event.ydata)

def on_motion(event):
    global ap_x, ap_y, dev_x, dev_y, dragging_target, drag_press_pos
    if not dragging_target or event.inaxes != ax_hm or not event.xdata: return
    dx, dy = event.xdata - drag_press_pos[0], event.ydata - drag_press_pos[1]
    
    if dragging_target == 'AP':
        ap_x = np.clip(ap_x + dx, 0, room_width)
        ap_y = np.clip(ap_y + dy, 0, room_height)
    elif dragging_target == 'DEV':
        dev_x = np.clip(dev_x + dx, 0, room_width)
        dev_y = np.clip(dev_y + dy, 0, room_height)
        entry_x.delete(0, tk.END); entry_x.insert(0, f"{dev_x:.1f}")
        entry_y.delete(0, tk.END); entry_y.insert(0, f"{dev_y:.1f}")

    update_ui_rssi()
    drag_press_pos = (event.xdata, event.ydata)
    update_heatmap()

def on_release(event):
    global dragging_target
    dragging_target = None

# --- 5. UI Layout ---
fig, ax = plt.subplots(figsize=(4, 1.8), dpi=100)
plt.subplots_adjust(left=0.15, right=0.95, top=0.8, bottom=0.3)
x_data, y_data = [], []
line, = ax.plot([], [], lw=2, color="#8E44AD") 
ax.set_ylim(-110, -10); ax.set_title("Live RSSI Monitor (dBm)", fontsize=9)

def animate(frame):
    y_data.append(manual_rssi)
    x_data.append(frame)
    rssi_label.config(text=f"{int(manual_rssi)}", fg=get_color(manual_rssi))
    if frame > 30: ax.set_xlim(frame - 30, frame)
    else: ax.set_xlim(0, 30)
    line.set_data(x_data, y_data)
    return line,

hm_fig, ax_hm = plt.subplots(figsize=(5, 5), dpi=100)
root = tk.Tk()
root.title("RSSI Simulation Master - Hatyai Technical College")
root.geometry("1200x800")

# Panel ซ้าย
ctrl_frame = ttk.Frame(root, padding=10); ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)
ttk.Label(ctrl_frame, text="SIGNAL SIMULATOR", font=("Arial", 12, "bold")).pack()

in_f = ttk.LabelFrame(ctrl_frame, text=" 1. Current RSSI (Auto) ", padding=5); in_f.pack(fill=tk.X, pady=5)
entry_rssi = ttk.Entry(in_f, font=("Arial", 12), width=10); entry_rssi.insert(0, "-30"); entry_rssi.pack()
rssi_label = tk.Label(ctrl_frame, text="-30", font=("Arial", 70, "bold")); rssi_label.pack()

log_f = ttk.LabelFrame(ctrl_frame, text=" 2. Device (Target) ", padding=5); log_f.pack(fill=tk.X, pady=5)
ttk.Label(log_f, text="X:").grid(row=0, column=0); entry_x = ttk.Entry(log_f, width=6); entry_x.grid(row=0, column=1); entry_x.insert(0, "5.0")
ttk.Label(log_f, text="Y:").grid(row=0, column=2); entry_y = ttk.Entry(log_f, width=6); entry_y.grid(row=0, column=3); entry_y.insert(0, "5.0")
ttk.Button(log_f, text="CAPTURE DATA POINT", command=log_point).grid(row=1, column=0, columnspan=4, pady=10, sticky='ew')

table_f = ttk.LabelFrame(ctrl_frame, text=" 3. Simulation History ", padding=5); table_f.pack(fill=tk.BOTH, expand=True, pady=5)
columns = ("#", "X", "Y", "RSSI")
log_table = ttk.Treeview(table_f, columns=columns, show="headings", height=10)
for col in columns: log_table.heading(col, text=col); log_table.column(col, width=45, anchor="center")
log_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

ttk.Button(ctrl_frame, text="Show Combined Heatmap", command=show_combined_heatmap).pack(fill=tk.X, pady=5)
ttk.Button(ctrl_frame, text="Clear All", command=clear_data).pack(fill=tk.X)
status_label = ttk.Label(ctrl_frame, text="Drag symbols to simulate", foreground="gray"); status_label.pack(side=tk.BOTTOM)

# Panel ขวา
graph_frame = ttk.Frame(root); graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
FigureCanvasTkAgg(fig, master=graph_frame).get_tk_widget().pack(side=tk.TOP, fill=tk.X)
canvas_hm = FigureCanvasTkAgg(hm_fig, master=graph_frame)
canvas_hm.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# เริ่มต้นระบบ
update_ui_rssi()
update_heatmap()
hm_fig.canvas.mpl_connect('button_press_event', on_press)
hm_fig.canvas.mpl_connect('button_release_event', on_release)
hm_fig.canvas.mpl_connect('motion_notify_event', on_motion)
ani = animation.FuncAnimation(fig, animate, interval=100, cache_frame_data=False)
root.mainloop()