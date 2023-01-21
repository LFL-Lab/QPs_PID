from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config
import matplotlib.pyplot as plt
from qm import SimulationConfig

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

f_min = 48e6; f_max = 52e6; df = 0.02e6; f_vec = np.arange(f_min, f_max, df)
a_min = 0.01; a_max = 1.0; da = 0.05; a_vec = np.arange(a_min, a_max + da/2, da)

with program() as rr_spec_power:

    I = declare(fixed)
    Q = declare(fixed)
    N = declare(int)
    f = declare(int) # Hz
    a = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(N, 0, N < 100, N+1):
        with for_(f, f_min, f<f_max, f+df):
            with for_(a, a_min, a< a_max + da/2, a+da):
                wait(2000, "rr")
                update_frequency("rr", f)
                measure("readout"*amp(a), "rr", None, dual_demod.full("Wc", "out1", "-Ws", "out2", I), dual_demod.full("Ws", "out1", "Wc", "out2", Q))
                save(I, I_st)
                save(Q, Q_st)

    with stream_processing():

        I_st.buffer(len(f_vec), len(a_vec)).average().save("I")
        Q_st.buffer(len(f_vec), len(a_vec)).average().save("Q")

job = qm.execute(rr_spec_power)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
I = res_hanldes.I.fetch_all()
Q = res_hanldes.Q.fetch_all()
s = I + 1j*Q
plt.pcolor(np.abs(s).T)
plt.figure(); plt.plot(np.abs(s)[0])

