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
