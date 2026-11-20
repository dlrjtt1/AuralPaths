# What AuralPaths has been checked for (version 0.9.0)

A short summary of the checks in `docs/MODEL_en.md`, written for someone deciding whether AuralPaths BRIRs can be
used for a given purpose, for example stimuli for a listening test on the precedence effect with delayed loudspeaker
(PA) paths. Every number below comes from a section of `docs/MODEL_en.md` (named in brackets), where the method,
the data and the commands are given. AuralPaths 0.9.0 is archived as https://doi.org/10.5281/zenodo.24386517 (0.8.1: https://doi.org/10.5281/zenodo.24243050; 0.7.0: https://doi.org/10.5281/zenodo.24053630; section 5 lists what was added since). A table of uses with a verdict for each (usable, conditional, not supported) and the comparison with the 2019 round-robin programs: [BENCHMARK_en.md](BENCHMARK_en.md), section 1.

Measured data used: BRAS CR3 / CR4 (Aspöck et al. 2020, [doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3),
CC BY-SA 4.0) and the Fratoni dataset (Mendeley Data, [doi:10.17632/y7xnv6xg5s.1](https://doi.org/10.17632/y7xnv6xg5s.1),
CC BY 4.0). Two real halls with RIRs per position and BRIRs at one listener position, and four halls with room
criteria averaged over receivers. That is a small sample; the results describe these halls, not halls in general.

## 1. Checked and in agreement

| What | Result | Section in MODEL_en.md |
|---|---|---|
| Direct-sound arrival time | measured onset within −0.67 … +0.07 ms of distance / c at all 20 BRAS position pairs | Position-by-position check |
| Direct-sound ITD and ILD | within 16–19 µs and 0.7–0.9 dB of the measured BRIRs with the KU100 head; 8–11 µs and 0.5–0.9 dB with the measurement's head (FABIAN) (mean over 5 loudspeakers, CR3 and CR4; BRIRs computed by the page) | Binaural check against measured BRIRs |
| Octave spectrum at the binaural listener, same head and loudspeaker as the measurement | within 1.4 dB, 125 Hz–4 kHz (relative to 250 Hz–1 kHz) | Binaural check against measured BRIRs |
| ITDG and level ratio set by the stimulus builder | equal to the nominal values at the reference seat (0.000 ms, 0.000 dB); files rebuilt independently to 1.5·10⁻⁵ | Stimuli for the listening tests |
| Browser page vs Python | C80 / D50 / EDT / T30 within 0.007 dB / 0.001 / 0.001 s / 0.001 s; IACC_E3 within 0.035 (shoebox, 36 conditions) | Browser vs Python |
| Reverberation after calibration on measured T30 | held-out positions within 1.6 JND in T30 (median absolute) (BRAS CR3 and CR4) | Position-by-position check |
| Room criteria with another program's calibrated inputs | ULH: EDT, C50 and Ts within about 1 JND, T30 within 1.7 JND at 500 Hz–4 kHz (page's engine); DUS: T30 within about 1 JND at mid frequencies | Room criteria against measured halls; The two opera houses |
| Against an independent simulator (I-Simpa SPPS) | diffuse box within 0–4 %, CR4 within about 1–2 JND | Comparison with an independent free simulator |

## 2. Checked, with known deviations

| What | Result | Section |
|---|---|---|
| T30 without calibration | 5–16 % long with Eyring-fitted coefficients (BRAS RIRs, median over the positions, page's engine: CR3 5–10 %, CR4 13–16 %); 14–22 % long in CR4 at 500 Hz–4 kHz in the binaural check | Position-by-position check; Binaural check |
| First-order reflection levels | median +1.6 dB (CR3) and +2.7 dB (CR4) re measured; reflection by reflection poor in CR4 | Position-by-position check |
| Early energy and clarity at the binaural listener | C80 1–4 dB low at 500 Hz–1 kHz; in CR4 13–20 % of the 0–80 ms energy at 20–50 ms against 5–9 % measured (mainly the ceiling panels; cause not established) | Binaural check |
| Early interaural cross-correlation, IACC_E3 | low in CR3, right in CR4: 0.38 vs 0.52 (CR3), 0.82 vs 0.83 (CR4) (BRIRs computed by the page, the measurement's head FABIAN, measured loudspeaker directivity, calibrated materials; with the page's KU100 head 0.46 and 0.82); 0.41 vs 0.45 (Detmold) | Binaural check |
| Late interaural cross-correlation, IACC_L | 0.12 vs 0.16 (CR3), 0.13 vs 0.33 (CR4): 40–75 % of the measured value (the late part is rendered as an ideal diffuse field) | Binaural check; Late interaural coherence |
| Halls far from the inputs' assumptions | STC 18–27 % long (3D model, page's engine); TCB (box-tier opera house) decays too fast and is not counted as a successful check | Room criteria against measured halls; The two opera houses |
| Drawn 2.5D halls | reverberation and clarity within a few JND, but individual early reflections of a hall with balconies are not reproduced | Position-by-position check |
| Hall not used in development, modelled from published drawings | Arvedi Auditorium (post hoc, after the fixes of 2026-11-12): T20 within 3 %, C80 within 1 dB for the omnidirectional source, but EDT 14–30 % long and, for directional loudspeakers, C80 1.2–2.8 dB low at 2–4 kHz | `validation/arvedi_check.md` |

## 3. Not checked or not modelled

- Whether listeners hear simulated and measured BRIRs of the same hall as equivalent: no listening test has
  compared them. The checks above are physical, not perceptual.
- Seat dip: without the optional seat-dip model (BRAS RS7: no 500 Hz dip; behind the first row 5–11 dB too
  loud); with it, RS7 within 1.8–2.5 dB in sight of the source and 3.3–6.2 dB behind the first block, the 400–500 Hz
  dip within 3 dB but starting about a third octave low, generic seats, one real hall checked with default seats (`docs/MODEL_en.md`, *Seat dip*). Diffraction beyond
  second order (second order is opt-in and checked only on BRAS RS6), edge end points, seats as geometry.
- Loudspeaker frequency responses (only directivity patterns are modelled); individual HRTFs (KU100 only, nearest
  HRIR, no interpolation).
- Halls other than the seven above, and seat positions other than those measured.

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

## 5. Added for version 0.8.0 (2026-11-15)

Sections 1 - 4 describe the checks up to 2026-11-13, computed with the Python engine (pyroomacoustics ray tracing).
What changed and what was found since, with the numbers in [BENCHMARK_en.md](BENCHMARK_en.md), section 4a:

| What | Result | Where |
|---|---|---|
| Python tools computing with the page's engine | `engine_js.py` gives the page's own energy histograms (largest relative difference 3·10⁻¹² against the page; drawn hall, 90° loudspeakers, 3-D hall); measured directivity gives the same band amplitudes in both engines (10⁻¹² dB) | `validation/check_engine_js.py`, `check_engine_js_dir.py` |
| Page vs Python in a **drawn (2.5-D) hall** | NOT the same model: the two scatter differently and need different absorption for the same T30 (Detmold 1 kHz: T30 1.50 s against 1.34 - 1.39 s with the same materials). Calibrate with the engine that computes. In 3-D halls they agreed within about 2 % (2026-11-15); in BRAS CR4 the page's engine gives T30 4–5 % longer before calibration (2026-11-20, cause not found) | `validation/detmold_js.md` |
| Hall checks with the page's engine | Arvedi, Arni, OperaRIR and Detmold give the same picture as with the Python engine | `validation/engine_js_halls.md` |
| Energy of the first 80 ms by time window | within about 1.3 dB at 500 Hz - 4 kHz in BRAS CR3 / CR4 and Detmold (means over positions); Arvedi -4 ... -5 dB at 20 - 50 ms | `validation/bras_decay_shape.md`, `arvedi_placement.md` |
| Cause of the long EDT in Arvedi | the early reflection pattern of that model (drawn from published plans); ruled out: absorption placement, scattering coefficient and model, engine, aim, volume, image-source order | `validation/arvedi_placement.md` |
| Ray noise | EDT of one receiver: 8 % between seeds at 20000 rays, 3 % at 80000, 2 % at 320000; hall means below 1 % | `validation/timing.md` |
| Stimuli from the page's BRIRs | `make_stimuli.py` reads the SOFA file the page exports; the BRIRs equal the page's arrays | `CHANGELOG.md` |
| Level ratio in the page | with dry files loaded it is defined as in `make_stimuli.py` (energy of the ear signals); the PA gain is then the same in both (fan hall: -3.30 dB, -0.59 dB with an unamplified source) | `docs/MODEL_en.md`, *Conditions* |

For use, in addition to section 4:

- EDT depends on whether the model holds the surfaces that reflect in the first 80 ms. Fitting the absorption
  (also on T30 and EDT together) does not repair a missing reflection. With a few measured RIRs of the hall, compare
  the energy in time windows (`validation/arvedi_decay_shape.py` shows how).
- Directional loudspeakers at 2 - 4 kHz: mixed evidence, with both engines. With measured directivity and the 3-D
  models of the data set, C80 is -2.2 / +0.4 dB (BRAS CR3) and -1.1 / 0.0 dB (CR4) at 2 / 4 kHz (five sources, one
  listening position each); in OperaRIR C80 is 1.7 - 2.5 dB high, the error grows towards the rear seats, and the
  scattering of the hall surfaces (no source; start values) explains about half of it, the rest is open. Arvedi
  (C80 1.5 - 3 dB low) is no longer used as evidence for loudspeakers: its model does not have the measured early
  reflections (above), and the loudspeaker data and aim were stand-ins. Analyses of a PA condition are best supported at 500 Hz - 1 kHz.
- Use enough rays for the quantity read: single seats need about 16 times the rays of hall means.
- Still not checked: a delayed PA condition against a measurement; simulated against measured BRIRs by listening.
