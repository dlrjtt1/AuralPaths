# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: generic directional pattern, 105 deg nominal, aimed at the listener (an approximation of the QSC K8; brir_proto.dir_model). Simulated BRIRs: `bras_brir_CR3_K8_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -68 | +2.4 / +2.5 | 0.48 / 0.28 | 0.10 / 0.10 |
| LS4 | -23 / -23 | +0.8 / +0.6 | 0.44 / 0.31 | 0.11 / 0.10 |
| LS5 | +45 / +23 | -1.2 / -2.4 | 0.50 / 0.26 | 0.14 / 0.08 |
| LS6 | +91 / +68 | -2.6 / -4.3 | 0.42 / 0.29 | 0.15 / 0.10 |
| LS7 | +23 / +0 | -0.2 / -1.4 | 0.73 / 0.30 | 0.29 / 0.08 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 2.14 | 1.46 / 1.53 | 1.41 / 1.42 | 1.34 / 1.47 | 1.38 / 1.43 | 1.15 / 1.10 |
| LS4 | 1.45 / 1.63 | 1.50 / 1.49 | 1.38 / 1.29 | 1.32 / 1.30 | 1.34 / 1.34 | 1.15 / 1.09 |
| LS5 | 1.61 / 1.51 | 1.45 / 1.43 | 1.40 / 1.30 | 1.36 / 1.32 | 1.35 / 1.29 | 1.14 / 1.14 |
| LS6 | 1.67 / 1.61 | 1.49 / 1.50 | 1.31 / 1.34 | 1.34 / 1.47 | 1.34 / 1.44 | 1.15 / 1.30 |
| LS7 | 1.56 / 1.40 | 1.51 / 1.53 | 1.39 / 1.33 | 1.37 / 1.37 | 1.36 / 1.34 | 1.14 / 1.15 |
| mean simulated - measured | +4 % | +1 % | -3 % | +3 % | +1 % | +1 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.70 | 1.56 / 1.70 | 1.39 / 1.70 | 1.35 / 1.72 | 1.27 / 1.68 | 1.29 / 1.34 |
| LS4 | 1.75 / 1.71 | 1.60 / 1.94 | 1.23 / 1.52 | 1.45 / 1.65 | 1.32 / 1.53 | 1.25 / 1.33 |
| LS5 | 1.30 / 2.08 | 1.41 / 1.92 | 1.27 / 1.60 | 1.39 / 1.82 | 1.30 / 1.69 | 1.21 / 1.18 |
| LS6 | 1.43 / 2.04 | 1.54 / 1.86 | 1.39 / 1.69 | 1.30 / 1.74 | 1.41 / 1.67 | 1.22 / 1.26 |
| LS7 | 1.49 / 2.08 | 1.47 / 1.32 | 1.21 / 1.56 | 1.33 / 1.55 | 1.12 / 1.60 | 1.19 / 1.26 |
| mean simulated - measured | +28 % | +15 % | +24 % | +25 % | +28 % | +3 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -3.97 | -1.55 / -0.20 | 2.14 / 0.36 | 1.79 / 0.86 | 5.37 / 1.71 | 4.40 / 4.53 |
| LS4 | -1.38 / -1.99 | -1.46 / -3.71 | 1.46 / -2.09 | 1.85 / -0.25 | 4.73 / 0.56 | 4.45 / 2.70 |
| LS5 | -1.63 / -0.78 | -1.04 / -2.67 | 1.90 / -0.81 | 2.07 / 0.23 | 4.99 / 1.63 | 4.42 / 4.80 |
| LS6 | -2.51 / -1.63 | 1.35 / -0.86 | 0.24 / -0.45 | 0.99 / 1.61 | 5.18 / 2.74 | 5.34 / 5.00 |
| LS7 | -0.26 / -5.02 | 0.75 / -2.13 | 1.87 / 0.39 | 2.12 / 0.09 | 5.03 / 1.35 | 5.67 / 3.96 |
| mean simulated - measured | -1.3 dB | -1.5 dB | -2.0 dB | -1.3 dB | -3.5 dB | -0.7 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -2.92 | -3.01 / -0.82 | -0.85 / -0.47 | 3.85 / 1.29 | 8.92 / 0.54 | 16.31 / 2.76 |
| LS4 | -2.29 / -4.11 | -3.28 / -1.76 | -0.66 / 0.04 | 3.93 / 1.73 | 9.26 / 0.72 | 16.59 / 2.38 |
| LS5 | -2.67 / -3.21 | -2.99 / -1.21 | -0.45 / 0.15 | 3.44 / 1.06 | 8.69 / 0.91 | 18.20 / 2.98 |
| LS6 | -2.77 / -3.66 | -2.35 / -1.37 | 0.22 / -0.13 | 2.13 / 1.50 | 9.30 / 0.93 | 19.21 / 3.17 |
| LS7 | -1.98 / -4.16 | -3.14 / -1.27 | -0.53 / -0.26 | 3.67 / 1.53 | 8.86 / 0.24 | 16.69 / 2.37 |
| mean simulated - measured | -1.2 dB | +1.7 dB | +0.3 dB | -2.0 dB | -8.3 dB | -14.7 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.29; IACC_L measured 0.16, simulated 0.09; |ITD difference| 18 us; |ILD difference| 0.9 dB.
