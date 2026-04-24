import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import numpy as np

def run():
    t = np.linspace(0, 1, 100)
    x = np.sin(2 * np.pi * 5 * t)

    fig, ax = plt.subplots()
    ax.plot(t, x)
    ax.set_title("Quantization Demo")

    return fig

# --- 1. ตั้งค่าสัญญาณ Analog และ Sampling ---
# อาจารย์สามารถปรับ fs (Sampling Rate) ตรงนี้ได้เลยครับ
fs = 1000          # 1000 Samples per second (Hz)
duration = 1.0
t_fine = np.linspace(0, duration, 1000)
y_analog = 0.8 * np.sin(2 * np.pi * 2 * t_fine) 

# --- 2. เตรียมพื้นที่วาดกราฟ ---
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.25, top=0.85) # เว้นพื้นที่ด้านบนให้กล่องข้อความ

line_analog, = ax.plot(t_fine, y_analog, 'k--', alpha=0.3, label='Original Analog')
pcm_step, = ax.plot([], [], 'r-', drawstyle='steps-mid', linewidth=2, label='Quantized Signal')

ax.set_title("Quantization & Bit Rate Real-time Calculation", fontsize=14, fontweight='bold', pad=20)
ax.set_ylim(-1.2, 1.2)
ax.grid(True, alpha=0.2)
ax.legend(loc='lower right')

# --- 3. ส่วนการแสดงผล Bit Rate (Text Box) ---
# วางไว้ตำแหน่ง (0.02, 1.1) ของพิกัด Axes เพื่อให้อยู่เหนือกราฟ
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
info_text = ax.text(0.02, 1.12, '', transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=props, family='monospace', fontweight='bold')

# --- 4. สร้าง Slider สำหรับปรับ Bit Depth (n) ---
ax_bits = plt.axes([0.2, 0.1, 0.6, 0.03])
s_bits = Slider(ax_bits, 'Bit Depth (n) ', 1, 12, valinit=3, valstep=1)

# --- 5. ฟังก์ชันอัปเดตการทำงาน ---
def update(val):
    n = int(s_bits.val)
    levels = 2**n
    
    # สูตรคำนวณ: Bit Rate = fs * n
    bitrate = fs * n
    
    # กระบวนการ Quantization
    y_scaled = (y_analog + 1) / 2 * (levels - 1)
    y_quantized = (np.round(y_scaled) / (levels - 1)) * 2 - 1
    
    # อัปเดตกราฟ
    pcm_step.set_data(t_fine, y_quantized)
    
    # แสดงการคำนวณบนหน้าจอ
    display_str = (
        f" [ Calculation ] \n"
        f" Sampling Rate (fs) = {fs} Hz\n"
        f" Bit Depth     (n)  = {n} bits\n"
        f" ------------------------------\n"
        f" Bit Rate (fs * n)  = {bitrate:,} bps\n"
        f" Levels   (2^n)     = {levels:,} levels"
    )
    info_text.set_text(display_str)
    
    fig.canvas.draw_idle()

s_bits.on_changed(update)
update(None) # เรียกครั้งแรกเพื่อให้แสดงค่าเริ่มต้น

print(f"โปรแกรมกำลังทำงาน... (Sampling Rate: {fs} Hz)")
plt.show()
