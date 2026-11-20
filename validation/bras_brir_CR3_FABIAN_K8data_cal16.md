# BRAS CR3: binaural check, AuralPaths (the web page itself, HRIR set FABIAN_HATO0.sofa) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted; with 8 / 16 kHz when the calibration had them). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR3_FABIAN_K8data_cal16_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -45 / -62 | +2.4 / +1.6 | 0.48 / 0.33 | 0.10 / 0.13 |
| LS4 | -23 / +0 | +0.8 / -0.3 | 0.44 / 0.45 | 0.11 / 0.11 |
| LS5 | +45 / +42 | -1.2 / -2.1 | 0.50 / 0.24 | 0.14 / 0.15 |
| LS6 | +91 / +83 | -2.6 / -3.7 | 0.42 / 0.40 | 0.15 / 0.11 |
| LS7 | +23 / +21 | -0.2 / -0.8 | 0.73 / 0.47 | 0.29 / 0.09 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.67 / 1.77 | 1.46 / 1.77 | 1.41 / 1.46 | 1.34 / 1.42 | 1.38 / 1.31 | 1.15 / 1.06 |
| LS4 | 1.45 / 1.70 | 1.50 / 1.62 | 1.38 / 1.33 | 1.32 / 1.24 | 1.34 / 1.14 | 1.15 / 0.92 |
| LS5 | 1.61 / 1.61 | 1.45 / 1.55 | 1.40 / 1.42 | 1.36 / 1.45 | 1.35 / 1.34 | 1.14 / 1.10 |
| LS6 | 1.67 / 1.38 | 1.49 / 1.41 | 1.31 / 1.27 | 1.34 / 1.27 | 1.34 / 1.28 | 1.15 / 1.10 |
| LS7 | 1.56 / 1.57 | 1.51 / 1.41 | 1.39 / 1.37 | 1.37 / 1.27 | 1.36 / 1.23 | 1.14 / 1.03 |
| mean simulated - measured | +1 % | +5 % | -0 % | -1 % | -7 % | -9 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 1.75 / 2.12 | 1.56 / 1.50 | 1.39 / 1.44 | 1.35 / 1.26 | 1.27 / 1.11 | 1.29 / 1.04 |
| LS4 | 1.75 / 1.43 | 1.60 / 1.32 | 1.23 / 1.16 | 1.45 / 1.18 | 1.32 / 1.51 | 1.25 / 1.37 |
| LS5 | 1.30 / 1.95 | 1.41 / 1.46 | 1.27 / 1.25 | 1.39 / 1.16 | 1.30 / 1.06 | 1.21 / 0.81 |
| LS6 | 1.43 / 1.89 | 1.54 / 1.75 | 1.39 / 1.61 | 1.30 / 1.28 | 1.41 / 1.05 | 1.22 / 0.97 |
| LS7 | 1.49 / 1.83 | 1.47 / 1.69 | 1.21 / 1.38 | 1.33 / 1.28 | 1.12 / 1.25 | 1.19 / 1.11 |
| mean simulated - measured | +22 % | +2 % | +5 % | -9 % | -6 % | -14 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.95 / -0.91 | -1.55 / -0.86 | 2.14 / 0.66 | 1.79 / 2.31 | 5.37 / 3.74 | 4.40 / 5.53 |
| LS4 | -1.38 / -2.45 | -1.46 / -0.32 | 1.46 / 1.56 | 1.85 / 0.42 | 4.73 / 2.71 | 4.45 / 4.68 |
| LS5 | -1.63 / -0.14 | -1.04 / -0.67 | 1.90 / 1.80 | 2.07 / 2.30 | 4.99 / 4.18 | 4.42 / 6.02 |
| LS6 | -2.51 / -3.47 | 1.35 / -0.42 | 0.24 / 1.29 | 0.99 / 0.90 | 5.18 / 4.18 | 5.34 / 6.24 |
| LS7 | -0.26 / -3.73 | 0.75 / -1.15 | 1.87 / 2.28 | 2.12 / 0.23 | 5.03 / 3.19 | 5.67 / 5.12 |
| mean simulated - measured | -0.8 dB | -0.3 dB | -0.0 dB | -0.5 dB | -1.5 dB | +0.7 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -2.22 / -3.11 | -3.01 / -3.64 | -0.85 / -0.50 | 3.85 / 4.14 | 8.92 / 8.15 | 16.31 / 15.87 |
| LS4 | -2.29 / -3.37 | -3.28 / -3.82 | -0.66 / -0.06 | 3.93 / 3.88 | 9.26 / 7.90 | 16.59 / 15.76 |
| LS5 | -2.67 / -2.66 | -2.99 / -3.48 | -0.45 / -0.46 | 3.44 / 3.93 | 8.69 / 7.61 | 18.20 / 15.91 |
| LS6 | -2.77 / -4.10 | -2.35 / -3.49 | 0.22 / -0.36 | 2.13 / 3.85 | 9.30 / 8.16 | 19.21 / 16.17 |
| LS7 | -1.98 / -4.46 | -3.14 / -4.14 | -0.53 / 0.30 | 3.67 / 3.84 | 8.86 / 8.04 | 16.69 / 16.27 |
| mean simulated - measured | -1.2 dB | -0.8 dB | +0.2 dB | +0.5 dB | -1.0 dB | -1.4 dB |

Means over the five sources: IACC_E3 measured 0.52, simulated 0.38; IACC_L measured 0.16, simulated 0.12; |ITD difference| 11 us; |ILD difference| 0.9 dB.
