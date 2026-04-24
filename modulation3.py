import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider

# --- 1. การตั้งค่าเบื้องต้น ---
fs = 2000 # เพิ่ม Sample rate เพื่อให้รองรับความถี่สูงขึ้นได้สวยงาม
bit_duration = 0.2
initial_fc = 40
initial_fc0, initial_fc1 = 20, 80

fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
plt.subplots_adjust(bottom=0.25, hspace=0.5) # เผื่อพื้นที่ด้านล่างสำหรับ Slider

def plot_modulation(val=None):
    text = text_box.text
    fc = slider_fc.val
    
    # คำนวณความถี่ FSK ตามสัดส่วนของ fc (หรือจะล็อกค่าไว้ก็ได้ครับ)
    fc0_fsk = fc * 0.5
    fc1_fsk = fc * 1.5
    
    bits_list = [int(b) for b in text if b in '01']
    if not bits_list: return
    bits = np.array(bits_list)

    samples_per_bit = int(fs * bit_duration)
    num_bits = len(bits)
    t = np.linspace(0, num_bits * bit_duration, num_bits * samples_per_bit, endpoint=False)
    
    for ax in axs: 
        ax.clear()
        ax.grid(True, alpha=0.3)

    digital_signal = np.repeat(bits, samples_per_bit)
    
    # 1) ASK
    ask_signal = digital_signal * np.sin(2 * np.pi * fc * t)
    
    # 2) FSK
    fsk_signal = np.zeros(len(t))
    for i, bit in enumerate(bits):
        start, end = i*samples_per_bit, (i+1)*samples_per_bit
        f_fsk = fc1_fsk if bit==1 else fc0_fsk
        fsk_signal[start:end] = np.sin(2 * np.pi * f_fsk * t[start:end])
        
    # 3) PSK
    psk_signal = np.zeros(len(t))
    for i, bit in enumerate(bits):
        start, end = i*samples_per_bit, (i+1)*samples_per_bit
        phase = 0 if bit==1 else np.pi
        psk_signal[start:end] = np.sin(2 * np.pi * fc * t[start:end] + phase)

    # --- วาดกราฟ ---
    t_step = np.arange(num_bits + 1) * bit_duration
    bits_step = np.append(bits, bits[-1])
    axs[0].step(t_step, bits_step, where='post', color='black', lw=2)
    axs[0].set_title(f"Input Data: {''.join(map(str, bits))}", fontweight='bold')
    
    axs[1].plot(t, ask_signal, color='blue')
    axs[1].set_title(f"ASK (Carrier: {fc:.1f} Hz)")
    
    axs[2].plot(t, fsk_signal, color='green')
    axs[2].set_title(f"FSK (f0:{fc0_fsk:.1f}Hz, f1:{fc1_fsk:.1f}Hz)")
    
    axs[3].plot(t, psk_signal, color='red')
    axs[3].set_title(f"PSK (Phase Shift 180°)")

    for ax in axs:
        for i in range(num_bits + 1):
            ax.axvline(i * bit_duration, color='gray', linestyle='--', alpha=0.3)

    fig.canvas.draw_idle()

# --- 2. ส่วนควบคุม (UI) ---
# ช่องใส่บิต
ax_box = plt.axes([0.2, 0.08, 0.6, 0.04])
text_box = TextBox(ax_box, 'Enter Bits: ', initial='10110')

# Slider ปรับความถี่ Carrier
ax_slider = plt.axes([0.2, 0.02, 0.6, 0.03])
slider_fc = Slider(ax_slider, 'Carrier Freq (Hz)', 10, 200, valinit=initial_fc)

# เชื่อมต่อ Event
text_box.on_submit(lambda x: plot_modulation())
slider_fc.on_changed(plot_modulation)

plot_modulation()
plt.show()