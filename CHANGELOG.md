# Changelog

Dates are those of the commits on GitHub. The version is shown on the page and recorded in saved configs and exported
files.

## Unreleased
- Page, Mark stage front: the plan labels the stage and the audience side; a stage point on the line is refused and a
  second event of the same click is ignored.
- Ray tracing in 3D models: nearest-surface search with a surface-area-heuristic tree, flat arrays and near-first
  order (identical results; 3 - 4.4x faster in Node, DUS hall computation at 50000 rays about 320 -> 155 s on 2 cores).
- Page, 3D models: the engine works in the model's own frame, so turning the plan changes the view only; with the stage
  front marked the listeners face the stage and a turn keeps all results without a computation (without it they face
  +y of the page as before and the hall is computed again). Turn 0 without a stage front is bit-identical to before.
- Page, 3D models: 50000 rays by default (10000 gave 23 - 25 % RMS run-to-run spread of a seat's T30, 50000 gives
  4 - 8 %, `validation/ray_noise.md`); up to 8 ray-tracing workers (before 4).
- `engine_geom.js` `rays`: option `face` (direction the listeners face, for the direction bins); default unchanged.
- Page, 3D models: turning the plan stops the hall computation in progress and computes once the plan has not been
  turned for 1.5 s (several turns, one computation); the aim of directional loudspeakers now turns with the plan
  (before, a loudspeaker pointed elsewhere in the hall after a turn).
- Page, 3D models: **Mark stage front…** (three clicks: both ends of the stage opening, then the stage) places the
  sources and seats from that line as in the built-in layout; saved as `geometry.mesh.stage_front`.
- Page, 3D models: opening a different OBJ while one is loaded no longer keeps the items in the old model's frame;
  they keep their place relative to the room (the same model reloaded with other settings still keeps the frame).
- Image sources: rejection tests on squared distances and packed planes, no allocation in the back-trace (identical
  arrivals); 3D model DUS: 181 -> 70 s for 4 sources, page load 205 -> 128 s on 2 cores.
- Page start-up: the late-noise templates of the shoebox hall are made only when used and, at start-up, in workers
  (BRIRs bit-identical); the page responds after 0.7 s instead of 5.3 s on 2 cores.
- Page and `engine_js.py`: faster computation. The ray tracer reads the surface planes from a flat array and allocates
  nothing per surface test (bit-identical results, about 1.5x faster); the three early-window noise pairs are generated
  only as long as they are used (late field bit-identical, early part a new noise realization within seed-to-seed
  variation). Fan hall example on 2 cores: 63 -> 27 s. See `validation/timing.md`.
- Page footer: the known weak spot now gives the seat-dip error with and without the optional model and states that
  delayed-loudspeaker conditions have not been compared with measurements; footer notes in the banner's font size (12 px).
- Docs: `docs/MODEL_*` no longer say that RS6 / RS7 are outside the model (stale sentence from 2026-11-03).
- Zenodo DOI of 0.8.1 (https://doi.org/10.5281/zenodo.24243050) in `CITATION.cff`, README and `docs/VALIDITY_*`.

## 0.8.1 (2026-11-15)
- Docs: the statement on directional loudspeakers at 2 - 4 kHz now gives the evidence per hall (BRAS CR3 / CR4
  agree at 4 kHz, OperaRIR open); Arvedi is marked as excluded from further checks (model error).

## 0.8.0 (2026-11-15)
- Detmold binaural comparison with BRIRs computed by the page itself (`validation/detmold_page.py`,
  `validation/detmold_js.md`): IACC_E3 +0.02 (60 % of 136 pairs within 0.075), IACC_L3 +0.01 (92 %), EDT -2.0 /
  -1.4 / -4.6 % and C80 -0.1 / +0.5 / +0.9 dB at 500 Hz / 1 / 2 kHz.
- `docs/BENCHMARK_*` (section 4a) and `docs/VALIDITY_*` (section 5), en / ko / ja: the reruns with the page's
  engine next to the Python-engine values, and the findings of 2026-11-15 (scattering in drawn halls, energy of the
  first 80 ms by time window, the cause of the long EDT in Arvedi, ray noise, median calibration).
- `validation/detmold_page.py`, `tests/page_brirs.js`: the Detmold binaural comparison with BRIRs computed by the page
  itself (results follow).
- Page: the noise pairs of the directional late field and of the early scattered-energy windows (four per path;
  two thirds of the main-thread time of a drawn hall, `validation/timing.md`) are computed in a pool of workers
  (up to 6) before the paths are rendered. Same code and seeds: the BRIRs of the fan hall are identical to before
  (largest difference 0). The page stays responsive while it renders (main thread 97 % idle instead of 34 %); on
  the 2-core test machine the total time is unchanged (one worker), the gain on machines with more cores was not
  measured. `DSPLIB` and `lateDirFactory` hold the shared code.
- Page: the level ratio follows `make_stimuli.py`. With dry files loaded in *Listen*, the PA gain of a nominal
  level ratio is set from the energy of the ear signals those files give at the reference seat (PA over direct,
  unamplified sources with a file included in the direct sound), no longer from the BRIR energies alone; the
  displayed effective level ratio uses the same definition. Without a file for the amplified source nothing
  changes. Fan hall, 20 ms / 0 dB: PA gain -3.30 dB (one file) and -0.59 dB (with an unamplified source) in the
  page and in `make_stimuli.py`; effective level ratio at seat L -0.91 dB in both. This changes the criteria the
  page shows once a file is loaded.
- `make_stimuli.py`: `"input_brirs": {"<input>": "<BRIR name>"}` convolves an input of path A with its own BRIR
  (the page's unamplified sources at their own positions); default unchanged.
- `make_stimuli.py`: `"brir_sofa"` takes the SOFA file the page exports instead of a folder of WAV files, so that
  the listening-test stimuli are built from exactly the BRIRs the page plays (its provenance record and the file's
  hash go into the manifest). Checked on the fan hall: the BRIRs read from the SOFA equal the page's arrays, and the
  stimuli equal those made from the same BRIRs as WAV files. `tests/page_export_sofa.js` saves the page's export
  headless (with a local copy of h5wasm where the CDN is not reachable).
- `engine_js.py`: sources with measured directivity (polar CSV, SOFA, inline balloon). The page's table model gets
  the data `brir_proto.dir_model` read; band amplitudes of both engines agree to 1e-12 dB
  (`validation/check_engine_js_dir.py`, regression check `engine_js_dir`). `validation/opera_check.py --engine js`
  (default).
  Arvedi (4292-L, Genelec 8020A) and OperaRIR (8331A) rerun: same findings as with pyroomacoustics
  (`validation/engine_js_halls.md`). Fix: the bridge passes `t_max` to the ray tracer (histograms longer than
  2.5 s ended early).
- BRAS CR3 / CR4, decay in time windows (`validation/bras_decay_shape.py`, `validation/bras_decay_shape.md`): with
  the measured halls' own 3-D models the energy of every window of the first 80 ms is within about 1.3 dB at
  500 Hz - 4 kHz. The Arvedi deficit at 20 - 80 ms is a property of that model, not of the engine.
- Detmold, decay in time windows (`validation/detmold_decay_shape.py`, `validation/detmold_js.md`): in the drawn
  hall the mean energy of every window of the first 80 ms is within about 1 dB of the measurement at 500 Hz -
  4 kHz (Arvedi: -4 ... -5 dB at 20 - 50 ms), with both scattering models.
- Arvedi, early decay (`validation/arvedi_placement.py`, `validation/arvedi_decay_shape.py`,
  `validation/arvedi_placement.md`): moving the absorption between the seating / stage and the walls / ceiling by
  a factor of 4 at constant T30 changes the EDT bias by 5 points only (EDT / T30 1.07 -> 1.02, measured 0.90). The
  mean decays agree within 0.3 dB from 80 ms on; in the first 80 ms the simulation has 1 - 2 dB too much energy
  before 20 ms and 4 - 5 dB too little at 20 - 50 ms. The EDT error is an error of the early reflection pattern
  (model geometry), not of absorption, scattering or the late field.
- `engine_js.py`: the browser engine from Python (Node). `energy_hists(cfg, src, recs)` returns what
  `brir_proto.energy_hists` returns, computed as the page computes a path. For this the page's path assembly moved
  into `engine_geom.js` (`GEOM.withDiffraction`, `GEOM.withSeatDip`, `GEOM.pathHist`; the page calls them, its
  results are unchanged: fan hall histograms identical before and after). `validation/check_engine_js.py` loads a
  config into the page (`tests/page_dump.js`) and compares: with the page's own job the histograms agree to 3e-12
  (drawn hall with diffraction, with 90 degree loudspeakers) and 2e-14 (3-D hall, BRAS CR3 example); the config is
  read as the page reads it, except that the page ignores "c" of a config (it computes with 343 m/s). New
  regression check `engine_js`. Not covered yet: measured directivity, seat dip in 3-D halls. The Python tools
  (`run.py`, `make_stimuli.py`, the binaural and loudspeaker checks) are not switched to it yet.
- `calibrate.py`, `validation/arvedi_check.py` and `validation/arni_check.py` compute with the page's engine by
  default (`--engine js`; `--engine python` is pyroomacoustics, the engine of the results documented so far). Runs
  the bridge does not cover (measured directivity, seat dip in 3-D halls) are skipped with a message under `js`.
  Reruns of the omnidirectional checks (`validation/engine_js_halls.md`): Arvedi S0 and Arni give the same picture
  as with pyroomacoustics (Arvedi C80 within 0.3 dB of the earlier bias, EDT 3 - 7 points longer; Arni decay times
  3 - 6 points longer, C80 0.1 - 0.3 dB closer); Detmold needs factors of 1.00 - 1.20 instead of 0.71 - 0.94. The
  documented numbers of the hall checks and of `docs/BENCHMARK_*` are still those of the Python engine.
- Scattering model as a diagnostic (`GEOM.rays` `mix: true / false`, `--mix either|mix`): Arvedi and Arni with the
  either-or model of the drawn halls (`validation/engine_js_halls.md`). Arvedi: EDT error unchanged (simulated
  EDT / T30 1.08 with both, measured 0.84 - 0.92). Arni: EDT / T30 0.96 - 0.98 with either-or, 0.88 - 0.94 with the
  mixed direction, measured 0.91 - 0.96. No model closer in all halls; defaults unchanged.
- Page: **Calibrate…** combines the positions by the median (as `calibrate.py`; the mean before). The calibration
  record gets `avg` and its note states that drawn halls need separate calibrations for the page and Python.
- Timing diagnostic (`validation/timing.py`, `validation/timing_js.py`, `validation/timing.md`): 86 - 87 % of the
  Python engine's time is pyroomacoustics' ray tracer; the browser tracer on one thread is about 16 (drawn hall) and
  80 (mesh) times faster at the same ray count, with similar noise per ray. On the page's default hall the time is
  in the late-noise rendering on the main thread.
- Found with it (`validation/check_drawn_pyjs.py`): in a drawn hall the two engines do not agree. Detmold, same
  materials: browser T30 1.94 s, Python 1.51 s at 1 kHz (Sabine 2.03 s, Eyring 1.87 s). The browser scatters a ray
  with probability s, pyroomacoustics mixes the direction; in mesh halls both mix and agree.
- Detmold with the browser engine and both scattering models (`validation/detmold_js.py`, `validation/detmold_js.md`;
  new diagnostic option `GEOM.rays(..., { mix: true })`, off by default): the mixed direction reproduces the Python
  engine (T30 1.33 s with the start materials, Python 1.34 - 1.39 s; either-or 1.50 s). Calibrated on T30 separately,
  both models and the Python engine agree with the measured EDT and C80 about equally (C80 within 0.3 dB of each
  other, EDT at 500 Hz - 1 kHz within 3 points); the absorption they need differs (factor 0.97 against 0.72 at
  1 kHz). Page default unchanged.
- Detmold calibrated and compared at 20000 and 80000 rays (`validation/ray_noise.md`): the T30 calibration is not
  robust. Single-position T30 has outliers (up to 2.8 s against 1.4 s) from the ray-starved late histogram, and the
  mean over positions gave an absorption factor of 0.74 (20000 rays) or 1.00 (80000 rays) at 1 kHz; with the latter
  EDT is 17 - 28 % short.
- `calibrate.py --avg median | summed | mean`, default now `median` (was the mean): median over the positions, or T30 of their summed
  decay. Detmold with either: factor 0.71 - 0.78 at 1 kHz at 20000 and 80000 rays, and 80000 rays change the mean
  differences to the measurement by 0.2 dB (C80) and 3 points (EDT) at most (`validation/ray_noise.md`). The options
  were added after the result with the mean was seen. The hall-check scripts take `--avg` with the same default; their documented results (mean) are not redone,
  `--avg mean` reproduces them. Arvedi and Arni show no such outliers (shared trace per source).
- Ray noise against the ray count (`validation/ray_noise.py`, `validation/ray_noise.md`; Detmold, 20000 - 320000
  rays, two seeds): the noise falls with the square root of the ray count and the hall means do not drift, but at
  20000 rays the hall means of T30 and EDT differ by 5 - 10 % and 4 % between two seeds (the receivers share the
  rays), which is the uncertainty of the T30 calibrations of the hall checks.
- Fix: criteria of a condition with a delayed loudspeaker (`run.py`, `iso3382_energy`): the start bin and the shift of
  the delayed histograms were rounded differently, so the first direct sound could fall one 1 ms bin before the start
  and be left out (seen only in 0 ms conditions; up to 1 dB C80 at single receivers). New `brir_proto.hist_start`.
- Scattering and the effect of a reinforcement condition (`validation/scatter_delta.py`, `validation/scatter_delta.md`,
  plan committed before the run): the change of C80 by a condition depends on the scattering of the hard surfaces by
  less than half a JND on the hall mean, except Arvedi with B at +6 dB and 0 / 30 ms (+0.6 dB); robustness is shown
  only for C80 in Arvedi and Detmold with B at 0 dB. Elsewhere the per-receiver ray noise at 20000 rays (about 1 JND
  or more for EDT in all three halls, for C80 in OperaRIR) is too large to decide. Defaults unchanged.
- New check: OperaRIR, Finnish National Opera (https://doi.org/10.5281/zenodo.8096639, CC BY-NC 4.0), Genelec 8331A
  with its measured directivity (Aalto SOFA, read as spherical although it declares cartesian), 97 stalls seats, model
  from the published plan and section (`validation/opera_model.py`, `validation/opera_check.py`,
  `validation/opera_check.md`): after a T30 calibration the simulated C80 is 3.0 - 3.2 dB too high at 2 - 4 kHz, the
  opposite sign of Arvedi, growing from the front rows (within 1 - 2 dB) to row 17 (+8 dB); untested reading: no seat
  rows in the model (grazing over the seating). Directional loudspeakers at 2 - 4 kHz stay "not supported".
- OperaRIR seat-row experiment (`opera_check.py --seats`, `--start`): backrests as geometric strips on every row,
  recalibrated on T30, 10000 rays. The C80 bias still grows from the front rows to row 17 (+9 dB at 2 - 4 kHz); the
  missing seat rows as geometry do not explain it (no diffraction in the model; see `validation/opera_check.md`).
- OperaRIR with the engine seat-dip model (`opera_check.py --seat-dip`): C80 0.2 - 0.5 dB lower at 125 - 250 Hz,
  0.9 - 1.1 dB higher at 1 - 4 kHz (rigid rows add the floor reflection, +2 ... +4 dB on the direct sound above
  500 Hz, extrapolated above 1 kHz); the growth with the row stays.
- OperaRIR: seat-dip BEM with absorbing seats up to 4 kHz (`validation/seat_bem_hf.py`): at most 2 dB change of the
  direct path at 2 - 4 kHz. Levels by row show that the measured direct sound falls with distance as the simulated
  one; the C80 bias comes from the late energy, which in the simulation falls more steeply towards the rear stalls.
- OperaRIR: balcony overhang checked against the published drawing (same as the model; 3 - 4 m over the rear stalls);
  the late-energy error grows with the distance also at seats not under a balcony, so the overhang is not the main
  cause.
- OperaRIR scattering sensitivity (`opera_check.py --scatter 0.5`, fixed in advance): C80 bias at 2 / 4 kHz +3.2 /
  +3.0 -> +2.2 / +1.4 dB, row 17 +8 -> +6 / +5.4 dB, EDT 7 - 16 % closer; part of the bias, the growth with the
  distance about halved. Defaults unchanged.
- Scattering 0.5 also in Detmold and Arvedi (recalibrated, fixed in advance): EDT at 2 kHz closer in all three halls
  (Detmold -15 -> -5 %, Arvedi +21 ... +98 -> +19 ... +62 %); C80 at 2 kHz closer in OperaRIR and Detmold (+1.6 ->
  +0.5 dB) but 0.2 - 0.4 dB lower in Arvedi, where it was already too low. Differs by hall; defaults unchanged
  (`validation/detmold_kh.md`, `validation/arvedi_check.md`).
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
