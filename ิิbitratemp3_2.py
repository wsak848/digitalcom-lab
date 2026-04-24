import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import butter, lfilter

# --- 1. ตั้งค่าพื้นฐาน (ปรับให้โชว์ 1 Cycle ของความถี่หลัก 100Hz) ---
fs = 44100  
f_main = 100               # ความถี่หลัก 100 Hz
duration = 1 / f_main      # ระยะเวลาสำหรับ 1 รอบ (0.01 วินาที)
t = np.linspace(0, duration, int(fs * duration))

# สัญญาณ Analog ต้นฉบับ (ผสมความถี่สูงเพื่อโชว์รายละเอียด)
def get_original_signal(t):
    low = 0.6 * np.sin(2 * np.pi * f_main * t)      # 100 Hz (ตัวหลัก)
    high = 0.2 * np.sin(2 * np.pi * 1000 * t)       # 1 kHz (รายละเอียดกลาง)
    ultra = 0.1 * np.sin(2 * np.pi * 5000 * t)      # 5 kHz (รายละเอียดสูง)
    return low + high + ultra

y_analog = get_original_signal(t)

# --- 2. ฟังก์ชัน Filter ---
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

# --- 3. การแสดงผลกราฟ ---
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.25)

# วาดเส้นประ Analog ไว้เทียบ
line_orig, = ax.plot(t * 1000, y_analog, 'k--', alpha=0.3, label='Original PCM (High Res)')
line_mp3, = ax.plot([], [], 'r-', linewidth=2.5, label='Simulated MP3 Output')

ax.set_title(f"MP3 Quality Simulation: 1 Cycle Analysis ({f_main} Hz)", fontsize=14, fontweight='bold')
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Amplitude")
ax.set_ylim(-1.1, 1.1)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper right')

text_info = ax.text(0.02, 1.05, '', transform=ax.transAxes, color='darkred', fontweight='bold')

# --- 4. Slider ---
ax_br = plt.axes([0.2, 0.1, 0.6, 0.03])
s_br = Slider(ax_br, 'Bitrate (kbps) ', 32, 320, valinit=320, valstep=16)

def update(val):
    br = s_br.val
    # จำลองการตัดความถี่แหลม (Cutoff)
    cutoff = np.interp(br, [32, 320], [800, 15000])
    y_filtered = butter_lowpass_filter(y_analog, cutoff, fs)
    
    # จำลองการลดความละเอียด (Quantization)
    bits = np.interp(br, [32, 320], [4, 16])
    levels = 2**bits
    y_final = (np.round(((y_filtered + 1) / 2) * (levels - 1)) / (levels - 1)) * 2 - 1
    
    line_mp3.set_data(t * 1000, y_final)
    text_info.set_text(f"Bitrate: {int(br)} kbps | Cutoff: {cutoff/1000:.1f} kHz | Resolution: {int(bits)} bits")
    fig.canvas.draw_idle()
 
s_br.on_changed(update)
update(None)

print("แสดงผล 1 รอบสัญญาณเรียบร้อยครับ...")
plt.show()