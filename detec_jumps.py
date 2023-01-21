from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config, rr_IF
import matplotlib.pyplot as plt
from qm import SimulationConfig
from helper_functions import electrical_dalay

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

with program() as detect_jumps:

    I = declare(fixed)
    Q = declare(fixed)
    N = declare(int)
    f = declare(int, value=int(rr_IF)) # Hz
    a = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()
    I2_st = declare_stream()
    Q2_st = declare_stream()
    cos = declare(fixed)
    sin = declare(fixed)

    # frame_rotation(np.pi * (-3.3/10), "rr")

    with for_(N, 0, N < 100000, N+1):

        wait(5000, 'rr')
        measure("low_p_readout", "rr", None, dual_demod.full("Wc", "out1", "-Ws", "out2", I), dual_demod.full("Ws", "out1", "Wc", "out2", Q))
        I2, Q2 = electrical_dalay(I, Q, f, config['elements']['rr']['time_of_flight'])
        save(I2, I2_st)
        save(Q2, Q2_st)

    with stream_processing():

        I2_st.save_all("I2")
        Q2_st.save_all("Q2")


# job = qmm.simulate(config, detect_jumps, SimulationConfig(20000, include_analog_waveforms=True))
# sw = job.simulated_analog_waveforms()
# dt = sw['elements']['rr'][2]['timestamp'] - sw['elements']['rr'][0]['timestamp']
# print(dt)
dt = 2792
job = qm.execute(detect_jumps)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
I2 = res_hanldes.I2.fetch_all()['value']
Q2 = res_hanldes.Q2.fetch_all()['value']
t_vec = np.arange(0, dt*len(I2), dt)
plt.plot(t_vec, I2, '-')
# plt.plot(t_vec, Q2, '.')
plt.figure(); plt.hist2d(I2, Q2, 40)


