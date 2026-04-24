import numpy as np

# ======================================
# Generate Signals
# ======================================
def generate_signals(freqs, t, amplitudes=None):
    """
    สร้างสัญญาณ sinusoid หลายตัว

    freqs: list ความถี่
    t: time array
    amplitudes: list amplitude (optional)

    return: array shape (num_signals, len(t))
    """
    signals = []

    if amplitudes is None:
        amplitudes = [1] * len(freqs)

    for f, a in zip(freqs, amplitudes):
        signals.append(a * np.sin(2 * np.pi * f * t))

    return np.array(signals)


# ======================================
# TDM Multiplexing
# ======================================
def tdm_mux(signals):
    """
    รวมสัญญาณแบบ TDM (interleave sample)

    signals: shape (num_signals, num_samples)

    return: 1D array (mux signal)
    """
    num_signals, num_samples = signals.shape

    mux = np.zeros(num_signals * num_samples)

    idx = 0
    for i in range(num_samples):
        for ch in range(num_signals):
            mux[idx] = signals[ch, i]
            idx += 1

    return mux


# ======================================
# TDM Demultiplexing
# ======================================
def tdm_demux(mux_signal, num_signals):
    """
    แยกสัญญาณ TDM กลับ

    mux_signal: 1D array
    num_signals: จำนวนช่อง

    return: list ของ signals
    """
    demux = [[] for _ in range(num_signals)]

    for i, val in enumerate(mux_signal):
        ch = i % num_signals
        demux[ch].append(val)

    return [np.array(sig) for sig in demux]


# ======================================
# Slot Index (สำหรับ animation/debug)
# ======================================
def get_slot_indices(num_signals, num_samples):
    """
    บอกว่า sample แต่ละจุดมาจาก channel ไหน

    return: array เช่น [0,1,2,0,1,2,...]
    """
    slots = []

    for i in range(num_samples):
        for ch in range(num_signals):
            slots.append(ch)

    return np.array(slots)


# ======================================
# Optional: Add Noise
# ======================================
def add_noise(signal, noise_level=0.1):
    """
    เพิ่ม noise ลงในสัญญาณ
    """
    noise = np.random.normal(0, noise_level, size=len(signal))
    return signal + noise