# Scattering and the simulated effect of a reinforcement condition (2026-11-14, diagnostic)

Question: the absolute EDT and C80 of the simulation depend on the scattering coefficient of the hard surfaces by
about one JND ([arvedi_check.md](arvedi_check.md), [detmold_kh.md](detmold_kh.md), [opera_check.md](opera_check.md)),
and no measured scattering is known for these halls. Does the CHANGE that a reinforcement condition (delay and level
of the loudspeakers) makes to EDT and C80 depend on it as much? Engineering assumption to be tested: errors common to
both conditions cancel in the change.

## Plan (fixed before the run)

- Halls: OperaRIR, Detmold, Arvedi. Per hall the two calibrated configurations of the scattering test (default
  scattering, and 0.5 on the hard surfaces; each calibrated on the measured T30 by itself), the hall's measurement
  receivers (97, 34, 65).
- Sources (omnidirectional, positions in `scatter_delta.py`, chosen without a real installation): A on the stage
  centre line at the height of the measured sources; B_L / B_R at the front of the stage, 5.5 - 6 m to either side,
  2 - 3.5 m above the stage floor.
- Conditions as in `run.py`: delay of B so that it arrives 0, 30, 60 ms after A at the reference receiver (the
  receiver nearest the centroid of the receivers), level of B 0 and +6 dB relative to A there (energy in 500 Hz -
  1 kHz). Change Delta = metric(A + B) - metric(A alone) per receiver, EDT as ratio in %, C80 in dB, 500 Hz - 4 kHz.
- Compared: d = Delta(scattering 0.5) - Delta(default) per receiver. Ray noise: the default configuration again with
  another ray seed. 20000 rays in every run.
- Reading fixed in advance: the change is called robust to the scattering in a hall, condition and band when the
  mean of d is within half a JND (EDT 2.5 %, C80 0.5 dB) and at least 80 % of the receivers are within one JND, or,
  where the ray noise alone gives fewer than 80 %, when d is not further from zero than the noise.

## Run notes

- The first attempt ran all three runs of a hall in one process and did not fit the background time limit (Opera:
  about 2 h per run on one core). `scatter_delta.py` now caches the histograms of each (run, source) and can trace
  them in separate processes (`--only`); each `energy_hists` call sets the ray seed itself, so the result is the same
  as in one process. Positions, conditions, rays and seeds unchanged.
- The noise clause of the reading ("d is not further from zero than the noise") was not made operational in advance.
  Two readings are reported below, both with the half-JND condition on the mean of d: (a) share of receivers within
  1 JND for d at least that for the noise, (b) RMS of d over the receivers at most that of the noise. Both were chosen
  after the Arvedi result was seen and before the Opera and Detmold results were.

## Results (2026-11-15)

20000 rays, receivers 97 (OperaRIR), 34 (Detmold), 65 (Arvedi). Delta (default) is the effect of the condition
itself, averaged over the receivers. Ranges are over the four octave bands. Full per-receiver values:
`out/scatter_delta/<hall>/scatter_delta.csv` (not in the repository, derived from CC BY-NC data).

EDT (%): Delta(default) / mean d / mean noise / receivers within 1 JND, d vs noise; range over 500 Hz - 4 kHz

| condition | hall | Delta (default) | mean d | mean noise | within 1 JND: d / noise | rms d / noise |
|---|---|---|---|---|---|---|
| 0 ms / +0 dB | opera | -1.5 … +0.8 | +0.51 … +1.93 | +0.45 … +1.87 | 19–31 / 23–31 % | 13.81 … 15.14 / 13.00 … 16.36 |
| 0 ms / +0 dB | detmold | +0.3 … +1.1 | +0.86 … +1.25 | +3.73 … +4.06 | 35–47 / 38–50 % | 6.67 … 7.55 / 7.78 … 8.88 |
| 0 ms / +0 dB | arvedi | -7.0 … -6.1 | +1.80 … +2.58 | -0.96 … -0.57 | 63–66 / 65–74 % | 5.76 … 6.03 / 4.70 … 5.18 |
| 0 ms / +6 dB | opera | -1.1 … +2.2 | +1.13 … +3.17 | +1.14 … +2.66 | 13–18 / 12–25 % | 22.73 … 24.41 / 20.91 … 24.53 |
| 0 ms / +6 dB | detmold | +0.5 … +2.0 | +1.48 … +1.69 | +5.64 … +6.69 | 26–29 / 24–29 % | 10.40 … 11.44 / 12.49 … 13.76 |
| 0 ms / +6 dB | arvedi | -8.8 … -7.6 | +1.83 … +3.01 | -1.16 … -0.93 | 42–46 / 46–57 % | 8.78 … 9.13 / 6.85 … 7.51 |
| 30 ms / +0 dB | opera | -1.1 … +0.4 | +1.50 … +2.75 | +0.80 … +2.11 | 23–24 / 21–32 % | 15.98 … 17.25 / 14.06 … 18.45 |
| 30 ms / +0 dB | detmold | +2.8 … +5.4 | +0.96 … +1.10 | +3.46 … +4.42 | 29–47 / 32–44 % | 7.76 … 8.71 / 8.69 … 10.05 |
| 30 ms / +0 dB | arvedi | -15.2 … -13.0 | +0.72 … +1.22 | -1.02 … -0.58 | 66–72 / 68–69 % | 5.06 … 5.39 / 4.55 … 5.03 |
| 30 ms / +6 dB | opera | -0.6 … +1.5 | +1.75 … +3.65 | +1.56 … +2.94 | 13–18 / 13–24 % | 23.45 … 25.06 / 21.06 … 24.95 |
| 30 ms / +6 dB | detmold | +4.1 … +7.5 | +1.64 … +1.67 | +5.33 … +6.73 | 24–29 / 24–29 % | 10.93 … 12.07 / 12.94 … 14.14 |
| 30 ms / +6 dB | arvedi | -18.9 … -16.7 | +0.13 … +1.28 | -1.06 … -0.76 | 54–62 / 51–57 % | 7.21 … 7.57 / 6.12 … 7.00 |
| 60 ms / +0 dB | opera | +2.5 … +4.9 | +0.87 … +2.83 | +1.66 … +2.86 | 20–21 / 16–31 % | 18.45 … 19.81 / 15.80 … 21.53 |
| 60 ms / +0 dB | detmold | +8.6 … +14.6 | +0.44 … +0.84 | +3.69 … +4.92 | 29–38 / 35–41 % | 8.80 … 10.54 / 9.84 … 11.33 |
| 60 ms / +0 dB | arvedi | -14.8 … -12.9 | +0.21 … +0.45 | -1.18 … -0.85 | 65–71 / 60–65 % | 5.54 … 5.90 / 4.85 … 5.32 |
| 60 ms / +6 dB | opera | +4.0 … +6.3 | +1.64 … +3.63 | +2.35 … +3.78 | 11–14 / 11–21 % | 24.67 … 26.41 / 21.81 … 26.85 |
| 60 ms / +6 dB | detmold | +11.7 … +18.4 | +1.06 … +1.40 | +5.25 … +6.89 | 18–24 / 24–29 % | 11.71 … 13.36 / 13.73 … 14.80 |
| 60 ms / +6 dB | arvedi | -17.3 … -15.4 | +0.16 … +0.73 | -1.18 … -0.86 | 54–65 / 49–55 % | 7.22 … 7.56 / 6.12 … 6.91 |

C80 (dB): Delta(default) / mean d / mean noise / receivers within 1 JND, d vs noise; range over 500 Hz - 4 kHz

| condition | hall | Delta (default) | mean d | mean noise | within 1 JND: d / noise | rms d / noise |
|---|---|---|---|---|---|---|
| 0 ms / +0 dB | opera | -0.5 … -0.4 | -0.09 … -0.04 | +0.03 … +0.05 | 66–71 / 65–68 % | 1.02 … 1.05 / 1.03 … 1.13 |
| 0 ms / +0 dB | detmold | -0.6 … -0.6 | +0.14 … +0.17 | -0.11 … -0.09 | 91–94 / 94–94 % | 0.67 … 0.71 / 0.54 … 0.56 |
| 0 ms / +0 dB | arvedi | -0.0 … +0.0 | +0.31 … +0.36 | -0.01 … -0.00 | 100–100 / 100–100 % | 0.46 … 0.50 / 0.28 … 0.29 |
| 0 ms / +6 dB | opera | -0.5 … -0.4 | -0.11 … -0.05 | +0.04 … +0.06 | 44–46 / 48–52 % | 1.52 … 1.57 / 1.57 … 1.72 |
| 0 ms / +6 dB | detmold | -0.9 … -0.8 | +0.23 … +0.27 | -0.17 … -0.13 | 68–74 / 74–76 % | 1.04 … 1.10 / 0.83 … 0.86 |
| 0 ms / +6 dB | arvedi | +0.0 … +0.1 | +0.58 … +0.66 | -0.02 … -0.01 | 68–78 / 95–98 % | 0.78 … 0.85 / 0.45 … 0.47 |
| 30 ms / +0 dB | opera | -1.4 … -1.3 | +0.02 … +0.13 | -0.01 … -0.00 | 69–72 / 70–73 % | 0.97 … 1.03 / 0.96 … 1.08 |
| 30 ms / +0 dB | detmold | -2.0 … -1.8 | +0.13 … +0.16 | -0.12 … -0.10 | 85–88 / 94–94 % | 0.71 … 0.77 / 0.54 … 0.58 |
| 30 ms / +0 dB | arvedi | -0.5 … -0.4 | +0.35 … +0.40 | -0.04 … -0.03 | 95–98 / 100–100 % | 0.50 … 0.54 / 0.29 … 0.30 |
| 30 ms / +6 dB | opera | -2.2 … -2.0 | -0.04 … +0.08 | +0.00 … +0.02 | 47–52 / 49–55 % | 1.51 … 1.58 / 1.46 … 1.59 |
| 30 ms / +6 dB | detmold | -3.1 … -3.0 | +0.18 … +0.22 | -0.19 … -0.15 | 71–71 / 74–74 % | 1.15 … 1.23 / 0.83 … 0.87 |
| 30 ms / +6 dB | arvedi | -0.7 … -0.7 | +0.55 … +0.63 | -0.06 … -0.05 | 72–75 / 97–98 % | 0.78 … 0.84 / 0.44 … 0.46 |
| 60 ms / +0 dB | opera | -3.2 … -2.9 | +0.09 … +0.37 | -0.10 … -0.08 | 65–73 / 74–79 % | 0.87 … 1.02 / 0.83 … 1.01 |
| 60 ms / +0 dB | detmold | -3.8 … -3.5 | +0.18 … +0.24 | -0.13 … -0.11 | 91–94 / 85–91 % | 0.57 … 0.64 / 0.56 … 0.61 |
| 60 ms / +0 dB | arvedi | -1.3 … -1.2 | +0.15 … +0.21 | -0.03 … -0.01 | 98–100 / 100–100 % | 0.40 … 0.44 / 0.30 … 0.32 |
| 60 ms / +6 dB | opera | -5.1 … -4.7 | -0.02 … +0.30 | -0.08 … -0.06 | 55–58 / 57–64 % | 1.32 … 1.42 / 1.20 … 1.38 |
| 60 ms / +6 dB | detmold | -6.4 … -6.0 | +0.19 … +0.26 | -0.19 … -0.15 | 74–74 / 79–79 % | 0.92 … 0.99 / 0.85 … 0.89 |
| 60 ms / +6 dB | arvedi | -2.0 … -1.9 | +0.25 … +0.34 | -0.03 … -0.01 | 82–85 / 95–97 % | 0.62 … 0.69 / 0.45 … 0.47 |

### Reading (as fixed in advance)

| | OperaRIR | Detmold | Arvedi |
|---|---|---|---|
| ray noise alone, receivers within 1 JND | EDT 11 - 32 %, C80 48 - 79 % | EDT 24 - 50 %, C80 74 - 94 % | EDT 46 - 74 %, C80 95 - 100 % |
| C80, B at 0 dB | not shown (noise < 80 %; mean d -0.09 … +0.37 dB) | robust (85 - 94 % within 1 JND, mean d ≤ 0.24 dB) | robust (95 - 100 %, mean d ≤ 0.40 dB) |
| C80, B at +6 dB | not shown (noise < 80 %; mean d -0.11 … +0.30 dB) | not shown (noise < 80 %; mean d ≤ 0.27 dB) | NOT robust at 0 and 30 ms (mean d +0.55 … +0.66 dB, 68 - 75 % within 1 JND against 95 - 98 % from the noise); robust at 60 ms |
| EDT | not shown (noise < 80 %) | not shown (noise < 80 %) | not shown (noise < 80 %) |

"Not shown": the ray noise alone puts fewer than 80 % of the receivers within 1 JND, and under either reading of the
noise clause most cells fail by a few percent or a few tenths of the RMS, so the test cannot tell a small scattering
dependence from the ray noise there. It is not evidence of robustness.

### What can still be said

- Systematic part (mean of d over the receivers, which averages the ray noise down): C80 within half a JND in every
  hall, condition and band except Arvedi with B at +6 dB and 0 or 30 ms (+0.55 … +0.66 dB, all positive: with
  scattering 0.5 the reinforcement lowers C80 less). EDT: +0.1 … +3.7 %, always positive, of the same size as the
  mean of the seed-to-seed noise in OperaRIR (+0.5 … +3.8 %) and smaller than it in Detmold (+3.5 … +6.9 %).
- The ray noise is the larger problem for the study: at 20000 rays the per-receiver noise of the condition effect
  is about 1 JND or more for EDT in all three halls (RMS 5 - 26 %) and for C80 in OperaRIR (RMS 0.8 - 1.7 dB), and
  in Detmold the hall mean of the EDT effect moves by +3.5 … +6.9 % between two seeds. Per-seat effects of a
  condition need more rays, several seeds, or reporting over groups of receivers.
- Engineering setup only: omnidirectional sources at chosen positions, not a real installation; the result says
  how the simulator's condition effect depends on its scattering input, not how a hall responds.
