# Ray noise of the room criteria against the number of rays (2026-11-15, diagnostic)

Reason: [scatter_delta.md](scatter_delta.md) found the seed-to-seed noise of the criteria at 20000 rays to be about
1 JND or more per receiver. Fixed before the run: Detmold, default calibrated configuration, source A of
`scatter_delta.py` alone, the 34 measurement receivers, 20000 / 80000 / 320000 rays, ray seeds 1 and 2
(`validation/ray_noise.py`).

Seed 2 against seed 1 at 1 kHz (the other bands are alike; full table `out/noise_rays/detmold.log`, not in the
repository):

| rays | EDT: RMS over receivers / hall mean | C80: RMS / hall mean | T30: RMS / hall mean | time per source |
|---|---|---|---|---|
| 20000 | 11.1 % / -4.4 % | 0.93 dB / +0.27 dB | 22.8 % / +9.6 % | 75 s |
| 80000 | 8.0 % / +2.6 % | 0.47 dB / -0.01 dB | 12.1 % / -1.7 % | about 5 min |
| 320000 | 2.9 % / +0.6 % | 0.27 dB / 0.00 dB | 6.0 % / -0.2 % | 18 min |

Hall means at 1 kHz (seed 1, seed 2): EDT 1.475, 1.400 s (20000 rays); 1.411, 1.442 s (80000); 1.432, 1.439 s
(320000). C80 0.74, 1.01 dB; 1.00, 0.99 dB; 0.99, 0.99 dB. T30 1.495, 1.617 s; 1.551, 1.507 s; 1.548, 1.543 s.

Reading:
- The noise falls roughly with the square root of the ray count (C80 exactly: 0.93, 0.47, 0.27 dB).
- No drift of the hall means with the ray count beyond the noise: no sign of a bias from clipping the ray residual
  at zero (`energy_hists`) at these ray counts.
- The noise is common to the receivers (all receivers share the rays): at 20000 rays the HALL MEAN of T30 differs
  by 5 - 10 % and that of EDT by about 4 % between two seeds, so averaging over receivers does not remove it.
  The T30 calibrations of the hall checks used one seed at 20000 rays (Detmold, Arvedi) or 5000 rays (OperaRIR);
  their calibrated absorption carries this uncertainty, and differences of a few percent in EDT or T30 between
  configurations in those checks are inside it.
- Per receiver, half a JND (EDT 2.5 %, C80 0.5 dB) needs about 80000 rays for C80 and more than 320000 for EDT in
  this hall.

One hall, one source, two seeds: the size of the noise in other halls is taken from `scatter_delta.md` (OperaRIR
larger, Arvedi smaller), its scaling there is not tested.

## Calibration and comparison at 20000 and 80000 rays (2026-11-15)

Detmold, same procedure twice with only `geometry.rays` changed (fixed before the run): `calibrate.py` (4 iterations,
24 positions, each traced by itself), `detmold_kh.py render` (S2, S3, S6, S7) and `compare` (136 pairs). Mean
difference simulation - measurement:

| | 20000 rays | 80000 rays |
|---|---|---|
| C80 500 / 1k / 2k Hz | +0.32 / +0.70 / +1.41 dB | +1.43 / +2.28 / +2.66 dB |
| EDT 500 / 1k / 2k Hz | -2.9 / -5.9 / -11.4 % | -16.5 / -23.6 / -28.0 % |
| IACC_E3 | -0.106 | -0.078 |
| calibration factor on absorption, 500 / 1k / 2k Hz | 0.80 / 0.74 / 0.79 | 1.00 / 1.00 / 1.00 |

The 80000 result is NOT the effect of the ray count on the rendering; the calibration differed. With the
uncalibrated materials the mean T30 over the 24 positions is 1.35 s (20000) and 1.52 s (80000) at 1 kHz, the mean
EDT 1.24 and 1.22 s. The 80000 mean is carried by 4 of 24 positions with T30 of 1.95 - 2.83 s (median 1.39 s;
20000: one position at 2.28 s, median 1.34 s), so at 80000 rays the mean T30 already met the measured 1.55 s, the
absorption was left unchanged and EDT stayed short.

Check (uncalibrated materials, 8 of the 24 positions, 1 kHz, same seed per position): T30 of one position is
1.50 / 2.83 / 1.42 s and of another 1.02 / 1.97 / 1.45 s at 20000 / 80000 / 320000 rays, while EDT moves by 0.1 s
at most; mean T30 of the 8 positions 1.39 / 1.60 / 1.35 s. The Schroeder curve of such a position is -22 dB at 0.5 s
at every ray count and -64 / -32 / -48 dB at 1 s: the late part of a single-position histogram holds too few rays
(receiver radius 0.5 m), and T30 (-5 to -35 dB) reaches into it.

Reading:
- T30 of a single position is not reliable at 20000 or 80000 rays, and the MEAN over positions used by
  `calibrate.py` is not robust against the outliers. The calibrated absorption of the hall checks depends on this
  (a factor of 0.74 or 1.00 at 1 kHz from the same data).
- Whether 80000 rays change the agreement with the measurement is not answered by this run. It needs a calibration
  that is robust first (for example the median over positions, T30 from the summed decay of the positions, or
  more rays for the calibration); not changed here.
