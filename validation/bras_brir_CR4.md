# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: omnidirectional. Simulated BRIRs: `bras_brir_CR4_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -68 | +2.0 / +3.3 | 0.82 / 0.40 | 0.22 / 0.13 |
| LS4 | -23 / -45 | +0.5 / +1.3 | 0.82 / 0.25 | 0.29 / 0.09 |
| LS5 | +45 / +45 | -1.4 / -2.4 | 0.83 / 0.24 | 0.38 / 0.11 |
| LS6 | +91 / +68 | -3.4 / -4.1 | 0.75 / 0.40 | 0.19 / 0.12 |
| LS7 | +23 / +0 | -0.3 / -0.6 | 0.92 / 0.38 | 0.56 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 3.11 | 2.37 / 2.78 | 2.03 / 2.53 | 2.01 / 2.53 | 1.77 / 2.18 | 1.45 / 1.74 |
| LS4 | 2.26 / 2.88 | 2.40 / 2.77 | 2.05 / 2.47 | 2.06 / 2.46 | 1.73 / 2.23 | 1.40 / 1.75 |
| LS5 | 2.27 / 2.57 | 2.36 / 2.52 | 2.05 / 2.35 | 2.06 / 2.28 | 1.67 / 1.95 | 1.39 / 1.59 |
| LS6 | 2.40 / 2.58 | 2.50 / 2.93 | 2.04 / 2.61 | 2.05 / 2.60 | 1.76 / 2.33 | 1.39 / 1.94 |
| LS7 | 2.26 / 2.80 | 2.32 / 2.72 | 2.04 / 2.40 | 2.04 / 2.40 | 1.66 / 2.02 | 1.37 / 1.58 |
| mean simulated - measured | +21 % | +15 % | +21 % | +20 % | +25 % | +23 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 1.76 | 2.25 / 1.83 | 2.03 / 1.92 | 2.24 / 1.78 | 1.75 / 1.65 | 1.18 / 1.22 |
| LS4 | 2.65 / 2.08 | 2.15 / 2.84 | 2.02 / 2.08 | 1.95 / 2.24 | 2.06 / 1.90 | 2.06 / 1.54 |
| LS5 | 2.47 / 2.90 | 2.56 / 2.78 | 1.96 / 2.38 | 1.92 / 2.41 | 2.15 / 2.24 | 2.14 / 1.87 |
| LS6 | 2.10 / 2.95 | 2.49 / 2.43 | 2.10 / 2.24 | 2.10 / 2.16 | 1.52 / 1.89 | 1.22 / 1.60 |
| LS7 | 2.79 / 2.25 | 2.13 / 2.22 | 1.84 / 2.10 | 1.82 / 1.92 | 2.45 / 1.94 | 1.35 / 1.62 |
| mean simulated - measured | -3 % | +5 % | +8 % | +6 % | -1 % | +3 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -3.73 | -2.15 / -2.87 | 3.84 / 0.27 | 2.35 / -1.11 | 6.80 / -0.52 | 9.80 / 0.82 |
| LS4 | -0.01 / -1.05 | -5.26 / -4.24 | 2.82 / -2.73 | 1.88 / -1.92 | 5.14 / -1.72 | 7.04 / -0.21 |
| LS5 | 0.41 / -1.80 | -4.93 / -3.72 | 2.37 / -2.27 | 1.10 / -2.24 | 4.45 / -1.09 | 6.80 / 1.54 |
| LS6 | -0.70 / -4.61 | 0.71 / -5.04 | 0.76 / -4.11 | 2.42 / -2.33 | 7.45 / -0.81 | 8.64 / 0.77 |
| LS7 | -1.93 / -5.35 | -3.18 / -5.23 | 3.88 / -1.58 | 0.49 / -2.34 | 4.96 / -1.61 | 8.31 / 0.14 |
| mean simulated - measured | -2.8 dB | -1.3 dB | -4.8 dB | -3.6 dB | -6.9 dB | -7.5 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -6.33 | -4.52 / -3.47 | 0.59 / 0.08 | 3.93 / 3.40 | 8.36 / 5.05 | 16.72 / 6.92 |
| LS4 | -4.56 / -7.18 | -4.44 / -4.15 | 0.29 / 0.27 | 4.15 / 3.88 | 7.92 / 5.44 | 15.61 / 7.21 |
| LS5 | -3.84 / -6.12 | -4.77 / -3.32 | 0.38 / 0.09 | 4.39 / 3.24 | 7.87 / 5.17 | 15.64 / 6.88 |
| LS6 | -3.33 / -5.91 | -4.57 / -3.09 | -0.18 / -0.11 | 4.76 / 3.21 | 9.39 / 5.53 | 17.16 / 7.43 |
| LS7 | -5.53 / -7.20 | -3.72 / -3.72 | 0.49 / -0.10 | 3.23 / 3.81 | 7.35 / 5.03 | 15.37 / 6.84 |
| mean simulated - measured | -2.3 dB | +0.9 dB | -0.3 dB | -0.6 dB | -2.9 dB | -9.0 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.33; IACC_L measured 0.33, simulated 0.11; |ITD difference| 14 us; |ILD difference| 0.8 dB.
