# BRAS CR4: binaural check, AuralPaths (the web page itself, HRIR set FABIAN_HATO0.sofa) vs measured BRIRs (FABIAN)

Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted estimates with absorption calibrated on measured T30 (`config_cal.json`, calibrate.py; scattering as fitted; with 8 / 16 kHz when the calibration had them). 16000 rays per source; image sources, specular paths, late field and all other settings as the page's defaults. Sources: measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, LS7 horizontal). Simulated BRIRs: `bras_brir_CR4_FABIAN_K8data_cal16_LSk_sim.wav`.

## Direct sound and spatial measures

| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |
|---|---|---|---|---|
| LS3 | -68 / -62 | +2.0 / +1.7 | 0.82 / 0.89 | 0.22 / 0.11 |
| LS4 | -23 / -21 | +0.5 / -0.5 | 0.82 / 0.82 | 0.29 / 0.13 |
| LS5 | +45 / +42 | -1.4 / -1.2 | 0.83 / 0.77 | 0.38 / 0.10 |
| LS6 | +91 / +83 | -3.4 / -3.0 | 0.75 / 0.80 | 0.19 / 0.16 |
| LS7 | +23 / +0 | -0.3 / +0.2 | 0.92 / 0.84 | 0.56 / 0.14 |

ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the nearest HRIR of the set (no interpolation).

## T30 (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.36 / 2.10 | 2.37 / 2.27 | 2.03 / 2.07 | 2.01 / 2.10 | 1.77 / 1.89 | 1.45 / 1.50 |
| LS4 | 2.26 / 2.36 | 2.40 / 2.17 | 2.05 / 2.16 | 2.06 / 2.19 | 1.73 / 1.85 | 1.40 / 1.37 |
| LS5 | 2.27 / 2.19 | 2.36 / 2.31 | 2.05 / 1.96 | 2.06 / 2.08 | 1.67 / 1.76 | 1.39 / 1.29 |
| LS6 | 2.40 / 2.39 | 2.50 / 2.23 | 2.04 / 2.20 | 2.05 / 2.23 | 1.76 / 1.97 | 1.39 / 1.35 |
| LS7 | 2.26 / 2.46 | 2.32 / 2.21 | 2.04 / 2.18 | 2.04 / 2.17 | 1.66 / 1.82 | 1.37 / 1.34 |
| mean simulated - measured | -0 % | -6 % | +3 % | +5 % | +8 % | -2 % |

## EDT (s), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | 2.57 / 2.81 | 2.25 / 2.62 | 2.03 / 2.60 | 2.24 / 2.70 | 1.75 / 2.21 | 1.18 / 1.45 |
| LS4 | 2.65 / 1.85 | 2.15 / 2.29 | 2.02 / 2.07 | 1.95 / 2.00 | 2.06 / 2.26 | 2.06 / 1.79 |
| LS5 | 2.47 / 2.37 | 2.56 / 2.08 | 1.96 / 2.06 | 1.92 / 2.08 | 2.15 / 1.55 | 2.14 / 1.33 |
| LS6 | 2.10 / 2.06 | 2.49 / 2.52 | 2.10 / 2.33 | 2.10 / 2.07 | 1.52 / 1.37 | 1.22 / 1.44 |
| LS7 | 2.79 / 1.66 | 2.13 / 2.21 | 1.84 / 1.87 | 1.82 / 1.61 | 2.45 / 1.34 | 1.35 / 1.48 |
| mean simulated - measured | -14 % | +2 % | +10 % | +4 % | -9 % | -0 % |

## C80 (dB), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -0.43 / -1.21 | -2.15 / -5.14 | 3.84 / 1.50 | 2.35 / 1.86 | 6.80 / 5.38 | 9.80 / 8.86 |
| LS4 | -0.01 / -1.45 | -5.26 / -2.45 | 2.82 / 2.47 | 1.88 / 1.79 | 5.14 / 5.84 | 7.04 / 8.35 |
| LS5 | 0.41 / -0.08 | -4.93 / -4.12 | 2.37 / 1.24 | 1.10 / 1.79 | 4.45 / 4.62 | 6.80 / 5.87 |
| LS6 | -0.70 / -0.72 | 0.71 / -0.00 | 0.76 / 2.43 | 2.42 / 3.35 | 7.45 / 4.64 | 8.64 / 7.26 |
| LS7 | -1.93 / 1.45 | -3.18 / 0.15 | 3.88 / 4.16 | 0.49 / 2.14 | 4.96 / 5.46 | 8.31 / 6.71 |
| mean simulated - measured | +0.1 dB | +0.6 dB | -0.4 dB | +0.5 dB | -0.6 dB | -0.7 dB |

## spectrum_dB (dB re 250 Hz - 1 kHz), measured / simulated

| source | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|
| LS3 | -4.20 / -2.86 | -4.52 / -4.48 | 0.59 / 0.33 | 3.93 / 4.15 | 8.36 / 8.26 | 16.72 / 16.84 |
| LS4 | -4.56 / -3.36 | -4.44 / -4.41 | 0.29 / 0.34 | 4.15 / 4.06 | 7.92 / 8.34 | 15.61 / 16.57 |
| LS5 | -3.84 / -3.24 | -4.77 / -4.18 | 0.38 / -0.07 | 4.39 / 4.24 | 7.87 / 8.08 | 15.64 / 16.20 |
| LS6 | -3.33 / -5.18 | -4.57 / -4.23 | -0.18 / -0.27 | 4.76 / 4.50 | 9.39 / 8.36 | 17.16 / 16.65 |
| LS7 | -5.53 / -4.32 | -3.72 / -4.47 | 0.49 / 0.47 | 3.23 / 4.00 | 7.35 / 8.57 | 15.37 / 16.60 |
| mean simulated - measured | +0.5 dB | +0.1 dB | -0.2 dB | +0.1 dB | +0.1 dB | +0.5 dB |

Means over the five sources: IACC_E3 measured 0.83, simulated 0.82; IACC_L measured 0.33, simulated 0.13; |ITD difference| 8 us; |ILD difference| 0.5 dB.
