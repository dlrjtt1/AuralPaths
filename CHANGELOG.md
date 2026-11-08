# Changelog

Dates are those of the commits on GitHub. The version is shown on the page and recorded in saved configs and exported
files.

## Unreleased
- BRAS binaural check with the FABIAN HRIRs of the BRAS release (`tools/fabian_to_sofa.py`) and the K8 on-axis
  response: the 2–4 kHz spectrum difference (−7 … −13 dB with the KU100) drops to within 1.4 dB, ITD within 5 µs;
  low IACC_E3 and C80 remain (room model). Stimulus builder and protocol draft for a listening test
  (`validation/listening_bras.py`, `validation/listening_bras_protocol.md`; not run).
- `docs/VALIDITY_en.md` (`_ko`, `_ja`): what the checks support and what they do not, with the numbers and the
  sections they come from.

## 0.7.0 (2026-11-08)
- Binaural check against the measured BRAS BRIRs in CR3 and CR4 (`validation/check_bras_brir.py`, new `--coverage`
  option for directional sources): direct-sound ITD within 14–18 µs and ILD within 0.8 dB; with a 105° source the
  direct-to-early ratio matches; IACC_E3 too low (split per band in `validation/iacc_split.py`: the noise rendering
  of the early remainder explains only a part, the early energy distribution as much), C80 low, CR4 T30 15–25 % long
  (not resolved). With the measured K8 directivity of the BRAS release (`--k8-mps`) IACC_E3 rises from 0.29 to 0.34
  (CR3) and 0.53 to 0.59 (CR4) and C80 at 500 Hz improves by 0.2–0.8 dB. In CR4 the excess early energy at 20–50 ms
  comes mainly from the ceiling panels and the aisle floor (`validation/early_paths.py`, new optional arrival log
  `opts.log` in the browser ray tracer); only a clearly more absorbing ceiling brings it near the measurement
  (hypothesis, BRAS materials unchanged).
- Fix: image sources on a mesh were counted twice when the reflection point lay on the shared edge of two coplanar
  triangles (symmetry plane, centred source and listener); both engines now count images of the same order within
  1 cm once. CR4 binaural results and the Fratoni TCB / DUS checks rerun (Fratoni: one DUS receiver pair changes
  slightly).
- Comparison with an independent free simulator, I-Simpa's SPPS (`validation/check_isimpa.py`): diffuse box within
  0–4 %, CR4 within about 1–2 JND; in CR3 SPPS decays about 17 % slower (not resolved).
- Fratoni opera houses TCB and DUS checked with the browser engine (`validation/check_fratoni_js.py`): DUS T30 within
  about 1 JND at mid frequencies; TCB decays too fast (not counted as a successful check, cause not determined).

## 0.6.0 (2026-11-07)
- 3D halls from OBJ models (SketchUp / Blender) in Python and in the browser: voxel room, BVH ray tracing, image
  sources to order 2 in the browser (order 1 in Python), material per face group.
- OBJ to 2.5D conversion (`obj_to_hall.py`).
- Image sources with finite panel size and scattering loss per reflection.
- Python ray tracing: energy floor 1e-20 (was 1e-9, which cut scattered energy after about 0.5 s); validations re-run.
- Checks against measured halls: Fratoni dataset (ULH, STC; room criteria) and BRAS CR3 / CR4 (position by position,
  room criteria and first-order reflections, including a timing-tolerant reflection check).
- Page: Calibrate button (absorption to measured T30, with held-out check positions), trust panel and ray-tracing
  spread, provenance record in saved configs, BRIR export as SOFA (SingleRoomSRIR) and WAV, loadable HRIR set (SOFA),
  parallel ray tracing, per-ray random streams, a demo with measured data (BRAS CR3), quick guide in Korean, Japanese
  and English.
- Regression checks (`tests/regression.py`) run on GitHub for every push; `tools/build_page.py`; citation metadata.

## 0.5 (2026-11-03)
- First public version: shoebox and drawn 2.5D halls, image sources, ray tracing and first-order UTD edge diffraction,
  binaural rendering with KU100 HRIRs, direction-dependent late reverberation, A/B listening, Python tools for BRIR
  sets, stimuli and calibration.
