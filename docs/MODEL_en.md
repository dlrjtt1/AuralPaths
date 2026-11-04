# AuralPaths

Path-separated binaural simulator for reinforced performance. LABO 1557.

A hall (shoebox, or a drawn plan outline with floor and ceiling lines) with an **amplified source** (direct sound plus a left/right PA pair), any number of
**unamplified sources** (direct sound only) and listener seats. For each source-seat pair it builds a
binaural room impulse response (BRIR) per path, applies the nominal ITDG and level-ratio conditions,
and reports timing, level and room-acoustic parameters.

> Hall size and absorption in `config.json` are placeholders. Do not read the numbers as properties of
> a real hall.

## Run (macOS)

```bash
pip install pyroomacoustics sofar soundfile scipy matplotlib
# hrir/KU100.sofa = HRIR_FULL2DEG.sofa from Zenodo record 3928297 (Bernschütz 2013)
python run.py                    # Python reference + out/viewer.html
python hall/make_hall.py         # reference-hall drawing (plan + section)
python test_signals/make_sines.py
```

A drawn hall goes into `config.json` as a `geometry` block (plan, floor, ceiling, materials, ism_order,
rays); **Copy config** in the viewer writes it. `examples/fan_hall_config.json` is a fictional fan hall
with raked seating: `python run.py examples/fan_hall_config.json` (about 1.5 min, writes `out_fan/`).

Keep each of your own halls in its own folder with its `config.json` and `out/`
(e.g. `python run.py my_hall/config.json`). Hall drawings and traced hall configs are not part of this repository.

Open `out/viewer.html` in a browser. Without the SOFA file, `run.py` only writes omni RIRs and the
plan figure.

## Viewer (`out/viewer.html`)

The page rebuilds every BRIR itself, so these work without rerunning Python:

- **Hall shape**: **Shoebox** or **Drawn hall**. A drawn hall is a plan outline (any polygon, e.g. a
  fan) plus a floor line and a ceiling line along the depth (raked seating, risers, stepped or sloped
  ceilings). Trace them over the loaded drawings:
  - **Trace outline** (plan): click the inside corners; click the first point, double-click or Enter to
    close; Backspace undoes, Esc cancels. Self-crossing outlines are rejected. **Edit corners** drags them.
  - **Trace floor / Trace ceiling** (section): click from the back of the hall (left) to the stage
    (right). A click within 15 cm of the previous depth makes a vertical step. The ceiling must stay at
    least 1.5 m above the floor.
  - Four materials (audience floor, stage floor, walls, ceiling), α per octave band and scattering s.
  - Image-source order (default 4) and number of rays (10k draft to 100k) trade speed against noise.
  - Width / depth / height are the drawing frame; the traced shape scales with them.
  - Heights in the layout table are above the local floor, so seats follow the rake.
  - **Dimensions** labels wall lengths on the plan and floor / ceiling levels on the section (m).
- **Semi-automatic tracing (works in any copy, no Claude needed):**
  1. Load the plan (and the section). In the align step, **Set scale…**: click the two ends of a dimension you know
     (clicks snap to line ends in a PDF) and type its length in metres. The box then sets the hall's width and depth
     (section: height, and depth if the plan has none); without a scale the box is stretched over the current size.
  2. Trace as above. With **Snap to drawing** on (default), each click goes to the nearest corner or crossing of the
     PDF's own lines within 10 screen pixels, else onto the nearest line, else to the 5 cm grid. The cursor shows which
     (square = corner, ring = line, cross = grid). Hold **Alt** to place a point freely. **Edit corners** snaps too.
  3. Vector lines exist only in PDFs exported from CAD; PNG / JPG / scanned PDFs keep the 5 cm grid.
  Check: a CAD plan PDF with 22 908 drawing lines; 40 random hovers near lines all snapped to a corner;
  Alt disables the snap.
- **Auto-trace from PDFs…** (web version inside Claude only; it asks Claude to read the drawings, using
  the viewer's Claude usage): choose the plan and / or the section, about 1–3 minutes.
  1. The page renders each sheet and reads every drawn line from the PDF.
  2. Claude reads the whole sheet: orientation, the room, 2–4 dimension strings.
  3. Scale = the dimensions with both ends snapped to the drawn extension lines (the dimensions must agree).
  4. Claude traces the outline (plan) or the floor and ceiling lines (section) on a crop of the room.
  5. Every traced edge is snapped to the nearest parallel drawn line within 0.3 m; corners are rebuilt as
     line intersections.
  6. Optional second pass: Claude sees its trace drawn over four 2× tiles and corrects points; they are
     snapped again (0.2 m).
  7. Plan and section are aligned on the stage front line; both drawings are laid under the result.
  Claude's simplifications are listed. **Undo auto-trace** restores the previous hall.
  Limits: precision depends on how well Claude reads the sheet; walls snap only where the PDF has vector
  lines (PNG / JPG keep Claude's positions). Stepped seating in sections is the hardest part (structure
  lines just below the treads); always check the overlay and fix with Edit corners or a retrace.
- **Hall**: width, depth, height, stage depth, absorption per octave band. Stage depth previews the
  stage edge while you type and applies on Enter.
- **Drawings**: a plan drawing (top view) and a section drawing (side view, stage on the right) can be
  loaded separately, by file, button or drag-and-drop onto the plan / section. PDF (first page), PNG,
  JPG and SVG are accepted. After loading, an align step rotates / mirrors the sheet and boxes the inside
  of the hall; the box is stretched over the room interior. **Adjust…** reopens it. The page starts with an empty room; **Show drawing** without a file shows a
  built-in schematic (seats, stage edge) that follows the hall size and stage depth.
- **On resize**: unlocked items move with the hall (x with the width, stage items with the stage,
  seats with the audience depth, heights unchanged) or stay in place.
- **Conditions**: nominal ITDG 0–60 ms (1 ms steps) and level ratio −9 to +6 dB (0.5 dB steps), by slider
  or typed value; the A/B inputs take the same ranges. Python reference values exist for the grid in
  `config.json` (`conditions`: ITDG 0 / 20 / 40 / 60 ms × level ratio −9 / −6 / −3 / 0 / +3 / +6 dB). The trend
  plot draws ITDG 0 / 20 / 40 / 60 ms over the whole level range; the ring is the current condition.
- **PA aiming**: coverage (Omni, 120°, 90°, 60°), azimuth (0° = straight down the hall, + towards +x) and
  elevation (+ up) per PA; **Aim at seat** points it at the selected seat. In `config.json`:
  `"coverage": 90, "aim": {"az": 29.7, "el": -1.4}` on `B_L` / `B_R`.
- **Layout**: drag sources, PAs and seats on the plan or type x/y/z. Lock items one by one or all
  at once; **Reset layout** returns to `config.json`.
- **Seat map** (halls with a `"seats"` list in the config, e.g. seats traced one by one from the plan drawing): every seat drawn on the plan, coloured by the
  effective ITDG (nearest PA minus amplified direct sound) or by a level-ratio estimate; PA-first seats get
  an orange ring. Hover shows the seat's x/y/z, ITDG via B_L and B_R and the estimate. **Clicking a seat
  moves L / C / R there** (choose which in the menu). **Copy seat CSV** copies the current condition.
  The level estimate is the reference seat's level ratio plus the direct-sound difference
  (1/r² and PA directivity, 500 / 1000 Hz) between the seat and the reference seat. It is not a room
  simulation per seat; at the L / R positions it differs from the BRIR energy ratio by up to about
  1.5 dB (see `run_log.txt`).
- **Unamplified sources**: add up to 5, remove any.
- **Listen**: one dry file for the amplified source, one per unamplified source; Mix / Direct only /
  PA only; headphones. **Sennheiser HD600 compensation** (on by default when the config names a headphone filter) runs the
  output through the Sennheiser HD600 compensation filter, so the binaural signal is equalised for those
  headphones; turn it off for other headphones or loudspeakers.
- **Save config…** (next to Load config): downloads the complete current config (`<hall>_config_edited.json`):
  the config the page was built from (or the one loaded) with the current hall, sources, aims, directivity data
  and seats. Put it in the AuralPaths folder and run `python run.py <file>`. **Copy config** copies the same JSON.
- **Load config…**: opens a config JSON (e.g. `my_hall/config.json`; dropping it on the plan works too)
  and switches the page to that hall, its materials, sources and seats. **Reset to config** goes back to
  the config the page was built from.

While the geometry matches `config.json` the Python reference values appear in brackets next to the
browser values.

## Model

### Shoebox

| Part | Method |
|---|---|
| Early (direct + 100 ms) | Shoebox image sources to order 12 (pyroomacoustics damping and air absorption), nearest KU100 HRIR per image, fractional delay |
| Late | Octave-band noise shaped by the image-source energy envelope (order 60, incoherent sum, 5 ms smoothing) times the diffuse-field HRTF band gain; independent noise per path. Left and right noise carry the diffuse-field interaural coherence Γ(f) of the KU100 set (see below) |
| Join | sin² crossfade, 10 ms, starting at direct + 100 ms |
| PA directivity | Generic axisymmetric pattern (an engineering assumption, not a measured loudspeaker): nominal −6 dB full angle at and above 2 kHz, widening below as BW(f) = min(360°, coverage·max(1, (2000/f)^0.7)); amplitude ((1 + cos θ)/2)^n with −6 dB at BW/2, floor −30 dB. Applied exactly to every image source (emission direction = direction to the first reflection point); the ray-traced diffuse part is scaled by the pattern's mean energy 1/(2n + 1). Polar data can replace it (see Loudspeaker directivity from data) |
| Conditions | Reference seat C: PA delay = nominal ITDG − (PA arrival − amplified arrival); PA gain sets the binaural energy ratio |
| Parameters | C80, D50, Ts, EDT, T30 from the summed energy histograms of the amplified chain (500 + 1000 Hz octave mean); IACC E3 from the binaural sum over 0–80 ms; Python also writes IACC L (80 ms to the end, 500 / 1k / 2k Hz) and IACC L at 125 / 250 Hz |

Room-acoustic parameters use the incoherent image-energy sum. Band-filtering the synthesised omni
waveform of a perfectly regular shoebox lattice was found to inflate late energy (+9.6 dB at 500 Hz in
the placeholder hall), so it is no longer used.

### Drawn hall

| Part | Method |
|---|---|
| Surfaces | Plan polygon × floor/ceiling profiles → planar polygons (floor strips, risers, ceiling strips, walls split at profile breaks) |
| Specular | Image sources to the chosen order, each path back-traced through its reflecting polygons and checked for occlusion (non-convex rooms); rendered with KU100 HRIRs in the first 100 ms |
| Diffuse | Stochastic ray tracing: N rays of power 4π/N, Lambert reflection with probability s, receiver sphere r = 0.5 m; histogram in the same energy unit as the image sources |
| Combination | Total energy = image sources + max(0, rays − image sources) (10 ms smoothing). The residual is added as noise inside the early window (both engines; Python only since this version, before it the Python BRIRs lacked this energy in the first 100 ms, about 0.5–1 dB); the total shapes the late noise |
| Python reference | Same surfaces passed to pyroomacoustics (image sources + its ray tracer), `geometry` block in `config.json` |

Checks: on a shoebox, the browser image sources match pyroomacoustics exactly (62 images) and the
ray-tracing histogram matches the analytic energy within ±1 dB. On a non-convex fan hall with risers
(31 surfaces) the image lists match pyroomacoustics exactly. A drawn rectangle with s = 0 reproduces the
shoebox (T30 1.54 / 1.54 s, EDT 1.18 / 1.20 s, C80 2.05 / 2.21 dB); with s = 0.1 the decay shortens
(T30 1.29 s) because scattering is modelled in the drawn hall and not in the shoebox.

Browser vs Python on the fan test hall (3 seats, 50 000 rays, different random rays): C80 within
0.7 dB, D50 0.04, Ts 7 ms, EDT 0.10 s, T30 0.05 s, IACC E3 0.10. EDT and C80 differences are near the
usual JND, so read single-seat differences below about 1 dB C80 as ray-tracing noise; raise the rays
for final numbers. (Measured before the air-absorption fix below, which changes the Python values at
500 Hz–1 kHz by less than 0.5 dB.) BRIR energies browser vs Python after the fixes (two drawn test halls, 24 paths): first
100 ms within 1.0 dB, 120–300 ms within 0.9 dB, 0.3–1.6 s within 1.8 dB (independent noise and rays).

### Edge diffraction (first order, UTD)

Drawn halls only, both engines (`diffraction.py`, `GEOM.edges` / `GEOM.diffract`; the two agree to 1e-10).
Method: Uniform Theory of Diffraction, Kouyoumjian & Pathak (1974), "A uniform geometrical theory of diffraction
for an edge in a perfectly conducting surface", Proc. IEEE 62, 1448–1461
([Google Scholar](https://scholar.google.com/scholar?q=A+uniform+geometrical+theory+of+diffraction+for+an+edge+in+a+perfectly+conducting+surface)),
in the room-acoustics form of Tsingos, Funkhouser, Ngan & Carlbom (2001), SIGGRAPH,
[doi:10.1145/383259.383323](https://doi.org/10.1145/383259.383323): spherical-wave incidence, rigid wedge faces whose
reflection terms are weighted by R = √(1 − α) of each face (a heuristic, as in Tsingos et al.).

| Item | Choice |
|---|---|
| Edges | Every straight edge shared by two surfaces whose room-side angle exceeds 180° (riser tops, stage lip, ceiling steps, re-entrant plan corners, convex profile breaks ≥ 2°). Concave edges have no first-order term |
| Path | Source → apex on the edge (Keller cone, shortest path) → receiver; both legs checked for occlusion |
| Coefficient | Complex UTD coefficient on 32 frequencies (16 Hz–24 kHz), transition function F(X) by its power series (X ≤ 16) and asymptotic series (X > 16) |
| Rendering | One arrival per edge with the HRIR of the apex direction, complex spectrum applied with the path delay |
| Energy | Added to the image-source histogram including its interference with the geometrical arrivals of the same boundary (direct sound, reflections in the two wedge faces), averaged over 8 frequencies per octave band |
| Switch | `"diffraction": false` in the `geometry` block, or *Edge diffraction* in the viewer |

Check (stage lip, 1 m step, source 0.3 m above the stage): across the shadow boundary of the direct sound the
energy is continuous (−1.0 / −0.9 dB at 250 Hz, −1.7 / −1.7 dB at 1 kHz, −3.0 / −2.9 dB at 4 kHz just
below / above the boundary); without diffraction it jumps from 0 dB to nothing. Half-plane test: total field
continuous across the shadow boundary, tending to half the free-field amplitude at high frequencies.

Measured check, BRAS RS5 (`validate_bras.py`, results in `validation/bras_RS5.*`): 16 RIRs of a 2.07 m partition
on a hard floor (4 loudspeaker × 4 microphone heights), compared with UTD + floor images in third-octave bands inside
a window that ends before the partition's side edges. Mean absolute difference 500 Hz–2 kHz: 2.2 dB over the 11
shadow positions, 1.8 dB over all 16; 250 Hz–8 kHz 2.1 / 1.8 dB. The predicted level is on average 0.1–1.9 dB high
(more above 5 kHz in the shadow), which includes what the model leaves out: the loudspeaker's response and
directivity (only its 1 kHz calibration is used), the 25 mm thickness of the partition, air absorption. The interference
pattern of the four paths (dips near 1 and 3 kHz with the low loudspeaker) is reproduced. Three IRs with the
source or receiver at floor level (LS4-MP1, LS1-MP2, LS4-MP2) show sound arriving at the straight-line time,
before the diffracted path — most likely transmission through the partition (the BRAS documentation notes it),
which is not modelled; LS4-MP2 also has only a 1 ms window. Arrival times agree within 0.1 ms elsewhere.

Not modelled: higher-order paths (diffraction combined with reflections, edge to edge), diffraction from edge
end points, edges of objects the 2.5D model does not have (seats, balcony fronts, reflectors). The
reflection-factor weighting is not a solution for absorbing wedges.

### Directional late field

The late noise used to take the ear energies and the interaural coherence of an ideal diffuse field. It now
takes them from the directions the late sound actually arrives from (drawn halls):

1. A ray tracer records, per receiver, the energy arriving after direct + 100 ms from each of 64 direction bins
   (Fibonacci sphere, head frame) per octave band (`dirrays.py`, 20 000 rays per source, receiver sphere 1 m;
   in the browser the same bins are filled by its own ray tracer).
2. With ρ_d = energy per bin / HRIR area weight of the bin, ear energy per band = Σ ρ_d·BE_d / Σ ρ_d·Ω_d and
   coherence Γ(f) = Σ ρ_d X_d / √(Σ ρ_d P_L,d · Σ ρ_d P_R,d), where BE, X, P are sums over the KU100 directions in
   each bin (`late_dir_tables`). Γ is complex; the right channel gets its phase.
3. Noise pairs with that coherence (same mixing as above), one per band, shaped by the energy histogram as before.

For a uniform field this gives exactly the diffuse-field values (checked: 6e−15). The overall late energy and its
decay still come from the energy histogram; only its split between the ears and their coherence changed.
Seed-to-seed spread of the late ILD: about 0.1 dB (20 000 rays, 1 m sphere; 0.3–0.4 dB with 0.5 m). One
direction distribution for the whole late part (no change of direction with time); the source is taken as
omnidirectional for the directions. Shoebox: still the diffuse field. Switch: `"late_directional": false` in
`binaural`.

### Air absorption in the ray-traced energy (fixed)

pyroomacoustics 0.10 leaves air absorption out of its ray-tracing histograms (checked: the histograms with and
without `air_absorption` are identical); it applies it only when synthesising an RIR. `energy_hist` now applies
exp(−m c t) per bin. Before the fix the Python late energy of drawn halls was too high at high frequencies
(drawn test hall, 0.1–1 s after the direct sound: +2 to +3 dB at 4 kHz, +6 to +11 dB at 8 kHz, up to +0.5 dB at 500 Hz–1 kHz), so the
Python T30 / EDT of drawn halls at 2 kHz and above were too long and the late part too bright. Browser and
Python histograms now agree within 0.5 dB in every band (drawn test hall, one path). The shoebox model was not affected.

### Late interaural coherence

Target: Γ(f) = Re Σ w·H_L·H_R* / √(Σ w·|H_L|² · Σ w·|H_R|²) over all KU100 directions (area weights), i.e. the
interaural coherence of an ideal diffuse field for this head. Two independent noises n1, n2 are mixed per
frequency as L = cos a·n1 + sin a·n2, R = cos a·n1 − sin a·n2 with a = arccos(Γ)/2 (coherence = Γ, unit power;
the two-channel case of Habets, Cohen & Gannot 2008, JASA 124(5), doi:10.1121/1.2987429).
Check: a field of 3000 plane waves from random directions rendered with the KU100 HRIRs has the same
third-octave coherence within 0.07. For the KU100, Γ is about 0.9 at 125 Hz, 0.65 at 250 Hz and near 0
above 500 Hz, so the change shows mainly below 500 Hz (late IACC at 125 Hz rose from about 0.2 to 0.9);
IACC L in the standard 500–2000 Hz bands hardly changes.

### Browser vs Python (placeholder shoebox hall, 36 conditions)

| Quantity | Max difference |
|---|---|
| C80 / D50 / EDT / T30 | 0.007 dB / 0.001 / 0.001 s / 0.001 s |
| Ts | 0.1 ms |
| IACC E3 | 0.035 (browser uses a ~4° HRIR subset) |
| First 100 ms BRIR energy | 0.05 dB |
| Late BRIR energy (200–1200 ms) | 0.3 dB (different noise realisations) |

## Stimuli for the listening tests (`make_stimuli.py`)

`python make_stimuli.py examples/stimuli_example.json` builds every stimulus from path-separated BRIRs
(`{seat}_{path}.wav`, no headphone EQ). The same script is meant for both stages: AuralPaths BRIRs
(`out/brir/`) and measured KU100 BRIRs named the same way, so the stages differ only in where the
BRIRs came from.

- Path A = sum of `path_A_inputs` (e.g. vocal + piano) through BRIR A; path B = sum of `path_B_inputs`
  (vocal) through B_L + B_R.
- ITDG is set at the reference seat from the BRIR onsets (first sample within −20 dB of the peak,
  earlier ear; B = earlier of B_L, B_R). Whole-sample delays. A negative electrical delay is not
  realisable in a hall; it is implemented by delaying path A and flagged.
- Level ratio is set at the reference seat as defined in the proposal: RMS of the ear signals over the
  whole stimulus, path B (B_L + B_R) over path A, energy averaged over both ears, before headphone EQ.
- The same delays and gain are used at every seat; `stimuli.csv` lists per stimulus the delays, gain,
  effective ITDG via B_L and B_R, PA-first flag, effective level ratio, RMS and peak level and a hash.
- Path A level is the same in every condition (one global scale factor, peak at `headroom_dbfs`).
  Total loudness therefore changes with the level ratio, as intended in the proposal; it is recorded.
- One path-A-only stimulus per seat (`*_ref_pathA.wav`) as the timbre anchor.
- Optional headphone compensation (`headphone_filter`) is applied to the final mix only.
- `manifest.json` records the config, code, dry-file and BRIR hashes (and the BRIR set's own manifest).

Checks done: at the reference seat the measured ITDG and level ratio equal the nominal values
(0.000 ms, 0.000 dB); an independent rebuild of every click stimulus from the raw BRIRs matches the
files to 1.5·10⁻⁵ (float32 rounding); the B-path onset measured in the files equals the listed effective ITDG.
Playback level calibration, presentation, randomisation and responses belong to the experiment program.

## Calibration from measurements (`calibrate.py`)

`python calibrate.py my_hall/config.json measurements.csv --source-directivity directivity/dodeca_NTi_DS3.csv`

- `measurements.csv`: `label, src_x, src_y, src_z, rec_x, rec_y, rec_z, band_hz, T30_s, EDT_s` (one row per position
  and octave band 125 Hz–4 kHz; EDT optional). Template with synthetic values: `examples/calibration_measurements_example.csv`.
- Per band, one factor scales the absorption of the adjustable groups (`--adjust aud,wall,ceil`; default all) until
  the simulated T30, averaged over the positions, is within 2 % of the measured average (the JND of reverberation is
  5 %, ISO 3382-1 Annex A). Update: k ← k·T_sim/T_meas (Sabine scaling), coefficients kept in 0.01–0.95.
- Writes `<config>_calibrated.json` (materials replaced, `_calibration` record with factors and before / after values)
  and `_report.csv` / `_report.md` (per band and position, EDT as an unfitted check).
- One factor per band cannot tell which surface is wrong. Calibrate and validate at different positions.

Check with synthetic "measurements" (a drawn test hall with altered materials, 2 calibration positions, ~30 s):
T30 error at the calibration positions −13 % → −1.3 % (worst band); at a held-out position T30 −16 % → −4 % and
EDT −11 % → +3 %.

## Checking diffraction against measurements (`validate_bras.py`)

BRAS (Aspöck, Brinkmann, Ackermann, Weinzierl & Vorländer 2020, *Benchmark for Room Acoustical Simulation*, v3,
[doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3), CC BY-SA 4.0 — verify on the page)
has scene RS5 "simple diffraction (infinite edge)": a 25 mm MDF partition 2.07 m high, 4 loudspeaker × 4
microphone heights, Genelec 8020c, 44.1 kHz, RIRs in Pa as SOFA and WAV. Not bundled and not reachable from the
build environment: download `1_scene_descriptions-RS5.zip` yourself.

```bash
python validate_bras.py "RS5 diffraction (infinite wedge)/RIRs/RS5_RIRs.sofa" --out validation/bras_RS5
```

Scene geometry is built in (from `Geometry/RS5_RIR.png`: front face x = 5.487 m, 25 mm, 2.066 m high, 4.75 m wide,
centred at y = 2.985 m, hard floor z = 0); positions are read from the SOFA file. Model: thin rigid half-plane, rigid
floor by images (direct and floor-reflected paths when not blocked, four diffraction paths), point source of 0.4 Pa at
1 m (the stated 80 dB SPL at 2 m, 1 kHz), flat in frequency. Measured and predicted IRs get the same window, from the
first arrival − 0.5 ms to the first arrival via the side edges − 0.3 ms; bands below 2 / window are marked. Run
on BRAS RS5 v3 (2026-11-03); results above under *Edge diffraction*.
RS6 (finite body) and RS7 (seat dip, 15 blocks) need multiple diffraction, which this model does not have.

## 3D OBJ halls and conversion to a drawn hall (`obj_to_hall.py`)

The Python engine can also run a hall given as a Wavefront OBJ mesh (`"geometry": {"mesh": {...}}`, described at
the top of the mesh part of `geometry.py`). The browser page stays 2.5D; `obj_to_hall.py` turns a mesh hall into a
drawn hall that the page opens with **Load config…**.

- Mesh: faces have no reliable winding, so the room is found by a voxel flood fill (5 cm) from a source position;
  each face's inward normal is the side where the room is, faces with no room on either side are dropped, and
  every kept face also gets a back-facing twin 2 mm behind it (a ray that slips behind a face is reflected instead
  of lost). OBJ group names select the materials (case-insensitive substring match, so the SketchUp tags that
  Blender writes into the group names work). Large meshes are decimated (`max_faces`, fast-simplification, MIT).
  Image sources to order 1 only (pyroomacoustics enumerates N^order images), no diffraction (a tessellated curved
  surface has thousands of shallow edges that are not wedges), isotropic late field above 3000 surfaces.
- Conversion to 2.5D: plan outline = outline of the room's voxels; for each 0.25 m slice along the depth axis,
  floor = plan-area mean of the lowest room voxel per column (seat blocks count as raised floor) and ceiling =
  floor + slice volume / slice area, so the volume is kept (ULH 742 → 719 m³, STC 816 → 805 m³). A dome becomes a
  vault extruded across the width; balconies and overhangs are lost; an object covering part of the width (a
  lectern) becomes a raised strip across the whole width.
- Materials: faces go to the four 2.5D groups by their inward normal (floor / stage, ceiling, wall). The 2.5D hall
  has less surface than the mesh (ULH 942 → 622 m²: no seat risers, no small faces), so keeping each group's
  absorption area A_g (`--preserve sabine`) raises the mean α, and the 2.5D hall then decays faster than the mesh.
  The default (`--preserve eyring`) sets α_g = 1 − exp(−A_g / S_g,2.5D): the 2.5D group's Eyring exponent equals the
  mesh group's Sabine absorption area. Reason: the ray-traced T30 of both 3D meshes was close to Sabine (STC 1.47 s
  vs 1.43 s; ULH 1 kHz 1.94 vs 1.95 s), while a simple 2.5D hall decays like Eyring (check below). In ULH the 2.5D
  T30 is then 0.07–0.14 s below the mesh at 125 Hz–4 kHz; keeping A gives 0.17–0.28 s, and one factor per band that
  keeps the room's Eyring exponent (`room-eyring`) 0.14–0.25 s (`validation/fratoni_ULH_preserve.md`). A
  per-material Eyring sum (Millington's form) was also tried and was worse (it weights the absorbing seat faces up).
- Check of the ray tracer itself (`validation/check_rt_eyring.py`, shoebox 12 × 9 × 7 m, uniform α): with
  scattering 0.7 the ray-traced T30 is within 1–3 % of Eyring at α = 0.05–0.3; with scattering 0.1 it lies between
  Eyring and Sabine (up to +12 % over Eyring at α = 0.3).

```bash
python obj_to_hall.py mesh_config.json --depth-axis y --stage-end min --stage-depth 2.4   # -> mesh_config_2p5d.json
```

## Room criteria against measured halls (`validate_fratoni.py`)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*,
Mendeley Data, [doi:10.17632/y7xnv6xg5s.1](https://doi.org/10.17632/y7xnv6xg5s.1), CC BY 4.0 (SketchUp models,
ISO 3382-1 criteria averaged over the receivers per source, boundary conditions, FDTD IRs). Not bundled. Two of
its four rooms fit the model: **ULH**, a raked university lecture hall, and **STC**, an elliptical concert hall with
domed ceilings (about 900 and 950 m³, 200 seats each: Fratoni 2022, AIA 48° Convegno Nazionale, ISBN
978-88-88942-62-9). The two opera houses (TCB, DUS) have box tiers and balconies, outside a 2.5D model.

Method:
- Models exported from SketchUp via Blender as OBJ with "Object Groups" and "Material Groups" on, so that the
  SketchUp tags survive as group names. ULH: the four tags are the four materials of the dataset sheet. STC: the
  tags do not match the sheet's five materials one to one; assignment (AuralPaths' judgement): `shell_sidewalls`
  split by orientation into "Plasterboard (walls)" and "Ceiling", `crown` → Ceiling, `seat-cushion` → Seats,
  `seats-wood_stage` → Wood, `floor` → Wood (the sheet has no floor material), `doors_organ` → Furniture.
  Swapping `doors_organ` to Wood changes T30 by 0.03–0.05 s (`validation/fratoni_STC_doors_*.md`).
- Absorption and scattering: the dataset's values for its geometrical-acoustics (GA) calibration, unchanged. These
  were tuned by the dataset's authors in Odeon (Fratoni, D'Orazio & Garai 2023, Forum Acusticum, Turin,
  [doi:10.61782/fa.2023.1114](https://doi.org/10.61782/fa.2023.1114), describe this calibration procedure for
  opera houses); Odeon adds scattering from surface size and path length to the given coefficient (Christensen &
  Rindel 2005, Forum Acusticum, Budapest,
  [DTU Orbit](https://orbit.dtu.dk/en/publications/a-new-scattering-method-that-combines-roughness-and-diffraction-e/)),
  which this engine does not. The check therefore tests this engine with another program's calibrated inputs; it
  is not a calibration of this engine.
- Positions: not in the dataset as numbers; read from the position figures in the Room_Criteria sheets (plan for
  x / y, section for heights), uncertain by about ±0.3 m.
- Engine: image sources order 1 + ray tracing (ULH 20 000 rays; STC 6 000 rays, mesh decimated to 3 000 faces),
  air absorption on; EDT, T30, C80 / C50 and Ts per octave band at each receiver, averaged over the receivers like
  the measured sheets, and compared in JND (ISO 3382-1 Annex A: 5 % EDT / T30, 1 dB C80 / C50, 10 ms Ts).

Results (simulated − measured, in JND; full tables and figures in `validation/fratoni_ULH.*`, `fratoni_STC.*`):

| hall, source | model | T30 125 / 250 / 500 / 1k / 2k / 4k Hz | EDT 500–4k | C50 / C80 500–4k | Ts 500–4k |
|---|---|---|---|---|---|
| ULH, S1 (26 receivers) | 3D mesh | −2.3 / −1.2 / +0.9 / +1.0 / +0.1 / −0.9 | −0.1 … +0.7 | −0.2 … +0.2 | −0.2 … +0.4 |
| | 2.5D | −3.9 / −2.1 / −0.7 / +0.1 / −1.2 / −2.5 | −1.0 … +0.9 | −0.6 … +0.3 | −0.6 … +0.6 |
| STC, S1 (10) | 3D mesh | +6.8 / +4.1 / +4.0 / +2.3 / +3.6 / +3.5 | +3.8 … +5.2 | −1.6 … −1.0 | +2.1 … +3.1 |
| | 2.5D | +7.4 / +4.5 / +4.1 / +2.1 / +3.3 / +3.3 | +5.1 … +6.9 | −2.1 … −1.6 | +2.4 … +3.4 |
| STC, S2 (4) | 3D mesh | +8.8 / +2.8 / +2.5 / +2.6 / +4.1 / +4.0 | +2.8 … +5.4 | −2.1 … −1.0 | +1.7 … +2.8 |
| | 2.5D | +8.6 / +2.6 / +2.0 / +1.6 / +3.2 / +3.1 | +2.1 … +4.4 | −1.6 … −0.4 | +1.2 … +2.4 |

Reading:
- ULH: from 500 Hz to 4 kHz all criteria of the 3D mesh are within about 1 JND of the measurement; at 125–250 Hz
  T30 and EDT are 1–2 JND short and C50 about 1.3 dB high. A Sabine estimate from the same inputs is also short there
  (1.15 s vs 1.56 s measured at 125 Hz, mesh volume 742 m³), so the low-frequency gap is in the inputs (volume and
  coefficients as used here), not in the ray tracing. The 2.5D hall is within 0.15 s of the mesh from 250 Hz to
  2 kHz.
- STC: both models are about 15 % long (1 kHz: 1.47 s vs 1.32 s measured), the 3D mesh and the 2.5D hall agree
  with each other within 0.06 s in T30, and a Sabine estimate from the same inputs is also long (1.43 s). Eyring
  from the same inputs gives 1.32 s, the measured value, but the ray tracer does not reach it here: the absorption
  sits on the seats while the shell and the domes reflect almost everything (α ≈ 0.1, scattering 0.02–0.05), so the
  late field is not diffuse. Raising all scattering to at least 0.2 or 0.5 (`--min-scatter`) changed T30 by less
  than 0.05 s. The likely cause is the inputs tuned for Odeon's scattering model; an engine error is not
  indicated (shoebox check above). The 2.5D conversion (domes → vault) is not the cause.
- For comparison, the same authors' Odeon calibrations of four opera houses end within −0.06 … +0.12 s in T30 and
  −0.4 … +0.6 dB in C80 at 500–1000 Hz (Fratoni, D'Orazio & Garai 2023, Table 1); calibrated commercial GA is not
  exact either.
- What this means for use: in a hall like ULH, with inputs from a GA calibration, the engine reproduces the
  measured room criteria at mid and high frequencies; in a hall with strongly non-diffuse geometry (STC) it does
  not without calibration of its own (`calibrate.py` with measured T30). Neither check tests the early arrivals,
  ITDG or the PA paths seat by seat: the measured values are receiver means.

```bash
python validate_fratoni.py "<dataset folder>" ULH --obj ULH_model.obj --rays 20000 --out validation/fratoni_ULH
python validate_fratoni.py "<dataset folder>" STC --obj STC_model.obj --rays 6000 --out validation/fratoni_STC
python validate_fratoni.py "<dataset folder>" STC --obj STC_model.obj --no-3d --stc-doors Wood --out validation/fratoni_STC_doors_Wood
```
The converted halls (`validation/fratoni_*_2p5d_config.json`, CC BY 4.0 with the dataset's attribution) open in the
page with **Load config…**. Run 2026-11-05 (ULH 3D mesh 64 min, STC 46 min on 2 CPU cores).

## Seat dip

Not modelled. A literature check found no closed-form or parametric model that predicts the seat-dip filter
for a given hall: Meyer, Tahvanainen, Saarelma & Lokki (2023), JASA 154(3), 1628–1639,
[doi:10.1121/10.0020826](https://doi.org/10.1121/10.0020826), review the analytical models (Takahashi 1997:
qualitative only; Ishida 1995, Sakurai et al. 1993: not fully consistent with measurements) and rely on FDTD for
simplified geometries; their results (dips near 80–100 Hz and 250 Hz, dependent on seat underpass, rake and stage
height, mainly in the early response) are not a transfer function that can be applied per seat. A filter made
up here would be an invented parameter set. Options if needed later: a measured seat-dip response per seat
area (phase 2 measurements) applied to the direct sound, or wave-based simulation of the seating.

## Reproducibility (`out/manifest.json`)

`run.py` writes `manifest.json` next to the BRIRs: AuralPaths version, the config as used and its hash,
hashes of the code files, the KU100 SOFA file and the headphone filter, Python / NumPy versions, the
seed scheme and a hash of every BRIR (audio samples only; float WAV files carry a time stamp).
Late-noise and ray-tracing seeds are fixed per path, so the same code and config give identical BRIRs
(checked: two runs, 24 / 24 files identical). Keep the manifest with any BRIR set used in an experiment.

## Loudspeaker directivity from data

In the viewer: **Layout (06) → Directivity** button on any source row → choose a SOFA or CSV file. The data is
stored with that source; set the aim in the aiming table below; **×** removes it. **Copy config**
writes the data into the config (`"directivity": {"name": …, "data": [[band_hz, plane, angle_deg, level_db], …]}`),
so `run.py` uses it without the separate file, and **Load config…** restores it.

**SOFA (full sphere)**: AES69 files with `Data.Real`/`Data.Imag` and frequencies `N` (FreeFieldDirectivityTF,
e.g. the TU Berlin instrument database) or with impulse responses `Data.IR`. Directions come from
`ReceiverPosition` when there are several receivers (microphones around the source), otherwise from
`SourcePosition`; coordinates as stored (x front, y left, z up of the source); power is averaged over
measurements (e.g. notes) and over each octave band, then resampled to a 5° balloon (4 nearest points,
inverse-distance weighting) and normalised to straight ahead. The aim points the source's x axis.
Copy config stores the balloon (`"directivity": {"name": …, "balloon": {"bands": […], "db": [band][el][az]}}`).
In a config file use `"directivity": "path/to/file.sofa"`. Check: `examples/directivity_test_generic90.sofa`
(TEST DATA: the generic 90° pattern, constant within each octave, on 2522 directions) reproduces the
generic model within 0.8 dB above −20 dB (0.4 dB up to 4 kHz), and C80 / IACC E3 / level ratio within
0.04 dB / 0.006 / 0.2 dB; browser and Python balloons agree within 0.005 dB.
Reading SOFA in the browser loads the h5wasm library once from jsDelivr (needs the internet).

**Normalisation**: by default each band is 0 dB straight ahead. For nominally omnidirectional sources
(dodecahedra) add the line `# normalize=mean` to the CSV: each band is then 0 dB at the power mean over the
horizontal circle, so the pattern does not change the source's spectrum. Lines starting with `#` are comments.

**Dodecahedron data (`directivity/`)**, read from the manufacturers' data sheets (typical data of the model,
horizontal plane only; the vertical plane is assumed equal):
- `dodeca_HBK_4292L.csv`: B&K OmniPower 4292-L, Product Data BP 1689 Fig. 6, 1 / 2 / 4 / 8 kHz (1/3 octave),
  traced from the PDF's vector curves; 500 Hz and below omni, as the data sheet states. Ripple 3 / 12 / 10 / 10 dB.
- `dodeca_NTi_DS3.csv`: NTi Audio DS3, Product Data p. 2, 1 / 2 / 4 / 5 kHz, traced from the raster plots
  (±0.5 dB); assumed: first band in each caption = solid curve. Ripple 0.7 / 3.3 / 4.6 / 4.0 dB; below 1 kHz
  and above 5 kHz the nearest measured band is used.
- `directivity/checks/`: the traced curves drawn over the original figures.
- `meyer_CQ-1_nominal.csv` (80° H × 40° V) and `meyer_UPM-1P_nominal.csv` (100° × 100°):
  NOT measured data. Meyer Sound publishes coverage figures only (detailed data only inside MAPP); these files apply
  the generic pattern to the nominal coverage, separately per plane.

In a config file a source can also point to a CSV file instead of the generic coverage pattern:
`"directivity": "path/to/file.csv", "aim": {"az": …, "el": …}` (any source, e.g. a dodecahedron for
path A or the hall's PA model). CSV columns `band_hz, plane, angle_deg, level_db`: plane `h` = horizontal
polar (+ = loudspeaker's right, seen from behind), `v` = vertical polar (+ = up); one-sided data
(0–180°) is mirrored, missing `v` = rotationally symmetric. Levels are normalised to 0 dB on axis per
band and interpolated to the model octave bands (log frequency). Between the two planes the level is
blended as cos²φ·Lh + sin²φ·Lv in dB (φ = angle around the axis): an engineering assumption, exact only
on the measured planes. The diffuse share uses 1/Q integrated from the same pattern. The viewer shows
the source as "Data: file" in the aiming table; aim stays editable.
`examples/directivity_test_generic90.csv` is TEST DATA sampled from the generic 90° pattern (not a real
loudspeaker): with it, C80 / D50 / EDT / T30 / IACC agree with the generic model within 0.04 dB / 0.005 /
0.003 s / 0.001 s / 0.007, and the effective level ratio within 0.2 dB.
For other loudspeakers, use manufacturer data or your own measurements.

## Outputs (`out/`)

- `brir/{seat}_{path}.wav` — 2-channel BRIR per path, no delay/gain applied
- `brir_Sennheiser-HD600/{seat}_{path}.wav` — the same BRIRs through the HD600 compensation filter
  (only when `binaural.headphone_filter` is set; use these for headphone listening tests)
- `manifest.json` — generation record (see Reproducibility)
- `seat_map.csv` — every traced seat × ITDG × level ratio: effective ITDG via B_L / B_R, PA first,
  level-ratio estimate (direct-sound geometry, see Seat map)
- `conditions.csv` — seat × ITDG × level ratio
- `path_checks.csv` — direct-sound arrival: geometry vs detected onset
- `brir_parts.npz`, `plan_itdg.png`, `run_log.txt`, `viewer.html`

## Known limitations

- Drawn hall is 2.5D: the cross-section along the depth is the same at every x (no side balconies,
  no boxes, no ceiling reflectors that vary across the width); four material groups only
- OBJ mesh halls: Python engine only; image sources to order 1, no diffraction; the conversion to a drawn hall
  keeps the volume and maps the absorption so that T30 stays close to the mesh, not where absorption sits (see *3D OBJ halls*)
- Room-criteria check against measured halls: within about 1 JND at 500 Hz–4 kHz in a raked lecture hall (ULH),
  about 15 % too long in an elliptical domed hall (STC) with the dataset's Odeon-calibrated inputs (see *Room
  criteria against measured halls*)
- Drawn hall values come from ray tracing and carry random noise (see above); the shoebox ones do not
- Shoebox: uniform absorption, no diffraction, diffuse late field. Both: scattering not modelled in the image sources
- Diffraction: first order only, straight edges of the drawn surfaces; no seats, no edge end points (see above)
- No seat-dip effect (see above)
- Level ratio is a BRIR energy ratio (white-input equivalent), not the stimulus RMS defined in the
  proposal. The simulator uses it only to set the PA gain; the listening-test program sets the
  experiment's levels with the proposal's RMS definition
- Seat map: seat positions are cushion centres from the plan drawings; ear height 1.2 m above the model
  floor 0.2 m in front of the cushion (chairs at the rear of their tier). The model's tiers are straight,
  so side seats on curved tiers use the model floor at their own depth (up to one step, about 0.3 m,
  off)
- Late field: drawn halls use the ray-traced arrival directions (one distribution for the whole late part);
  the shoebox uses an ideal diffuse field. Compare late IACC with the phase-2 measurements before relying on it
- Seat C on the centre line of a symmetric layout gives IACC ≈ 1; this is an artefact of the model
- Nearest-neighbour HRIR selection (no interpolation)
- T30 / EDT are left blank when the decay does not fall far enough inside the 2.5 s analysis window
  (very large or very reverberant halls); listening uses a 1.6 s BRIR
- Some comments in `brir_proto.py` and `run.py` are still in Korean

## Third-party

- BRAS database (for `validate_bras.py` only; not bundled): CC BY-SA 4.0 per the repository page, doi:10.14279/depositonce-6726.3.
- Fratoni dataset (for `validate_fratoni.py`; not bundled): CC BY 4.0, doi:10.17632/y7xnv6xg5s.1. Derived files in
  `validation/fratoni_*` carry its attribution.
- fast-simplification (Python, MIT licence; optional): mesh decimation for large OBJ halls.

- h5wasm 0.10.3 (NIST software licence; includes the HDF5 library), loaded from jsDelivr only when a
  SOFA directivity file is opened; not bundled. Check the licence text before distributing the viewer.
- Directivity databases (not bundled, check each licence): TU Berlin musical instruments and a soprano
  (Ackermann, Brinkmann & Weinzierl; CC BY-SA 4.0), TH Köln voice directivity (Pörschmann & Arend; CC BY 4.0),
  IEM DirPat loudspeakers (Brandner; public domain mark).
- pdf.js 3.11.174 (Mozilla, Apache License 2.0), loaded from cdnjs only when a PDF drawing is opened;
  not bundled. Needs an internet connection the first time.
- KU100 HRIR set: Bernschütz (2013), Zenodo record 3928297; check the dataset licence before
  redistributing the SOFA file.
- `hrir/HPCF_Sennheiser-HD600.mat`: headphone compensation filter from the same KU100 compilation
  (Bernschütz 2013, Zenodo record 3928297, CC BY 3.0: attribution required when redistributed). It was
  measured on the KU100 dummy head, not on the listener; individual fit differs.
