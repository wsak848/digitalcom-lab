import numpy as np
import matplotlib.pyplot as plt

# 1. ปรับแต่งค่าเริ่มต้น
fs = 100       # Sampling frequency (Hz)
f_signal = 5   # Signal frequency (Hz)
duration = 0.5 # ระยะเวลา (วินาที)
n_bits = 3     # จำนวนบิต (ใช้ 3 บิต = 8 ระดับ)

# 2. สร้างสัญญาณ Analog (Sine Wave)
t_analog = np.linspace(0, duration, 1000)
y_analog = np.sin(2 * np.pi * f_signal * t_analog)

# 3. กระบวนการ PCM
# Sampling
t_sample = np.arange(0, duration, 1/fs)
y_sample = np.sin(2 * np.pi * f_signal * t_sample)

# Quantization
levels = 2**n_bits
y_quantized = np.round(((y_sample + 1) / 2) * (levels - 1))
y_normalized = (y_quantized / (levels - 1)) * 2 - 1

# 4. เตรียมข้อมูล Line Coding (ตัวอย่าง 8 บิตแรก)
bits = [1, 0, 1, 1, 0, 0, 1, 0]
bit_t = np.repeat(np.arange(len(bits) + 1), 100)
unipolar_nrz = np.repeat(bits, 100)
polar_nrz = np.repeat([1 if b == 1 else -1 for b in bits], 100)

# --- การสร้างกราฟ ---
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
plt.subplots_adjust(hspace=0.5)

# กราฟ 1: Sampling & Quantization
axs[0].plot(t_analog, y_analog, label='Analog Signal', color='blue', alpha=0.3)
axs[0].stem(t_sample, y_normalized, 'r', label='PCM Quantized', basefmt=" ")
axs[0].set_title('Step 1: Sampling & Quantization (PCM)')
axs[0].legend()
axs[0].grid(True)

# กราฟ 2: Unipolar NRZ
axs[1].step(np.arange(len(bits)), bits, where='post', color='green', linewidth=2)
axs[1].set_title('Step 2: Line Coding - Unipolar NRZ (1=High, 0=Low)')
axs[1].set_ylim(-0.5, 1.5)
axs[1].set_xticks(range(len(bits)))
axs[1].grid(True)

# กราฟ 3: Polar NRZ
polar_data = [1 if b == 1 else -1 for b in bits]
axs[2].step(np.arange(len(bits)), polar_data, where='post', color='orange', linewidth=2)
axs[2].set_title('Step 3: Line Coding - Polar NRZ (1=+V, 0=-V)')
axs[2].set_ylim(-1.5, 1.5)
axs[2].axhline(0, color='black', linewidth=1)
axs[2].set_xticks(range(len(bits)))
axs[2].grid(True)

print(f"Binary Bits for demonstration: {bits}")
plt.show()