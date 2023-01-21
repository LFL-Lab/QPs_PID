from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config, rr_IF
import matplotlib.pyplot as plt
from qm import SimulationConfig

qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

target = 1.7e-5
gain_P = 0.2 # (0.5 * 250e3 / 4e-5)*2**-32

with program() as PID:

    I = declare(fixed)
    Q = declare(fixed)
    N = declare(int)
    f = declare(int, value=int(rr_IF)) # Hz
    a = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()
    error = declare(fixed)
    error_st = declare_stream()
    f_st = declare_stream()
    temp_fixed = declare(fixed)
    df = declare(int)
    temp_fixed_st = declare_stream()
    df_st = declare_stream()

    frame_rotation(np.pi/2, "rr")

    with for_(N, 0, N < 1000, N+1):

        measure("low_p_readout", "rr", None, dual_demod.full("Wc", "out1", "-Ws", "out2", I), dual_demod.full("Ws", "out1", "Wc", "out2", Q))

        # calculate the error
        assign(error, target-I)

        #PID
        assign(temp_fixed, gain_P * error)
        save(temp_fixed, temp_fixed_st)
        assign(df, Cast.unsafe_cast_int(temp_fixed)<<5)
        save(df, df_st)
        assign(f, f - df)
        update_frequency('rr', f)

        save(I, I_st)
        save(error, error_st)
        save(Q, Q_st)
        save(f, f_st)



    with stream_processing():

        I_st.save_all("I")
        Q_st.save_all("Q")
        error_st.save_all('e')
        f_st.save_all('f')
        temp_fixed_st.save_all('temp_fixed')
        df_st.save_all('df')


# job = qmm.simulate(config, PID, SimulationConfig(20000, include_analog_waveforms=True))
# sw = job.simulated_analog_waveforms()
# dt = sw['elements']['rr'][2]['timestamp'] - sw['elements']['rr'][0]['timestamp']
# print(dt)

dt = 2324
job = qm.execute(PID)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
I = res_hanldes.I.fetch_all()
Q = res_hanldes.Q.fetch_all()
e = res_hanldes.e.fetch_all()
f = res_hanldes.f.fetch_all()
temp_fixed = res_hanldes.temp_fixed.fetch_all()
df = res_hanldes.df.fetch_all()
t_vec = np.arange(0, dt*len(I), dt)
plt.plot(t_vec, I, '.')
plt.plot(t_vec, Q, '.')
plt.figure(); plt.hist2d(I['value'], Q['value'], bins=40); plt.title('I vs Q')
plt.figure(); plt.plot(t_vec, e, 'b*'); plt.plot(t_vec, target-I['value'], 'r.'); plt.title('error vs time')
plt.figure(); plt.plot(t_vec, temp_fixed, 'b*'); plt.plot(t_vec, e['value'] * gain_P, 'r.'); plt.title('temp fixed vs time')
plt.figure(); plt.plot(t_vec, df['value'], 'b*'); plt.plot(t_vec, temp_fixed['value']*2**(28+5), 'r.'); plt.title('temp int vs time')
plt.figure(); plt.plot(t_vec, f, '.'); plt.title('calulated f vs time')
