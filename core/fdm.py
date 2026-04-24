import numpy as np

# =========================
# Generate baseband signals
# =========================
def generate_signals(freqs, t):
    signals = []
    for f in freqs:
        signals.append(np.sin(2*np.pi*f*t))
    return np.array(signals)


# =========================
# FDM Modulation
# =========================
def fdm_modulate(signals, carriers, t):
    """
    signals: baseband signals
    carriers: carrier frequencies
    """
    modulated = []

    for sig, fc in zip(signals, carriers):
        carrier = np.cos(2*np.pi*fc*t)
        modulated.append(sig * carrier)

    return np.array(modulated)


# =========================
# Combine signals
# =========================
def fdm_combine(modulated_signals):
    return np.sum(modulated_signals, axis=0)


# =========================
# Demodulate (simple)
# =========================
def fdm_demodulate(combined, carriers, t):
    recovered = []

    for fc in carriers:
        carrier = np.cos(2*np.pi*fc*t)
        recovered_signal = combined * carrier
        recovered.append(recovered_signal)

    return np.array(recovered)