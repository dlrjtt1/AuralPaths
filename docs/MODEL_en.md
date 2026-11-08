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
  The saved config also carries a `_provenance` block (page version, SHA-256 of the browser engine and of a 3D
  model, model type, the page's ray count / image-source order / diffraction, the fixed ray seeds, date). Loading a
  config saved with the same page and engine reproduces its results exactly (the seeds are fixed: checked on the fan
  hall, identical histograms in two runs); with another version the page says that results may differ. The Python
  side ignores the block and writes its own `out/manifest.json`.
- **Export BRIRs (SOFA)…**: all seats × sources of the current hall in one SOFA file (AES69-2022, convention
  SingleRoomSRIR 1.0): one measurement per seat and source, two receivers (left, right ear), the raw path BRIRs
  (time zero = emission at the source, propagation delay included, no PA delay or gain), 1.6 s at the page's
  sampling rate. Positions are in the config's coordinates (model coordinates for a 3D model), ListenerView is the
  direction the seats face (+y in the page). The measurement order ("seat | source"), the time reference and the
  `_provenance` record are in the file's `Comment` attribute; the KU100 HRIR licence (CC BY 3.0) is in `License`.
  Written with h5wasm in the netCDF-4 layout and checked with `sofar.read_sofa(verify=True)` (sofar 1.3; values
  identical to the page's BRIRs). Needs the internet once for h5wasm.
- **Export WAV…**: the seat on display under the current condition (nominal ITDG, level ratio, Mix / Direct only /
  PA only) as heard in the player: amplified source with its delay plus the PA pair with the PA delay and gain;
  stereo, 32-bit float, not normalised, time zero = emission of the amplified source.
- **HRIR set…** (Listening): renders with another HRIR set from a SOFA file (2 receivers, source directions per
  measurement, e.g. SimpleFreeFieldHRIR; a measured individual set or another dummy head). Directions are read as SOFA
  spherical (azimuth counter-clockwise from the front, elevation up) or cartesian; other sampling rates are resampled
  by the browser; at most 896 taps are kept (the note shows how much energy is cut). The diffuse-field band energies
  and the interaural coherence of the late field are computed from the loaded set as `brir_proto.load_hrir` does
  (cos-elevation weights); the late field then has no arrival directions (the directional tables are made from the
  KU100 set in Python). Check: loading the full KU100 SOFA gives the same diffuse-field energies as the embedded
  set (0.00 dB in all bands) and an interaural coherence within 0.005. The headphone filter stays the one measured
  on the KU100. **Back to KU100** restores the embedded set; the set's name and SHA-256 go into `_provenance`, and
  SOFA exports carry its name instead of the KU100 licence.
- Ray tracing runs in several workers in parallel (cores − 1, at most 8; 4 for 3D models, which build their room in
  each worker). Every ray has its own random stream, so the result does not depend on the number of workers (fan
  hall: identical histograms with 1, 2 and 3 workers; 2 workers on 2 cores: 8.6 s → 4.4 s).
- **How far to trust these values** (under the room-acoustic parameters): model type, whether the materials are
  placeholders, loaded / edited or calibrated, the ray count and the share of rays lost through gaps, and the evidence
  from the measured-hall checks that applies to this model (BRAS CR3 / CR4, *Position-by-position check*).
  **Ray-tracing spread…** (drawn halls and 3D models) re-runs the ray tracing of the seat on display with three
  other seeds and shows the range of C80, D50, Ts, EDT and T30 of the amplified chain, also in JND (ISO 3382-1
  Annex A). Example, fan hall at 50 000 rays, seat C: C80 0.7, D50 1.1, Ts 0.4, EDT 1.1, T30 0.8 JND, so seat-to-seat
  or condition-to-condition differences below about 1 JND are within the ray-tracing noise there. Each ray has its
  own random stream (seed, ray index), so changing a material or a delay leaves the other rays' paths unchanged and
  such like-for-like comparisons carry less noise than the spread shows.
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

### Specular reflection factors (finite reflector size, scattering loss)

Drawn and OBJ halls, both engines (`reflections.py`, `engine_geom.js` `specFactor`; identical code, image energies
agree within 2·10⁻⁶ up to order 4). An image source treats every surface as an infinite plane and reflects all
non-absorbed energy specularly. Each reflection of an image-source path now gets, per octave band, the energy factor

  (1 − s) · K₁ · K₂

- (1 − s): the scattered part leaves the specular path (the ray tracer carries it). Scattering may be one value or
  one value per band (`"s": [...]`, Python; the page's material table keeps one value).
- K₁, K₂: Kirchhoff–Fresnel factors of the reflecting panel in two orthogonal sections through the reflection point
  (Rindel 2005, "Reflection of sound from finite-size plane and curved surfaces", 150th ASA meeting, JASA 118(3);
  presentation [core.ac.uk/download/13729852.pdf](https://core.ac.uk/download/13729852.pdf); design form in Rindel
  1992, Proc. IoA 14(2), [PDF](https://www.ioa.org.uk/system/files/publications/JH%20RINDEL%20ACOUSTIC%20DESIGN%20OF%20REFLECTORS%20IN%20AUDITORIA.pdf)):
  K = ½[(C(v₂) − C(v₁))² + (S(v₂) − S(v₁))²], v = 2x cos θ / √(λ a*), a* = 2a₁a₂ / (a₁ + a₂), with x the distances from
  the reflection point to the panel edges in that section, θ the angle of incidence (cos θ only in the section that
  contains the incidence direction), a₁, a₂ the unfolded path lengths from the source to the point and from the point
  to the receiver (for higher orders an engineering extension; Rindel's formula is for one reflection). K = 1 for an
  infinite plane, ¼ (−6 dB) for a point on an edge. Averaged over the band centre and ± ⅓ octave.
- Panel: the connected surfaces in one plane (touching within 1 cm, normals within 2°). In drawn halls each wall
  edge, floor strip and step is its own panel, so steps and narrow strips reflect weakly at low frequencies.
- Implementation detail: pyroomacoustics keeps only the images a receiver can hear and does not store their parents,
  so the wall sequence of each image is recovered by generating all images from the source (as the browser engine
  does) and keeping the sequence whose reflection points lie on their surfaces.
- Switch off with `"geometry": {"finite_reflectors": false, "specular_scatter_loss": false}` (Python). The shoebox is
  unchanged.

Check against the measured first-order reflections of BRAS CR3 / CR4 (same 36 / 35 reflections before and after,
see *Position-by-position check*): CR4 median predicted − measured +6.5 → +2.7 dB, mean absolute 6.1 → 5.3 dB,
correlation 0.30 → 0.35; CR3 +1.2 → +1.6 dB, mean absolute 2.8 → 2.8 dB, correlation 0.59 → 0.55. The systematic
overestimate in CR4 is mostly gone; reflection-by-reflection accuracy in CR4 stays poor. A 10° panel tolerance (so
that gentle bends count as one panel) gave +4.1 dB in CR4 and was not kept. Energy histograms of a drawn test hall
change by about −0.1 dB in the first 100 ms (the ray-traced diffuse part fills in most of what the specular paths
lose); individual reflections change by up to tens of dB (small steps, edges).

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

In the page: **Calibrate…** (next to Save config) takes the same CSV and runs the same method with the browser
engine (omnidirectional source, all material groups the hall uses, or the shoebox's uniform absorption; at most 6
iterations). An optional column `role` with the value `check` keeps a position out of the fit; its T30 error before
and after is shown next to the fit positions. Materials are replaced, the record is saved in the config as
`_calibration` (as calibrate.py writes it, plus `engine`) and shown in *How far to trust these values*; **Undo
calibration** restores the previous materials. The calibration traces at least 30 000 rays per source (at 10 000
rays the T30 band means of CR3 moved by up to 6 % between seeds). A config for Python runs is better calibrated
again with `calibrate.py`. Demo with measured data: `examples/bras_cr3/` (BRAS CR3, LS1 × 5 positions fit, LS2 × 5
check; about 8 min): fit within 2 %, check −1 … +7 % (T30 at 125 Hz – 4 kHz, before: +5 … +14 %).

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

Both engines can run a hall given as a Wavefront OBJ mesh (`"geometry": {"mesh": {...}}`, described at the top of
the mesh part of `geometry.py`; in the page: **Hall → Shape → 3D model (OBJ)**, see *3D models in the browser* below).
`obj_to_hall.py` turns a mesh hall into a drawn hall (2.5D) where image sources above order 1 and edge diffraction
are wanted.

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
  mesh group's Sabine absorption area. The ray-traced T30 of both 3D meshes is close to Sabine (STC 1 kHz 1.48 s vs
  1.43 s; ULH 1 kHz 1.93 vs 1.95 s); the choice of mapping is empirical: in ULH the 2.5D T30 is 0.04–0.12 s below
  the mesh at 125 Hz–4 kHz with `eyring`, 0.14–0.25 s with `sabine` (keeping A), and 0.11–0.21 s with one factor per
  band that keeps the room's Eyring exponent (`room-eyring`) (`validation/fratoni_ULH_preserve.md`). A per-material
  Eyring sum (Millington's form) was also tried and was worse (it weights the absorbing seat faces up). (Until
  2026-11-06 this paragraph said that a simple 2.5D hall decays like Eyring; that came from the ray-tracing energy
  floor described next.)
- Check of the ray tracer itself (`validation/check_rt_eyring.py`, shoebox 12 × 9 × 7 m, uniform α): with
  scattering 0.7 the ray-traced T30 is 7–12 % above Eyring at α = 0.05–0.3 (close to Sabine); with scattering 0.1,
  −0.4 … +12 %. The spread of the free path lengths makes the mean decay slower than Eyring; the browser tracer gives
  the same values on a tiled box and follows a prediction from its own free paths (`validation/check_box_lambert.js`).
- Ray-tracing energy floor (fixed 2026-11-06): pyroomacoustics uses `energy_thres` both to end a ray (relative to
  its start energy) and as an absolute floor for each scattered ("diffuse rain") contribution to a receiver
  (`libroom_src/room.cpp`, `scat_ray`, pyroomacoustics 0.10.1), and a ray starts with 2 / n_rays. With the earlier
  setting 1e-9 the scattered energy was dropped from about 0.5 s on, so T30 came out short and fell with the ray
  count (tiled box, s = 1: 1.11 / 1.04 / 0.99 s at 2 000 / 20 000 / 100 000 rays). `brir_proto.RT_ENERGY_THRES` is
  now 1e-20 (box: 1.12 s at any ray count, as the browser). All Python results in this document were re-run with
  it; in the measured halls the changes were small for T30 (≤ 0.4 JND in ULH / STC, CR3 −3 … −4 %, CR4 unchanged) and
  larger for EDT and clarity (CR4 EDT +10–12 %, C80 −0.3 … −0.4 dB; see the sections below).

```bash
python obj_to_hall.py mesh_config.json --depth-axis y --stage-end min --stage-depth 2.4   # -> mesh_config_2p5d.json
```

### 3D models in the browser

**Hall → Shape → 3D model (OBJ)** opens an OBJ file (or **Load config…** a config with `geometry.mesh`; a config
saved by the page carries the OBJ as `mesh.obj_text`, a Python config asks for the OBJ file next). `engine_geom.js`
builds the room as `geometry.build_mesh` does (voxel flood fill from the first source or seat inside, inward
normals, hidden faces dropped, back-facing twins, 1 mm inflate). Checked on BRAS CR3 at 5 cm voxels: same 4638
surfaces, 279 dropped faces, volume 3188 m³ and the same 37 first-order image sources as Python (largest relative
energy difference 7 × 10⁻⁷).

- Page settings: up axis (y up for SketchUp / Blender OBJ exports), plan turn (0 / 90 / 180 / 270°, display only:
  the page shows the depth along y), voxel size (auto: at least 5 cm and at most 2 × 10⁷ cells, for browser memory).
  Each name in the model (its OBJ material, else its group) is mapped to the audience floor, stage floor, walls,
  ceiling, or a material of its own. Plan and section show the room projected from the voxels (outline = x range
  of each 0.25 m row; floor / ceiling lines = lowest floor and highest ceiling of each row), with the model's wall
  faces drawn on the plan. Heights of sources and seats are above the lowest floor under each point.
- Image sources to order 2 (default; order 1 selectable): every pair of room surfaces is tried and each path is
  checked by back-tracing and occlusion, as for drawn halls. CR3 (2600 faces): order 1 takes 0.2 s, order 2 about 7 s
  per source (the image sources of different sources run in different workers); order 3 would take about 2300 times
  longer and is not offered. In CR3 the second-order paths carry 22–45 % of the specular energy in the first 100 ms
  (1 kHz, five receivers). Room criteria hardly change (the ray tracing already carries that energy; CR3 / CR4 band
  means within 0.1 dB / 1 %), the early arrival pattern does. Check against the measured RIRs
  (`validation/check_reflections_js.py`, same window test as *Position-by-position check*): CR3 order 2, 11 isolated
  reflections: predicted − measured median −0.5 dB (IQR −2.8 … +2.7), measured above the random-time median in 82 %
  but above the window 2 ms later in only 45 % (timing not confirmed reflection by reflection); CR4, 6 reflections:
  +6.4 dB, as its first-order reflections (+6.2 dB). The Python mesh path stays at order 1 (pyroomacoustics);
  configs keep `ism_order: 1` for Python and the page's order as `geometry.mesh.page_ism_order`.
- Model: specular reflection factors on every image source, no edge diffraction, ray tracing in a
  bounding-volume hierarchy. A ray's new direction after a hit is the normalised mix s·Lambert + (1 − s)·specular
  with s the mean over bands, as in the pyroomacoustics tracer that the Python mesh path uses (`libroom_src/room.cpp`
  in pyroomacoustics 0.10.1); the browser leaves out pyroomacoustics' extra "diffuse rain" term (scattered energy
  sent from each hit straight to the receivers). Rays that pass through a crack into a solid are ended (two
  back-facing twins in a row, or a segment through free space that the room flood fill did not reach), so that they
  do not ring on inside the solid. First tried: a random choice per hit between Lambert and specular with per-band
  weights (energy kept per band); on CR3 its T30 band means were 0–20 % above Python's (largest at 125 Hz), so the
  page uses Python's direction rule.
- Check against Python and the measurement (`validation/check_mesh_pyjs.py`, BRAS fitted materials, measured
  positions; band means over the 10 position pairs, browser / Python / measured):

  | | 500 Hz | 1 kHz | 2 kHz |
  |---|---|---|---|
  | CR3 T30 (s) | 1.42 / 1.40 / 1.30 | 1.47 / 1.44 / 1.34 | 1.46 / 1.43 / 1.32 |
  | CR3 C80 (dB) | 1.4 / 1.4 / 1.5 | 1.0 / 0.9 / 1.7 | 1.2 / 1.1 / 1.6 |
  | CR4 T30 (s) | 2.25 / 2.28 / 2.07 | 2.27 / 2.30 / 2.10 | 2.02 / 2.05 / 1.84 |
  | CR4 C80 (dB) | −0.8 / −0.8 / 0.2 | −0.8 / −0.8 / −0.7 | −0.1 / −0.3 / −0.1 |

  T30: the browser is within −1.5 … +2 % of Python (CR3 16 000 rays, CR4 8 000 rays per source); both are 7–11 %
  above the measured T30. C80 within 0.2 dB of Python, EDT −3 … +4 %. These are one ray realisation: with 10 000 rays
  the browser's CR3 T30 band means moved by up to 6 % between seeds (an earlier realisation, before each ray got its
  own random stream, gave +5–6 % against Python). Per position pair the scatter is larger still, so use band means
  and many rays.
- Shoebox written as an OBJ of 1 m tiles (α 0.2; `validation/check_box_lambert.js`, `validation/check_mesh_box.py`):
  browser and Python give the same T30 within 0.01 s (s = 1: 1.12 / 1.10 / 1.06–1.07 s at 125 / 500 / 2000 Hz; s = 0.5:
  1.16 / 1.14 / 1.10 s; s = 0.1: 1.15 / 1.14 / 1.10 s), and the browser follows the prediction from its own free paths
  (mean 5.93 m = 4V/S, relative variance 0.35 at s = 1: 1.11 s; derived in the script: the number of reflections
  in time t is about normal, so the mean energy decays as exp((ct/m)(ln(1 − α) + γ²/2 · ln²(1 − α))), slower than
  Eyring 1.07 s). Before the energy-floor fix Python gave 1.03 s at s = 1, below Eyring; that difference was in the
  Python setting, not in the browser.
- Diffuse rain in the browser: tried (the scattered share of each hit sent straight to the visible receivers, as
  pyroomacoustics does). It added about 45 % ray energy with the same decay on the box (T30 unchanged), raised C80 on
  CR3 by 0.2–0.3 dB and made ray tracing 3–4 times slower; it did not reduce the seed-to-seed spread of T30. Left
  out: without it the browser's C80 is within 0.2 dB of Python's (table).
- Time: CR3 (2600 faces) builds in about 4 s; 10 000 rays per source take about 25 s. The worker rebuilds the room
  for every computation (no shared memory with the page).

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
  Swapping `doors_organ` to Wood changes T30 by 0.02–0.06 s (`validation/fratoni_STC_doors_*.md`).
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
| ULH, S1 (26 receivers) | 3D mesh | −2.4 / −1.3 / +0.5 / +0.9 / −0.0 / −0.9 | −0.1 … +0.7 | −0.3 … +0.1 | −0.1 … +0.5 |
| | 2.5D | −3.8 / −2.0 / −0.5 / +0.4 / −0.9 / −2.4 | −1.2 … +1.0 | −0.8 … +0.1 | −0.5 … +0.8 |
| STC, S1 (10) | 3D mesh | +7.0 / +4.4 / +4.1 / +2.4 / +3.6 / +3.4 | +3.8 … +5.0 | −2.0 … −1.4 | +2.3 … +3.3 |
| | 2.5D | +7.6 / +4.7 / +4.3 / +2.2 / +3.5 / +3.4 | +5.1 … +7.0 | −2.2 … −1.6 | +2.4 … +3.5 |
| STC, S2 (4) | 3D mesh | +8.9 / +2.8 / +2.5 / +2.3 / +4.1 / +4.0 | +2.5 … +4.8 | −2.2 … −1.1 | +1.9 … +2.9 |
| | 2.5D | +8.9 / +2.7 / +2.2 / +1.8 / +3.4 / +3.3 | +2.2 … +4.4 | −1.6 … −0.4 | +1.3 … +2.5 |

Reading:
- ULH: from 500 Hz to 4 kHz all criteria of the 3D mesh are within about 1 JND of the measurement; at 125–250 Hz
  T30 and EDT are 1–2 JND short and C50 about 1.3 dB high. A Sabine estimate from the same inputs is also short there
  (1.15 s vs 1.56 s measured at 125 Hz, mesh volume 742 m³), so the low-frequency gap is in the inputs (volume and
  coefficients as used here), not in the ray tracing. The 2.5D hall is within 0.15 s of the mesh from 250 Hz to
  2 kHz.
- STC: both models are about 15 % long (1 kHz: 1.48 s vs 1.32 s measured), the 3D mesh and the 2.5D hall agree
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
page with **Load config…**. Run 2026-11-05, re-run 2026-11-06 with the specular reflection factors (changes ≤ 0.2 JND)
and again with the ray-tracing energy floor fixed (changes ≤ 0.4 JND; ULH 3D mesh about 77 min, STC 38 min on 2 CPU
cores).

### The two opera houses with the browser engine (TCB, DUS; `validation/check_fratoni_js.py`, 2026-11-07)

With 3D models in the engine, the two opera houses of the dataset can be checked too: **TCB** (historic opera house,
five tiers of boxes, about 25 900 m³ with the stage house) and **DUS** (opera house with two balconies, about
8 200 m³). They run with the browser engine (image sources to order 2, 20 000 rays per source; 2.5 and 5 min), since
the Python ray tracer would take hours on these 6 000 – 10 000-face models.
- Models: OBJ from the dataset's SketchUp files with the tags as groups. The tags do not match the sheets' materials
  (TCB 13 tags vs 8 materials, DUS 11 vs 8); the assignments are AuralPaths' judgement and are listed in
  `validate_fratoni.py` (e.g. TCB hall and gallery plaster → "Plaster (boxes)", box floors → Carpet, fly tower →
  "Stage house"; DUS "Carpet" floors → Wood, as its sheet has no carpet).
- Positions: plan figures registered to the model (scale and offset fitted to the walls of a horizontal cut; mean
  residual 7–9 px at 30–43 px/m), dots read from the figures. Heights are **assumptions**: receivers 1.2 m above the
  floor below them (stalls, box, gallery or balcony floor from the mesh), sources 1.5 m above the stage or pit floor.
- Rays lost through gaps in the models: 17–24 % of the rays over the whole run (CR4: similar).

Results (simulated − measured, mean absolute difference in JND at 500 Hz – 1 kHz over sources and receiver zones,
signed mean in brackets; tables and figures in `validation/fratoni_DUS.*`, `fratoni_TCB.*`):

| hall | EDT | T30 | C80 | Ts |
|---|---|---|---|---|
| DUS (2 sources × 3 zones) | 2.7 (+2.7) | 1.2 (−0.1) | 1.2 (−0.6) | 0.9 (+0.6) |
| TCB (2 sources × 3 zones) | 8.2 (−8.2) | 4.0 (−4.0) | 2.7 (+2.3) | 3.5 (−3.5) |
| TCB, hall plaster as Wood (sensitivity) | 5.1 (−5.1) | 2.4 (−2.4) | 2.0 (+1.3) | 2.5 (−2.1) |

Reading:
- DUS: T30 at mid frequencies within about 1 JND; as in ULH, T30 is short at 125–250 Hz (−3 … −4 JND) and long at
  4 kHz (+3 … +4 JND); EDT up to 20 % long (mean about 14 %).
- TCB: everything decays too fast (T30 about 20 % short, EDT about 40 % short, C80 mostly 2–4 dB high). A Sabine estimate
  from the same inputs is already 8 % below the measured T30 (1.37 s vs about 1.5 s at 500–1000 Hz), so with this
  material assignment the model holds too much absorption; giving the hall plaster the Wood coefficients instead
  halves the T30 gap but leaves EDT 25 % short. The cause is not determined: the undocumented tag-to-material
  assignment (the GA coefficients were tuned in Odeon on the authors' own assignment), the coupling of the boxes
  (small absorbing rooms opening into the hall) and the lost rays are candidates. **TCB is therefore not counted as
  a successful check**; it shows that a box-tier opera house cannot be simulated reliably here without a calibration
  of its own.

```bash
python validation/check_fratoni_js.py "<dataset folder>" DUS --obj DUS_model.obj
python validation/check_fratoni_js.py "<dataset folder>" TCB --obj TCB.obj
python validation/check_fratoni_js.py "<dataset folder>" TCB --obj TCB.obj --swap "Plaster_(hall)=Wood" --out validation/fratoni_TCB_hall-plaster-as-Wood
```

## Position-by-position check against two real halls (`validate_bras_cr.py`)

BRAS v3 (Aspöck et al. 2020, [doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3),
CC BY-SA 4.0) has measured RIRs of two real halls with their 3D models and surface descriptions: **CR3**, a chamber
music hall (3331 m³, 342 seats, balconies) and **CR4**, a university auditorium (8657 m³, raked seating, balconies).
Per hall: 2 dodecahedron positions × 5 microphone positions, RIRs in Pa (44.1 kHz), positions in the SOFA file.
Unlike the Fratoni check, the values are per position and the RIRs are available, so early reflections can be
tested too. Not bundled: download the two scene folders and `3_surface_descriptions`, export `Geometry/CRn.skp` as OBJ
with the SketchUp materials as group names (the groups then carry the BRAS material names, `mat_CRn_…`).

Inputs:
- Geometry: the BRAS model as exported. The mesh reproduces the documented surface areas (CR3 2759 vs 2763 m²; CR4,
  decimated to 3000 faces, 5750 vs 5851 m²) and volumes (voxel estimate CR3 3188 vs 3331 m³, CR4 8175 vs 8657 m³;
  the voxel band shaves 4–6 %). CR4 needs 8 cm voxels (`--voxel 0.08`): at 5 cm the flood fill used more than 6 GB.
- Materials: BRAS `fitted_estimates` (absorption adjusted by the BRAS authors so that Eyring's formula gives the
  measured reverberation time), third-octave values averaged to octaves; scattering from the same files.
- Direct sound: the measured onset is within −0.67 … +0.07 ms of distance / c at all 20 pairs, so the SOFA
  positions and the OBJ share one coordinate frame.

Three model runs: (a) 3D mesh, BRAS coefficients unchanged; (b) 3D mesh after a one-step calibration of this engine
on the LS1 positions (each material's −ln(1 − α) scaled per band by mean T30 simulated / measured), judged on the
LS2 positions it did not see; (c) the 2.5D hall from `obj_to_hall.py` (balconies lost; image sources order 2, no
diffraction). 4000 rays. With 500 rays T30 came out 13–33 % long in CR3 (noisy late tail); use thousands of rays for
reverberation criteria.

Room criteria (simulated − measured in JND, mean absolute over the positions, 500 Hz–2 kHz; signed values and all
bands in `validation/bras_CR3.md`, `bras_CR4.md`). Current model (specular reflection factors, ray-tracing energy
floor fixed); in brackets the previous run with the old energy floor (see *3D OBJ halls*):

| hall | model | EDT | T30 | C80 | C50 | Ts |
|---|---|---|---|---|---|---|
| CR3 | 3D mesh | 3.0 (2.6) | 1.8 (2.7), all long, +8 % | 0.8 (1.0) | 1.0 (1.6) | 1.0 (1.2) |
| | 3D calibrated, held-out LS2 | 1.8 (1.7) | 0.8 (1.6) | 0.7 (0.9) | 0.9 (1.3) | 0.7 (1.0) |
| | 2.5D | 4.4 (4.4) | 3.2 (2.9) | 2.3 (1.7) | 2.6 (2.3) | 2.4 (2.1) |
| CR4 | 3D mesh | 3.7 (2.3) | 2.1 (2.2), all long, +10–11 % | 1.6 (0.9) | 1.8 (1.2) | 2.3 (1.2) |
| | 3D calibrated, held-out LS2 | 2.2 (2.7) | 0.8 (0.8) | 1.3 (0.9) | 1.2 (1.3) | 2.2 (1.3) |
| | 2.5D | 2.1 (1.9) | 1.3 (1.1) | 1.5 (0.8) | 1.4 (1.4) | 1.9 (1.1) |

Early reflections (500 Hz–2 kHz): every first-order image source the engine predicts at ≥ −15 dB re direct, ≥ 2 ms
after the direct sound and 1.5 ms away from other predicted ones, against the measured energy in a 1 ms window at
its predicted time (dB re the same window on the direct sound). Controls: the same window 2 ms later, and random
times 3–20 ms after the direct sound. Current model (the set of reflections above −15 dB changes with the model;
on the same set as the first run, see *Specular reflection factors*: CR3 +1.2 → +1.6 dB, CR4 +6.5 → +2.7 dB):

| hall | model | n | predicted (median) | measured at predicted time | measured 2 ms later | measured at random times | predicted − measured (median, IQR) | r |
|---|---|---|---|---|---|---|---|---|
| CR3 | 3D mesh | 36 | −5.5 dB | −6.8 dB | −10.4 dB | −11.5 dB | +1.6 dB (+0.1 … +3.4) | 0.55 |
| | 2.5D | 20 | −5.8 | −13.1 | −10.1 | −11.5 | +5.6 (+2.4 … +8.1) | 0.17 |
| CR4 | 3D mesh | 28 | −9.0 | −13.5 | −14.0 | −21.0 | +4.6 (+1.9 … +7.8) | 0.46 |
| | 2.5D | 23 | −9.3 | −13.8 | −13.9 | −21.0 | +5.0 (+1.0 … +8.2) | 0.28 |
| first run, without the factors: CR3 | 3D mesh | 36 | −5.3 | −6.8 | −10.4 | −11.5 | +1.2 (+0.1 … +3.9) | 0.59 |
| CR4 | 3D mesh | 35 | −6.7 | −13.7 | −14.3 | −21.0 | +6.5 (+2.6 … +8.9) | 0.30 |

Reading:
- Reverberation: with Eyring-fitted coefficients the ray tracer gives T30 8–11 % too long in both halls (band means
  500 Hz–2 kHz; 1.6–2.3 JND). A ray tracer decays slower than Eyring even in a diffuse box (7–12 % at scattering 0.7,
  `validation/check_rt_eyring.py`, `validation/check_mesh_box.py`), so coefficients fitted with Eyring are too low
  for it. Calibrating this engine on measured T30 is therefore needed (`calibrate.py`). Calibrated on LS1, the
  held-out LS2 positions came within 0.8 JND in T30 in both halls; EDT, C80 / C50 and Ts within 0.7–2.2 JND.
- Clarity and Ts are within 0.8–2.3 JND (mean absolute) in the 3D runs before calibration. In CR4 the fixed energy
  floor made EDT 10–12 % longer and C80 0.3–0.4 dB lower (more late scattered energy), which moved EDT, C80 and Ts
  away from the measurement (EDT 2.3 → 3.7 JND).
- Effect of the specular reflection factors on the room criteria (runs with the old energy floor): EDT better (CR3 3.3 → 2.6, CR4 2.7 → 2.3 JND), T30
  of the held-out CR3 positions after calibration better (3.7 → 1.6), C50 worse (CR3 1.0 → 1.6, CR4 1.0 → 1.2), the
  rest within ±0.2 JND, except EDT of the held-out CR4 positions after calibration (1.4 → 2.7). The cause of the
  C50 change is not identified.
- Early reflections, 3D mesh: in CR3 the predicted reflections are real (at their predicted times the measured level
  is 4.7 dB above random times and drops by 3.6 dB 2 ms later) and their levels are right to +1.6 dB (median). In CR4
  the measured energy at the predicted times is above random times but not above the same window 2 ms later; the
  predicted levels were 6.5 dB too high (median) before the specular reflection factors and 2.7 dB on the same
  reflections after them (finite panels: the white panels between concrete beams had been +8.6 dB). Reflection by
  reflection, CR4 stays poor (correlation 0.35–0.46). For ITDG and level-ratio work in a real hall, check the early
  reflections of the hall at hand against a measurement before relying on them.
- Why CR4's first-order reflections look too strong (browser engine, `validation/check_reflections_window.py`,
  `validation/reflections_window_CR4.md`): on the 28 isolated first-order reflections, predicted − measured is +4.9 dB
  (median) in the 1 ms window at the predicted time, but +0.2 dB for the energy within −1.5 … +2.5 ms of it after
  subtracting the diffuse background of that window. By material: white panels (n 16) +6.3 dB at the predicted time,
  +0.2 dB over the wider window, with the strongest measured 1 ms window scattered over ±1 ms (IQR −1.1 … +1.1 ms);
  concrete (n 4) early in three of four (1.0–1.5 ms, a path about 0.35–0.5 m shorter: a geometry or position offset; the fourth −0.25 ms);
  brick (n 7) on time (offset IQR 0 … +0.25 ms), +1.1 dB at the predicted time. So the CR4 excess is mainly energy that
  arrives spread in time or slightly displaced, not missing absorption. A likely reason for the white panels is
  structure the model leaves out: the BRAS model notes say the steel construction behind the ceiling panels was not
  modelled, and their fitted scattering coefficient is 0.05, so the model returns one sharp specular reflection
  (an interpretation, not tested). CR3 for comparison: offsets near 0 (IQR within ±0.5 ms), +1.9 dB at the predicted
  time, +1.6 dB over the wider window (in 10 of 33 reflections the wider window holds nothing above the background).
  Small samples per material; the strongest-window search is biased upwards by about 4–5 dB at random times, so it is
  used for timing only. Not changed in the engine or the materials.
- 2.5D hall: reverberation and clarity stay within a few JND, but in CR3 its predicted reflections are not in the
  measurement (the measured level at their times equals that at random times): with balconies and side galleries
  reduced to a 2.5D plan × section, the individual early reflections, and so the ITDG of a seat, do not correspond
  to the real hall. A drawn 2.5D hall is valid for halls that are close to 2.5D.
- This check found a bug in `obj_to_hall.py`: a plan mask with several pieces (stage house, pillars) was joined into
  one self-intersecting outline (CR4). Fixed (largest piece kept); the ULH, STC and CR3 conversions are unchanged.

```bash
python validate_bras_cr.py "CR3 medium room (chamber music hall)" "3 Surface descriptions" --obj CR3.obj --rays 4000 --out validation/bras_CR3
python validate_bras_cr.py "CR4 large room (auditorium)" "3 Surface descriptions" --obj CR4.obj --rays 4000 --voxel 0.08 --out validation/bras_CR4
```
Run 2026-11-05, re-run 2026-11-06 with the specular reflection factors and again with the energy floor fixed (CR3
about 25 min, CR4 about 40 min on 2 CPU cores). The 2.5D halls
(`validation/bras_CR*_2p5d_config.json`, CC BY-SA 4.0) open in the page with **Load config…**. `calibrate.py` now
traces once per source for mesh halls (all receivers of that source together).

## Comparison with an independent free simulator: I-Simpa (SPPS) (`validation/check_isimpa.py`, 2026-11-07)

I-Simpa (Université Gustave Eiffel, GPL-3.0, [github.com/Universite-Gustave-Eiffel/I-Simpa](https://github.com/Universite-Gustave-Eiffel/I-Simpa))
is a free room-acoustics program; its SPPS solver traces sound particles through a tetrahedral mesh of the room. It
was run headless on the same BRAS halls with the same inputs as the Python 3D runs above (geometry, BRAS fitted
absorption and scattering per octave, positions, receiver radius 0.5 m, air absorption; 300 000 particles per source
and band) and on a shoebox. I-Simpa is not bundled or linked; the script writes its input files and runs it. On Linux
one source fix in SPPS was needed (`abs()` on doubles truncated to integers, so every point receiver recorded zero;
see the script's docstring).

Results (simulated − measured or SPPS − AuralPaths, mean absolute difference in JND at 500 Hz – 2 kHz over the 10
position pairs, signed mean in brackets; `validation/isimpa_check.md`):

| | T30 | EDT | C80 | Ts |
|---|---|---|---|---|
| CR3: SPPS − measured | 5.1 (+5.1) | 3.7 (+3.7) | 1.1 (−0.9) | 1.6 (+1.5) |
| CR3: AuralPaths − measured | 1.8 (+1.6) | 3.0 (+2.6) | 0.8 (−0.4) | 1.0 (+0.7) |
| CR3: SPPS − AuralPaths | 3.4 (+3.4) | 1.2 (+1.1) | 0.5 (−0.4) | 0.8 (+0.8) |
| CR4: SPPS − measured | 3.0 (+3.0) | 3.0 (+3.0) | 1.6 (−1.5) | 3.0 (+3.0) |
| CR4: AuralPaths − measured | 2.1 (+2.1) | 3.7 (+3.5) | 1.6 (−0.5) | 2.3 (+1.8) |
| CR4: SPPS − AuralPaths | 1.4 (+0.8) | 1.9 (−0.2) | 1.6 (−1.1) | 1.8 (+1.3) |

Shoebox (12 × 9 × 7 m, α 0.2, no air), T30: SPPS 1.12 / 1.10 / 1.13 s at scattering 1.0 / 0.5 / 0.1; the browser
tracer 1.11 / 1.15 s at 1.0 / 0.5 (`check_box_lambert.js`).

Reading: in a diffuse box the two tracers agree within 0–4 %, and in CR4 within about 1–2 JND. In CR3 SPPS decays
clearly slower (T30 about 17 % longer than AuralPaths, about 25 % longer than measured) while the early criteria
agree better; the cause is not resolved (candidates: the reflection model at the low scattering of most CR3 surfaces —
SPPS reflects diffusely with probability s, AuralPaths blends one direction as pyroomacoustics does — and the rays the
browser tracer loses through gaps, about 12 % over 3 s in CR3 against about 0.01 % in SPPS). Neither program
reproduces the measurement with these inputs, which were fitted with the Eyring formula for neither of them;
differences of this size between simulators are expected (Brinkmann et al. 2019,
[doi:10.1121/1.5096178](https://doi.org/10.1121/1.5096178)). The check shows that AuralPaths is not an outlier
against an independent implementation in CR4 and in a diffuse box, and records the CR3 difference.

## Binaural check against measured BRIRs (BRAS CR3 / CR4; `validation/check_bras_brir.py`, 2026-11-08)

BRAS (Aspöck et al. 2020, [doi:10.14279/depositonce-6726.3](https://doi.org/10.14279/depositonce-6726.3), CC BY-SA 4.0)
contains BRIRs measured with the FABIAN head at one listener position (MP6 = RIR position MP1, head facing LS7) for five
loudspeakers LS3–LS7 (QSC K8). The script renders the same five pairs with the Python mesh path (BRAS OBJ, fitted
materials unchanged, not calibrated; image sources order 1, 5000 rays per source, KU100 HRIRs) and compares direct-sound
ITD / ILD, IACC_E3 (0–80 ms) and IACC_L (80 ms–end; mean of 500 Hz–2 kHz, lag ±1 ms), T30, EDT, C80 and the octave
spectrum relative to 250 Hz–1 kHz. It was run twice: omnidirectional sources, and a frequency-independent 105° coverage
cone aimed at the listener (`--coverage 105`; 105° is the K8's nominal coverage,
[QSC K8 specifications](https://www.qsys.com/resource-files/productresources/spk/k/k8/q_spk_k_8_archengspecs.txt)).
Results: `validation/bras_brir_CR3.md`, `_CR3_K8.md`, `_CR4.md`, `_CR4_K8.md` (CR4 rerun after the image-source fix
below).

| mean over LS3–LS7 | CR3 measured | CR3 omni | CR3 105° | CR4 measured | CR4 omni | CR4 105° |
|---|---|---|---|---|---|---|
| direct (first 3 ms) / 0–80 ms energy, dB | −3.1 | −8.3 | −3.2 | −0.7 | −4.4 | −1.3 |
| IACC_E3 | 0.52 | 0.18 | 0.29 | 0.83 | 0.33 | 0.53 |
| IACC_L | 0.16 | 0.09 | 0.09 | 0.33 | 0.11 | 0.11 |
| T30, sim − meas, 125 Hz–4 kHz | | −3…+4 % | −3…+4 % | | +15…+25 % | +15…+23 % |
| EDT, sim − meas | | +3…+28 % | +3…+28 % | | −3…+8 % | −3…+8 % |
| C80 at 500 / 1k / 2k Hz, sim − meas, dB | | −2.4 / −1.9 / −5.0 | −2.0 / −1.3 / −3.5 | | −4.8 / −3.6 / −6.9 | −4.2 / −2.1 / −3.1 |

Direct sound: |ITD difference| 18 µs (CR3) and 14 µs (CR4), within one or two samples of the nearest-HRIR rendering;
|ILD difference| 0.8–0.9 dB in both halls.

Reading, set-up first:
- The direct-to-early energy ratio is a set-up difference: with the coverage cone it matches the measurement within
  about 0.5 dB, without it the simulated direct sound is 4–5 dB too weak. Comparisons against measured BRIRs need the
  source directivity.
- The spectrum (simulated 4 kHz about 9–15 dB below the measurement relative to 250 Hz–1 kHz) comes from the head:
  with the FABIAN HRIRs it is within 1.4 dB (see below).

Model findings:
- IACC_E3 stays too low even when the direct-to-early ratio is right (CR3 0.29 vs 0.52, CR4 0.53 vs 0.83).
  `validation/iacc_split.py` (`validation/bras_brir_iacc_split.md`, 105° sources) splits it per band into the first
  3.5 ms ("direct") and the rest, both at the lag of the direct sound. In CR3 the measured rest adds +0.17 to +0.61 at
  500 Hz (LS7 also +0.44 / +0.30 at 1 / 2 kHz), the simulated rest 0.00 to +0.16: measured early reflections add
  coherently to the direct sound, the simulated ones hardly. In CR4 the larger difference is the direct part at
  500 Hz (measured +0.63 to +0.77, simulated +0.28 to +0.47): in that band the simulation has too much energy besides
  the direct sound, and broadband 20–50 ms holds 13–20 % of the 0–80 ms energy against 5–9 % measured, in line with
  the low C80 at 500 Hz.
- Rendering tests (2026-11-08; prototypes, not in the repository), CR3 LS7 with the 105° source (measured 0.73):
  the early remainder rendered as noise with the interaural coherence of its traced arrival directions (Python mesh
  path) raised IACC_E3 from 0.35 to 0.39; with the browser engine's image sources and rays, rendering the remainder
  as the individual ray arrivals (exact time and direction, random sign) raised it from 0.37 to 0.45, image sources
  to order 2 from 0.38 to 0.44, both together to 0.46. In CR4 order 2 raised LS3 from 0.52 to 0.59 (measured 0.82).
  The noise rendering of the early remainder therefore explains only a part of the
  gap; the early energy distribution matters at least as much (inputs: materials fitted to reverberation; the
  source pattern below 2 kHz, which here widens from 105° by an assumed rule, not K8 data). The engine is unchanged.
- Measured K8 pattern (`--k8-mps`: the QSC K8 directivity of the BRAS release, RWTH Aachen, 1° grid, third-octave
  spectra, BRAS documentation sections 3.3.1 / 3.4.2; octave balloon, pattern only, LS3–LS6 aimed at the head, LS7
  horizontal; `validation/bras_brir_CR3_K8data.md`, `_CR4_K8data.md`, `bras_brir_iacc_split_K8data.md`). The K8 is
  more directional at 250–500 Hz than the assumed rule (Q 1.9 / 3.0 against 1.0 / 1.7). Against the 105° rule:
  IACC_E3 0.29 → 0.34 in CR3 (measured 0.52) and 0.53 → 0.59 in CR4 (0.83); C80 at 500 Hz −2.0 → −1.8 dB (CR3) and
  −4.2 → −3.4 dB (CR4); the spectrum at 125 Hz–1 kHz within about 1.6 dB in CR3 and 2.2 dB in CR4 (before 2.0 and
  3.0); T30, EDT, ITD / ILD and the direct-to-early ratio practically unchanged. The source pattern explains a part of
  the difference. In CR4 LS6 matches per band (IACC 0.66 / 0.69 / 0.86 against 0.69 / 0.79 / 0.87); for the other
  four the simulation puts 14–19 % of the 0–80 ms energy into 20–50 ms (measured 5–8 %).
- Where the CR4 excess comes from (`validation/early_paths.py`, `validation/bras_early_paths_CR4.md`; browser engine,
  same inputs, measured K8 pattern, 300 000 rays per source, arrivals logged with the surfaces they last reflected
  from). For all five sources the browser engine also puts 25–27 % of the 0–80 ms energy (250 Hz–2 kHz) into
  20–50 ms (measured 9–11 %) and 0–1 % into 3–20 ms (measured 6–11 %). Of the 20–50 ms ray energy about half last
  reflected from the ceiling panels (`whitePanels`, about 7–8 m above the floor between stage and audience; strongest
  image sources: the first-order ceiling reflection at 21–33 ms and stage floor → ceiling at 31–40 ms) and about a
  third from the aisle floor just in front of the listener (`linoleum`, mostly ceiling → floor). Sensitivity (LS3 and
  LS7, 50 000 rays, `--set`): ceiling scattering 0.5 changes the 20–50 ms share little and 0.9 lowers it to 17–20 %;
  floor absorption 0.3 changes it little; ceiling absorption 0.3 / 0.6 lowers it to 20–21 % / 13–14 %. Only a
  clearly more absorbing (or transmitting) ceiling brings the early distribution near the measurement, which would
  also shorten the CR4 T30 that is 15–25 % long. The BRAS photographs show panels hung between deep concrete beams
  and the model notes say the steel construction behind them is not modelled (`CR4_ModelSimplifications.pdf`, item 8),
  so sound may pass behind the panels; this is a hypothesis, not tested against data, and the BRAS materials are left
  as they are. The missing 3–20 ms energy (the model has the chairs only as a material, item 2, and no equipment near
  the sources or the listener) is not explained either.
- Image-source fix found with this check: on a mesh a reflection point on the shared edge of two coplanar triangles
  (on the symmetry plane, centred source and listener) was valid for both triangles, so the image was counted twice
  (in CR4 the ceiling reflection of LS7, twice its energy). Both engines now count images of the same order within
  1 cm once (`brir_proto.visible_images`, `engine_geom.js` ism). Of the earlier checks, the BRAS RIR check has one
  affected pair (CR4 LS2 → MP1, one first-order reflection); the CR4 binaural results above are reruns; the
  Fratoni TCB / DUS browser runs, rerun, are unchanged except one DUS pair (S2 → R14, C80 up to 0.2 dB). The earlier
  CR4 LS7 IACC_E3 of 0.84 with the K8 pattern came from the doubled ceiling reflection; it is 0.63 now (0.92 measured).
- FABIAN head (`tools/fabian_to_sofa.py`: the FABIAN HRIRs of the BRAS release, head-above-torso orientation 0°, 2°
  grid; left / right checked on the data) together with the measured K8 pattern and on-axis response
  (`validation/bras_brir_CR3_FABIAN_K8data.md`, `_CR4_FABIAN_K8data.md`): the spectrum difference at 2–4 kHz
  (−7 … −13 dB with the KU100) drops to within 1.4 dB in both halls, so it was the head, not the room; |ITD
  difference| 0–5 µs, |ILD difference| 0.3–0.5 dB; IACC_E3 0.35 (CR3) and 0.63 (CR4) against 0.52 and 0.83; C80 at
  500 Hz −1.3 dB (CR3) and −2.5 dB (CR4); T30 and EDT unchanged. With head and loudspeaker matched, what remains is
  the room model: low IACC_E3, low C80, CR4 T30 long, CR3 EDT long.
- IACC_L is about a third to a half of the measurement. The late part is rendered with the coherence of an ideal
  diffuse field for the head, which is near 0 above 500 Hz (see "Late interaural coherence"); the measured late part
  is more coherent than that at this position.
- C80 is too low at 500 Hz–1 kHz in both halls, by 1–4 dB with the coverage cone. EDT is 15–28 % long in CR3 but
  within 8 % in CR4.
- T30 is 15–25 % long in CR4, about twice the deviation of the RIR check in the same hall (about +2 JND ≈ +10 %,
  dodecahedron, LS1 / LS2, decimated mesh); the cause is not resolved (the two runs differ in sources, mesh decimation
  and ray count).

These are laboratory-style comparisons at one listener position in two rooms; they do not say how audible the
differences are.

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
- OBJ mesh halls: image sources to order 2 in the browser and 1 in Python, no diffraction; the conversion to a drawn hall keeps the volume and
  maps the absorption so that T30 stays close to the mesh, not where absorption sits (see *3D OBJ halls*). In the
  browser, the plan and section are projections (balconies show only as the column's lowest floor and highest
  ceiling), heights are above the lowest floor, and the ray tracer has no diffuse-rain term (T30 within about 2 % of
  Python on CR3 / CR4 and on a tiled shoebox, C80 within 0.2 dB; ray noise: up to 6 % between seeds at 10 000 rays)
- Room-criteria check against measured halls: within about 1 JND at 500 Hz–4 kHz in a raked lecture hall (ULH),
  about 15 % too long in an elliptical domed hall (STC) with the dataset's Odeon-calibrated inputs (see *Room
  criteria against measured halls*)
- Position-by-position check against two real halls (BRAS CR3 / CR4): T30 8–11 % long with Eyring-fitted
  coefficients (calibrate first); first-order reflection levels +1.6 dB (CR3) and +2.7 dB (CR4) median, reflection by
  reflection poor in CR4; a 2.5D
  version of a hall with balconies does not reproduce its individual early reflections (see *Position-by-position
  check*)
- Drawn hall values come from ray tracing and carry random noise (see above); the shoebox ones do not
- Shoebox: uniform absorption, no diffraction, diffuse late field, image sources without scattering loss or finite-size
  factor (drawn and OBJ halls have both, see *Specular reflection factors*)
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

- BRAS database (for `validate_bras.py` and `validate_bras_cr.py`; not bundled): CC BY-SA 4.0 per the repository page, doi:10.14279/depositonce-6726.3.
- Fratoni dataset (for `validate_fratoni.py`; not bundled): CC BY 4.0, doi:10.17632/y7xnv6xg5s.1. Derived files in
  `validation/fratoni_*` carry its attribution.
- fast-simplification (Python, MIT licence; optional): mesh decimation for large OBJ halls.

- h5wasm 0.10.3 (NIST software licence; includes the HDF5 library), loaded from jsDelivr only when a
  SOFA directivity file is opened or BRIRs are exported as SOFA; not bundled. Check the licence text before distributing the viewer.
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
