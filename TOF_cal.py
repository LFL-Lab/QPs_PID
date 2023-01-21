from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config
import matplotlib.pyplot as plt
from qm import SimulationConfig

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

with program() as tof_cal:

    N = declare(int)
    adc_st = declare_stream(adc_trace=True)

    update_frequency("rr", 51099876)
    with for_(N, 0, N < 500, N+1):
        wait(2001, "rr")
        reset_phase("rr")
        measure("readout", "rr", adc_st)

    with stream_processing():

        adc_st.input1().average().save('A')
        adc_st.input2().average().save('B')

job = qm.execute(tof_cal)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
adc_I = res_hanldes.A.fetch_all()
adc_Q = res_hanldes.B.fetch_all()
plt.plot(adc_I)
plt.plot(adc_Q)