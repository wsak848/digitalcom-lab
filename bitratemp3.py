import numpy as np
import matplotlib.pyplot as plt

# --- 1. สร้างสัญญาณเสียงจำลอง (ผสมหลายความถี่) ---
fs = 44100  # Sampling Rate มาตรฐาน CD/MP3
duration = 0.02  # ดูช่วงสั้นๆ 20ms เพื่อให้เห็นลูกคลื่นชัดๆ
t = np.linspace(0, duration, int(fs * duration))

# สร้างสัญญาณที่มีทั้งความถี่ต่ำ (เสียงเบส) และความถี่สูง (รายละเอียดเสียง)
signal_low = 0.6 * np.sin(2 * np.pi * 150 * t)   # 150 Hz
signal_high = 0.2 * np.sin(2 * np.pi * 4000 * t) # 4 kHz (รายละเอียด)
noise_high = 0.1 * np.sin(2 * np.pi * 12000 * t) # 12 kHz (ความถี่สูงมาก)

y_original = signal_low + signal_high + noise_high

# --- 2. จำลองการบีบอัดแบบ MP3 (Lossy Compression) ---
# MP3 มักจะตัดความถี่ที่สูงมากๆ ออกเพื่อลดปริมาณข้อมูล
y_compressed = signal_low + signal_high  # สมมติว่าโดนตัด 12kHz ทิ้งไป

# --- 3. การสร้างกราฟเปรียบเทียบ ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
plt.subplots_adjust(hspace=0.3)

# กราฟบน: Original PCM (High Quality)
ax1.plot(t * 1000, y_original, color='blue', label='Original (PCM 1.4 Mbps)')
ax1.set_title("Original High Fidelity Signal (Full Detail)")
ax1.set_ylabel("Amplitude")
ax1.grid(True, alpha=0.3)
ax1.legend()

# กราฟล่าง: Simulated MP3 128kbps (Lossy)
ax2.plot(t * 1000, y_compressed, color='red', label='Compressed (MP3 128 kbps)')
ax2.set_title("Compressed Signal (Lossy - High Frequencies Removed)")
ax2.set_ylabel("Amplitude")
ax2.set_xlabel("Time (ms)")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.show()