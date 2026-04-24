import numpy as np
import matplotlib.pyplot as plt

# 1. ข้อมูลบิตดิจิทัล (Data bits)
bits = np.array([1, 0, 1, 1, 0, 1])
time_per_bit = 0.1 
num_samples = 1200 # เพิ่มจุดให้หาร 6 ลงตัวพอดี (200 จุดต่อบิต)

# 2. สร้างฐานเวลา (Time base)
t = np.linspace(0, len(bits) * time_per_bit, num_samples, endpoint=False)

# 3. สร้างสัญญาณ Digital (Baseband)
samples_per_bit = num_samples // len(bits)
digital_signal = np.repeat(bits, samples_per_bit)

# 4. สร้างคลื่นพาหะ (Carrier Wave)
fc = 60 # ลองใช้ 60Hz จะเห็นลูกคลื่นสวยครับ
carrier = np.sin(2 * np.pi * fc * t)

# 5. ทำ ASK Modulation
ask_signal = digital_signal * carrier

# --- ส่วนการพล็อตกราฟ 3 ชั้น ---
plt.figure(figsize=(10, 8))

# กราฟที่ 1: Digital Data
plt.subplot(3, 1, 1)
plt.step(t, digital_signal, where='post', color='blue', lw=2)
plt.title("1) Digital Data Bits (Message)", fontsize=12)
plt.ylim(-0.2, 1.2)
plt.grid(True, alpha=0.3)

# กราฟที่ 2: Carrier Wave
plt.subplot(3, 1, 2)
plt.plot(t, carrier, color='gray', lw=1)
plt.title(f"2) Carrier Wave ({fc} Hz)", fontsize=12)
plt.grid(True, alpha=0.3)

# กราฟที่ 3: ASK Modulated Signal
plt.subplot(3, 1, 3)
plt.plot(t, ask_signal, color='red', lw=1.5)
plt.title("3) ASK Modulated Signal (Digital * Carrier)", fontsize=12)
plt.xlabel("Time (s)")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()