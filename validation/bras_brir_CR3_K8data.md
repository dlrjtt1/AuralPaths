# BRAS CR3: binaural check, AuralPaths (the web page itself, HRIR set KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -62 | +2.4 / +2.3 | 0.48 / 0.51 | 0.10 / 0.23 |
| LS4 | -23 / -21 | +0.8 / +0.5 | 0.44 / 0.51 | 0.11 / 0.13 |
| LS5 | +45 / +21 | -1.2 / -2.2 | 0.50 / 0.43 | 0.14 / 0.21 |
| LS6 | +91 / +62 | -2.6 / -4.6 | 0.42 / 0.48 | 0.15 / 0.16 |
| LS7 | +23 / +0 | -0.2 / -1.3 | 0.73 / 0.37 | 0.29 / 0.14 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 1.97 | 1.46 / 1.64 | 1.41 / 1.50 | 1.34 / 1.49 | 1.38 / 1.51 | 1.15 / 1.11 |
| LS4 | 1.45 / 1.83 | 1.50 / 1.57 | 1.38 / 1.32 | 1.32 / 1.31 | 1.34 / 1.30 | 1.15 / 1.00 |
| LS5 | 1.61 / 1.79 | 1.45 / 1.56 | 1.40 / 1.43 | 1.36 / 1.46 | 1.35 / 1.45 | 1.14 / 1.14 |
| LS6 | 1.67 / 1.71 | 1.49 / 1.47 | 1.31 / 1.30 | 1.34 / 1.29 | 1.34 / 1.35 | 1.15 / 1.14 |
| LS7 | 1.56 / 1.79 | 1.51 / 1.46 | 1.39 / 1.32 | 1.37 / 1.33 | 1.36 / 1.35 | 1.14 / 1.12 |
| mean simulated - measured | +14 % | +4 % | -0 % | +2 % | +3 % | -4 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 1.46 | 1.56 / 1.46 | 1.39 / 1.42 | 1.35 / 1.29 | 1.27 / 1.21 | 1.29 / 1.00 |
| LS4 | 1.75 / 1.71 | 1.60 / 1.42 | 1.23 / 1.24 | 1.45 / 1.20 | 1.32 / 1.38 | 1.25 / 1.38 |
| LS5 | 1.30 / 1.57 | 1.41 / 1.32 | 1.27 / 1.19 | 1.39 / 1.19 | 1.30 / 1.14 | 1.21 / 0.82 |
| LS6 | 1.43 / 2.18 | 1.54 / 1.74 | 1.39 / 1.24 | 1.30 / 1.39 | 1.41 / 1.04 | 1.22 / 1.02 |
| LS7 | 1.49 / 1.99 | 1.47 / 1.76 | 1.21 / 1.22 | 1.33 / 1.32 | 1.12 / 1.15 | 1.19 / 1.12 |
| mean simulated - measured | +18 % | +2 % | -3 % | -6 % | -7 % | -13 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -2.87 | -1.55 / 2.67 | 2.14 / -0.78 | 1.79 / 2.14 | 5.37 / 3.08 | 4.40 / 4.69 |
| LS4 | -1.38 / -2.32 | -1.46 / -0.34 | 1.46 / -0.52 | 1.85 / 0.78 | 4.73 / 1.92 | 4.45 / 3.66 |
| LS5 | -1.63 / -2.51 | -1.04 / 2.60 | 1.90 / 2.23 | 2.07 / 2.61 | 4.99 / 3.24 | 4.42 / 5.52 |
| LS6 | -2.51 / -3.43 | 1.35 / 1.44 | 0.24 / 1.05 | 0.99 / 1.14 | 5.18 / 4.02 | 5.34 / 5.49 |
| LS7 | -0.26 / -2.78 | 0.75 / 1.11 | 1.87 / 1.22 | 2.12 / 0.71 | 5.03 / 3.02 | 5.67 / 4.43 |
| mean simulated - measured | -1.4 dB | +1.9 dB | -0.9 dB | -0.3 dB | -2.0 dB | -0.1 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -1.64 | -3.01 / -2.41 | -0.85 / -0.86 | 3.85 / 3.27 | 8.92 / 2.30 | 16.31 / 4.53 |
| LS4 | -2.29 / -3.00 | -3.28 / -3.50 | -0.66 / -0.18 | 3.93 / 3.68 | 9.26 / 2.56 | 16.59 / 4.32 |
| LS5 | -2.67 / -2.57 | -2.99 / -2.81 | -0.45 / -0.10 | 3.44 / 2.92 | 8.69 / 1.46 | 18.20 / 3.82 |
| LS6 | -2.77 / -3.35 | -2.35 / -2.91 | 0.22 / 0.09 | 2.13 / 2.82 | 9.30 / 3.20 | 19.21 / 4.51 |
| LS7 | -1.98 / -3.45 | -3.14 / -3.45 | -0.53 / 0.41 | 3.67 / 3.04 | 8.86 / 2.80 | 16.69 / 4.40 |
| mean simulated - measured | -0.4 dB | -0.1 dB | +0.3 dB | -0.3 dB | -6.5 dB | -13.1 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.46; IACC_L measured 0.16, simulated 0.18; |ITD difference| 19 us; |ILD difference| 0.9 dB.
