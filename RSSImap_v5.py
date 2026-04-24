import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

# --- 1. ตั้งค่าพื้นฐาน (Scale 100x100m) ---
manual_rssi = -30.0
measured_points = [] 
ap_x, ap_y = 10.0, 90.0
dev_x, dev_y = 50.0, 50.0
dragging_target = None 
drag_press_pos = None
room_width, room_height = 100, 100 

# --- 2. ฟังก์ชันคำนวณและจัดการสี ---
def calculate_rssi_by_distance(ax, ay, dx, dy):
    """คำนวณ RSSI ตามระยะห่างจริงโดยใช้ Log-Distance Path Loss Model"""
    distance = np.sqrt((ax - dx)**2 + (ay - dy)**2)
    tx_power = -30  # RSSI ที่ 1 เมตร
    if distance <= 1.0: return float(tx_power)
    # n = 2.5 สำหรับสภาพแวดล้อมกึ่งเปิดโล่ง
    calculated = tx_power - 10 * 2.5 * np.log10(distance)
    return float(np.clip(calculated, -100, -30))

def get_color_smooth(val):
    """ไล่สีแบบนุ่มนวล: เขียว -> เหลือง -> ส้ม -> แดงเข้ม (เริ่มแดงที่ -80 dBm)"""
    if val >= -45: return "#1A9641"   # เขียวเข้ม (สัญญาณดีมาก)
    elif val >= -60: return "#A6D96A" # เขียวอ่อน
    elif val >= -70: return "#FEE08B" # เหลือง
    elif val >= -80: return "#FDAE61" # ส้ม (เริ่มอ่อนกำลัง)
    elif val >= -90: return "#D73027" # แดง (สัญญาณวิกฤต)
    else: return "#67001F"            # แดงเลือดหมูเข้ม (จุดบอดสัญญาณ)

def update_ui_rssi():
    global manual_rssi
    manual_rssi = int(calculate_rssi_by_distance(ap_x, ap_y, dev_x, dev_y))
    entry_rssi.delete(0, tk.END)
    entry_rssi.insert(0, str(manual_rssi))

# --- 3. ฟังก์ชันวิเคราะห์ Concentric Heatmap (ฉบับปรับปรุงความสวยงาม) ---
def show_combined_heatmap():
    if not measured_points:
        messagebox.showwarning("คำเตือน", "กรุณากด CAPTURE ข้อมูลก่อนแสดงผล!")
        return
    
    combo_window = tk.Toplevel(root)
    combo_window.title("RSSI Advanced Analysis (Concentric)")
    combo_fig, combo_ax = plt.subplots(figsize=(7, 7), dpi=100)
    combo_ax.set_aspect('equal')
    combo_ax.set_xlim(-110, 110)
    combo_ax.set_ylim(-110, 110)
    combo_ax.set_facecolor('#F8F9F9') # พื้นหลังสีสว่างเพื่อให้เห็น Gradient ชัด
    
    # เรียงลำดับข้อมูลจากไกลไปใกล้ (เพื่อให้วงกลมเล็กทับวงใหญ่)
    sorted_points = sorted(measured_points, key=lambda p: abs(p[2]), reverse=True)
    
    for point in sorted_points:
        rssi = point[2]
        # คำนวณรัศมีวงกลมตามสมการระยะทาง
        dist_radius = 10**((rssi - (-30)) / (-10 * 2.5))
        color = get_color_smooth(rssi)
        
        # วาดวงกลมรัศมีแบบไม่มีเส้นขอบ (Smooth Edges)
        circle = plt.Circle((0, 0), dist_radius, color=color, alpha=0.25, edgecolor='none')
        combo_ax.add_patch(circle)
        
        # แสดงค่าตัวเลขเฉพาะจุดสำคัญ
        if rssi % 10 == 0 or rssi <= -80:
            combo_ax.text(0, dist_radius + 1, f"{int(rssi)} dBm", ha='center', fontsize=8, alpha=0.6)
    
    combo_ax.scatter(0, 0, c='black', marker='*', s=400, label='AP Location', zorder=5)
    combo_ax.set_title("RSSI Propagation Gradient (No Borders)", fontweight='bold', pad=15)
    combo_ax.grid(True, linestyle='--', alpha=0.3)
    combo_ax.legend(loc='upper right')
    
    FigureCanvasTkAgg(combo_fig, master=combo_window).get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- 4. ฟังก์ชันจัดการ Mapping และ Event ---
def update_heatmap():
    global ap_x, ap_y, dev_x, dev_y
    ax_hm.clear()
    ax_hm.set_title(f"Live Simulation Master (Scale: {room_width}x{room_height} m)")
    ax_hm.set_xlim(0, room_width); ax_hm.set_ylim(0, room_height)
    ax_hm.grid(True, alpha=0.2)
    
    # วาดจุดประวัติ
    if measured_points:
        data = np.array(measured_points)
        ax_hm.scatter(data[:, 0], data[:, 1], c=data[:, 2], cmap='RdYlGn_r', 
                      vmin=-100, vmax=-30, s=150, edgecolors='none', alpha=0.5)

    # วาด AP (Source) และ Device (Receiver)
    ax_hm.scatter(ap_x, ap_y, c='black', marker='^', s=300, label='Access Point', zorder=10)
    ax_hm.scatter(dev_x, dev_y, c='#007bff', marker='o', s=250, edgecolors='white', linewidth=2, label='Current Device', zorder=11)

    # วาดเส้นประและระยะทาง
    dist = np.sqrt((ap_x-dev_x)**2 + (ap_y-dev_y)**2)
    ax_hm.plot([ap_x, dev_x], [ap_y, dev_y], 'k--', alpha=0.1)
    ax_hm.text((ap_x+dev_x)/2, (ap_y+dev_y)/2, f" {dist:.1f}m", fontsize=10, fontweight='bold', backgroundcolor='white')

    ax_hm.legend(loc='upper right', frameon=True)
    canvas_hm.draw()

def log_point():
    global manual_rssi, dev_x, dev_y
    measured_points.append([dev_x, dev_y, manual_rssi])
    log_table.insert("", "end", values=(len(measured_points), f"{dev_x:.1f}", f"{dev_y:.1f}", f"{manual_rssi}"))
    log_table.yview_moveto(1)
    update_heatmap()

def clear_all():
    measured_points.clear()
    for item in log_table.get_children(): log_table.delete(item)
    update_heatmap()

# --- 5. ระบบควบคุม Drag & Drop ---
def on_press(event):
    global dragging_target, drag_press_pos
    if not event.inaxes: return
    # ตรวจจับในรัศมี 5 เมตรเพื่อให้จับง่ายในสเกล 100m
    if np.sqrt((event.xdata-dev_x)**2 + (event.ydata-dev_y)**2) < 6: dragging_target = 'DEV'
    elif np.sqrt((event.xdata-ap_x)**2 + (event.ydata-ap_y)**2) < 6: dragging_target = 'AP'
    drag_press_pos = (event.xdata, event.ydata)

def on_motion(event):
    global ap_x, ap_y, dev_x, dev_y, drag_press_pos
    if not dragging_target or not event.inaxes: return
    dx, dy = event.xdata - drag_press_pos[0], event.ydata - drag_press_pos[1]
    
    if dragging_target == 'AP':
        ap_x = np.clip(ap_x + dx, 0, 100); ap_y = np.clip(ap_y + dy, 0, 100)
    else:
        dev_x = np.clip(dev_x + dx, 0, 100); dev_y = np.clip(dev_y + dy, 0, 100)
        entry_x.delete(0, tk.END); entry_x.insert(0, f"{dev_x:.1f}")
        entry_y.delete(0, tk.END); entry_y.insert(0, f"{dev_y:.1f}")
        
    update_ui_rssi()
    drag_press_pos = (event.xdata, event.ydata)
    update_heatmap()

def on_release(event):
    global dragging_target
    dragging_target = None

# --- 6. UI Layout & Animation ---
root = tk.Tk()
root.title("RSSI Smart Simulator v3.0 - Hatyai Technical College")
root.geometry("1300x880")

# Panel ด้านซ้าย
ctrl_frame = ttk.Frame(root, padding=15); ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)
ttk.Label(ctrl_frame, text="SIGNAL SIMULATOR (100m)", font=("Arial", 14, "bold")).pack(pady=5)

# แสดงผล RSSI
in_f = ttk.LabelFrame(ctrl_frame, text=" 1. Real-time RSSI (dBm) ", padding=10); in_f.pack(fill=tk.X)
entry_rssi = ttk.Entry(in_f, font=("Arial", 12), width=12); entry_rssi.pack()
rssi_label = tk.Label(ctrl_frame, text="-30", font=("Arial", 75, "bold")); rssi_label.pack()

# พิกัดและการ Capture
log_f = ttk.LabelFrame(ctrl_frame, text=" 2. Device Position (X, Y) ", padding=10); log_f.pack(fill=tk.X, pady=10)
entry_x = ttk.Entry(log_f, width=7); entry_y = ttk.Entry(log_f, width=7)
ttk.Label(log_f, text="X:").grid(row=0, column=0); entry_x.grid(row=0, column=1)
ttk.Label(log_f, text="Y:").grid(row=0, column=2); entry_y.grid(row=0, column=3)
entry_x.insert(0, "50.0"); entry_y.insert(0, "50.0")
ttk.Button(log_f, text="CAPTURE DATA POINT", command=log_point).grid(row=1, columnspan=4, pady=10, sticky='ew')

# ตารางประวัติ
table_f = ttk.LabelFrame(ctrl_frame, text=" 3. Simulation History ", padding=5); table_f.pack(fill=tk.BOTH, expand=True)
columns = ("#", "X", "Y", "RSSI")
log_table = ttk.Treeview(table_f, columns=columns, show="headings", height=12)
for c in columns: log_table.heading(c, text=c); log_table.column(c, width=50, anchor="center")
log_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# ปุ่มสั่งการด้านล่าง
ttk.Button(ctrl_frame, text="Show Combined Heatmap", command=show_combined_heatmap).pack(fill=tk.X, pady=5)
ttk.Button(ctrl_frame, text="Clear All Data", command=clear_all).pack(fill=tk.X)
ttk.Label(ctrl_frame, text="Tip: Drag symbols to see real-time loss", foreground="gray").pack(side=tk.BOTTOM)

# Panel ด้านขวา (กราฟ)
graph_frame = ttk.Frame(root); graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# กราฟ Monitor ด้านบน
mon_fig, ax_mon = plt.subplots(figsize=(5, 1.8), dpi=100)
plt.subplots_adjust(bottom=0.3)
line, = ax_mon.plot([], [], color="#8E44AD", lw=2); ax_mon.set_ylim(-110, -10)
ax_mon.set_title("Live RSSI Monitor Stream", fontsize=9)
canvas_mon = FigureCanvasTkAgg(mon_fig, master=graph_frame)
canvas_mon.get_tk_widget().pack(fill=tk.X)

# กราฟ Heatmap ด้านล่าง
hm_fig, ax_hm = plt.subplots(figsize=(6, 6), dpi=100)
canvas_hm = FigureCanvasTkAgg(hm_fig, master=graph_frame)
canvas_hm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# เริ่มต้นระบบ
x_stream, y_stream = [], []
def animate(i):
    global manual_rssi
    y_stream.append(manual_rssi); x_stream.append(i)
    if len(x_stream) > 50: x_stream.pop(0); y_stream.pop(0)
    ax_mon.set_xlim(min(x_stream), max(x_stream)+1)
    line.set_data(x_stream, y_stream)
    rssi_label.config(text=f"{int(manual_rssi)}", fg=get_color_smooth(manual_rssi))
    return line,

hm_fig.canvas.mpl_connect('button_press_event', on_press)
hm_fig.canvas.mpl_connect('button_release_event', on_release)
hm_fig.canvas.mpl_connect('motion_notify_event', on_motion)

update_ui_rssi(); update_heatmap()
ani = animation.FuncAnimation(mon_fig, animate, interval=200, cache_frame_data=False)
root.mainloop()