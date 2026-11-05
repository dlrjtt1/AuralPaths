# AuralPaths

A browser-based binaural room simulator for **direct vs. loudspeaker (PA) paths**: draw a hall from its plan and
section, place a stage source and a pair of PA loudspeakers, and hear and measure how the arrival-time gap (ITDG)
and the level ratio between the paths change from seat to seat.

**Open the simulator:** `index.html` (GitHub Pages: `https://<user>.github.io/<repo>/`). Everything runs in the
browser; drawings and audio files you load stay on your computer.

By LABO 1557 (Dong-Gyun You).

## What it does
- Hall: shoebox, or a 2.5D drawn hall (plan outline × floor and ceiling profile) traced over your own PDF / image
  drawings, with scale from a known dimension and snapping to the PDF's lines.
- Acoustics: image sources (early part) + ray tracing (diffuse part) + first-order edge diffraction (UTD);
  binaural rendering with KU100 HRIRs; late reverberation with the ear energies and interaural coherence of the
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
- 2.5D geometry (the cross-section is the same across the width); first-order diffraction only; no seat-dip
  effect; scattering as a random (Lambert) model; nearest-direction HRIRs; non-individual (dummy-head) HRTFs.
- Diffraction check against BRAS scene RS5 (a 2.07 m partition on a hard floor, 16 positions): mean absolute
  difference 1.8 dB in third-octave bands 500 Hz–2 kHz (2.2 dB at the 11 shadow positions). This is one simple
  scene, not a measure of whole-hall accuracy. Details: `validation/`, `docs/MODEL_en.md`.
- Room-criteria check against two measured halls (Fratoni dataset, inputs from the authors' Odeon calibration,
  unchanged): raked lecture hall (ULH) EDT / T30 / C50 / Ts within about 1 JND at 500 Hz–4 kHz, T30 1–2 JND short
  at 125–250 Hz; elliptical domed hall (STC) T30 about 15 % too long at all bands (non-diffuse field; calibrate
  first in such halls). Receiver means only: early arrivals and PA paths are not tested by it.
  Details: `validation/fratoni_*`, `docs/MODEL_en.md`.
- Position-by-position check against measured RIRs of two real halls (BRAS CR3 chamber music hall, CR4 auditorium;
  3D models): with the BRAS coefficients T30 is 8–16 % too long (calibrate with measured T30 first), C80 / C50 / Ts
  within about 1–1.4 JND. First-order reflections: right in time and level (+1.2 dB median) in CR3, about 6.5 dB too
  strong in CR4. A drawn 2.5D version of a hall with balconies keeps reverberation and clarity roughly but **not its
  individual early reflections**, so check ITDG-related results of such halls against a measurement.
- Loudspeaker directivity files are approximations (see `NOTICE.md`).

## Python tools
```bash
pip install pyroomacoustics sofar soundfile scipy matplotlib
# put HRIR_FULL2DEG.sofa (Zenodo 3928297) at hrir/KU100.sofa
python run.py config.json          # BRIRs, metrics, out/viewer.html
python export_viewer.py config.json
# 3D hall from SketchUp/Blender OBJ (Python engine) and its 2.5D version for the page (Load config…)
pip install fast-simplification openpyxl            # optional: large meshes, dataset sheets
python obj_to_hall.py mesh_config.json             # -> mesh_config_2p5d.json
```
Full description of the model, the checks and the outputs: `docs/MODEL_en.md` (Korean: `docs/MODEL_ko.md`, Japanese: `docs/MODEL_ja.md`). Literature and data used:
`docs/REFERENCES_ko.md` (Korean).

## Licence
Code: MIT (`LICENSE`). Third-party data keep their own licences (KU100 HRIRs and headphone filter: CC BY 3.0;
BRAS-derived validation results: CC BY-SA 4.0; Fratoni-derived validation results and converted halls:
CC BY 4.0): see `NOTICE.md`.
