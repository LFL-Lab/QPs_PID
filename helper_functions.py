import numpy as np
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *

def gauss(amplitude, mu, sigma, length):
    t = np.linspace(-length / 2, length / 2, length)
    gauss_wave = amplitude * np.exp(-((t - mu) ** 2) / (2 * sigma ** 2))
    return [float(x) for x in gauss_wave]

def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    N = 1 / ((1-g**2)*(2*c**2-1))
    return [float(N * x) for x in [(1-g)*c, (1+g)*s, (1-g)*s, (1+g)*c]]

def electrical_dalay(I, Q, f, TOF):
    I2 = declare(fixed)
    Q2 = declare(fixed)
    cos = declare(fixed)
    sin = declare(fixed)
    assign(cos, Math.cos2pi(((Cast.mul_fixed_by_int(2*np.pi*TOF*1e-9, f >> 8)) / (2 * np.pi)) << 8))
    assign(sin, Math.sin2pi(((Cast.mul_fixed_by_int(2*np.pi*TOF*1e-9, f >> 8)) / (2 * np.pi)) << 8))
    assign(I2, Q * cos - I * sin)
    assign(Q2, Q * sin + I * cos)
    return I2, Q2

