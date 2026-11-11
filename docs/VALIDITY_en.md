# What AuralPaths has been checked for (version 0.7.0)

A short summary of the checks in `docs/MODEL_en.md`, written for someone deciding whether AuralPaths BRIRs can be
used for a given purpose, for example stimuli for a listening test on the precedence effect with delayed loudspeaker
(PA) paths. Every number below comes from a section of `docs/MODEL_en.md` (named in brackets), where the method,
the data and the commands are given. AuralPaths 0.7.0 is archived as https://doi.org/10.5281/zenodo.24053630.

Measured data used: BRAS CR3 / CR4 (Aspöck et al. 2020, [doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3),
CC BY-SA 4.0) and the Fratoni dataset (Mendeley Data, [doi:10.17632/y7xnv6xg5s.1](https://doi.org/10.17632/y7xnv6xg5s.1),
CC BY 4.0). Two real halls with RIRs per position and BRIRs at one listener position, and four halls with room
criteria averaged over receivers. That is a small sample; the results describe these halls, not halls in general.

## 1. Checked and in agreement

| What | Result | Section in MODEL_en.md |
|---|---|---|
| Direct-sound arrival time | measured onset within −0.67 … +0.07 ms of distance / c at all 20 BRAS position pairs | Position-by-position check |
| Direct-sound ITD and ILD | within 14–18 µs and 0.8–0.9 dB of the measured BRIRs with the KU100 head; 0–5 µs and 0.3–0.5 dB with the measurement's head (FABIAN) (5 loudspeakers × 2 halls) | Binaural check against measured BRIRs |
| Octave spectrum at the binaural listener, same head and loudspeaker as the measurement | within 1.4 dB, 125 Hz–4 kHz (relative to 250 Hz–1 kHz) | Binaural check against measured BRIRs |
| ITDG and level ratio set by the stimulus builder | equal to the nominal values at the reference seat (0.000 ms, 0.000 dB); files rebuilt independently to 1.5·10⁻⁵ | Stimuli for the listening tests |
| Browser page vs Python | C80 / D50 / EDT / T30 within 0.007 dB / 0.001 / 0.001 s / 0.001 s; IACC_E3 within 0.035 (shoebox, 36 conditions) | Browser vs Python |
| Reverberation after calibration on measured T30 | held-out positions within 0.8 JND in T30 (BRAS CR3 and CR4) | Position-by-position check |
| Room criteria with another program's calibrated inputs | ULH: all criteria within about 1 JND at 500 Hz–4 kHz; DUS: T30 within about 1 JND at mid frequencies | Room criteria against measured halls; The two opera houses |
| Against an independent simulator (I-Simpa SPPS) | diffuse box within 0–4 %, CR4 within about 1–2 JND | Comparison with an independent free simulator |

## 2. Checked, with known deviations

| What | Result | Section |
|---|---|---|
| T30 without calibration | 8–11 % long with Eyring-fitted coefficients (BRAS RIRs); 15–25 % long in CR4 in the binaural check | Position-by-position check; Binaural check |
| First-order reflection levels | median +1.6 dB (CR3) and +2.7 dB (CR4) re measured; reflection by reflection poor in CR4 | Position-by-position check |
| Early energy and clarity at the binaural listener | C80 1–4 dB low at 500 Hz–1 kHz; in CR4 13–20 % of the 0–80 ms energy at 20–50 ms against 5–9 % measured (mainly the ceiling panels; cause not established) | Binaural check |
| Early interaural cross-correlation, IACC_E3 | too low: 0.34 vs 0.52 (CR3) and 0.59 vs 0.83 (CR4) with the measured loudspeaker directivity | Binaural check |
| Late interaural cross-correlation, IACC_L | a third to a half of the measured value (the late part is rendered as an ideal diffuse field) | Binaural check; Late interaural coherence |
| Halls far from the inputs' assumptions | STC about 15 % long; TCB (box-tier opera house) decays too fast and is not counted as a successful check | Room criteria against measured halls; The two opera houses |
| Drawn 2.5D halls | reverberation and clarity within a few JND, but individual early reflections of a hall with balconies are not reproduced | Position-by-position check |

## 3. Not checked or not modelled

- Whether listeners hear simulated and measured BRIRs of the same hall as equivalent: no listening test has
  compared them. The checks above are physical, not perceptual.
- Seat dip: without the optional seat-dip model (BRAS RS7: no 500 Hz dip; behind the first row 5–11 dB too
  loud); with it, RS7 within 3.0–3.3 dB in sight of the source and 3.4–6.7 dB behind the first block, the 500 Hz dip
  only in part, generic seats, not checked in a real hall (`docs/MODEL_en.md`, *Seat dip*). Diffraction beyond
  second order (second order is opt-in and checked only on BRAS RS6), edge end points, seats as geometry.
- Loudspeaker frequency responses (only directivity patterns are modelled); individual HRTFs (KU100 only, nearest
  HRIR, no interpolation).
- Halls other than the six above, and seat positions other than those measured.

## 4. What this means for use

- Timing and direction of the direct sound and of the delayed PA path, and the ITDG and level ratio of a stimulus,
  are the best-supported parts. Stimuli whose experimental variable is the delay or the level of a path rest on these.
- Reverberation should be calibrated on measured T30 of the hall at hand (`calibrate.py`) before T30, EDT or C80
  are reported as properties of that hall.
- Early reflections of a specific hall (their level and timing seat by seat) should be checked against a
  measurement of that hall before results depend on them.
- Spatial impression (IACC_E3, IACC_L) is under-estimated in both measured halls; results that depend on it
  should say so or use measured BRIRs.
- A simulated BRIR is a model of a hall, and a listening test with it is a laboratory test. Findings from such
  tests do not by themselves show what happens with real sound reinforcement in a real hall.
