import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

def draw_fsk(data_string):
    try:
        # 1. เตรียมข้อมูล
        bits = np.array([int(b) for b in data_string if b in '01'])
        if len(bits) == 0: return
        
        time_per_bit = 0.1
        num_samples = 1000
        t = np.linspace(0, len(bits) * time_per_bit, num_samples, endpoint=False)
        
        # 2. สร้างสัญญาณ
        samples_per_bit = num_samples // len(bits)
        digital_signal = np.repeat(bits, samples_per_bit)
        digital_signal = np.resize(digital_signal, t.shape)
        
        f1, f0 = 100, 30
        carrier1 = np.sin(2 * np.pi * f1 * t)
        carrier0 = np.sin(2 * np.pi * f0 * t)
        fsk_signal = np.where(digital_signal == 1, carrier1, carrier0)
        
        # 3. อัปเดตกราฟ
        ax1.clear()
        ax2.clear()
        
        ax1.step(t, digital_signal, where='post', color='blue', lw=2)
        ax1.set_title(f"Digital Data: {data_string}", color='blue')
        ax1.set_ylim(-0.2, 1.2)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(t, fsk_signal, color='red', lw=1)
        ax2.set_title(f"FSK Signal (1:{f1}Hz, 0:{f0}Hz)", color='red')
        ax2.set_xlabel("Time (s)")
        ax2.grid(True, alpha=0.3)
        
        plt.draw()
    except Exception as e:
        print(f"Error: {e}")

# --- ส่วนสร้างหน้าต่างกราฟ ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
plt.subplots_adjust(bottom=0.2) # เผื่อพื้นที่ด้านล่างไว้ใส่ช่องกรอก

# สร้างช่องกรอกข้อความ (TextBox)
axbox = plt.axes([0.2, 0.05, 0.6, 0.075])
text_box = TextBox(axbox, 'Enter Bits: ', initial="101101")

# เชื่อมต่อเหตุการณ์เมื่อกด Enter ในช่องกรอก
text_box.on_submit(draw_fsk)

# รันครั้งแรกด้วยค่าเริ่มต้น
draw_fsk("101101")

print("เปิดหน้าต่างกราฟแล้ว ลองเปลี่ยนตัวเลขในช่อง Enter Bits แล้วกด Enter ดูครับอาจารย์")
plt.show()