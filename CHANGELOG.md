# Changelog

Dates are those of the commits on GitHub. The version is shown on the page and recorded in saved configs and exported
files.

## Unreleased
- Seat dip (optional, `"geometry": {"seat_dip": {"on": true}}`, page: Hall → Seat dip): the direct sound of every
  source over the audience floor gets the transfer function of the seat rows from a 2-D boundary element model of
  generic seats along the path (Davies & Cox 2000 approach; `seatdip.py`, `engine_geom.js` seatPath, both engines,
  agree to 1e-10). Row spacing from the user or the steps of a drawn section; seat back 0.80 m and openings 0 /
  0.10 / 0.24 m as defaults (Tahvanainen et al. 2020). *Seat-dip range…* shows the effect of the unknown seat
  dimensions at the current seat. BRAS RS7: 3.0–3.3 dB in sight of the source (3.8–6.4 dB without), 3.4–6.7 dB behind
  the first block (5.6–9.1 dB). New regression check `seatdip`; `validation/rs7_seatdip_bem.py`,
  `validation/check_seatdip_pyjs.py`.
- Round robin, all the objective comparisons of Brinkmann et al. 2019 (https://doi.org/10.1121/1.5096178) that do not
  need listeners: room acoustical parameters of the three rooms (`validation/rr_extract_ra.py`,
  `validation/rr_complex.py`), energy decay in the coupled rooms (`validation/rr_coupled.py`) and source
  lateralization (`validation/rr_lateral.py`); results in `docs/BENCHMARK_*` sections 2.2 - 2.4. Section 2.0 states
  them in the paper's own measures (T20 deviation, JND, correlations, decay transition, tone colour in 37 gammatone
  bands: `validation/rr_tonecolor.py`). New mesh option
  `"seeds"` (both engines): further points inside the room, for a coupled room behind a gap narrower than the voxel
  band (in BRAS CR1 at 4.1 deg the flood fill from the source missed the reverberation chamber).
- `docs/BENCHMARK_en.md` (`_ko`, `_ja`): all scores against public measured data on one page, with how to rerun
  them; a one-line summary with a link at the bottom of the page. `validation/bras_rs5.md` renamed to
  `validation/bras_rs5_engine.md` (it clashed with `bras_RS5.md` on case-insensitive file systems, e.g. macOS).
  Fix: `brir_proto.image_arrivals` referenced undefined names when diffraction was on (no callers); `run.py --help`.
- Diffraction over rows of edges in sight of the source: the engine added a first-order term for every edge near its
  boundary, and over 15 block rows at grazing incidence (BRAS RS7) these added up to 5–20 dB too much. Now, with
  the source in sight, only the edge nearest to its boundary keeps its boundary term (plus the edges of a face that
  reflects to the receiver), both engines: RS7 in sight −0.7 … −4.7 dB, round-robin median shape error
  1.9 → 1.5 dB, other scenes unchanged or within 0.4 dB. Behind the first row still 5–11 dB too loud
  (`validation/bras_rs.md` section 5).
- Diffraction at thin plates: two faces back to back closer than 5 cm (a partition, a free-standing panel) now end
  in one thin-plate edge (n = 2). Before, behind such a box the first-order paths were blocked by the box itself:
  in BRAS RS5 given as geometry, 10 of 11 positions behind the partition got no sound. New opt-in
  `"geometry": {"diffraction_refl": 1}`: diffraction combined with one specular reflection before and/or after the
  edge (both engines, checked against each other; new regression check `diffraction_plate`). RS5 with the
  round-robin post-processing: 2.1–2.7 dB mean absolute difference per 1/3-octave band behind the partition,
  spectral shape in the range of the better of the two round-robin simulators (`validation/bras_rs5_engine.md`).
- BRAS reference scenes RS1–RS4, RS6, RS7 (`validation/bras_rs.py`, `validation/bras_rs.md`) and the round-robin
  simulators' spectra read from SuppPub2 (`validation/rr_extract.py`, `validation/rr_compare.py`): over the 15
  figures the spectral-shape error of AuralPaths (median 1.9 dB) lies between the round-robin participants
  (1.0–2.8 dB), without the loudspeaker directivity they had. Not modelled: thick obstacles (RS6: 4 of 8 positions
  behind a 0.72 m body get no sound) and grazing incidence over rows (RS7: 5–20 dB too loud, no seat dip).
  Thin-plate edges are no longer found where another surface meets the edge or inside a panel (mesh twin faces).
- Second-order edge diffraction (two edges in sequence, e.g. over a thick obstacle), opt-in with
  `"geometry": {"diffraction_order": 2}`, both engines (new regression check `diffraction_order2`): UTD on the edge
  sequence with the hard-face coefficient halved at grazing incidence (Kouyoumjian & Pathak 1974). BRAS RS6 (0.72 m
  body on a floor): the 4 positions behind it that got no sound now agree with the other 4 within −0.6 … +1.6 dB
  level bias, 2.3–2.8 dB mean absolute difference per 1/3-octave band. Does not fix the seat dip (RS7) and is not
  for plates thinner than 5 cm (those stay thin-plate edges).
- BRAS binaural check with the FABIAN HRIRs of the BRAS release (`tools/fabian_to_sofa.py`) and the K8 on-axis
  response: the 2–4 kHz spectrum difference (−6 … −13 dB with the KU100) drops to within 1.4 dB, ITD within 5 µs;
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
