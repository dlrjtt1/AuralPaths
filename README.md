# AuralPaths

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24053630.svg)](https://doi.org/10.5281/zenodo.24053630)

*A research and teaching tool for the precedence effect in sound reinforcement: vary hall, loudspeaker and seat
positions, delay and level, then compute, listen to and export binaural room responses.*

A browser-based binaural room simulator for **direct vs. loudspeaker (PA) paths**: draw a hall from its plan and
section, place a stage source and a pair of PA loudspeakers, and hear and measure how the arrival-time gap (ITDG)
and the level ratio between the paths change from seat to seat.

**Open the simulator:** `index.html` (GitHub Pages: `https://<user>.github.io/<repo>/`). Everything runs in the
browser; drawings and audio files you load stay on your computer.

By LABO 1557 (Dong-Gyun You).

## What it does
- Hall: shoebox, a 2.5D drawn hall (plan outline × floor and ceiling profile) traced over your own PDF / image
  drawings, with scale from a known dimension and snapping to the PDF's lines, or a 3D model (Wavefront OBJ, e.g.
  exported from SketchUp or Blender) with each surface name mapped to a material.
- Acoustics: image sources (early part; each reflection weighted for finite panel size, Kirchhoff–Fresnel after
  Rindel, and for scattering loss) + ray tracing (diffuse part) + first-order edge diffraction (UTD);
  binaural rendering with KU100 HRIRs (or an HRIR set of your own, SOFA); late reverberation with the ear energies and interaural coherence of the
  ray-traced arrival directions.
- Output: echogram, arrivals by direction, C80 / D50 / Ts / EDT / T30 / IACC, seat maps of effective ITDG and
  level ratio, A/B listening with your own dry recordings (optional headphone EQ for Sennheiser HD600).
- Python tools (same model, for research use): `run.py` (BRIR sets), `make_stimuli.py` (listening-test stimuli),
  `calibrate.py` (fit absorption to measured T30), `validate_bras.py` (diffraction check against BRAS),
  `obj_to_hall.py` (3D OBJ hall → drawn hall the page can open), `validate_fratoni.py` (room criteria against
  two measured halls), `validate_bras_cr.py` (room criteria and early reflections position by position against
  measured RIRs of two real halls, BRAS CR3 / CR4).

## Accuracy and limits — read before using the results
- **It does not claim to reproduce a real hall.** Room-acoustic simulation tools differ noticeably from
  measurements (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178). Calibrate the absorption with measured
  T30 (`calibrate.py`) and check against measurements before drawing conclusions about a real room.
  Demo with a real hall and its measured T30 (BRAS CR3, 3D model, calibration file with fit and check
  positions): `examples/bras_cr3/`.
- Drawn halls are 2.5D (the cross-section is the same across the width); 3D models get image sources to order 2
  (browser; order 1 in Python) and no diffraction (browser and Python ray tracers agree within about 2 % in T30 on two real halls); diffraction
  at one edge per path (optionally with one reflection before and after it, or two edges in sequence with
  `diffraction_order` 2), no seat-dip effect; scattering as a random (Lambert) model; nearest-direction HRIRs; non-individual (dummy-head) HRTFs.
- Diffraction check against BRAS scene RS5 (a 2.07 m partition on a hard floor, 16 positions): mean absolute
  difference 1.8 dB in third-octave bands 500 Hz–2 kHz (2.2 dB at the 11 shadow positions). This is one simple
  scene, not a measure of whole-hall accuracy. Details: `validation/`, `docs/MODEL_en.md`. The same scene given to
  the engine as geometry (`validation/bras_rs5.md`): 2.1–2.7 dB mean absolute difference at 125 Hz–4 kHz behind the
  partition, in the range of the better of the two round-robin simulators that handled this scene. Reference scenes
  RS1–RS4 (reflections on floors, plates, arrays): spectral shape between the round-robin participants
  (`validation/bras_rs.md`); thick obstacles need `diffraction_order` 2 (BRAS RS6: within about 3 dB behind a 0.72 m
  body); behind seat rows at grazing incidence the simulation is
  still 5–11 dB too loud and the seat dip is not produced.
- Room-criteria check against two measured halls (Fratoni dataset, inputs from the authors' Odeon calibration,
  unchanged): raked lecture hall (ULH) EDT / T30 / C50 / Ts within about 1 JND at 500 Hz–4 kHz, T30 1–2 JND short
  at 125–250 Hz; elliptical domed hall (STC) T30 about 15 % too long at all bands (non-diffuse field; calibrate
  first in such halls). Receiver means only: early arrivals and PA paths are not tested by it.
  Details: `validation/fratoni_*`, `docs/MODEL_en.md`.
- Position-by-position check against measured RIRs of two real halls (BRAS CR3 chamber music hall, CR4 auditorium;
  3D models): with the BRAS coefficients T30 is 7–18 % too long (calibrate with measured T30 first), C80 / C50 / Ts
  within about 0.9–1.6 JND. First-order reflections: right in time and level in CR3 (+1.6 dB median); in CR4 +2.7 dB
  median after the finite-panel correction (+6.5 dB before), with poor reflection-by-reflection agreement. A drawn 2.5D version of a hall with balconies keeps reverberation and clarity roughly but **not its
  individual early reflections**, so check ITDG-related results of such halls against a measurement.
- Loudspeaker directivity files are approximations (see `NOTICE.md`).

## Python tools
```bash
pip install -r requirements.txt     # pyroomacoustics sofar soundfile scipy matplotlib
# put HRIR_FULL2DEG.sofa (Zenodo 3928297) at hrir/KU100.sofa
python run.py config.json          # BRIRs, metrics, out/viewer.html
python export_viewer.py config.json
# 3D hall from SketchUp/Blender OBJ (the page opens the OBJ too) and its 2.5D version (order > 1, diffraction)
pip install fast-simplification openpyxl            # optional: large meshes, dataset sheets
python obj_to_hall.py mesh_config.json             # -> mesh_config_2p5d.json
```
Full description of the model, the checks and the outputs: `docs/MODEL_en.md` (Korean: `docs/MODEL_ko.md`, Japanese: `docs/MODEL_ja.md`). What the
checks support and what they do not, in two pages: `docs/VALIDITY_en.md` (`_ko`, `_ja`). Literature and data used:
`docs/REFERENCES_ko.md` (Korean).

## Checks and citing
- `python tests/regression.py` runs the checks that need no external data (page build, Python vs browser agreement of
  image sources, diffraction and ray tracing, reverberation baselines, calibration); they run on GitHub for every push
  to main. Checks against measured halls need the datasets: see `validation/` and `docs/MODEL_en.md`.
- To cite AuralPaths, use `CITATION.cff` (GitHub: "Cite this repository") with the version you used; version 0.7.0
  is archived on Zenodo, https://doi.org/10.5281/zenodo.24053630. Changes:
  `CHANGELOG.md`; how to report problems or contribute: `CONTRIBUTING.md`.

## Licence
Code: MIT (`LICENSE`). Third-party data keep their own licences (KU100 HRIRs and headphone filter: CC BY 3.0;
BRAS-derived validation results: CC BY-SA 4.0; Fratoni-derived validation results and converted halls:
CC BY 4.0): see `NOTICE.md`.
