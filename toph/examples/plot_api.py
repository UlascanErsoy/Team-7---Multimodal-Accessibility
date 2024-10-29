"""This is just a mock API designed to
mimick popular plotting apis
(think plotly.js, charts.js
"""

import numpy as np

import toph.plots as plt

if __name__ == "__main__":

    x = np.array([1, 2, 4, 8])
    y = np.array([10, 40, 20, 80])

    plt.bar(x, y)
