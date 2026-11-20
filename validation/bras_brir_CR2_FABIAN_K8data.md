# BRAS CR2: binaural check, AuralPaths (the web page itself, HRIR set FABIAN_HATO0.sofa) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR2_FABIAN_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -136 / -167 | +5.0 / +5.8 | 0.43 / 0.26 | 0.11 / 0.10 |
| LS4 | -45 / -42 | +1.5 / +2.0 | 0.35 / 0.20 | 0.12 / 0.08 |
| LS5 | +91 / +104 | -2.9 / -2.4 | 0.37 / 0.20 | 0.10 / 0.11 |
| LS6 | +204 / +188 | -6.8 / -5.3 | 0.28 / 0.17 | 0.13 / 0.08 |
| LS7 | +23 / +42 | -0.6 / -0.9 | 0.49 / 0.23 | 0.09 / 0.08 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.43 / 1.15 | 1.59 / 1.35 | 1.80 / 1.69 | 1.75 / 1.74 | 1.57 / 1.66 | 1.41 / 1.56 |
| LS4 | 1.23 / 1.12 | 1.43 / 1.32 | 1.77 / 1.72 | 1.72 / 1.75 | 1.55 / 1.66 | 1.37 / 1.54 |
| LS5 | 1.29 / 1.15 | 1.46 / 1.40 | 1.80 / 1.70 | 1.70 / 1.74 | 1.55 / 1.67 | 1.42 / 1.57 |
| LS6 | 1.44 / 1.13 | 1.45 / 1.31 | 1.77 / 1.72 | 1.70 / 1.76 | 1.59 / 1.66 | 1.43 / 1.54 |
| LS7 | 1.49 / 1.13 | 1.44 / 1.32 | 1.80 / 1.71 | 1.73 / 1.75 | 1.57 / 1.66 | 1.43 / 1.54 |
| mean simulated - measured | -17 % | -9 % | -5 % | +2 % | +6 % | +10 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.61 / 1.62 | 1.16 / 1.47 | 1.71 / 1.91 | 1.73 / 1.91 | 1.48 / 1.72 | 1.40 / 1.53 |
| LS4 | 1.27 / 1.56 | 1.18 / 1.46 | 1.52 / 1.89 | 1.74 / 1.80 | 1.43 / 1.78 | 1.48 / 1.57 |
| LS5 | 1.40 / 1.63 | 1.29 / 1.48 | 1.69 / 1.89 | 1.71 / 1.91 | 1.51 / 1.68 | 1.45 / 1.49 |
| LS6 | 1.25 / 1.59 | 1.50 / 1.35 | 1.61 / 1.91 | 1.68 / 1.82 | 1.50 / 1.76 | 1.43 / 1.55 |
| LS7 | 1.04 / 1.64 | 1.18 / 1.43 | 1.78 / 1.93 | 1.81 / 1.85 | 1.52 / 1.82 | 1.41 / 1.62 |
| mean simulated - measured | +25 % | +15 % | +15 % | +7 % | +18 % | +8 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -1.87 / 0.89 | 2.56 / 1.32 | 0.71 / 0.77 | 0.60 / 0.36 | 1.77 / 0.90 | 2.16 / 2.16 |
| LS4 | 1.25 / -2.25 | 3.01 / 0.21 | 0.57 / -0.09 | 0.10 / -0.67 | 1.39 / 0.03 | 1.57 / 1.32 |
| LS5 | 3.53 / 0.24 | 1.16 / -0.24 | 0.94 / 0.65 | 0.49 / -0.27 | 1.17 / 0.11 | 1.86 / 1.68 |
| LS6 | 0.58 / 1.31 | 1.27 / 1.34 | -0.56 / 0.18 | 0.34 / -0.69 | 2.19 / 0.62 | 2.58 / 1.56 |
| LS7 | 0.90 / 0.28 | 1.49 / 0.97 | -0.30 / 0.80 | 0.06 / -0.08 | 2.22 / 0.90 | 2.02 / 1.70 |
| mean simulated - measured | -0.8 dB | -1.2 dB | +0.2 dB | -0.6 dB | -1.2 dB | -0.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -6.36 / -4.26 | -4.40 / -3.92 | -0.46 / 0.05 | 4.86 / 3.87 | 6.17 / 6.96 | 14.31 / 14.90 |
| LS4 | -5.94 / -6.06 | -4.09 / -4.29 | -0.32 / 0.13 | 4.41 / 4.16 | 5.65 / 6.88 | 13.54 / 15.12 |
| LS5 | -6.23 / -4.35 | -4.46 / -4.30 | -0.30 / 0.40 | 4.76 / 3.90 | 5.76 / 6.99 | 13.75 / 15.05 |
| LS6 | -6.65 / -4.85 | -4.99 / -3.87 | -0.11 / -0.01 | 5.11 / 3.88 | 5.90 / 6.98 | 14.59 / 15.12 |
| LS7 | -5.18 / -5.34 | -3.87 / -4.28 | -0.64 / 0.23 | 4.50 / 4.05 | 5.89 / 6.87 | 13.67 / 14.80 |
| mean simulated - measured | +1.1 dB | +0.2 dB | +0.5 dB | -0.8 dB | +1.1 dB | +1.0 dB |

Means over the five sources: IACC_E3 measured 0.39, simulated 0.21; IACC_L measured 0.11, simulated 0.09; |ITD difference| 17 us; |ILD difference| 0.7 dB.
