import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

# --- 1. การตั้งค่าเบื้องต้น ---
fs = 1000                          
bit_duration = 0.2                 
fc = 40                            # Carrier Frequency
fc0, fc1 = 20, 80                  # Frequencies for FSK

# สร้าง Figure และ Axes
fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
plt.subplots_adjust(bottom=0.15, hspace=0.5)

def plot_modulation(text):
    # กรองเอาเฉพาะเลข 0 และ 1
    bits_list = [int(b) for b in text if b in '01']
    if not bits_list: return
    bits = np.array(bits_list)

    samples_per_bit = int(fs * bit_duration)
    num_bits = len(bits)
    # สร้างแกนเวลาให้พอดีกับจำนวนบิตที่พิมพ์
    t = np.linspace(0, num_bits * bit_duration, num_bits * samples_per_bit, endpoint=False)
    
    # เคลียร์กราฟเก่าก่อนวาดใหม่
    for ax in axs: 
        ax.clear()
        ax.grid(True, alpha=0.3)

    # --- คำนวณสัญญาณ ---
    # สร้างสัญญาณ Digital (Square Wave)
    digital_signal = np.repeat(bits, samples_per_bit)
    
    # ASK
    carrier = np.sin(2 * np.pi * fc * t)
    ask_signal = digital_signal * carrier
    
    # FSK
    fsk_signal = np.zeros(len(t))
    for i, bit in enumerate(bits):
        start, end = i*samples_per_bit, (i+1)*samples_per_bit
        f_val = fc1 if bit==1 else fc0
        fsk_signal[start:end] = np.sin(2 * np.pi * f_val * t[start:end])
        
    # PSK
    psk_signal = np.zeros(len(t))
    for i, bit in enumerate(bits):
        start, end = i*samples_per_bit, (i+1)*samples_per_bit
        phase = 0 if bit==1 else np.pi
        psk_signal[start:end] = np.sin(2 * np.pi * fc * t[start:end] + phase)

    # --- วาดกราฟ ---
    # 0) Input Data (Step plot)
    t_step = np.arange(num_bits + 1) * bit_duration
    bits_step = np.append(bits, bits[-1])
    axs[0].step(t_step, bits_step, where='post', color='black', lw=2)
    axs[0].set_title(f"Input Data: {''.join(map(str, bits))}", fontweight='bold', color='black')
    axs[0].set_ylim(-0.2, 1.2)
    
    # 1) ASK
    axs[1].plot(t, ask_signal, color='blue')
    axs[1].set_title(f"ASK (Amplitude Shift Keying) - Carrier: {fc}Hz", color='blue')
    
    # 2) FSK
    axs[2].plot(t, fsk_signal, color='green')
    axs[2].set_title(f"FSK (Frequency Shift Keying) | 0:{fc0}Hz, 1:{fc1}Hz", color='green')
    
    # 3) PSK
    axs[3].plot(t, psk_signal, color='red')
    axs[3].set_title(f"PSK (Phase Shift Keying) | 0:180°, 1:0°", color='red')
    axs[3].set_xlabel("Time (s)")

    # เพิ่มเส้นประแบ่งช่วงบิตในทุกกราฟ
    for ax in axs:
        for i in range(num_bits + 1):
            ax.axvline(i * bit_duration, color='gray', linestyle='--', alpha=0.3)

    # คำสั่งสำคัญเพื่อให้ GUI อัปเดตรูป
    fig.canvas.draw_idle()

# --- 2. สร้างช่องใส่ข้อมูล (TextBox) ---
ax_box = plt.axes([0.2, 0.03, 0.6, 0.05])
text_box = TextBox(ax_box, 'Enter Bits: ', initial='10110')
text_box.on_submit(plot_modulation)

# รันครั้งแรก
plot_modulation('10110')

print("รันโปรแกรมสำเร็จ! อาจารย์ลองเปลี่ยนเลขในช่อง Enter Bits แล้วกด Enter ดูครับ")
plt.show()