import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_script(script_name):
    try:
        # 1. หาตำแหน่งที่ตั้งของไฟล์ main.py นี้แบบ Absolute Path
        # เพื่อใช้เป็นฐานในการหาไฟล์ .py อื่นๆ ในโฟลเดอร์เดียวกัน
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, script_name)
        
        # 2. ตรวจสอบว่ามีไฟล์อยู่จริงไหมก่อนสั่งรัน
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"ไม่พบไฟล์: {script_name}\nกรุณาตรวจสอบการตั้งชื่อไฟล์ในโฟลเดอร์ครับ")
            return

        # 3. สั่งรันโดยใช้ sys.executable เพื่อดึง Python จาก venv2 มาใช้
        # และกำหนด cwd (Current Working Directory) ให้เป็นโฟลเดอร์ของโปรเจกต์
        subprocess.Popen([sys.executable, script_path], cwd=base_dir)
        
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการรัน {script_name}: {e}")

# --- สร้างหน้าต่างหลัก ---
root = tk.Tk()
root.title("Digital Communication Simulation - Ajarn Sakda")
root.geometry("450x650")

# หัวข้อโปรแกรม
tk.Label(root, text="การจำลองระบบสื่อสารดิจิทัล", font=("Arial", 16, "bold")).pack(pady=20)
tk.Label(root, text="แผนกวิชาเทคโนโลยีอิเล็กทรอนิกส์", font=("Arial", 10)).pack()

# เฟรมสำหรับจัดกลุ่มปุ่ม
frame = tk.Frame(root)
frame.pack(pady=10)

# รายชื่อโมดูล (ตรวจสอบชื่อไฟล์ให้ตรงกับที่ปรากฏใน Explorer ของอาจารย์)
modules = [
    ("1. Sampling & Aliasing", "samplintrate.py"),
    ("2. Bitrate Change", "ิิbitratechange.py"),      # แก้ไขชื่อไฟล์ที่มีสระอิเกิน
    ("3. Bitrate MP3 Comparison", "bitratemp3_2.py"),
    ("4. MODULATION", "modulation3.py"), 
    ("5. ASK Modulation", "askmod.py"), 
    ("6. FSK Modulation", "fskmod.py"),
    ("7. PSK Mod/Demod (Noise)", "pskcodec.py"),
    ("8. Line Coding (Unipolar/Polar)", "linecode4.py"),
    ("9. PCM & Quantization", "quantizedsim1.py"),
    ("10. WiFi RSSI Analyzer", "RSSImap_v3.py"),
    ("11. WiFi RSSI Simulation", "RSSImap_dual.py")
]

# สร้างปุ่มแบบวนลูป
for text, file in modules:
    btn = tk.Button(frame, text=text, width=35, height=2, bg="#f0f0f0",
                    command=lambda f=file: run_script(f))
    btn.pack(pady=4)

# ส่วนท้าย
tk.Label(root, text="วิทยาลัยเทคนิคหาดใหญ่", fg="gray").pack(side="bottom", pady=15)

# เริ่มต้นทำงาน
root.mainloop()