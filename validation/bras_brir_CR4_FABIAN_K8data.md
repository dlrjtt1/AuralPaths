# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_FABIAN_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -45 | +2.0 / +2.4 | 0.82 / 0.63 | 0.22 / 0.14 |
| LS4 | -23 / -23 | +0.5 / +1.2 | 0.82 / 0.59 | 0.29 / 0.10 |
| LS5 | +45 / +45 | -1.4 / -1.1 | 0.83 / 0.58 | 0.38 / 0.11 |
| LS6 | +91 / +91 | -3.4 / -2.4 | 0.75 / 0.72 | 0.19 / 0.13 |
| LS7 | +23 / +23 | -0.3 / -0.0 | 0.92 / 0.63 | 0.56 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 3.11 | 2.37 / 2.79 | 2.03 / 2.54 | 2.01 / 2.52 | 1.77 / 2.10 | 1.45 / 1.69 |
| LS4 | 2.26 / 2.89 | 2.40 / 2.77 | 2.05 / 2.48 | 2.06 / 2.48 | 1.73 / 2.21 | 1.40 / 1.60 |
| LS5 | 2.27 / 2.55 | 2.36 / 2.54 | 2.05 / 2.34 | 2.06 / 2.25 | 1.67 / 1.89 | 1.39 / 1.60 |
| LS6 | 2.40 / 2.58 | 2.50 / 2.92 | 2.04 / 2.61 | 2.05 / 2.62 | 1.76 / 2.29 | 1.39 / 1.86 |
| LS7 | 2.26 / 2.79 | 2.32 / 2.73 | 2.04 / 2.35 | 2.04 / 2.38 | 1.66 / 1.97 | 1.37 / 1.55 |
| mean simulated - measured | +21 % | +15 % | +21 % | +20 % | +22 % | +19 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 1.75 | 2.25 / 1.82 | 2.03 / 1.91 | 2.24 / 1.75 | 1.75 / 1.48 | 1.18 / 1.26 |
| LS4 | 2.65 / 2.08 | 2.15 / 2.85 | 2.02 / 2.08 | 1.95 / 2.25 | 2.06 / 1.81 | 2.06 / 1.75 |
| LS5 | 2.47 / 2.90 | 2.56 / 2.77 | 1.96 / 2.41 | 1.92 / 2.54 | 2.15 / 2.31 | 2.14 / 1.69 |
| LS6 | 2.10 / 2.94 | 2.49 / 2.45 | 2.10 / 2.20 | 2.10 / 2.16 | 1.52 / 2.05 | 1.22 / 1.71 |
| LS7 | 2.79 / 2.26 | 2.13 / 2.21 | 1.84 / 2.21 | 1.82 / 1.96 | 2.45 / 2.03 | 1.35 / 1.51 |
| mean simulated - measured | -3 % | +5 % | +9 % | +7 % | -1 % | +4 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -3.66 | -2.15 / -2.65 | 3.84 / 2.14 | 2.35 / 0.90 | 6.80 / 3.67 | 9.80 / 5.66 |
| LS4 | -0.01 / -0.94 | -5.26 / -4.17 | 2.82 / -0.59 | 1.88 / 0.38 | 5.14 / 2.52 | 7.04 / 4.65 |
| LS5 | 0.41 / -1.86 | -4.93 / -3.77 | 2.37 / -0.62 | 1.10 / 0.34 | 4.45 / 2.73 | 6.80 / 5.74 |
| LS6 | -0.70 / -3.91 | 0.71 / -4.49 | 0.76 / -1.05 | 2.42 / 1.39 | 7.45 / 4.41 | 8.64 / 6.65 |
| LS7 | -1.93 / -5.15 | -3.18 / -4.90 | 3.88 / 1.32 | 0.49 / -0.92 | 4.96 / 3.17 | 8.31 / 5.73 |
| mean simulated - measured | -2.6 dB | -1.0 dB | -2.5 dB | -1.2 dB | -2.5 dB | -2.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -3.66 | -4.52 / -3.73 | 0.59 / 0.03 | 3.93 / 3.70 | 8.36 / 7.22 | 16.72 / 16.10 |
| LS4 | -4.56 / -4.53 | -4.44 / -4.41 | 0.29 / 0.09 | 4.15 / 4.32 | 7.92 / 7.45 | 15.61 / 16.22 |
| LS5 | -3.84 / -3.40 | -4.77 / -3.58 | 0.38 / -0.25 | 4.39 / 3.83 | 7.87 / 7.15 | 15.64 / 15.78 |
| LS6 | -3.33 / -3.40 | -4.57 / -3.63 | -0.18 / -0.40 | 4.76 / 4.02 | 9.39 / 8.12 | 17.16 / 17.20 |
| LS7 | -5.53 / -4.52 | -3.72 / -3.98 | 0.49 / 0.22 | 3.23 / 3.77 | 7.35 / 7.41 | 15.37 / 16.43 |
| mean simulated - measured | +0.4 dB | +0.5 dB | -0.4 dB | -0.2 dB | -0.7 dB | +0.2 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.63; IACC_L measured 0.33, simulated 0.11; |ITD difference| 5 us; |ILD difference| 0.5 dB.
