import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

def draw_psk(data_string):
    try:
        # 1. กรองเฉพาะเลข 0 และ 1
        bits = np.array([int(b) for b in data_string if b in '01'])
        if len(bits) == 0: return
        
        time_per_bit = 0.1
        num_samples = 1200
        t = np.linspace(0, len(bits) * time_per_bit, num_samples, endpoint=False)
        
        # 2. สร้างสัญญาณ Digital
        samples_per_bit = num_samples // len(bits)
        digital_signal = np.repeat(bits, samples_per_bit)
        digital_signal = np.resize(digital_signal, t.shape)
        
        # 3. สร้าง PSK Modulation
        fc = 40  # ความถี่พาหะ (Carrier Frequency)
        # Bit 1: Phase 0, Bit 0: Phase pi (180 degree)
        psk_signal = np.where(digital_signal == 1, 
                              np.sin(2 * np.pi * fc * t), 
                              np.sin(2 * np.pi * fc * t + np.pi))
        
        # 4. อัปเดตกราฟ
        ax1.clear()
        ax2.clear()
        
        # พล็อตสัญญาณ Digital
        ax1.step(t, digital_signal, where='post', color='blue', lw=2)
        ax1.set_title(f"Digital Data: {data_string}", color='blue', fontsize=12)
        ax1.set_ylim(-0.2, 1.2)
        ax1.grid(True, alpha=0.3)
        
        # พล็อตสัญญาณ PSK
        ax2.plot(t, psk_signal, color='red', lw=1.5)
        ax2.set_title(f"PSK Signal ({fc}Hz) - Phase Shift 180° at Bit 0", color='red', fontsize=12)
        ax2.set_xlabel("Time (s)")
        ax2.grid(True, alpha=0.3)
        
        # เพิ่มเส้นประแบ่งช่วงบิตเพื่อให้ดูง่ายขึ้น
        for i in range(len(bits) + 1):
            ax1.axvline(i * time_per_bit, color='gray', linestyle='--', alpha=0.4)
            ax2.axvline(i * time_per_bit, color='gray', linestyle='--', alpha=0.4)
        
        plt.draw()
    except Exception as e:
        print(f"Error: {e}")

# --- ส่วนสร้าง GUI ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
plt.subplots_adjust(bottom=0.2)

# ช่องกรอกข้อมูลบิต
axbox = plt.axes([0.2, 0.05, 0.6, 0.075])
text_box = TextBox(axbox, 'Enter Bits: ', initial="101101")
text_box.on_submit(draw_psk)

# รันครั้งแรก
draw_psk("101101")

print("เปิดหน้าต่าง PSK แล้วครับอาจารย์ ลองป้อนบิตสลับไปมาเพื่อดูจุด Phase Shift นะครับ")
plt.show()