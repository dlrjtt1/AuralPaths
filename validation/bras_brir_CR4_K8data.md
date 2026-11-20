# BRAS CR4: binaural check, AuralPaths (the web page itself, HRIR set KU100) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -62 | +2.0 / +2.7 | 0.82 / 0.86 | 0.22 / 0.15 |
| LS4 | -23 / -42 | +0.5 / +1.0 | 0.82 / 0.84 | 0.29 / 0.20 |
| LS5 | +45 / +42 | -1.4 / -2.9 | 0.83 / 0.71 | 0.38 / 0.18 |
| LS6 | +91 / +62 | -3.4 / -3.7 | 0.75 / 0.85 | 0.19 / 0.18 |
| LS7 | +23 / +0 | -0.3 / -0.9 | 0.92 / 0.82 | 0.56 / 0.19 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 2.49 | 2.37 / 2.57 | 2.03 / 2.32 | 2.01 / 2.33 | 1.77 / 2.19 | 1.45 / 1.78 |
| LS4 | 2.26 / 2.66 | 2.40 / 2.65 | 2.05 / 2.37 | 2.06 / 2.29 | 1.73 / 2.19 | 1.40 / 1.79 |
| LS5 | 2.27 / 2.57 | 2.36 / 2.71 | 2.05 / 2.27 | 2.06 / 2.29 | 1.67 / 2.11 | 1.39 / 1.68 |
| LS6 | 2.40 / 2.53 | 2.50 / 2.44 | 2.04 / 2.29 | 2.05 / 2.27 | 1.76 / 2.24 | 1.39 / 1.85 |
| LS7 | 2.26 / 2.45 | 2.32 / 2.38 | 2.04 / 2.38 | 2.04 / 2.30 | 1.66 / 2.17 | 1.37 / 1.69 |
| mean simulated - measured | +10 % | +7 % | +14 % | +12 % | +27 % | +26 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 2.45 | 2.25 / 3.22 | 2.03 / 2.59 | 2.24 / 2.54 | 1.75 / 2.40 | 1.18 / 1.85 |
| LS4 | 2.65 / 2.45 | 2.15 / 2.36 | 2.02 / 1.95 | 1.95 / 2.09 | 2.06 / 2.24 | 2.06 / 2.29 |
| LS5 | 2.47 / 2.28 | 2.56 / 2.38 | 1.96 / 1.94 | 1.92 / 2.11 | 2.15 / 1.56 | 2.14 / 1.24 |
| LS6 | 2.10 / 3.55 | 2.49 / 2.90 | 2.10 / 2.42 | 2.10 / 2.45 | 1.52 / 1.50 | 1.22 / 1.22 |
| LS7 | 2.79 / 3.26 | 2.13 / 2.99 | 1.84 / 1.84 | 1.82 / 1.83 | 2.45 / 1.28 | 1.35 / 1.27 |
| mean simulated - measured | +13 % | +20 % | +8 % | +10 % | -6 % | +4 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -2.44 | -2.15 / -3.67 | 3.84 / 0.15 | 2.35 / 0.61 | 6.80 / 4.34 | 9.80 / 5.90 |
| LS4 | -0.01 / -0.21 | -5.26 / -1.06 | 2.82 / -0.03 | 1.88 / 0.80 | 5.14 / 4.91 | 7.04 / 6.80 |
| LS5 | 0.41 / -2.91 | -4.93 / -0.88 | 2.37 / 0.54 | 1.10 / 0.94 | 4.45 / 3.15 | 6.80 / 5.12 |
| LS6 | -0.70 / -3.02 | 0.71 / -0.45 | 0.76 / -0.03 | 2.42 / 1.73 | 7.45 / 4.39 | 8.64 / 5.10 |
| LS7 | -1.93 / -0.74 | -3.18 / -1.44 | 3.88 / -0.89 | 0.49 / -0.03 | 4.96 / 3.87 | 8.31 / 4.90 |
| mean simulated - measured | -1.3 dB | +1.5 dB | -2.8 dB | -0.8 dB | -1.6 dB | -2.6 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -1.68 | -4.52 / -3.39 | 0.59 / 0.15 | 3.93 / 3.24 | 8.36 / 2.95 | 16.72 / 4.94 |
| LS4 | -4.56 / -1.98 | -4.44 / -2.76 | 0.29 / -0.09 | 4.15 / 2.85 | 7.92 / 2.83 | 15.61 / 4.90 |
| LS5 | -3.84 / -2.95 | -4.77 / -2.93 | 0.38 / 0.32 | 4.39 / 2.61 | 7.87 / 2.88 | 15.64 / 5.15 |
| LS6 | -3.33 / -3.87 | -4.57 / -2.56 | -0.18 / -0.44 | 4.76 / 3.00 | 9.39 / 4.04 | 17.16 / 5.80 |
| LS7 | -5.53 / -3.02 | -3.72 / -3.10 | 0.49 / 0.32 | 3.23 / 2.78 | 7.35 / 3.97 | 15.37 / 5.65 |
| mean simulated - measured | +1.6 dB | +1.5 dB | -0.3 dB | -1.2 dB | -4.8 dB | -10.8 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.82; IACC_L measured 0.33, simulated 0.18; |ITD difference| 16 us; |ILD difference| 0.7 dB.
