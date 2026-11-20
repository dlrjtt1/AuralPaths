# BRAS CR4: binaural check, AuralPaths (the web page itself, HRIR set FABIAN_HATO0.sofa) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_FABIAN_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -62 | +2.0 / +1.7 | 0.82 / 0.88 | 0.22 / 0.11 |
| LS4 | -23 / -21 | +0.5 / -0.5 | 0.82 / 0.82 | 0.29 / 0.12 |
| LS5 | +45 / +42 | -1.4 / -1.2 | 0.83 / 0.77 | 0.38 / 0.09 |
| LS6 | +91 / +83 | -3.4 / -3.0 | 0.75 / 0.80 | 0.19 / 0.14 |
| LS7 | +23 / +0 | -0.3 / +0.2 | 0.92 / 0.83 | 0.56 / 0.13 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 2.40 | 2.37 / 2.49 | 2.03 / 2.33 | 2.01 / 2.25 | 1.77 / 2.10 | 1.45 / 1.75 |
| LS4 | 2.26 / 2.51 | 2.40 / 2.45 | 2.05 / 2.37 | 2.06 / 2.38 | 1.73 / 2.11 | 1.40 / 1.72 |
| LS5 | 2.27 / 2.58 | 2.36 / 2.66 | 2.05 / 2.35 | 2.06 / 2.25 | 1.67 / 2.02 | 1.39 / 1.65 |
| LS6 | 2.40 / 2.64 | 2.50 / 2.45 | 2.04 / 2.34 | 2.05 / 2.37 | 1.76 / 2.21 | 1.39 / 1.79 |
| LS7 | 2.26 / 2.62 | 2.32 / 2.38 | 2.04 / 2.39 | 2.04 / 2.36 | 1.66 / 2.08 | 1.37 / 1.63 |
| mean simulated - measured | +10 % | +4 % | +15 % | +14 % | +22 % | +22 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 2.71 | 2.25 / 2.91 | 2.03 / 2.81 | 2.24 / 2.91 | 1.75 / 2.53 | 1.18 / 1.84 |
| LS4 | 2.65 / 2.24 | 2.15 / 2.73 | 2.02 / 2.26 | 1.95 / 2.09 | 2.06 / 2.51 | 2.06 / 2.43 |
| LS5 | 2.47 / 2.37 | 2.56 / 2.34 | 1.96 / 2.24 | 1.92 / 2.21 | 2.15 / 1.91 | 2.14 / 1.22 |
| LS6 | 2.10 / 2.59 | 2.49 / 2.97 | 2.10 / 2.61 | 2.10 / 2.35 | 1.52 / 1.72 | 1.22 / 1.48 |
| LS7 | 2.79 / 1.94 | 2.13 / 2.89 | 1.84 / 2.16 | 1.82 / 1.75 | 2.45 / 1.44 | 1.35 / 1.34 |
| mean simulated - measured | -4 % | +20 % | +21 % | +12 % | +5 % | +10 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -2.01 | -2.15 / -5.93 | 3.84 / 0.67 | 2.35 / 1.17 | 6.80 / 4.36 | 9.80 / 7.38 |
| LS4 | -0.01 / -2.13 | -5.26 / -3.20 | 2.82 / 1.75 | 1.88 / 1.21 | 5.14 / 4.93 | 7.04 / 7.11 |
| LS5 | 0.41 / -0.92 | -4.93 / -4.81 | 2.37 / 0.53 | 1.10 / 1.22 | 4.45 / 3.84 | 6.80 / 4.91 |
| LS6 | -0.70 / -1.46 | 0.71 / -0.88 | 0.76 / 1.68 | 2.42 / 2.79 | 7.45 / 4.01 | 8.64 / 6.41 |
| LS7 | -1.93 / 0.77 | -3.18 / -0.63 | 3.88 / 3.45 | 0.49 / 1.69 | 4.96 / 4.79 | 8.31 / 5.82 |
| mean simulated - measured | -0.6 dB | -0.1 dB | -1.1 dB | -0.0 dB | -1.4 dB | -1.8 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -2.78 | -4.52 / -4.24 | 0.59 / 0.24 | 3.93 / 4.00 | 8.36 / 8.09 | 16.72 / 16.62 |
| LS4 | -4.56 / -3.27 | -4.44 / -4.23 | 0.29 / 0.28 | 4.15 / 3.95 | 7.92 / 8.21 | 15.61 / 16.43 |
| LS5 | -3.84 / -3.13 | -4.77 / -3.98 | 0.38 / -0.12 | 4.39 / 4.10 | 7.87 / 7.93 | 15.64 / 16.06 |
| LS6 | -3.33 / -5.05 | -4.57 / -4.06 | -0.18 / -0.30 | 4.76 / 4.36 | 9.39 / 8.21 | 17.16 / 16.50 |
| LS7 | -5.53 / -4.25 | -3.72 / -4.30 | 0.49 / 0.39 | 3.23 / 3.91 | 7.35 / 8.46 | 15.37 / 16.53 |
| mean simulated - measured | +0.6 dB | +0.2 dB | -0.2 dB | -0.0 dB | +0.0 dB | +0.3 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.82; IACC_L measured 0.33, simulated 0.12; |ITD difference| 8 us; |ILD difference| 0.5 dB.
