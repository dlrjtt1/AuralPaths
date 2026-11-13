# Changelog

Dates are those of the commits on GitHub. The version is shown on the page and recorded in saved configs and exported
files.

## Unreleased
- New check: OperaRIR, Finnish National Opera (https://doi.org/10.5281/zenodo.8096639, CC BY-NC 4.0), Genelec 8331A
  with its measured directivity (Aalto SOFA, read as spherical although it declares cartesian), 97 stalls seats, model
  from the published plan and section (`validation/opera_model.py`, `validation/opera_check.py`,
  `validation/opera_check.md`): after a T30 calibration the simulated C80 is 3.0 - 3.2 dB too high at 2 - 4 kHz, the
  opposite sign of Arvedi, growing from the front rows (within 1 - 2 dB) to row 17 (+8 dB); untested reading: no seat
  rows in the model (grazing over the seating). Directional loudspeakers at 2 - 4 kHz stay "not supported".
- OperaRIR seat-row experiment (`opera_check.py --seats`, `--start`): backrests as geometric strips on every row,
  recalibrated on T30, 10000 rays. The C80 bias still grows from the front rows to row 17 (+9 dB at 2 - 4 kHz); the
  missing seat rows as geometry do not explain it (no diffraction in the model; see `validation/opera_check.md`).
- New check: Arni variable-acoustics room (Aalto; https://doi.org/10.5281/zenodo.6985104, CC BY 4.0), 37 panel states
  predicted after calibrating only the bare surfaces on the all-closed state (`validation/arni_model.py`,
  `validation/arni_check.py`, `validation/arni_check.md`): 500 Hz - 4 kHz T30 / EDT -6 ... +7 %, C80 within 0.6 dB on
  average; simulated EDT / T30 0.87 - 0.95 vs measured 0.91 - 0.96, so the engine does give an early decay faster than
  the late one where the absorption calls for it (unlike the Arvedi model); 250 Hz +20 % (panel data); absorption on
  the ceiling too effective in T30.
- Fix (Python engine): the noise that carries the ray-traced energy the image sources do not explain (drawn and mesh
  halls) started up to about 5 ms before the direct sound, because the residual histogram is smoothed over 10 ms;
  it now starts at the direct sound.
- New option `path_brir(..., ew=early_resid_directions(...))`: that early noise with the ear energies and interaural
  coherence of the arrival directions of the scattered energy (windows 0 - 20, 20 - 50 ms, rest of the early part;
  the first window from the source direction) instead of the diffuse-field coherence. Off by default until checked
  in more halls (Detmold IACC_E3 0.34 -> 0.41, measured 0.45; validation/detmold_kh.md).
  Now on by default (Python `early_dir_on`, after BRAS CR3 / CR4: IACC_E3 0.40 -> 0.44 and 0.75 -> 0.76, measured 0.52,
  0.83) and in the browser: `GEOM.rays` option `tEarly` records the scattered energy per window and direction, the page
  renders the early residual with one noise pair per window (kept with the hall results, so a re-aim needs no new
  tracing; one tracing run, three more noise pairs per path when the hall changes). The browser residual also starts at
  the direct sound now. Browser vs Python direction statistics (`validation/check_early_dirs_pyjs.py`): drawn hall
  (Detmold) |Gamma| 500 Hz - 2 kHz within 0.04 after 20 ms; mesh box within 0.16, because the browser blends
  directions in meshes (as pyroomacoustics) and the Python direction tracer scatters stochastically.
- Fix (Python engine): the pyroomacoustics ray tracer counted the scattered energy twice: at every reflection on a
  scattering wall it sent s times the ray's energy to the receivers ("diffuse rain") and continued the ray with its
  full energy. Reflected energy in a shoebox: +1.1 ... +1.9 dB at s = 0.3, +2.2 ... +3.5 dB at s = 0.9 against exact
  image sources; now within 0.8 dB, as the browser tracer, which never had the rain (`brir_proto._no_diffuse_rain`,
  new check `validation/check_rays_energy.py`, regression `rays_energy`). It made the late field too strong relative
  to the direct sound wherever surfaces scatter (seating), i.e. C80 too low and EDT too long; Python results of the
  validations are being recomputed. Browser results were not affected.
- Directional sources in the ray tracing: rays now leave a directional source with the energy of its pattern in their
  launch direction (Python: `brir_proto.rt_add_source`, pyroomacoustics directive-source rays, amp^2 per band; browser:
  `GEOM.rays` keeps the energy of the first 250 ms per launch sector, 64 Fibonacci sectors, and the page weights it by
  the pattern, so a change of aim or directivity needs no new tracing). Before, the ray-traced energy was scaled by
  1 / Q at every time, so the early reflections of a loudspeaker aimed at the audience were too weak and its C80 hardly
  differed from an omnidirectional source (Arvedi Genelec S1: simulated C80 at 4 kHz 3.3 dB, S0 3.4 dB; measured
  11.1 dB and 4.9 dB). Browser vs Python with a directional source as close as without one (one ray realisation:
  0.1 - 1.1 dB in the first 80 ms, `validation/check_directional_rays_pyjs.py`).
- Fix (Python engine): `energy_hists` (several receivers in one run: room-criteria checks, `geometry.shared_rays`)
  took the emission direction of every image source from the first receiver, so a directional source was weighted
  by the direction towards receiver 1 at all receivers. `emission_dirs` now takes the receiver's own position. Single-
  receiver paths (BRIRs, `image_arrivals`) and the browser engine were not affected. Found in the Arvedi diagnostic
  (S1 direct sound at A109: -16.8 dB in a three-receiver run, -9.7 dB alone and after the fix). Checks with
  directional sources (Arvedi S1 - S4, Detmold KH 120) are recomputed.
- Seat dip (optional, `"geometry": {"seat_dip": {"on": true}}`, page: Hall → Seat dip): the direct sound of every
  source over the audience floor gets the transfer function of the seat rows from a 2-D boundary element model of
  generic seats along the path (Davies & Cox 2000 approach; `seatdip.py`, `engine_geom.js` seatPath, both engines,
  agree to 1e-10). Row spacing from the user or the steps of a drawn section; seat back 0.80 m and openings 0 /
  0.10 / 0.24 m as defaults (Tahvanainen et al. 2020). *Seat-dip range…* shows the effect of the unknown seat
  dimensions at the current seat. BRAS RS7: 1.8–2.5 dB in sight of the source (3.8–6.4 dB without), 3.3–6.2 dB behind
  the first block (5.6–9.1 dB). New regression check `seatdip`; `validation/rs7_seatdip_bem.py`,
  `validation/check_seatdip_pyjs.py`.
- Seat dip: T on 5.9 Hz bins (8192-point FFT at 48 kHz) instead of 23 Hz, the BEM on every bin up to 160 Hz and on
  every fourth bin above (interpolated): the rows' response wrapped around the shorter FIR (BRAS RS7: 200 Hz 8 - 9 dB
  too loud before, 3 - 4 dB now; 400 - 500 Hz dip within 3 dB). Browser BEM faster (order-1 Bessel only, block-
  circulant matrix product, GMRES started from the previous bin's solution): about the same time as before.
- Arvedi Auditorium (Cremona), a hall not used in development, modelled from the published drawings
  (`validation/arvedi_model.py`, `validation/arvedi_check.py`, protocol fixed beforehand in
  `validation/arvedi_protocol.md`). The blind run placed the receivers on the wrong side of the stage and is void;
  post hoc: T20 within 3 %, mid-frequency C80 within 1 dB, EDT 17 - 32 % too long, and for the directional
  loudspeakers C80 3 - 8 dB low at 2 - 4 kHz (`validation/arvedi_check.md`).
- Seat dip, lower edge of the dip in RS7 (315 Hz 5 - 7 dB too quiet) investigated and documented as a limit: not the
  2-D approximation (converged 3-D point-source calculation by the 2.5-D transform), not the block dimensions, not
  absorbing surfaces or MDF walls on the box cavity; `validation/rs7_seatdip_diag.py`.
- Seat dip checked in the Detmold Konzerthaus (136 binaural pairs, default seats): early IACC deficit 0.15 -> 0.10,
  C80 bias up to -0.8 dB -> within 0.2 dB (5.9 Hz grid; 0.09 / 0.3 dB with the 23 Hz grid); `validation/detmold_kh.md`. `detmold_kh.py compare --meas-csv` reuses the
  measured metrics of an earlier run.
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
