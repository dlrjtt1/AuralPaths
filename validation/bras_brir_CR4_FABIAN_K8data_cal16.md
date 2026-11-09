# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted; with 8 / 16 kHz when the calibration had them). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_FABIAN_K8data_cal16_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -45 | +2.0 / +2.2 | 0.82 / 0.69 | 0.22 / 0.13 |
| LS4 | -23 / -23 | +0.5 / +1.0 | 0.82 / 0.66 | 0.29 / 0.11 |
| LS5 | +45 / +45 | -1.4 / -1.3 | 0.83 / 0.58 | 0.38 / 0.10 |
| LS6 | +91 / +91 | -3.4 / -2.5 | 0.75 / 0.71 | 0.19 / 0.09 |
| LS7 | +23 / +23 | -0.3 / -0.2 | 0.92 / 0.63 | 0.56 / 0.10 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 2.60 | 2.37 / 2.35 | 2.03 / 2.05 | 2.01 / 1.94 | 1.77 / 1.72 | 1.45 / 1.31 |
| LS4 | 2.26 / 2.52 | 2.40 / 2.32 | 2.05 / 2.21 | 2.06 / 2.23 | 1.73 / 2.06 | 1.40 / 1.45 |
| LS5 | 2.27 / 2.43 | 2.36 / 2.36 | 2.05 / 2.28 | 2.06 / 2.42 | 1.67 / 2.02 | 1.39 / 1.45 |
| LS6 | 2.40 / 2.43 | 2.50 / 2.47 | 2.04 / 2.34 | 2.05 / 2.24 | 1.76 / 2.09 | 1.39 / 1.49 |
| LS7 | 2.26 / 2.48 | 2.32 / 2.45 | 2.04 / 2.31 | 2.04 / 2.29 | 1.66 / 1.95 | 1.37 / 1.35 |
| mean simulated - measured | +8 % | +0 % | +9 % | +9 % | +15 % | +1 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 2.02 | 2.25 / 2.14 | 2.03 / 2.42 | 2.24 / 2.26 | 1.75 / 1.84 | 1.18 / 1.53 |
| LS4 | 2.65 / 2.23 | 2.15 / 2.84 | 2.02 / 1.96 | 1.95 / 2.09 | 2.06 / 1.59 | 2.06 / 1.39 |
| LS5 | 2.47 / 3.22 | 2.56 / 3.25 | 1.96 / 2.73 | 1.92 / 2.71 | 2.15 / 2.23 | 2.14 / 1.02 |
| LS6 | 2.10 / 2.80 | 2.49 / 2.79 | 2.10 / 2.41 | 2.10 / 2.60 | 1.52 / 2.08 | 1.22 / 1.56 |
| LS7 | 2.79 / 2.94 | 2.13 / 2.41 | 1.84 / 2.06 | 1.82 / 1.87 | 2.45 / 1.62 | 1.35 / 1.02 |
| mean simulated - measured | +6 % | +16 % | +16 % | +15 % | -2 % | -11 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -4.43 | -2.15 / -3.81 | 3.84 / 2.09 | 2.35 / 1.05 | 6.80 / 4.46 | 9.80 / 7.55 |
| LS4 | -0.01 / -0.03 | -5.26 / -4.15 | 2.82 / -0.15 | 1.88 / 1.25 | 5.14 / 3.67 | 7.04 / 7.16 |
| LS5 | 0.41 / 1.18 | -4.93 / -1.87 | 2.37 / 0.76 | 1.10 / 2.05 | 4.45 / 4.90 | 6.80 / 8.56 |
| LS6 | -0.70 / -2.85 | 0.71 / -3.65 | 0.76 / -1.00 | 2.42 / 1.10 | 7.45 / 4.86 | 8.64 / 8.14 |
| LS7 | -1.93 / -2.73 | -3.18 / -1.30 | 3.88 / 3.57 | 0.49 / 1.08 | 4.96 / 5.15 | 8.31 / 9.06 |
| mean simulated - measured | -1.2 dB | +0.0 dB | -1.7 dB | -0.3 dB | -1.1 dB | -0.0 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -4.35 | -4.52 / -3.45 | 0.59 / -0.19 | 3.93 / 3.64 | 8.36 / 7.60 | 16.72 / 16.19 |
| LS4 | -4.56 / -4.72 | -4.44 / -4.36 | 0.29 / 0.17 | 4.15 / 4.19 | 7.92 / 7.65 | 15.61 / 16.37 |
| LS5 | -3.84 / -3.01 | -4.77 / -3.96 | 0.38 / 0.06 | 4.39 / 3.90 | 7.87 / 7.44 | 15.64 / 16.17 |
| LS6 | -3.33 / -3.81 | -4.57 / -3.86 | -0.18 / -0.45 | 4.76 / 4.31 | 9.39 / 8.23 | 17.16 / 17.14 |
| LS7 | -5.53 / -4.93 | -3.72 / -4.13 | 0.49 / 0.53 | 3.23 / 3.61 | 7.35 / 7.71 | 15.37 / 16.68 |
| mean simulated - measured | +0.1 dB | +0.5 dB | -0.3 dB | -0.2 dB | -0.5 dB | +0.4 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.66; IACC_L measured 0.33, simulated 0.11; |ITD difference| 5 us; |ILD difference| 0.4 dB.
