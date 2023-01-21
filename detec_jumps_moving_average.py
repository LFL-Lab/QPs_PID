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
    v1 = declare(fixed, size=100)
    v2 = declare(fixed, size=100)
    v3 = declare(fixed, size=100)
    v4 = declare(fixed, size=100)
    idx = declare(int)
    Is = declare(fixed)
    Qs = declare(fixed)
    Is_st = declare_stream()
    Qs_st = declare_stream()

    # frame_rotation(np.pi * (-3.3/10), "rr")

    measure("low_p_readout", "rr", None, demod.sliced("Wc", v1, 500, "out1"),
            demod.sliced("-Ws", v2, 500, "out2"),
            demod.sliced("Ws", v3, 500, "out1"),
            demod.sliced("Wc", v4, 500, "out2"))

    with for_(idx, 0, idx<v1.length(), idx+1):
        assign(Is, v1[idx] + v2[idx])
        assign(Qs, v3[idx] + v4[idx])
        I2, Q2 = electrical_dalay(Is, Qs, f, config['elements']['rr']['time_of_flight'])
        save(I2, Is_st)
        save(Q2, Qs_st)

    with stream_processing():

        Is_st.save_all("I2")
        Qs_st.save_all("Q2")



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


