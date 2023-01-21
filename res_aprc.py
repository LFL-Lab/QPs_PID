from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
import numpy as np
from configuration import config
import matplotlib.pyplot as plt
from qm import SimulationConfig
from helper_functions import electrical_dalay


qmm = QuantumMachinesManager()

qm = qmm.open_qm(config)

f_min = int(45e6); f_max = int(55.0e6); df = int(0.1e6); f_vec = np.arange(f_min, f_max, df)

with program() as rr_spec:

    I = declare(fixed)
    Q = declare(fixed)
    N = declare(int)
    f = declare(int) # Hz
    # phi = declare(int)

    # phi_st = declare_stream()

    I_st = declare_stream()
    Q_st = declare_stream()
    I2_st = declare_stream()
    Q2_st = declare_stream()
    # frame_rotation_2pi(0.1, "rr")

    with for_(N, 0, N < 3000, N+1):

        with for_(f, f_min, f<f_max, f+df):

            # wait(2000, 'rr')
            update_frequency("rr", f)
            measure("readout", "rr", None, dual_demod.full("Wc", "out1", "-Ws", "out2", I), dual_demod.full("Ws", "out1", "Wc", "out2", Q))
            save(I, I_st)
            save(Q, Q_st)
            # with if_(N==0):
                # assign(phi, 257470 + Cast.mul_int_by_fixed(f, 60947e-9))
                # save(phi, phi_st)
                # assign(cos, Math.cos2pi(Cast.unsafe_cast_fixed((257470 + Cast.mul_int_by_fixed(f, 60947e-9)))<<4)/np.pi)
                # assign(cos, Math.cos2pi(Cast.unsafe_cast_fixed((Cast.mul_int_by_fixed(f, 60947e-9))))/np.pi)

            I2, Q2 = electrical_dalay(I, Q, f, config['elements']['rr']['time_of_flight'])
            save(I2, I2_st)
            save(Q2, Q2_st)
            # save(cos, cos_st)

    with stream_processing():

        I_st.buffer(len(f_vec)).average().save("I")
        I2_st.buffer(len(f_vec)).average().save("I2")
        Q_st.buffer(len(f_vec)).average().save("Q")
        Q2_st.buffer(len(f_vec)).average().save("Q2")
        # phi_st.buffer(len(f_vec)).save_all("phi")
        # cos_st.buffer(len(f_vec)).save_all("cos")


job = qm.execute(rr_spec)
res_hanldes = job.result_handles
res_hanldes.wait_for_all_values()
I = res_hanldes.I.fetch_all()
I2 = res_hanldes.I2.fetch_all()
Q = res_hanldes.Q.fetch_all()
Q2 = res_hanldes.Q2.fetch_all()
# cos = res_hanldes.cos.fetch_all()['value'][0]
# phi = res_hanldes.phi.fetch_all()['value'][0]
s = Q + 1j*I
s2 = s*np.exp(+2j*np.pi*(f_vec)*config['elements']['rr']['time_of_flight']*1e-9)
# phi_ = 2*np.pi*(4.2245e9+f_vec)*9700e-9
I2_ = s2.real
Q2_ = s2.imag
# plt.plot(f_vec, np.unwrap(np.angle(s2)));
plt.figure(); plt.plot(f_vec,np.unwrap(np.angle(s)), '.'); plt.plot(f_vec,np.unwrap(np.angle(s2)), '.'); plt.title('I vs Q angle (b) ; I2 vs Q2 angle python')
plt.figure(); plt.plot(I2_, Q2_); plt.axis('equal'); plt.title('python I2 vs Q2')
plt.figure(); plt.plot(I2, Q2); plt.axis('equal'); plt.title('qua I2 vs Q2'); plt.grid()
# plt.figure()
# plt.plot(f_vec, np.abs(s2));

# plt.figure(); plt.plot(f_vec, phi, 'r*'); plt.plot(f_vec, phi_, 'b.')
# plt.figure(); plt.plot(f_vec, cos, 'r*'); plt.plot(f_vec, phi_*2**-24/np.pi, 'b.')
# plt.figure(); plt.plot(f_vec, cos, 'r-'); plt.plot(f_vec, np.cos(phi_), 'b-')
