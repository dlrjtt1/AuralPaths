# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_FABIAN_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -45 | +2.4 / +2.1 | 0.48 / 0.37 | 0.10 / 0.10 |
| LS4 | -23 / -23 | +0.8 / +0.9 | 0.44 / 0.35 | 0.11 / 0.11 |
| LS5 | +45 / +45 | -1.2 / -1.7 | 0.50 / 0.31 | 0.14 / 0.07 |
| LS6 | +91 / +91 | -2.6 / -3.1 | 0.42 / 0.31 | 0.15 / 0.11 |
| LS7 | +23 / +23 | -0.2 / -0.6 | 0.73 / 0.40 | 0.29 / 0.08 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 2.14 | 1.46 / 1.54 | 1.41 / 1.40 | 1.34 / 1.47 | 1.38 / 1.42 | 1.15 / 1.10 |
| LS4 | 1.45 / 1.63 | 1.50 / 1.50 | 1.38 / 1.29 | 1.32 / 1.30 | 1.34 / 1.33 | 1.15 / 1.08 |
| LS5 | 1.61 / 1.51 | 1.45 / 1.44 | 1.40 / 1.30 | 1.36 / 1.32 | 1.35 / 1.29 | 1.14 / 1.14 |
| LS6 | 1.67 / 1.61 | 1.49 / 1.50 | 1.31 / 1.35 | 1.34 / 1.46 | 1.34 / 1.43 | 1.15 / 1.30 |
| LS7 | 1.56 / 1.40 | 1.51 / 1.53 | 1.39 / 1.33 | 1.37 / 1.37 | 1.36 / 1.34 | 1.14 / 1.15 |
| mean simulated - measured | +4 % | +1 % | -3 % | +3 % | +1 % | +1 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.76 | 1.56 / 1.69 | 1.39 / 1.72 | 1.35 / 1.74 | 1.27 / 1.66 | 1.29 / 1.30 |
| LS4 | 1.75 / 1.71 | 1.60 / 1.95 | 1.23 / 1.53 | 1.45 / 1.65 | 1.32 / 1.50 | 1.25 / 1.30 |
| LS5 | 1.30 / 2.08 | 1.41 / 1.93 | 1.27 / 1.59 | 1.39 / 1.80 | 1.30 / 1.67 | 1.21 / 1.17 |
| LS6 | 1.43 / 2.05 | 1.54 / 1.87 | 1.39 / 1.69 | 1.30 / 1.77 | 1.41 / 1.63 | 1.22 / 1.19 |
| LS7 | 1.49 / 2.09 | 1.47 / 1.34 | 1.21 / 1.56 | 1.33 / 1.55 | 1.12 / 1.60 | 1.19 / 1.27 |
| mean simulated - measured | +29 % | +16 % | +25 % | +25 % | +26 % | +1 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -3.96 | -1.55 / 0.19 | 2.14 / 1.17 | 1.79 / 1.10 | 5.37 / 2.57 | 4.40 / 5.32 |
| LS4 | -1.38 / -1.86 | -1.46 / -3.46 | 1.46 / -1.62 | 1.85 / -0.41 | 4.73 / 1.47 | 4.45 / 3.68 |
| LS5 | -1.63 / -0.86 | -1.04 / -2.35 | 1.90 / -0.11 | 2.07 / 0.32 | 4.99 / 2.46 | 4.42 / 5.56 |
| LS6 | -2.51 / -1.52 | 1.35 / -0.57 | 0.24 / 0.06 | 0.99 / 1.35 | 5.18 / 3.69 | 5.34 / 5.71 |
| LS7 | -0.26 / -4.90 | 0.75 / -1.95 | 1.87 / 1.50 | 2.12 / -0.32 | 5.03 / 2.10 | 5.67 / 4.71 |
| mean simulated - measured | -1.3 dB | -1.2 dB | -1.3 dB | -1.4 dB | -2.6 dB | +0.1 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -2.22 | -3.01 / -2.90 | -0.85 / -0.95 | 3.85 / 3.84 | 8.92 / 7.31 | 16.31 / 15.90 |
| LS4 | -2.29 / -3.26 | -3.28 / -3.82 | -0.66 / -0.46 | 3.93 / 4.28 | 9.26 / 7.70 | 16.59 / 15.81 |
| LS5 | -2.67 / -2.43 | -2.99 / -3.34 | -0.45 / -0.31 | 3.44 / 3.65 | 8.69 / 7.86 | 18.20 / 16.21 |
| LS6 | -2.77 / -2.85 | -2.35 / -3.41 | 0.22 / -0.58 | 2.13 / 4.00 | 9.30 / 8.05 | 19.21 / 16.49 |
| LS7 | -1.98 / -3.42 | -3.14 / -3.43 | -0.53 / -0.46 | 3.67 / 3.89 | 8.86 / 7.07 | 16.69 / 15.59 |
| mean simulated - measured | -0.5 dB | -0.4 dB | -0.1 dB | +0.5 dB | -1.4 dB | -1.4 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.35; IACC_L measured 0.16, simulated 0.09; |ITD difference| 0 us; |ILD difference| 0.3 dB.
