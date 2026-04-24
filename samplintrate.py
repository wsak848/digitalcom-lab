import numpy as np
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าสัญญาณ Analog หลัก ---
f_signal = 2           # ความถี่ของสัญญาณ Sine (Hz)
duration = 1.0         # ระยะเวลาที่แสดงผล (วินาที)
t_fine = np.linspace(0, duration, 1000)
y_analog = np.sin(2 * np.pi * f_signal * t_fine)

# --- 2. ฟังก์ชันคำนวณ PCM และ Bitrate ---
def generate_pcm(fs, bit_depth):
    # Sampling
    t_sample = np.arange(0, duration, 1/fs)
    y_sample = np.sin(2 * np.pi * f_signal * t_sample)
    
    # Quantization
    levels = 2**bit_depth
    # แปลงค่าจาก -1 ถึง 1 ให้เป็นระดับชั้น 0 ถึง (levels-1)
    y_quantized = np.round(((y_sample + 1) / 2) * (levels - 1))
    # แปลงกลับเป็นค่าแรงดันเพื่อพลอตกราฟเทียบกับ Analog
    y_normalized = (y_quantized / (levels - 1)) * 2 - 1
    
    bitrate = fs * bit_depth
    return t_sample, y_normalized, bitrate

# --- 3. ตั้งค่าการเปรียบเทียบ (ปรับแต่งค่าตรงนี้ได้เลย) ---
# แบบที่ 1: Bitrate ต่ำ (เช่น 10 Hz, 3 bits)
fs1, depth1 = 12, 3
t1, y1, br1 = generate_pcm(fs1, depth1)

# แบบที่ 2: Bitrate สูง (เช่น 50 Hz, 8 bits)
fs2, depth2 = 60, 8
t2, y2, br2 = generate_pcm(fs2, depth2)

# --- 4. การสร้างกราฟเปรียบเทียบ ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.4)

# กราฟที่ 1: Low Bitrate
ax1.plot(t_fine, y_analog, 'k--', alpha=0.3, label='Original Analog')
ax1.step(t1, y1, where='mid', color='red', label=f'PCM {depth1}-bit')
ax1.stem(t1, y1, linefmt='r-', markerfmt='ro', basefmt=" ")
ax1.set_title(f"Case A: Low Bitrate = {br1} bits/sec\n(Sampling={fs1}Hz, Depth={depth1}bits)")
ax1.legend()
ax1.grid(True)

# กราฟที่ 2: High Bitrate
ax2.plot(t_fine, y_analog, 'k--', alpha=0.3, label='Original Analog')
ax2.step(t2, y2, where='mid', color='blue', label=f'PCM {depth2}-bit')
ax2.stem(t2, y2, linefmt='b-', markerfmt='bo', basefmt=" ")
ax2.set_title(f"Case B: High Bitrate = {br2} bits/sec\n(Sampling={fs2}Hz, Depth={depth2}bits)")
ax2.legend()
ax2.grid(True)

plt.xlabel("Time (sec)")
print(f"Case A Bitrate: {br1} bps")
print(f"Case B Bitrate: {br2} bps")
plt.show()