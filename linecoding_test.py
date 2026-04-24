import matplotlib.pyplot as plt
import numpy as np

def run():
    bits = np.random.randint(0, 2, 20)
    signal = np.repeat(bits, 10)

    t = np.arange(len(signal))

    fig, ax = plt.subplots()
    ax.step(t, signal, where='post')
    ax.set_title("Line Coding (NRZ)")
    ax.set_ylim(-0.5, 1.5)

    return fig
