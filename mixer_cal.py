from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config
import matplotlib.pyplot as plt
from qm import SimulationConfig

def IQ_imbalance(g, phi):
    c = np.cos(phi)
    s = np.sin(phi)
    N = 1 / ((1-g**2)*(2*c**2-1))
    return [float(N * x) for x in [(1-g)*c, (1+g)*s, (1-g)*s, (1+g)*c]]

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

with program() as mixer_cal:

    update_frequency("rr", -300e6)

    with infinite_loop_():

        play("const"*amp(0.3), "rr")

job = qm.execute(mixer_cal)