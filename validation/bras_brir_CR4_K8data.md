# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -68 | +2.0 / +3.0 | 0.82 / 0.59 | 0.22 / 0.14 |
| LS4 | -23 / -45 | +0.5 / +1.3 | 0.82 / 0.53 | 0.29 / 0.09 |
| LS5 | +45 / +45 | -1.4 / -2.6 | 0.83 / 0.53 | 0.38 / 0.11 |
| LS6 | +91 / +68 | -3.4 / -4.2 | 0.75 / 0.67 | 0.19 / 0.12 |
| LS7 | +23 / +0 | -0.3 / -0.7 | 0.92 / 0.63 | 0.56 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 3.11 | 2.37 / 2.79 | 2.03 / 2.53 | 2.01 / 2.53 | 1.77 / 2.13 | 1.45 / 1.70 |
| LS4 | 2.26 / 2.88 | 2.40 / 2.77 | 2.05 / 2.48 | 2.06 / 2.48 | 1.73 / 2.23 | 1.40 / 1.63 |
| LS5 | 2.27 / 2.56 | 2.36 / 2.54 | 2.05 / 2.35 | 2.06 / 2.26 | 1.67 / 1.91 | 1.39 / 1.60 |
| LS6 | 2.40 / 2.58 | 2.50 / 2.92 | 2.04 / 2.61 | 2.05 / 2.61 | 1.76 / 2.31 | 1.39 / 1.89 |
| LS7 | 2.26 / 2.79 | 2.32 / 2.73 | 2.04 / 2.38 | 2.04 / 2.38 | 1.66 / 1.99 | 1.37 / 1.56 |
| mean simulated - measured | +21 % | +15 % | +21 % | +20 % | +23 % | +20 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 1.75 | 2.25 / 1.82 | 2.03 / 1.92 | 2.24 / 1.76 | 1.75 / 1.49 | 1.18 / 1.26 |
| LS4 | 2.65 / 2.09 | 2.15 / 2.84 | 2.02 / 2.08 | 1.95 / 2.24 | 2.06 / 1.85 | 2.06 / 1.69 |
| LS5 | 2.47 / 2.90 | 2.56 / 2.78 | 1.96 / 2.40 | 1.92 / 2.53 | 2.15 / 2.34 | 2.14 / 1.76 |
| LS6 | 2.10 / 2.94 | 2.49 / 2.45 | 2.10 / 2.25 | 2.10 / 2.14 | 1.52 / 2.07 | 1.22 / 1.76 |
| LS7 | 2.79 / 2.25 | 2.13 / 2.22 | 1.84 / 2.14 | 1.82 / 1.97 | 2.45 / 2.07 | 1.35 / 1.61 |
| mean simulated - measured | -3 % | +5 % | +9 % | +7 % | +1 % | +7 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -3.85 | -2.15 / -2.62 | 3.84 / 1.34 | 2.35 / 0.30 | 6.80 / 3.22 | 9.80 / 4.46 |
| LS4 | -0.01 / -1.05 | -5.26 / -4.27 | 2.82 / -1.39 | 1.88 / -0.30 | 5.14 / 2.29 | 7.04 / 3.79 |
| LS5 | 0.41 / -1.95 | -4.93 / -3.75 | 2.37 / -1.28 | 1.10 / -0.60 | 4.45 / 2.51 | 6.80 / 5.02 |
| LS6 | -0.70 / -4.28 | 0.71 / -4.49 | 0.76 / -2.18 | 2.42 / 0.24 | 7.45 / 4.15 | 8.64 / 5.77 |
| LS7 | -1.93 / -5.18 | -3.18 / -5.01 | 3.88 / 0.17 | 0.49 / -0.45 | 4.96 / 2.99 | 8.31 / 4.37 |
| mean simulated - measured | -2.7 dB | -1.1 dB | -3.4 dB | -1.8 dB | -2.7 dB | -3.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -2.96 | -4.52 / -2.10 | 0.59 / -0.24 | 3.93 / 2.34 | 8.36 / 1.70 | 16.72 / 5.00 |
| LS4 | -4.56 / -3.81 | -4.44 / -2.84 | 0.29 / -0.06 | 4.15 / 2.90 | 7.92 / 2.07 | 15.61 / 5.37 |
| LS5 | -3.84 / -2.72 | -4.77 / -1.96 | 0.38 / -0.32 | 4.39 / 2.28 | 7.87 / 1.73 | 15.64 / 5.04 |
| LS6 | -3.33 / -2.58 | -4.57 / -1.87 | -0.18 / -0.54 | 4.76 / 2.41 | 9.39 / 2.79 | 17.16 / 6.39 |
| LS7 | -5.53 / -3.89 | -3.72 / -2.48 | 0.49 / -0.28 | 3.23 / 2.75 | 7.35 / 1.85 | 15.37 / 5.09 |
| mean simulated - measured | +1.1 dB | +2.2 dB | -0.6 dB | -1.6 dB | -6.2 dB | -10.7 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.59; IACC_L measured 0.33, simulated 0.11; |ITD difference| 14 us; |ILD difference| 0.8 dB.
