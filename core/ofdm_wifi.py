import numpy as np

# =========================
# Parameters (WiFi-like)
# =========================
N_FFT = 64
CP_LEN = 16

# Subcarrier allocation (802.11a-like)
DATA_IDXS = np.array([
    -26,-25,-24,-23,-22,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,
    -6,-5,-4,-3,-2,-1,
     1,2,3,4,5,6,
     8,9,10,11,12,13,14,15,16,17,18,19,20,
     22,23,24,25,26
])
PILOT_IDXS = np.array([-21,-7,7,21])

def idx_to_bin(idxs):
    return (idxs % N_FFT).astype(int)

DATA_BINS  = idx_to_bin(DATA_IDXS)
PILOT_BINS = idx_to_bin(PILOT_IDXS)

# =========================
# QPSK
# =========================
def bits_to_qpsk(bits):
    bits = bits.reshape(-1, 2)
    return (2*bits[:,0]-1) + 1j*(2*bits[:,1]-1)

def qpsk_to_bits(symbols):
    b0 = (np.real(symbols) > 0).astype(int)
    b1 = (np.imag(symbols) > 0).astype(int)
    return np.vstack([b0, b1]).T.reshape(-1)

# =========================
# TX
# =========================
def wifi_ofdm_tx(n_sym=1):
    """Return tx_signal, payload_bits, freq_symbols (per symbol)"""
    n_data = len(DATA_BINS)
    payload_bits = np.random.randint(0, 2, size=(n_sym, n_data*2))
    freq_syms = []

    tx_time = []

    for s in range(n_sym):
        X = np.zeros(N_FFT, dtype=complex)

        data_sym = bits_to_qpsk(payload_bits[s])
        X[DATA_BINS] = data_sym

        # pilots (BPSK fixed pattern)
        X[PILOT_BINS] = np.array([1, 1, 1, -1], dtype=complex)

        # IFFT
        x = np.fft.ifft(np.fft.ifftshift(X))

        # CP
        x_cp = np.concatenate([x[-CP_LEN:], x])
        tx_time.append(x_cp)
        freq_syms.append(X)

    return np.concatenate(tx_time), payload_bits, np.array(freq_syms)

# =========================
# Channel: multipath + AWGN
# =========================
def apply_channel(x, snr_db=20, taps=None):
    if taps is None:
        # simple 3-tap multipath
        taps = np.array([1.0, 0.5*np.exp(1j*0.5), 0.3*np.exp(1j*1.0)])

    y = np.convolve(x, taps, mode="same")

    # AWGN
    sig_power = np.mean(np.abs(y)**2)
    noise_power = sig_power / (10**(snr_db/10))
    noise = (np.random.randn(*y.shape) + 1j*np.random.randn(*y.shape)) * np.sqrt(noise_power/2)
    return y + noise, taps

# =========================
# RX (one symbol)
# =========================
def wifi_ofdm_rx(y, n_sym=1, eq=True):
    sym_len = N_FFT + CP_LEN
    rx_bits = []
    rec_const = []

    # simple channel estimate using pilots (per symbol, flat approx per bin)
    H_est = np.ones(N_FFT, dtype=complex)

    for s in range(n_sym):
        seg = y[s*sym_len:(s+1)*sym_len]

        # remove CP
        seg = seg[CP_LEN:]

        # FFT
        Y = np.fft.fftshift(np.fft.fft(seg))

        # crude LS channel estimate on pilots
        pilots_rx = Y[PILOT_BINS]
        pilots_tx = np.array([1,1,1,-1], dtype=complex)
        H_est_p = pilots_rx / pilots_tx

        # interpolate (very simple: fill all bins with mean)
        H_est[:] = np.mean(H_est_p)

        # equalize
        if eq:
            Y_eq = Y / (H_est + 1e-12)
        else:
            Y_eq = Y

        # take data bins
        data_eq = Y_eq[DATA_BINS]
        rec_const.append(data_eq)

        bits = qpsk_to_bits(data_eq)
        rx_bits.append(bits)

    return np.concatenate(rx_bits), np.array(rec_const), H_est

# =========================
# Spectrum
# =========================
def spectrum(x):
    X = np.fft.fft(x)
    f = np.fft.fftfreq(len(x))
    m = f >= 0
    return f[m], np.abs(X[m]) / len(x)