# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_FABIAN_K8data_cal_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -45 | +2.4 / +2.1 | 0.48 / 0.37 | 0.10 / 0.12 |
| LS4 | -23 / -23 | +0.8 / +0.9 | 0.44 / 0.35 | 0.11 / 0.15 |
| LS5 | +45 / +45 | -1.2 / -1.7 | 0.50 / 0.27 | 0.14 / 0.12 |
| LS6 | +91 / +91 | -2.6 / -3.1 | 0.42 / 0.33 | 0.15 / 0.12 |
| LS7 | +23 / +23 | -0.2 / -0.6 | 0.73 / 0.43 | 0.29 / 0.07 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 1.86 | 1.46 / 1.47 | 1.41 / 1.46 | 1.34 / 1.35 | 1.38 / 1.39 | 1.15 / 1.18 |
| LS4 | 1.45 / 1.87 | 1.50 / 1.48 | 1.38 / 1.31 | 1.32 / 1.34 | 1.34 / 1.38 | 1.15 / 1.04 |
| LS5 | 1.61 / 1.50 | 1.45 / 1.46 | 1.40 / 1.64 | 1.36 / 1.58 | 1.35 / 1.61 | 1.14 / 1.27 |
| LS6 | 1.67 / 1.58 | 1.49 / 1.44 | 1.31 / 1.32 | 1.34 / 1.35 | 1.34 / 1.34 | 1.15 / 1.08 |
| LS7 | 1.56 / 1.76 | 1.51 / 1.60 | 1.39 / 1.39 | 1.37 / 1.38 | 1.36 / 1.33 | 1.14 / 1.02 |
| mean simulated - measured | +8 % | +1 % | +3 % | +4 % | +4 % | -2 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.41 | 1.56 / 1.21 | 1.39 / 1.25 | 1.35 / 1.24 | 1.27 / 1.25 | 1.29 / 1.13 |
| LS4 | 1.75 / 1.71 | 1.60 / 1.90 | 1.23 / 1.42 | 1.45 / 1.44 | 1.32 / 1.33 | 1.25 / 1.09 |
| LS5 | 1.30 / 2.01 | 1.41 / 1.85 | 1.27 / 1.23 | 1.39 / 1.54 | 1.30 / 1.26 | 1.21 / 0.98 |
| LS6 | 1.43 / 1.48 | 1.54 / 1.49 | 1.39 / 1.41 | 1.30 / 1.46 | 1.41 / 1.30 | 1.22 / 1.07 |
| LS7 | 1.49 / 1.78 | 1.47 / 1.33 | 1.21 / 1.37 | 1.33 / 1.42 | 1.12 / 1.50 | 1.19 / 1.11 |
| mean simulated - measured | +11 % | +3 % | +3 % | +4 % | +4 % | -13 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -4.09 | -1.55 / -0.54 | 2.14 / 1.38 | 1.79 / 1.16 | 5.37 / 2.80 | 4.40 / 5.35 |
| LS4 | -1.38 / -0.43 | -1.46 / -2.65 | 1.46 / -0.28 | 1.85 / 0.85 | 4.73 / 2.54 | 4.45 / 4.86 |
| LS5 | -1.63 / -1.13 | -1.04 / -3.30 | 1.90 / -0.74 | 2.07 / 0.52 | 4.99 / 2.43 | 4.42 / 5.53 |
| LS6 | -2.51 / -3.81 | 1.35 / -1.28 | 0.24 / -0.40 | 0.99 / 0.61 | 5.18 / 3.23 | 5.34 / 5.22 |
| LS7 | -0.26 / -2.82 | 0.75 / -0.41 | 1.87 / 2.41 | 2.12 / 0.59 | 5.03 / 2.81 | 5.67 / 5.54 |
| mean simulated - measured | -1.1 dB | -1.2 dB | -1.0 dB | -1.0 dB | -2.3 dB | +0.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -2.68 | -3.01 / -2.52 | -0.85 / -1.07 | 3.85 / 3.58 | 8.92 / 7.01 | 16.31 / 15.59 |
| LS4 | -2.29 / -3.87 | -3.28 / -3.90 | -0.66 / -0.27 | 3.93 / 4.18 | 9.26 / 7.52 | 16.59 / 15.81 |
| LS5 | -2.67 / -2.45 | -2.99 / -3.56 | -0.45 / -0.17 | 3.44 / 3.73 | 8.69 / 7.78 | 18.20 / 16.17 |
| LS6 | -2.77 / -2.74 | -2.35 / -2.99 | 0.22 / -0.66 | 2.13 / 3.65 | 9.30 / 7.77 | 19.21 / 15.97 |
| LS7 | -1.98 / -4.03 | -3.14 / -3.47 | -0.53 / -0.15 | 3.67 / 3.62 | 8.86 / 6.89 | 16.69 / 15.40 |
| mean simulated - measured | -0.8 dB | -0.3 dB | -0.0 dB | +0.3 dB | -1.6 dB | -1.6 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.35; IACC_L measured 0.16, simulated 0.12; |ITD difference| 0 us; |ILD difference| 0.3 dB.
