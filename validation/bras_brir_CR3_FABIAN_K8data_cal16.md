# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted; with 8 / 16 kHz when the calibration had them). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_FABIAN_K8data_cal16_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -45 | +2.4 / +1.9 | 0.48 / 0.38 | 0.10 / 0.09 |
| LS4 | -23 / -23 | +0.8 / +0.7 | 0.44 / 0.31 | 0.11 / 0.11 |
| LS5 | +45 / +45 | -1.2 / -1.8 | 0.50 / 0.34 | 0.14 / 0.09 |
| LS6 | +91 / +91 | -2.6 / -3.2 | 0.42 / 0.33 | 0.15 / 0.11 |
| LS7 | +23 / +23 | -0.2 / -0.7 | 0.73 / 0.37 | 0.29 / 0.10 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 1.67 | 1.46 / 1.55 | 1.41 / 1.49 | 1.34 / 1.45 | 1.38 / 1.42 | 1.15 / 1.13 |
| LS4 | 1.45 / 1.53 | 1.50 / 1.32 | 1.38 / 1.34 | 1.32 / 1.31 | 1.34 / 1.40 | 1.15 / 1.21 |
| LS5 | 1.61 / 1.36 | 1.45 / 1.36 | 1.40 / 1.25 | 1.36 / 1.25 | 1.35 / 1.24 | 1.14 / 1.07 |
| LS6 | 1.67 / 1.77 | 1.49 / 1.64 | 1.31 / 1.39 | 1.34 / 1.49 | 1.34 / 1.44 | 1.15 / 1.09 |
| LS7 | 1.56 / 1.48 | 1.51 / 1.64 | 1.39 / 1.32 | 1.37 / 1.35 | 1.36 / 1.34 | 1.14 / 1.08 |
| mean simulated - measured | -2 % | +1 % | -1 % | +2 % | +1 % | -2 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.51 | 1.56 / 1.22 | 1.39 / 1.47 | 1.35 / 1.41 | 1.27 / 1.37 | 1.29 / 1.24 |
| LS4 | 1.75 / 1.75 | 1.60 / 2.15 | 1.23 / 1.69 | 1.45 / 1.69 | 1.32 / 1.64 | 1.25 / 1.36 |
| LS5 | 1.30 / 2.26 | 1.41 / 1.88 | 1.27 / 1.47 | 1.39 / 1.58 | 1.30 / 1.51 | 1.21 / 1.22 |
| LS6 | 1.43 / 2.07 | 1.54 / 1.57 | 1.39 / 1.47 | 1.30 / 1.48 | 1.41 / 1.39 | 1.22 / 0.99 |
| LS7 | 1.49 / 1.88 | 1.47 / 1.14 | 1.21 / 1.38 | 1.33 / 1.36 | 1.12 / 1.44 | 1.19 / 1.11 |
| mean simulated - measured | +26 % | +5 % | +16 % | +10 % | +15 % | -4 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -3.93 | -1.55 / -0.59 | 2.14 / 0.32 | 1.79 / 0.42 | 5.37 / 2.02 | 4.40 / 4.74 |
| LS4 | -1.38 / 0.66 | -1.46 / -2.00 | 1.46 / 0.05 | 1.85 / 1.32 | 4.73 / 2.96 | 4.45 / 5.28 |
| LS5 | -1.63 / -2.46 | -1.04 / -4.04 | 1.90 / -1.47 | 2.07 / -0.26 | 4.99 / 2.02 | 4.42 / 5.20 |
| LS6 | -2.51 / -1.25 | 1.35 / -0.15 | 0.24 / 0.13 | 0.99 / 1.55 | 5.18 / 3.94 | 5.34 / 5.76 |
| LS7 | -0.26 / -3.70 | 0.75 / -1.00 | 1.87 / 2.53 | 2.12 / 0.83 | 5.03 / 3.13 | 5.67 / 5.50 |
| mean simulated - measured | -0.8 dB | -1.2 dB | -1.2 dB | -1.0 dB | -2.2 dB | +0.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -2.15 | -3.01 / -2.53 | -0.85 / -0.91 | 3.85 / 3.44 | 8.92 / 7.16 | 16.31 / 15.55 |
| LS4 | -2.29 / -3.01 | -3.28 / -4.24 | -0.66 / -0.16 | 3.93 / 4.40 | 9.26 / 7.80 | 16.59 / 15.91 |
| LS5 | -2.67 / -2.59 | -2.99 / -3.67 | -0.45 / -0.16 | 3.44 / 3.82 | 8.69 / 7.99 | 18.20 / 16.29 |
| LS6 | -2.77 / -3.43 | -2.35 / -3.23 | 0.22 / -0.43 | 2.13 / 3.67 | 9.30 / 7.89 | 19.21 / 16.30 |
| LS7 | -1.98 / -3.98 | -3.14 / -3.42 | -0.53 / -0.34 | 3.67 / 3.76 | 8.86 / 7.13 | 16.69 / 15.48 |
| mean simulated - measured | -0.6 dB | -0.5 dB | +0.1 dB | +0.4 dB | -1.4 dB | -1.5 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.35; IACC_L measured 0.16, simulated 0.10; |ITD difference| 0 us; |ILD difference| 0.5 dB.
