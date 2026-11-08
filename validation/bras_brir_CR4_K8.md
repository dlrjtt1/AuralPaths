# BRAS CR4: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: generic directional pattern, 105 deg nominal, aimed at the listener (an approximation of the QSC K8; brir_proto.dir_model). Simulated BRIRs: `bras_brir_CR4_K8_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -68 | +2.0 / +3.1 | 0.82 / 0.55 | 0.22 / 0.14 |
| LS4 | -23 / -45 | +0.5 / +1.3 | 0.82 / 0.47 | 0.29 / 0.09 |
| LS5 | +45 / +45 | -1.4 / -2.6 | 0.83 / 0.45 | 0.38 / 0.11 |
| LS6 | +91 / +68 | -3.4 / -4.2 | 0.75 / 0.61 | 0.19 / 0.12 |
| LS7 | +23 / +0 | -0.3 / -0.7 | 0.92 / 0.56 | 0.56 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 3.11 | 2.37 / 2.78 | 2.03 / 2.54 | 2.01 / 2.53 | 1.77 / 2.15 | 1.45 / 1.70 |
| LS4 | 2.26 / 2.88 | 2.40 / 2.77 | 2.05 / 2.48 | 2.06 / 2.48 | 1.73 / 2.23 | 1.40 / 1.63 |
| LS5 | 2.27 / 2.57 | 2.36 / 2.52 | 2.05 / 2.35 | 2.06 / 2.26 | 1.67 / 1.92 | 1.39 / 1.61 |
| LS6 | 2.40 / 2.58 | 2.50 / 2.93 | 2.04 / 2.61 | 2.05 / 2.61 | 1.76 / 2.31 | 1.39 / 1.89 |
| LS7 | 2.26 / 2.80 | 2.32 / 2.72 | 2.04 / 2.40 | 2.04 / 2.38 | 1.66 / 1.99 | 1.37 / 1.56 |
| mean simulated - measured | +21 % | +15 % | +21 % | +20 % | +23 % | +20 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 1.76 | 2.25 / 1.83 | 2.03 / 1.92 | 2.24 / 1.77 | 1.75 / 1.49 | 1.18 / 1.27 |
| LS4 | 2.65 / 2.08 | 2.15 / 2.85 | 2.02 / 2.07 | 1.95 / 2.24 | 2.06 / 1.87 | 2.06 / 1.71 |
| LS5 | 2.47 / 2.89 | 2.56 / 2.79 | 1.96 / 2.38 | 1.92 / 2.51 | 2.15 / 2.34 | 2.14 / 1.72 |
| LS6 | 2.10 / 2.95 | 2.49 / 2.43 | 2.10 / 2.25 | 2.10 / 2.13 | 1.52 / 2.02 | 1.22 / 1.77 |
| LS7 | 2.79 / 2.24 | 2.13 / 2.23 | 1.84 / 2.12 | 1.82 / 1.97 | 2.45 / 2.04 | 1.35 / 1.60 |
| mean simulated - measured | -3 % | +5 % | +8 % | +7 % | +0 % | +7 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -3.73 | -2.15 / -3.01 | 3.84 / 0.68 | 2.35 / 0.09 | 6.80 / 2.84 | 9.80 / 4.80 |
| LS4 | -0.01 / -1.15 | -5.26 / -4.39 | 2.82 / -1.97 | 1.88 / -0.63 | 5.14 / 1.82 | 7.04 / 4.15 |
| LS5 | 0.41 / -1.86 | -4.93 / -3.84 | 2.37 / -1.89 | 1.10 / -0.90 | 4.45 / 2.04 | 6.80 / 5.33 |
| LS6 | -0.70 / -4.58 | 0.71 / -5.04 | 0.76 / -3.35 | 2.42 / -0.15 | 7.45 / 3.69 | 8.64 / 6.15 |
| LS7 | -1.93 / -5.39 | -3.18 / -5.38 | 3.88 / -0.78 | 0.49 / -0.84 | 4.96 / 2.69 | 8.31 / 4.78 |
| mean simulated - measured | -2.8 dB | -1.4 dB | -4.2 dB | -2.1 dB | -3.1 dB | -3.1 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -4.10 | -4.52 / -1.32 | 0.59 / 0.25 | 3.93 / 1.07 | 8.36 / 0.56 | 16.72 / 3.05 |
| LS4 | -4.56 / -5.02 | -4.44 / -2.06 | 0.29 / 0.53 | 4.15 / 1.53 | 7.92 / 0.83 | 15.61 / 3.38 |
| LS5 | -3.84 / -3.89 | -4.77 / -1.17 | 0.38 / 0.25 | 4.39 / 0.92 | 7.87 / 0.49 | 15.64 / 3.02 |
| LS6 | -3.33 / -3.82 | -4.57 / -1.05 | -0.18 / -0.04 | 4.76 / 1.09 | 9.39 / 1.62 | 17.16 / 4.52 |
| LS7 | -5.53 / -5.04 | -3.72 / -1.64 | 0.49 / 0.18 | 3.23 / 1.46 | 7.35 / 0.84 | 15.37 / 3.25 |
| mean simulated - measured | -0.1 dB | +3.0 dB | -0.1 dB | -2.9 dB | -7.3 dB | -12.7 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.53; IACC_L measured 0.33, simulated 0.11; |ITD difference| 14 us; |ILD difference| 0.9 dB.
