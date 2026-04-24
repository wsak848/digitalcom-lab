import matplotlib.pyplot as plt
import numpy as np

def run():
    t = np.linspace(0, 1, 500)
    signal = np.sin(2*np.pi*5*t)

    noise = np.random.normal(0, 0.3, len(t))
    noisy = signal + noise

    fig, ax = plt.subplots()
    ax.plot(t, signal, label="Signal")
    ax.plot(t, noisy, label="Noisy")
    ax.set_title("SNR Demo")
    ax.legend()

    return fig
