# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_FABIAN_K8data_cal_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -45 | +2.0 / +2.4 | 0.82 / 0.63 | 0.22 / 0.10 |
| LS4 | -23 / -23 | +0.5 / +1.2 | 0.82 / 0.62 | 0.29 / 0.12 |
| LS5 | +45 / +45 | -1.4 / -1.2 | 0.83 / 0.79 | 0.38 / 0.11 |
| LS6 | +91 / +91 | -3.4 / -2.4 | 0.75 / 0.62 | 0.19 / 0.09 |
| LS7 | +23 / +23 | -0.3 / -0.0 | 0.92 / 0.65 | 0.56 / 0.10 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 2.66 | 2.37 / 2.44 | 2.03 / 2.17 | 2.01 / 2.26 | 1.77 / 1.85 | 1.45 / 1.41 |
| LS4 | 2.26 / 2.65 | 2.40 / 2.46 | 2.05 / 1.94 | 2.06 / 1.97 | 1.73 / 1.74 | 1.40 / 1.37 |
| LS5 | 2.27 / 2.27 | 2.36 / 2.22 | 2.05 / 2.30 | 2.06 / 2.17 | 1.67 / 2.06 | 1.39 / 1.69 |
| LS6 | 2.40 / 2.63 | 2.50 / 2.60 | 2.04 / 2.30 | 2.05 / 2.35 | 1.76 / 1.84 | 1.39 / 1.29 |
| LS7 | 2.26 / 2.10 | 2.32 / 2.35 | 2.04 / 2.04 | 2.04 / 2.02 | 1.66 / 1.79 | 1.37 / 1.40 |
| mean simulated - measured | +6 % | +1 % | +5 % | +5 % | +8 % | +2 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 1.92 | 2.25 / 2.10 | 2.03 / 1.84 | 2.24 / 1.80 | 1.75 / 1.61 | 1.18 / 1.38 |
| LS4 | 2.65 / 2.42 | 2.15 / 2.89 | 2.02 / 1.88 | 1.95 / 2.08 | 2.06 / 1.91 | 2.06 / 1.49 |
| LS5 | 2.47 / 2.56 | 2.56 / 2.69 | 1.96 / 1.96 | 1.92 / 2.32 | 2.15 / 1.79 | 2.14 / 1.83 |
| LS6 | 2.10 / 2.88 | 2.49 / 2.24 | 2.10 / 2.08 | 2.10 / 2.06 | 1.52 / 1.85 | 1.22 / 1.26 |
| LS7 | 2.79 / 3.60 | 2.13 / 2.81 | 1.84 / 2.47 | 1.82 / 2.03 | 2.45 / 1.78 | 1.35 / 1.07 |
| mean simulated - measured | +7 % | +11 % | +4 % | +3 % | -8 % | -8 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -4.19 | -2.15 / -2.85 | 3.84 / 2.30 | 2.35 / 1.98 | 6.80 / 4.58 | 9.80 / 7.38 |
| LS4 | -0.01 / -0.19 | -5.26 / -2.17 | 2.82 / 0.71 | 1.88 / 1.75 | 5.14 / 4.31 | 7.04 / 7.53 |
| LS5 | 0.41 / -0.83 | -4.93 / -5.27 | 2.37 / -1.69 | 1.10 / 0.42 | 4.45 / 3.01 | 6.80 / 6.57 |
| LS6 | -0.70 / -0.93 | 0.71 / -1.84 | 0.76 / 0.60 | 2.42 / 2.70 | 7.45 / 5.65 | 8.64 / 8.52 |
| LS7 | -1.93 / -4.25 | -3.18 / -2.67 | 3.88 / 3.07 | 0.49 / 1.64 | 4.96 / 5.24 | 8.31 / 8.77 |
| mean simulated - measured | -1.5 dB | +0.0 dB | -1.7 dB | +0.1 dB | -1.2 dB | -0.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -4.08 | -4.52 / -3.35 | 0.59 / -0.21 | 3.93 / 3.56 | 8.36 / 7.35 | 16.72 / 16.07 |
| LS4 | -4.56 / -4.25 | -4.44 / -4.37 | 0.29 / 0.31 | 4.15 / 4.06 | 7.92 / 7.65 | 15.61 / 16.39 |
| LS5 | -3.84 / -3.67 | -4.77 / -3.76 | 0.38 / -0.01 | 4.39 / 3.77 | 7.87 / 7.68 | 15.64 / 16.40 |
| LS6 | -3.33 / -4.77 | -4.57 / -3.73 | -0.18 / -0.48 | 4.76 / 4.21 | 9.39 / 8.33 | 17.16 / 17.24 |
| LS7 | -5.53 / -4.82 | -3.72 / -4.10 | 0.49 / 0.45 | 3.23 / 3.65 | 7.35 / 7.84 | 15.37 / 16.93 |
| mean simulated - measured | -0.0 dB | +0.5 dB | -0.3 dB | -0.2 dB | -0.4 dB | +0.5 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.66; IACC_L measured 0.33, simulated 0.10; |ITD difference| 5 us; |ILD difference| 0.5 dB.
