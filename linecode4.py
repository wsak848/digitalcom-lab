import numpy as np
import matplotlib.pyplot as plt

# --- 1. ข้อมูลบิตตัวอย่าง (คุณสามารถเปลี่ยนเลขในนี้เพื่อโชว์เคสต่างๆ ได้) ---
bits = np.array([1, 0, 1, 1, 0, 0, 1, 1])
t = np.arange(len(bits))

# --- 2. คำนวณรูปแบบ Line Coding ต่างๆ ---

# Unipolar NRZ: 1 -> V, 0 -> 0
unipolar_nrz = bits

# Polar NRZ: 1 -> V, 0 -> -V
polar_nrz = np.where(bits == 1, 1, -1)

# Bipolar AMI: 0 -> 0, 1 -> สลับบวก/ลบ
bipolar_ami = np.zeros(len(bits))
last_one = -1
for i in range(len(bits)):
    if bits[i] == 1:
        last_one *= -1
        bipolar_ami[i] = last_one

# Manchester: 0 -> High to Low, 1 -> Low to High
# (สร้างข้อมูลละเอียดขึ้นเพื่อให้เห็นจุดเปลี่ยนกลางคาบ)
t_manchester = np.linspace(0, len(bits), len(bits) * 200)
manchester = []
for bit in bits:
    if bit == 1:
        # Low then High
        manchester.extend([-1] * 100 + [1] * 100)
    else:
        # High then Low
        manchester.extend([1] * 100 + [-1] * 100)

# --- 3. การสร้างกราฟ ---
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
plt.subplots_adjust(hspace=0.6)

# ฟังก์ชันช่วยวาดกราฟแบบ Step
def plot_step(ax, data, title, color, ylim=(-1.5, 1.5)):
    ax.step(np.arange(len(data)), data, where='post', color=color, linewidth=2)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylim(ylim)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='black', linewidth=0.8)
    # แสดงเลขบิตกำกับด้านบน
    for i, bit in enumerate(bits):
        ax.text(i + 0.5, ylim[1]-0.3, str(bit), ha='center', fontsize=10, color='blue')

# วาดแต่ละแบบ
plot_step(axs[0], unipolar_nrz, "1. Unipolar NRZ (1=V, 0=0V)", "green", (-0.5, 1.5))
plot_step(axs[1], polar_nrz, "2. Polar NRZ (1=+V, 0=-V)", "orange")
plot_step(axs[2], bipolar_ami, "3. Bipolar AMI (1=Alt +/- , 0=0V)", "red")

# สำหรับ Manchester ต้องใช้ plot ธรรมดาเพราะมีความละเอียดสูงกว่า
axs[3].plot(t_manchester, manchester, color='purple', linewidth=2)
axs[3].set_title("4. Manchester (0=H to L, 1=L to H)", fontsize=12, fontweight='bold')
axs[3].set_ylim(-1.5, 1.5)
axs[3].grid(True, alpha=0.3)
axs[3].axhline(0, color='black', linewidth=0.8)
for i, bit in enumerate(bits):
    axs[3].text(i + 0.5, 1.2, str(bit), ha='center', fontsize=10, color='blue')

plt.xlabel("Bit Intervals", fontsize=10)
print(f"แสดงกราฟสำหรับบิตชุดนี้: {bits.tolist()}")
plt.show()