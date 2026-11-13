# Arni variable-acoustics room: early decay where the absorption is known (2026-11-13)

Question: in Arvedi the measured EDT is 15 - 20 % shorter than T30 and the simulated EDT is about T30. Does the engine
produce an early decay faster than the late one at all, when the absorption sits in known places? And does it follow
where the absorption is?

Data: Arni at the Aalto Acoustics Lab, https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0); the part numClosed 46 - 55
(853 panel combinations, 5 microphones, up to 5 sweeps each). Room and panels: Prawda, Schlecht, Valimaki 2021,
https://acris.aalto.fi/ws/portalfiles/portal/76717691/2021_ArniMeasurements_Akupaivat_Prawda_paper.pdf (8.9 x 6.3 x
3.6 m; 55 panels 0.6 x 0.4 x 2.4 m with fronts open (absorptive) or closed (reflective); published octave absorption
250 Hz - 8 kHz of both states).

Method (`validation/arni_model.py`, `validation/arni_check.py`):
- The measured RIRs are reduced to octave-band energy histograms on the data side (`arni_hist.py`, as
  `validate_bras_cr.measured_hist`, energy mean over the sweeps, onset moved to the geometric direct-sound time).
- Model: shoebox with the 55 panels as boxes at the drawn positions, ceiling panels flush with the ceiling (assumed),
  four folded curtains as 0.5 x 0.5 m columns (assumed). Panel fronts: the published open / closed absorption, 125 Hz
  set equal to 250 Hz (not published). Scattering: fronts 0.10, bare surfaces 0.05, curtains 0.5 (assumed).
- Calibration: only the bare surfaces and the curtains, one factor per band, on the T30 of the all-closed state
  (combination 0, 5 microphones). Result: bare surfaces alpha 0.03 - 0.13, curtains 0.68 - 0.95 (at the 0.95 limit in
  five bands, so the unknown absorption of the room is larger than these two groups were meant to hold).
- Prediction without further calibration: 36 combinations (4 per number of closed panels 46 - 54: the ones with the
  fewest and the most open ceiling panels, two at random, seed 1), plus the calibration state; 10000 rays, image
  sources order 2.

## Results (185 combination x microphone pairs)

| | 125 | 250 | 500 | 1k | 2k | 4k Hz |
|---|---|---|---|---|---|---|
| T30 bias | +10 % | +23 % | +7 % | 0 % | -1 % | -5 % |
| EDT bias | +1 % | +19 % | +4 % | -2 % | -3 % | -6 % |
| EDT / T30 measured | 1.00 | 0.93 | 0.91 | 0.92 | 0.95 | 0.96 |
| EDT / T30 simulated | 0.89 | 0.87 | 0.88 | 0.91 | 0.93 | 0.95 |
| C80 bias | +0.46 | -0.85 | +0.32 | +0.25 | +0.58 | +0.29 dB |
| C80 within 1 dB | 40 % | 49 % | 55 % | 91 % | 80 % | 92 % |
| EDT within 5 % | 25 % | 10 % | 29 % | 68 % | 62 % | 30 % |

- The engine does produce an early decay faster than the late one here: simulated EDT / T30 0.87 - 0.95, measured 0.91 -
  0.96 at 250 Hz - 4 kHz. The Arvedi result (simulated EDT / T30 about 1.0) is therefore not a general property of the
  engine; what in the Arvedi model removes it (absorber placement, the seating model, the geometry) is still open.
- 500 Hz - 4 kHz: predicted states within -6 ... +7 % in T30 and EDT on average, C80 within 0.6 dB on average.
- 250 Hz (and 125 Hz) are off by about +20 %: the paper reports that the panels act almost as bass traps at low
  frequencies (largest EDT and T20 changes at 250 and 500 Hz between 54 and 55 closed panels), which the published
  absorption of the closed state (0.09 at 250 Hz) does not describe, and 125 Hz has no published value. Read as a limit of
  the material data, not tested against the engine.

Where the absorption is (within the same number of closed panels, measured vs simulated deviation of each combination
from the mean of its group, microphone means):

| | 500 Hz | 1 kHz | 2 kHz |
|---|---|---|---|
| EDT: correlation | 0.69 | 0.11 | 0.12 |
| EDT: spread measured / simulated | 4.7 / 2.8 % | 1.9 / 1.9 % | 1.6 / 1.2 % |
| C80: correlation | 0.60 | 0.41 | 0.35 |
| C80: spread measured / simulated | 0.39 / 0.14 dB | 0.15 / 0.11 dB | 0.15 / 0.09 dB |

| most minus fewest open ceiling panels (9 groups) | 500 Hz | 1 kHz | 2 kHz |
|---|---|---|---|
| EDT measured / simulated | -6.9 / -5.3 % | -0.7 / -3.2 % | -0.9 / -1.5 % |
| T30 measured / simulated | -4.7 / -13.9 % | -2.1 / -9.4 % | +3.0 / -4.9 % |

- At 500 Hz the simulation follows where the absorption is (correlation 0.6 - 0.7) but with about half the measured
  spread. At 1 - 2 kHz the measured effect of the distribution is 1 - 2 % in EDT and 0.15 dB in C80, below one JND and
  close to the repeatability of the measurement; the low correlation there says little.
- The model makes absorption on the ceiling too effective for the late decay: moving the open panels to the ceiling
  shortens the simulated T30 by 5 - 14 %, the measured one by -3 ... +5 %. Possible reasons, not tested: the ceiling
  panels hang below the ceiling in the room (flush in the model), the floor - ceiling path dominates the late decay of a
  low room more in the model than in the room.

Status: post hoc (the measured mean T30 per number of closed panels was looked at before the run); diagnostic for the
Arvedi EDT question. Derived histograms and simulated results stay in `out/arni/` (not in the repository).
