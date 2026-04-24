import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- 1. ตั้งค่าสัญญาณ Analog หลัก ---
f_signal = 2
duration = 1.0
t_fine = np.linspace(0, duration, 1000)
y_analog = np.sin(2 * np.pi * f_signal * t_fine)

# --- 2. เตรียมพื้นที่วาดกราฟ ---
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.25) # เว้นที่ด้านล่างไว้ใส่ Slider

line_analog, = ax.plot(t_fine, y_analog, 'k--', alpha=0.2, label='Original Analog')
# สร้างตัวแปรสำหรับกราฟ PCM (Step และ Stem)
pcm_step, = ax.plot([], [], 'r-', drawstyle='steps-mid', label='PCM Signal')
pcm_stem = ax.stem([0], [0], linefmt='r-', markerfmt='ro', basefmt=" ")

ax.set_title("Interactive PCM: Adjust Sampling & Bit Depth", fontsize=14)
ax.set_ylim(-1.2, 1.5)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')

# ข้อความแสดงค่า Bitrate
text_bitrate = ax.text(0.02, 1.3, '', fontsize=12, color='darkred', fontweight='bold')

# --- 3. สร้าง Slider สำหรับปรับค่า ---
ax_fs = plt.axes([0.2, 0.1, 0.6, 0.03])    # [left, bottom, width, height]
ax_bits = plt.axes([0.2, 0.05, 0.6, 0.03])

s_fs = Slider(ax_fs, 'Sampling (Hz) ', 4, 100, valinit=12, valstep=1)
s_bits = Slider(ax_bits, 'Bit Depth (n) ', 1, 8, valinit=3, valstep=1)

# --- 4. ฟังก์ชันอัปเดตกราฟ ---
def update(val):
    fs = int(s_fs.val)
    n = int(s_bits.val)
    
    # คำนวณ PCM ใหม่
    t_sample = np.arange(0, duration, 1/fs)
    y_sample = np.sin(2 * np.pi * f_signal * t_sample)
    
    levels = 2**n
    y_quantized = np.round(((y_sample + 1) / 2) * (levels - 1))
    y_norm = (y_quantized / (levels - 1)) * 2 - 1
    
    # อัปเดตข้อมูลกราฟ
    pcm_step.set_data(t_sample, y_norm)
    
    # อัปเดต Stem plot (ต้องลบของเก่าแล้ววาดใหม่)
    global pcm_stem
    pcm_stem.remove()
    pcm_stem = ax.stem(t_sample, y_norm, linefmt='r-', markerfmt='ro', basefmt=" ")
    
    # อัปเดตข้อความ Bitrate
    bitrate = fs * n
    text_bitrate.set_text(f"Bitrate: {bitrate} bps ({fs} Hz x {n} bits)")
    
    fig.canvas.draw_idle()

# สั่งให้ทำงานเมื่อมีการเลื่อน Slider
s_fs.on_changed(update)
s_bits.on_changed(update)

# รันฟังก์ชันครั้งแรกเพื่อโชว์กราฟเริ่มต้น
update(None)

plt.show()