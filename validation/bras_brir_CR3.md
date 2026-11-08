# BRAS CR3: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 5000 rays per source, image sources order 1. Sources: omnidirectional. Simulated BRIRs: `bras_brir_CR3_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -68 | +2.4 / +2.5 | 0.48 / 0.17 | 0.10 / 0.10 |
| LS4 | -23 / -23 | +0.8 / +0.7 | 0.44 / 0.22 | 0.11 / 0.10 |
| LS5 | +45 / +23 | -1.2 / -2.2 | 0.50 / 0.18 | 0.14 / 0.08 |
| LS6 | +91 / +68 | -2.6 / -4.5 | 0.42 / 0.16 | 0.15 / 0.10 |
| LS7 | +23 / +0 | -0.2 / -1.0 | 0.73 / 0.16 | 0.29 / 0.08 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest KU100 HRIR (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 2.14 | 1.46 / 1.52 | 1.41 / 1.42 | 1.34 / 1.47 | 1.38 / 1.43 | 1.15 / 1.10 |
| LS4 | 1.45 / 1.63 | 1.50 / 1.49 | 1.38 / 1.29 | 1.32 / 1.30 | 1.34 / 1.34 | 1.15 / 1.09 |
| LS5 | 1.61 / 1.51 | 1.45 / 1.43 | 1.40 / 1.30 | 1.36 / 1.33 | 1.35 / 1.29 | 1.14 / 1.12 |
| LS6 | 1.67 / 1.61 | 1.49 / 1.50 | 1.31 / 1.32 | 1.34 / 1.45 | 1.34 / 1.42 | 1.15 / 1.29 |
| LS7 | 1.56 / 1.40 | 1.51 / 1.53 | 1.39 / 1.32 | 1.37 / 1.37 | 1.36 / 1.34 | 1.14 / 1.15 |
| mean simulated - measured | +4 % | +1 % | -3 % | +3 % | +1 % | +0 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.70 | 1.56 / 1.70 | 1.39 / 1.69 | 1.35 / 1.72 | 1.27 / 1.65 | 1.29 / 1.30 |
| LS4 | 1.75 / 1.70 | 1.60 / 1.93 | 1.23 / 1.52 | 1.45 / 1.65 | 1.32 / 1.54 | 1.25 / 1.28 |
| LS5 | 1.30 / 2.08 | 1.41 / 1.91 | 1.27 / 1.61 | 1.39 / 1.78 | 1.30 / 1.66 | 1.21 / 1.22 |
| LS6 | 1.43 / 2.04 | 1.54 / 1.86 | 1.39 / 1.70 | 1.30 / 1.78 | 1.41 / 1.67 | 1.22 / 1.30 |
| LS7 | 1.49 / 2.08 | 1.47 / 1.32 | 1.21 / 1.56 | 1.33 / 1.53 | 1.12 / 1.54 | 1.19 / 1.24 |
| mean simulated - measured | +28 % | +15 % | +24 % | +25 % | +26 % | +3 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -4.00 | -1.55 / -0.03 | 2.14 / 0.32 | 1.79 / 0.50 | 5.37 / 0.38 | 4.40 / 2.27 |
| LS4 | -1.38 / -1.92 | -1.46 / -3.89 | 1.46 / -2.31 | 1.85 / -0.65 | 4.73 / -1.16 | 4.45 / 0.35 |
| LS5 | -1.63 / -0.77 | -1.04 / -2.72 | 1.90 / -1.30 | 2.07 / -0.07 | 4.99 / 0.29 | 4.42 / 2.59 |
| LS6 | -2.51 / -1.61 | 1.35 / -0.74 | 0.24 / -0.91 | 0.99 / 0.71 | 5.18 / 0.91 | 5.34 / 2.43 |
| LS7 | -0.26 / -5.06 | 0.75 / -2.11 | 1.87 / -0.00 | 2.12 / -0.96 | 5.03 / -0.19 | 5.67 / 1.37 |
| mean simulated - measured | -1.3 dB | -1.5 dB | -2.4 dB | -1.9 dB | -5.0 dB | -3.1 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -5.35 | -3.01 / -3.12 | -0.85 / -0.67 | 3.85 / 3.79 | 8.92 / 5.96 | 16.31 / 7.45 |
| LS4 | -2.29 / -6.48 | -3.28 / -4.11 | -0.66 / -0.17 | 3.93 / 4.28 | 9.26 / 6.14 | 16.59 / 7.32 |
| LS5 | -2.67 / -5.55 | -2.99 / -3.53 | -0.45 / -0.17 | 3.44 / 3.70 | 8.69 / 6.42 | 18.20 / 7.78 |
| LS6 | -2.77 / -5.91 | -2.35 / -3.54 | 0.22 / -0.36 | 2.13 / 3.89 | 9.30 / 6.18 | 19.21 / 7.79 |
| LS7 | -1.98 / -6.42 | -3.14 / -3.46 | -0.53 / -0.47 | 3.67 / 3.93 | 8.86 / 5.75 | 16.69 / 7.11 |
| mean simulated - measured | -3.6 dB | -0.6 dB | +0.1 dB | +0.5 dB | -2.9 dB | -9.9 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.18; IACC_L measured 0.16, simulated 0.09; |ITD difference| 18 us; |ILD difference| 0.8 dB.
