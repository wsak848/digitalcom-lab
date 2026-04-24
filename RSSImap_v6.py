import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

# --- 1. ตั้งค่าพื้นฐาน (Scale 100x100m) ---
manual_rssi = -30.0
measured_points = [] 
ap_x, ap_y = 10.0, 90.0  # ตำแหน่งเริ่มต้น Access Point
dev_x, dev_y = 50.0, 50.0 # ตำแหน่งเริ่มต้น Device
dragging_target = None 
drag_press_pos = None
room_width, room_height = 100, 100 

# --- 2. ฟังก์ชันคำนวณและจัดการสี ---
def calculate_rssi_by_distance(ax, ay, dx, dy):
    """คำนวณ RSSI ตามระยะห่างจริง (Log-Distance Path Loss Model)"""
    distance = np.sqrt((ax - dx)**2 + (ay - dy)**2)
    tx_power = -30  # RSSI ที่ระยะ 1 เมตร
    if distance <= 1.0: return float(tx_power)
    # n = 2.5 สำหรับสภาพแวดล้อมกึ่งเปิดโล่งในวิทยาลัย
    calculated = tx_power - 10 * 2.5 * np.log10(distance)
    return float(np.clip(calculated, -100, -30))

def get_color_smooth(val):
    """ฟังก์ชันไล่สี: เน้นสีแดงเข้ม (Deep Red) เมื่อสัญญาณต่ำกว่า -85 dBm"""
    if val >= -45: return "#1A9641"   # เขียวเข้ม (ดีมาก)
    elif val >= -55: return "#A6D96A" # เขียวอ่อน
    elif val >= -65: return "#FEE08B" # เหลือง
    elif val >= -75: return "#FDAE61" # ส้ม
    elif val >= -85: return "#D73027" # แดง
    else: return "#7B0000"            # แดงเข้มพิเศษ (Deep Red) แทนสีชมพู

def update_ui_rssi():
    global manual_rssi
    manual_rssi = int(calculate_rssi_by_distance(ap_x, ap_y, dev_x, dev_y))
    entry_rssi.delete(0, tk.END)
    entry_rssi.insert(0, str(manual_rssi))

# --- 3. หน้าต่างวิเคราะห์ Concentric Heatmap (ระบุค่าทุกวง + สีแดงเข้มไร้ขอบ) ---
def show_combined_heatmap():
    if not measured_points:
        messagebox.showwarning("แจ้งเตือน", "กรุณากด Capture ข้อมูลก่อนโชว์ผลลัพธ์ครับ")
        return
    
    combo_window = tk.Toplevel(root)
    combo_window.title("RSSI propagation Analysis - Hatyai Technical College")
    combo_fig, combo_ax = plt.subplots(figsize=(8, 8), dpi=100)
    combo_ax.set_aspect('equal')
    combo_ax.set_xlim(-110, 110)
    combo_ax.set_ylim(-110, 110)
    combo_ax.set_facecolor('#F2F2F2')
    
    # เรียงลำดับจากค่า RSSI น้อยไปมาก (ไกลไปใกล้) เพื่อให้วงกลมเล็กทับวงใหญ่
    sorted_points = sorted(measured_points, key=lambda p: p[2]) 
    
    for point in sorted_points:
        rssi = point[2]
        # รัศมีแปรผันตามระยะจริง
        dist_radius = 10**((rssi - (-30)) / (-10 * 2.5))
        color = get_color_smooth(rssi)
        
        # วาดวงกลมรัศมีแบบไร้เส้นขอบ (edgecolor='none') เพื่อความนุ่มนวล
        circle = plt.Circle((0, 0), dist_radius, color=color, alpha=0.3, edgecolor='none')
        combo_ax.add_patch(circle)
        
        # ระบุค่า RSSI ทุกตำแหน่งบนวงสี
        combo_ax.text(0, dist_radius + 0.8, f"{int(rssi)} dBm", 
                      ha='center', va='bottom', fontsize=9, 
                      fontweight='bold', color='#2C3E50')
    
    combo_ax.scatter(0, 0, c='black', marker='*', s=500, zorder=10, label='Access Point Center')
    combo_ax.set_title("RSSI Propagation Analysis (Deep Red Gradient)", fontsize=14, fontweight='bold', pad=20)
    combo_ax.grid(True, linestyle=':', alpha=0.5)
    combo_ax.legend(loc='upper right')
    
    FigureCanvasTkAgg(combo_fig, master=combo_window).get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- 4. ฟังก์ชันจัดการ Mapping และ UI หลัก ---
def update_heatmap():
    global ap_x, ap_y, dev_x, dev_y
    ax_hm.clear()
    ax_hm.set_title(f"Live Simulation (Scale: {room_width}x{room_height} m)")
    ax_hm.set_xlim(0, room_width); ax_hm.set_ylim(0, room_height)
    ax_hm.set_xlabel("Meters (X)"); ax_hm.set_ylabel("Meters (Y)")
    ax_hm.grid(True, alpha=0.2)
    
    # วาดจุดประวัติที่เคย Capture
    if measured_points:
        data = np.array(measured_points)
        ax_hm.scatter(data[:, 0], data[:, 1], c=data[:, 2], cmap='RdYlGn_r', 
                      vmin=-100, vmax=-30, s=150, alpha=0.6, edgecolors='none')

    # วาด AP และ Device
    ax_hm.scatter(ap_x, ap_y, c='black', marker='^', s=350, label='Access Point', zorder=20)
    ax_hm.scatter(dev_x, dev_y, c='#007bff', marker='o', s=250, edgecolors='white', linewidth=2, label='Current Device', zorder=21)

    # วาดเส้นประแสดงระยะห่าง
    dist = np.sqrt((ap_x-dev_x)**2 + (ap_y-dev_y)**2)
    ax_hm.plot([ap_x, dev_x], [ap_y, dev_y], 'k--', alpha=0.1)
    ax_hm.text((ap_x+dev_x)/2, (ap_y+dev_y)/2, f" {dist:.1f}m", fontsize=10, fontweight='bold', backgroundcolor='white')
    
    ax_hm.legend(loc='upper right')
    canvas_hm.draw()

def log_point():
    global manual_rssi, dev_x, dev_y
    measured_points.append([dev_x, dev_y, manual_rssi])
    log_table.insert("", "end", values=(len(measured_points), f"{dev_x:.1f}", f"{dev_y:.1f}", f"{manual_rssi}"))
    log_table.yview_moveto(1)
    update_heatmap()

# --- 5. ระบบ Drag & Drop สำหรับพื้นที่ 100m ---
def on_press(event):
    global dragging_target, drag_press_pos
    if not event.inaxes: return
    # ตรวจจับในระยะ 7 เมตรเพื่อให้เลือกง่ายในสเกลใหญ่
    if np.linalg.norm([event.xdata-dev_x, event.ydata-dev_y]) < 7: dragging_target = 'DEV'
    elif np.linalg.norm([event.xdata-ap_x, event.ydata-ap_y]) < 7: dragging_target = 'AP'
    drag_press_pos = (event.xdata, event.ydata)

def on_motion(event):
    global ap_x, ap_y, dev_x, dev_y, drag_press_pos
    if not dragging_target or not event.inaxes: return
    dx, dy = event.xdata - drag_press_pos[0], event.ydata - drag_press_pos[1]
    if dragging_target == 'AP':
        ap_x = np.clip(ap_x+dx, 0, 100); ap_y = np.clip(ap_y+dy, 0, 100)
    else:
        dev_x = np.clip(dev_x+dx, 0, 100); dev_y = np.clip(dev_y+dy, 0, 100)
        entry_x.delete(0, tk.END); entry_x.insert(0, f"{dev_x:.1f}")
        entry_y.delete(0, tk.END); entry_y.insert(0, f"{dev_y:.1f}")
    update_ui_rssi(); drag_press_pos = (event.xdata, event.ydata); update_heatmap()

def on_release(event):
    global dragging_target
    dragging_target = None

# --- 6. สร้าง UI หลัก ---
root = tk.Tk()
root.title("Wireless Propagation Lab Simulator v4.0")
root.geometry("1300x900")

# Panel ควบคุม (ซ้าย)
ctrl_frame = ttk.Frame(root, padding=15); ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)
ttk.Label(ctrl_frame, text="SIGNAL SIMULATOR (100m)", font=("Arial", 14, "bold")).pack(pady=5)

in_f = ttk.LabelFrame(ctrl_frame, text=" Real-time RSSI ", padding=10); in_f.pack(fill=tk.X)
entry_rssi = ttk.Entry(in_f, font=("Arial", 12), width=15); entry_rssi.pack()
rssi_label = tk.Label(ctrl_frame, text="-30", font=("Arial", 80, "bold")); rssi_label.pack()

pos_f = ttk.LabelFrame(ctrl_frame, text=" Position Control ", padding=10); pos_f.pack(fill=tk.X, pady=10)
entry_x = ttk.Entry(pos_f, width=7); entry_y = ttk.Entry(pos_f, width=7)
ttk.Label(pos_f, text="X:").grid(row=0, column=0); entry_x.grid(row=0, column=1)
ttk.Label(pos_f, text="Y:").grid(row=0, column=2); entry_y.grid(row=0, column=3)
entry_x.insert(0, "50.0"); entry_y.insert(0, "50.0")
ttk.Button(pos_f, text="CAPTURE POINT", command=log_point).grid(row=1, columnspan=4, pady=10, sticky='ew')

log_table = ttk.Treeview(ctrl_frame, columns=("#","X","Y","RSSI"), show="headings", height=15)
for c in ("#","X","Y","RSSI"): log_table.heading(c, text=c); log_table.column(c, width=50, anchor="center")
log_table.pack(fill=tk.BOTH, expand=True)

ttk.Button(ctrl_frame, text="Show Combined Heatmap", command=show_combined_heatmap).pack(fill=tk.X, pady=10)
ttk.Button(ctrl_frame, text="Clear Simulation", command=lambda: [measured_points.clear(), [log_table.delete(i) for i in log_table.get_children()], update_heatmap()]).pack(fill=tk.X)

# Panel กราฟ (ขวา)
graph_frame = ttk.Frame(root); graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
mon_fig, ax_mon = plt.subplots(figsize=(5, 1.8)); plt.subplots_adjust(bottom=0.3)
line, = ax_mon.plot([], [], color="#8E44AD", lw=2); ax_mon.set_ylim(-110, -10)
ax_mon.set_title("Live RSSI Stream")
canvas_mon = FigureCanvasTkAgg(mon_fig, master=graph_frame); canvas_mon.get_tk_widget().pack(fill=tk.X)

hm_fig, ax_hm = plt.subplots(figsize=(6, 6))
canvas_hm = FigureCanvasTkAgg(hm_fig, master=graph_frame); canvas_hm.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Animation Loop
x_data, y_data = [], []
def animate(i):
    y_data.append(manual_rssi); x_data.append(i)
    if len(x_data) > 50: x_data.pop(0); y_data.pop(0)
    ax_mon.set_xlim(min(x_data), max(x_data)+1)
    line.set_data(x_data, y_data)
    rssi_label.config(text=f"{int(manual_rssi)}", fg=get_color_smooth(manual_rssi))
    return line,

hm_fig.canvas.mpl_connect('button_press_event', on_press)
hm_fig.canvas.mpl_connect('button_release_event', on_release)
hm_fig.canvas.mpl_connect('motion_notify_event', on_motion)

update_ui_rssi(); update_heatmap()
ani = animation.FuncAnimation(mon_fig, animate, interval=200, cache_frame_data=False)
root.mainloop()