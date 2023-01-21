from helper_functions import gauss, IQ_imbalance

# readout params:
long_redout_len = 3600; readout_len = 200000; rr_IF = 50e6; rr_LO = 4.755e9  # 2000

# qubit params:
qubit_LO = 6.345e9; qubit_IF = 100e6

config = {

    'version': 1,

    'controllers': {
        'con1': {
            'type': 'opx1',
            'analog_outputs': {
                1: {'offset': 0.0},  # qubit I
                2: {'offset': 0.0},  # qubit Q
                3: {'offset': -0.006},  # RR I
                4: {'offset': 0.0102},  # RR Q
            },
            'digital_outputs': {},
            'analog_inputs': {
                1: {'offset': 0.00927734375},
                2: {'offset': 0.013916015625}
            }
        }
    },

    'elements': {

        'qubit': {
            'mixInputs': {
                'I': ('con1', 1),
                'Q': ('con1', 2),
                'lo_frequency': qubit_LO, # 6MHz
                'mixer': 'mixer_qubit'
            },
            'intermediate_frequency': qubit_IF, # 50MHz
            'operations': {
                'const': 'const',
                'saturation': 'saturation_pulse',
                'gaussian': 'gaussian_pulse',
                'pi': 'pi_pulse',
                'pi2': 'pi2_pulse',
                'minus_pi2': 'minus_pi2_pulse',
            }
        },

        'rr': {
            'mixInputs': {
                'I': ('con1', 3),
                'Q': ('con1', 4),
                'lo_frequency': rr_LO,
                'mixer': 'mixer_RR'
            },
            'intermediate_frequency': rr_IF,
            'operations': {
                'const': 'const',
                'long_readout': 'long_readout_pulse',
                'readout': 'readout_pulse',
                'low_p_readout': 'low_p_readout_pulse'
            },
            "outputs": {
                'out1': ('con1', 1),
                'out2': ('con1', 2),
            },
            'time_of_flight': 252,
            'smearing': 0
        },
    },

    "pulses": {

        "const": {
            'operation': 'control',
            'length': 100,
            'waveforms': {
                'I': 'const_wf',
                'Q': 'zero_wf'
            }
        },

        "saturation_pulse": {
            'operation': 'control',
            'length': 20000,  # several T1s
            'waveforms': {
                'I': 'saturation_wf',
                'Q': 'zero_wf'
            }
        },

        "gaussian_pulse": {
            'operation': 'control',
            'length': 60,
            'waveforms': {
                'I': 'gauss_wf',
                'Q': 'zero_wf'
            }
        },

        'pi_pulse': {
            'operation': 'control',
            'length': 60,
            'waveforms': {
                'I': 'pi_wf',
                'Q': 'zero_wf'
            }
        },

        'pi2_pulse': {
            'operation': 'control',
            'length': 60,
            'waveforms': {
                'I': 'pi2_wf',
                'Q': 'zero_wf'
            }
        },

        'minus_pi2_pulse': {
            'operation': 'control',
            'length': 60,
            'waveforms': {
                'I': 'minus_pi2_wf',
                'Q': 'zero_wf'
            }
        },

        'long_readout_pulse': {
            'operation': 'measurement',
            'length': long_redout_len,
            'waveforms': {
                'I': 'long_readout_wf',
                'Q': 'zero_wf'
            },
            'integration_weights': {
                'long_integW1': 'long_integW1',
                'long_integW2': 'long_integW2',
            },
            'digital_marker': 'ON'
        },

        'readout_pulse': {
            'operation': 'measurement',
            'length': readout_len,
            'waveforms': {
                'I': 'readout_wf',
                'Q': 'zero_wf'
            },
            'integration_weights': {
                'Wc': 'Wc',
                'Ws': 'Ws',
                '-Ws': '-Ws',
                'optW1': 'optW1',
                'optW2': 'optW2'
            },
            'digital_marker': 'ON'
        },

        'low_p_readout_pulse': {
            'operation': 'measurement',
            'length': readout_len,
            'waveforms': {
                'I': 'low_power_readout_wf',
                'Q': 'zero_wf'
            },
            'integration_weights': {
                'Wc': 'Wc',
                'Ws': 'Ws',
                '-Ws': '-Ws',
                'optW1': 'optW1',
                'optW2': 'optW2'
            },
            'digital_marker': 'ON'
        },

    },

    'waveforms': {

        'const_wf': {
            'type': 'constant',
            'sample': 0.4
        },

        'zero_wf': {
            'type': 'constant',
            'sample': 0.0
        },

        'saturation_wf': {
            'type': 'constant',
            'sample': 0.211
        },

        'gauss_wf': {
            'type': 'arbitrary',
            'samples': gauss(0.4, 0.0, 6.0, 60)
        },

        'pi_wf': {
            'type': 'arbitrary',
            'samples': gauss(0.3, 0.0, 6.0, 60)
        },

        'pi2_wf': {
            'type': 'arbitrary',
            'samples': gauss(0.15, 0.0, 6.0, 60)
        },

        'minus_pi2_wf': {
            'type': 'arbitrary',
            'samples': gauss(-0.15, 0.0, 6.0, 60)
        },

        'long_readout_wf': {
            'type': 'constant',
            'sample': 0.32
        },

        'readout_wf': {
            'type': 'constant',
            'sample': 0.02 # 0.12
        },

        'low_power_readout_wf': {
            'type': 'constant',
            'sample': 0.036
        }
    },

    'digital_waveforms': {
        'ON': {
            'samples': [(1, 0)]
        }
    },

    'integration_weights': {

        'long_integW1': {
            'cosine': [1.0] * int(long_redout_len / 4),
            'sine': [0.0] * int(long_redout_len / 4)
        },

        'long_integW2': {
            'cosine': [0.0] * int(long_redout_len / 4),
            'sine': [1.0] * int(long_redout_len / 4)
        },

        'Wc': {
            'cosine': [(0.01, readout_len)],
            'sine': [(0.00, readout_len)],
        },

        'Ws': {
            'cosine': [(0.00, readout_len)],
            'sine': [(0.01, readout_len)],
        },

        '-Ws': {
            'cosine': [(0.00, readout_len)],
            'sine': [(-0.01, readout_len)],
        },

        'optW1': {
            'cosine': [1.0] * int(readout_len / 4),
            'sine': [0.0] * int(readout_len / 4)
        },

        'optW2': {
            'cosine': [0.0] * int(readout_len / 4),
            'sine': [1.0] * int(readout_len / 4)
        },
    },

    'mixers': {
        'mixer_qubit': [
            {'intermediate_frequency': qubit_IF, 'lo_frequency': qubit_LO, 'correction': IQ_imbalance(0.0, 0.0)},
        ],
        'mixer_RR': [
            {'intermediate_frequency': rr_IF, 'lo_frequency': rr_LO, 'correction': IQ_imbalance(0.016,-0.0065)}
        ],
    }
}


