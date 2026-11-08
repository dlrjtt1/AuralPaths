# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -68 | +2.4 / +2.5 | 0.48 / 0.33 | 0.10 / 0.10 |
| LS4 | -23 / -23 | +0.8 / +0.6 | 0.44 / 0.34 | 0.11 / 0.11 |
| LS5 | +45 / +23 | -1.2 / -2.4 | 0.50 / 0.30 | 0.14 / 0.08 |
| LS6 | +91 / +68 | -2.6 / -4.3 | 0.42 / 0.33 | 0.15 / 0.10 |
| LS7 | +23 / +0 | -0.2 / -1.4 | 0.73 / 0.40 | 0.29 / 0.08 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 2.14 | 1.46 / 1.55 | 1.41 / 1.41 | 1.34 / 1.47 | 1.38 / 1.43 | 1.15 / 1.09 |
| LS4 | 1.45 / 1.63 | 1.50 / 1.50 | 1.38 / 1.29 | 1.32 / 1.30 | 1.34 / 1.34 | 1.15 / 1.09 |
| LS5 | 1.61 / 1.51 | 1.45 / 1.44 | 1.40 / 1.30 | 1.36 / 1.32 | 1.35 / 1.29 | 1.14 / 1.14 |
| LS6 | 1.67 / 1.61 | 1.49 / 1.50 | 1.31 / 1.34 | 1.34 / 1.47 | 1.34 / 1.44 | 1.15 / 1.30 |
| LS7 | 1.56 / 1.40 | 1.51 / 1.53 | 1.39 / 1.33 | 1.37 / 1.37 | 1.36 / 1.35 | 1.14 / 1.15 |
| mean simulated - measured | +4 % | +1 % | -3 % | +3 % | +1 % | +1 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.71 | 1.56 / 1.69 | 1.39 / 1.72 | 1.35 / 1.72 | 1.27 / 1.68 | 1.29 / 1.33 |
| LS4 | 1.75 / 1.71 | 1.60 / 1.94 | 1.23 / 1.52 | 1.45 / 1.65 | 1.32 / 1.53 | 1.25 / 1.33 |
| LS5 | 1.30 / 2.09 | 1.41 / 1.94 | 1.27 / 1.61 | 1.39 / 1.82 | 1.30 / 1.70 | 1.21 / 1.17 |
| LS6 | 1.43 / 2.04 | 1.54 / 1.87 | 1.39 / 1.69 | 1.30 / 1.75 | 1.41 / 1.67 | 1.22 / 1.26 |
| LS7 | 1.49 / 2.09 | 1.47 / 1.34 | 1.21 / 1.56 | 1.33 / 1.57 | 1.12 / 1.61 | 1.19 / 1.26 |
| mean simulated - measured | +28 % | +16 % | +25 % | +25 % | +28 % | +3 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -3.99 | -1.55 / 0.06 | 2.14 / 0.59 | 1.79 / 1.03 | 5.37 / 1.98 | 4.40 / 4.33 |
| LS4 | -1.38 / -1.85 | -1.46 / -3.38 | 1.46 / -1.93 | 1.85 / -0.15 | 4.73 / 1.04 | 4.45 / 2.41 |
| LS5 | -1.63 / -0.80 | -1.04 / -2.45 | 1.90 / -0.62 | 2.07 / 0.44 | 4.99 / 1.93 | 4.42 / 4.60 |
| LS6 | -2.51 / -1.65 | 1.35 / -0.58 | 0.24 / -0.14 | 0.99 / 1.62 | 5.18 / 3.07 | 5.34 / 4.74 |
| LS7 | -0.26 / -4.96 | 0.75 / -2.02 | 1.87 / 0.92 | 2.12 / 0.14 | 5.03 / 1.57 | 5.67 / 3.63 |
| mean simulated - measured | -1.3 dB | -1.3 dB | -1.8 dB | -1.1 dB | -3.1 dB | -0.9 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -1.66 | -3.01 / -1.46 | -0.85 / -1.15 | 3.85 / 2.60 | 8.92 / 1.64 | 16.31 / 4.86 |
| LS4 | -2.29 / -2.73 | -3.28 / -2.41 | -0.66 / -0.65 | 3.93 / 3.06 | 9.26 / 1.98 | 16.59 / 4.51 |
| LS5 | -2.67 / -1.94 | -2.99 / -1.88 | -0.45 / -0.55 | 3.44 / 2.43 | 8.69 / 2.06 | 18.20 / 5.13 |
| LS6 | -2.77 / -2.38 | -2.35 / -2.03 | 0.22 / -0.75 | 2.13 / 2.78 | 9.30 / 2.13 | 19.21 / 5.28 |
| LS7 | -1.98 / -2.88 | -3.14 / -2.02 | -0.53 / -0.77 | 3.67 / 2.79 | 8.86 / 1.31 | 16.69 / 4.39 |
| mean simulated - measured | +0.1 dB | +1.0 dB | -0.3 dB | -0.7 dB | -7.2 dB | -12.6 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.34; IACC_L measured 0.16, simulated 0.09; |ITD difference| 18 us; |ILD difference| 0.9 dB.
