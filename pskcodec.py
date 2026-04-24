import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider

def draw_system(val=None):
    data_string = text_box.text
    noise_level = slider_noise.val
    
    try:
        # 1. เตรียมข้อมูลบิต
        bits = np.array([int(b) for b in data_string if b in '01'])
        if len(bits) == 0: return
        
        time_per_bit = 0.1
        num_samples = 1200
        t = np.linspace(0, len(bits) * time_per_bit, num_samples, endpoint=False)
        fc = 40
        samples_per_bit = num_samples // len(bits)
        
        # 2. Modulation (ตัวส่ง)
        digital_signal = np.resize(np.repeat(bits, samples_per_bit), t.shape)
        carrier = np.sin(2 * np.pi * fc * t)
        psk_tx = np.where(digital_signal == 1, carrier, -carrier)
        
        # 3. Add Noise (จำลองสัญญาณรบกวนในอากาศ)
        # noise_level ยิ่งมาก เปรียบเสมือน RSSI ยิ่งต่ำเมื่อเทียบกับ Noise (SNR แย่)
        noise = np.random.normal(0, noise_level, t.shape)
        psk_rx = psk_tx + noise
        
        # 4. Demodulation (ตัวรับ)
        mixed = psk_rx * carrier # คูณด้วย Coherent Carrier
        
        recovered_bits = []
        for i in range(len(bits)):
            segment = mixed[i*samples_per_bit : (i+1)*samples_per_bit]
            recovered_bits.append(1 if np.mean(segment) > 0 else 0)
        
        recovered_signal = np.resize(np.repeat(recovered_bits, samples_per_bit), t.shape)

        # 5. อัปเดตกราฟ
        ax1.clear()
        ax2.clear()
        ax3.clear()
        
        # กราฟบน: ข้อมูลต้นทาง
        ax1.step(t, digital_signal, where='post', color='blue', lw=2)
        ax1.set_title(f"1) Original Data: {data_string}", fontsize=10)
        ax1.set_ylim(-0.2, 1.2)
        
        # กราฟกลาง: สัญญาณที่มี Noise (สังเกตความหยักของคลื่น)
        ax2.plot(t, psk_rx, color='red', lw=0.8)
        ax2.set_title(f"2) Received PSK Signal (Noise Level: {noise_level:.2f})", fontsize=10)
        ax2.set_ylim(-3, 3) # ล็อกแกนไว้เพื่อให้เห็นความแรง Noise ชัดๆ
        
        # กราฟล่าง: ข้อมูลที่กู้คืนมาได้
        is_error = not np.array_equal(bits, recovered_bits)
        color_rec = 'green' if not is_error else 'orange'
        ax3.step(t, recovered_signal, where='post', color=color_rec, lw=2)
        ax3.set_title(f"3) Recovered Data (Error: {is_error})", fontsize=10, color=color_rec)
        ax3.set_ylim(-0.2, 1.2)

        for ax in [ax1, ax2, ax3]:
            ax.grid(True, alpha=0.2)
            for i in range(len(bits) + 1):
                ax.axvline(i * time_per_bit, color='gray', linestyle='--', alpha=0.3)
        
        plt.draw()
    except Exception as e:
        print(f"Error: {e}")

# --- วางโครงสร้าง GUI ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
plt.subplots_adjust(bottom=0.25, hspace=0.5)

# ช่องกรอกบิต
axbox = plt.axes([0.2, 0.12, 0.6, 0.05])
text_box = TextBox(axbox, 'Enter Bits: ', initial="101101")

# Slider ปรับ Noise
ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
slider_noise = Slider(ax_slider, 'Noise Level', 0.0, 10.0, valinit=0.2)

# เชื่อมต่อ Event
text_box.on_submit(lambda x: draw_system())
slider_noise.on_changed(draw_system)

draw_system()
plt.show()