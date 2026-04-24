import numpy as np

# =========================
# OFDM Transmitter
# =========================
def ofdm_tx(symbols):
    """
    symbols: complex symbols (QAM)
    """
    return np.fft.ifft(symbols)


# =========================
# OFDM Receiver
# =========================
def ofdm_rx(signal):
    return np.fft.fft(signal)


# =========================
# QAM Mapping (simple)
# =========================
def generate_symbols(N):
    """
    สร้าง random QPSK
    """
    bits = np.random.randint(0, 2, (N, 2))

    symbols = (2*bits[:,0]-1) + 1j*(2*bits[:,1]-1)
    return symbols


# =========================
# Add Noise
# =========================
def add_noise(signal, noise_level=0.1):
    noise = (np.random.randn(len(signal)) + 1j*np.random.randn(len(signal))) * noise_level
    return signal + noise