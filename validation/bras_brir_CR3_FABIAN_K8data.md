# BRAS CR3: binaural check, AuralPaths (the web page itself, HRIR set FABIAN_HATO0.sofa) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates, unchanged (not calibrated). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_FABIAN_K8data_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -62 | +2.4 / +1.6 | 0.48 / 0.33 | 0.10 / 0.13 |
| LS4 | -23 / +0 | +0.8 / -0.3 | 0.44 / 0.44 | 0.11 / 0.11 |
| LS5 | +45 / +42 | -1.2 / -2.1 | 0.50 / 0.24 | 0.14 / 0.15 |
| LS6 | +91 / +83 | -2.6 / -3.7 | 0.42 / 0.40 | 0.15 / 0.11 |
| LS7 | +23 / +21 | -0.2 / -0.8 | 0.73 / 0.46 | 0.29 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 1.92 | 1.46 / 1.80 | 1.41 / 1.47 | 1.34 / 1.50 | 1.38 / 1.39 | 1.15 / 1.10 |
| LS4 | 1.45 / 1.82 | 1.50 / 1.68 | 1.38 / 1.34 | 1.32 / 1.34 | 1.34 / 1.24 | 1.15 / 0.97 |
| LS5 | 1.61 / 1.73 | 1.45 / 1.57 | 1.40 / 1.43 | 1.36 / 1.51 | 1.35 / 1.43 | 1.14 / 1.12 |
| LS6 | 1.67 / 1.56 | 1.49 / 1.44 | 1.31 / 1.27 | 1.34 / 1.33 | 1.34 / 1.33 | 1.15 / 1.12 |
| LS7 | 1.56 / 1.76 | 1.51 / 1.43 | 1.39 / 1.38 | 1.37 / 1.33 | 1.36 / 1.29 | 1.14 / 1.06 |
| mean simulated - measured | +11 % | +7 % | +0 % | +4 % | -1 % | -6 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 2.24 | 1.56 / 1.52 | 1.39 / 1.45 | 1.35 / 1.33 | 1.27 / 1.16 | 1.29 / 1.05 |
| LS4 | 1.75 / 1.68 | 1.60 / 1.33 | 1.23 / 1.15 | 1.45 / 1.21 | 1.32 / 1.51 | 1.25 / 1.39 |
| LS5 | 1.30 / 2.08 | 1.41 / 1.46 | 1.27 / 1.25 | 1.39 / 1.22 | 1.30 / 1.11 | 1.21 / 0.83 |
| LS6 | 1.43 / 2.04 | 1.54 / 1.75 | 1.39 / 1.62 | 1.30 / 1.37 | 1.41 / 1.10 | 1.22 / 1.00 |
| LS7 | 1.49 / 2.04 | 1.47 / 1.69 | 1.21 / 1.39 | 1.33 / 1.34 | 1.12 / 1.27 | 1.19 / 1.14 |
| mean simulated - measured | +33 % | +3 % | +5 % | -5 % | -3 % | -12 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -1.46 | -1.55 / -0.88 | 2.14 / 0.64 | 1.79 / 2.03 | 5.37 / 3.45 | 4.40 / 5.29 |
| LS4 | -1.38 / -2.94 | -1.46 / -0.33 | 1.46 / 1.54 | 1.85 / 0.15 | 4.73 / 2.41 | 4.45 / 4.40 |
| LS5 | -1.63 / -0.69 | -1.04 / -0.69 | 1.90 / 1.78 | 2.07 / 1.99 | 4.99 / 3.82 | 4.42 / 5.72 |
| LS6 | -2.51 / -4.00 | 1.35 / -0.45 | 0.24 / 1.27 | 0.99 / 0.60 | 5.18 / 3.84 | 5.34 / 5.95 |
| LS7 | -0.26 / -4.29 | 0.75 / -1.18 | 1.87 / 2.25 | 2.12 / -0.02 | 5.03 / 2.91 | 5.67 / 4.88 |
| mean simulated - measured | -1.3 dB | -0.3 dB | -0.0 dB | -0.8 dB | -1.8 dB | +0.4 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -2.76 | -3.01 / -3.70 | -0.85 / -0.56 | 3.85 / 4.25 | 8.92 / 8.23 | 16.31 / 15.90 |
| LS4 | -2.29 / -3.03 | -3.28 / -3.88 | -0.66 / -0.12 | 3.93 / 4.00 | 9.26 / 7.98 | 16.59 / 15.80 |
| LS5 | -2.67 / -2.30 | -2.99 / -3.54 | -0.45 / -0.53 | 3.44 / 4.07 | 8.69 / 7.72 | 18.20 / 15.96 |
| LS6 | -2.77 / -3.70 | -2.35 / -3.56 | 0.22 / -0.43 | 2.13 / 3.99 | 9.30 / 8.25 | 19.21 / 16.21 |
| LS7 | -1.98 / -4.05 | -3.14 / -4.21 | -0.53 / 0.23 | 3.67 / 3.98 | 8.86 / 8.13 | 16.69 / 16.30 |
| mean simulated - measured | -0.8 dB | -0.8 dB | +0.2 dB | +0.7 dB | -0.9 dB | -1.4 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.37; IACC_L measured 0.16, simulated 0.12; |ITD difference| 11 us; |ILD difference| 0.9 dB.
