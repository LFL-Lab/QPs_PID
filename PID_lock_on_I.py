from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config, rr_IF
import matplotlib.pyplot as plt
from qm import SimulationConfig
from helper_functions import electrical_dalay

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

target = -1.32e-5
gain_P = 0.005 # (0.5 * 250e3 / 4e-5)*2**-32

with program() as PID:

    I = declare(fixed)
    Q = declare(fixed)
    N = declare(int)
    f = declare(int, value=int(rr_IF))
    a = declare(fixed)
    I2_st = declare_stream()
    Q2_st = declare_stream()
    error = declare(fixed)
    error_st = declare_stream()
    f_st = declare_stream()
    temp_fixed = declare(fixed)
    df = declare(int)
    temp_fixed_st = declare_stream()
    df_st = declare_stream()
    sign = declare(int)

    frame_rotation(np.pi * (-3.1/10), "rr")

    with for_(N, 0, N < 10000, N+1):

        measure("low_p_readout", "rr", None, dual_demod.full("Wc", "out1", "-Ws", "out2", I), dual_demod.full("Ws", "out1", "Wc", "out2", Q))
        I2, Q2 = electrical_dalay(I, Q, f, config['elements']['rr']['time_of_flight'])

        # calculate the error
        assign(error, target-I2)

        #PID
        assign(temp_fixed, gain_P * error)
        save(temp_fixed, temp_fixed_st)
        assign(df, Cast.unsafe_cast_int(temp_fixed)<<5)
        save(df, df_st)
        assign(sign, 2*Cast.to_int(Q2>0)-1)
        assign(f, f + sign * df)
        update_frequency('rr', f)

        save(I2, I2_st)
        save(error, error_st)
        save(Q2, Q2_st)
        save(f, f_st)

    with stream_processing():

        I2_st.save_all("I2")
        Q2_st.save_all("Q2")
        error_st.save_all('e')
        f_st.save_all('f')
        temp_fixed_st.save_all('temp_fixed')
        df_st.save_all('df')


# job = qmm.simulate(config, PID, SimulationConfig(20000, include_analog_waveforms=True))
# sw = job.simulated_analog_waveforms()
# dt = sw['elements']['rr'][2]['timestamp'] - sw['elements']['rr'][0]['timestamp']
# print(dt)
#
dt = 3080
job = qm.execute(PID)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
I2 = res_hanldes.I2.fetch_all()
Q2 = res_hanldes.Q2.fetch_all()
e = res_hanldes.e.fetch_all()
f = res_hanldes.f.fetch_all()
temp_fixed = res_hanldes.temp_fixed.fetch_all()
df = res_hanldes.df.fetch_all()
t_vec = np.arange(0, dt*len(I2), dt)
plt.plot(t_vec, I2, '.', label='I2');
plt.plot(t_vec, Q2, '.', label='Q2'); plt.legend()
plt.figure(); plt.hist2d(I2['value'], Q2['value'], bins=40); plt.title('I vs Q')
plt.figure(); plt.plot(t_vec, e, 'b*'); plt.plot(t_vec, target-I2['value'], 'r.'); plt.title('error vs time')
# plt.figure(); plt.plot(t_vec, temp_fixed, 'b*'); plt.plot(t_vec, e['value'] * gain_P, 'r.'); plt.title('temp fixed vs time')
plt.figure(); plt.plot(t_vec, df['value'], 'b-'); plt.plot(t_vec, temp_fixed['value']*2**(28+5), 'r.'); plt.title('df vs time')
plt.figure(); plt.plot(t_vec, f, '.'); plt.title('calulated f vs time')
