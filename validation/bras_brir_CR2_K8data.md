# BRAS CR2: binaural check, AuralPaths (the web page itself, HRIR set KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR2_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -136 / -167 | +5.0 / +7.0 | 0.43 / 0.31 | 0.11 / 0.29 |
| LS4 | -45 / -62 | +1.5 / +2.9 | 0.35 / 0.29 | 0.12 / 0.27 |
| LS5 | +91 / +83 | -2.9 / -4.1 | 0.37 / 0.29 | 0.10 / 0.30 |
| LS6 | +204 / +167 | -6.8 / -7.5 | 0.28 / 0.36 | 0.13 / 0.27 |
| LS7 | +23 / +0 | -0.6 / -0.9 | 0.49 / 0.35 | 0.09 / 0.27 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.43 / 1.33 | 1.59 / 1.35 | 1.80 / 1.73 | 1.75 / 1.76 | 1.57 / 1.70 | 1.41 / 1.56 |
| LS4 | 1.23 / 1.33 | 1.43 / 1.30 | 1.77 / 1.74 | 1.72 / 1.70 | 1.55 / 1.70 | 1.37 / 1.56 |
| LS5 | 1.29 / 1.34 | 1.46 / 1.36 | 1.80 / 1.75 | 1.70 / 1.77 | 1.55 / 1.71 | 1.42 / 1.57 |
| LS6 | 1.44 / 1.34 | 1.45 / 1.31 | 1.77 / 1.74 | 1.70 / 1.70 | 1.59 / 1.70 | 1.43 / 1.55 |
| LS7 | 1.49 / 1.31 | 1.44 / 1.31 | 1.80 / 1.72 | 1.73 / 1.69 | 1.57 / 1.70 | 1.43 / 1.56 |
| mean simulated - measured | -3 % | -10 % | -3 % | +0 % | +9 % | +11 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.61 / 1.56 | 1.16 / 1.14 | 1.71 / 1.71 | 1.73 / 1.79 | 1.48 / 1.71 | 1.40 / 1.58 |
| LS4 | 1.27 / 1.94 | 1.18 / 1.57 | 1.52 / 1.64 | 1.74 / 1.80 | 1.43 / 1.65 | 1.48 / 1.60 |
| LS5 | 1.40 / 1.46 | 1.29 / 1.17 | 1.69 / 1.69 | 1.71 / 1.77 | 1.51 / 1.71 | 1.45 / 1.55 |
| LS6 | 1.25 / 1.72 | 1.50 / 1.58 | 1.61 / 1.63 | 1.68 / 1.77 | 1.50 / 1.66 | 1.43 / 1.58 |
| LS7 | 1.04 / 1.77 | 1.18 / 1.54 | 1.78 / 1.67 | 1.81 / 1.81 | 1.52 / 1.72 | 1.41 / 1.63 |
| mean simulated - measured | +32 % | +12 % | +1 % | +3 % | +14 % | +11 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -1.87 / -1.89 | 2.56 / 1.75 | 0.71 / -0.58 | 0.60 / -1.13 | 1.77 / 0.78 | 2.16 / 2.21 |
| LS4 | 1.25 / 1.48 | 3.01 / -0.18 | 0.57 / -1.40 | 0.10 / -1.14 | 1.39 / 0.58 | 1.57 / 1.51 |
| LS5 | 3.53 / -2.10 | 1.16 / 0.92 | 0.94 / -1.61 | 0.49 / -1.18 | 1.17 / 0.28 | 1.86 / 1.91 |
| LS6 | 0.58 / 0.34 | 1.27 / 0.27 | -0.56 / -1.14 | 0.34 / -1.03 | 2.19 / 0.73 | 2.58 / 2.15 |
| LS7 | 0.90 / 1.27 | 1.49 / 0.88 | -0.30 / -0.92 | 0.06 / -0.39 | 2.22 / 1.01 | 2.02 / 2.39 |
| mean simulated - measured | -1.1 dB | -1.2 dB | -1.4 dB | -1.3 dB | -1.1 dB | -0.0 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -6.36 / -4.97 | -4.40 / -2.65 | -0.46 / 0.23 | 4.86 / 2.41 | 6.17 / 1.24 | 14.31 / 3.78 |
| LS4 | -5.94 / -4.56 | -4.09 / -3.76 | -0.32 / 0.58 | 4.41 / 3.17 | 5.65 / 1.80 | 13.54 / 3.87 |
| LS5 | -6.23 / -4.63 | -4.46 / -2.90 | -0.30 / 0.13 | 4.76 / 2.77 | 5.76 / 1.21 | 13.75 / 3.91 |
| LS6 | -6.65 / -5.13 | -4.99 / -3.76 | -0.11 / 0.59 | 5.11 / 3.17 | 5.90 / 1.85 | 14.59 / 4.24 |
| LS7 | -5.18 / -4.60 | -3.87 / -3.57 | -0.64 / 0.40 | 4.50 / 3.17 | 5.89 / 1.52 | 13.67 / 3.86 |
| mean simulated - measured | +1.3 dB | +1.0 dB | +0.8 dB | -1.8 dB | -4.4 dB | -10.0 dB |

Means over the five sources: IACC_E3 measured 0.39, simulated 0.32; IACC_L measured 0.11, simulated 0.28; |ITD difference| 23 us; |ILD difference| 1.1 dB.
