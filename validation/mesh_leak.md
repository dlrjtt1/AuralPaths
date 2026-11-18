# Rays lost in 3D models: cause, fix and effect (2026-11-18)

Reported from the page with BRAS CR3 (Aspöck et al. 2020, *BRAS – Benchmark for Room Acoustical Simulation*, v3,
https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0; the CR3 numbers in this file are derived from it and are
CC BY-SA 4.0): the page showed 7 - 8 % of the rays "leaked through gaps" for a model that an independent ray tracer
on the same triangles found closed. Engine before the fix: commit `1e911b9`. Scripts: `validation/check_mesh_leak.js`
(regression check `mesh_leak`), `validation/check_leak_effect.py`.

"Rays lost" counts every ray that was ended early at any of its reflections (up to 400, or 2.5 s). It is not the
share of the energy: a ray lost at its 50th reflection has given most of its energy already (see *Effect*).

## Cause

`buildMesh` (`engine_geom.js`) and `build_mesh` (`geometry.py`) decide which side of a face is the room from the
voxels 2.5 voxels in front of and behind points on the face, and dropped a face with no room voxel on either side
as a "hidden face". A face narrower than the surface band of its neighbours (band = the surface voxel and one voxel
of dilation on each side) has no room voxel at that distance although it bounds the room, and was dropped too.

CR3, the page's set-up (OBJ from Blender, 2598 triangles, 6.53 cm voxels, 20 000 rays per source, 4 sources):

| | faces dropped | area of the dropped faces | rays that found no surface | rays ended behind faces / in unreached space |
|---|---|---|---|---|
| before | 285 | 8.10 m² of 2763.0 m² | 8.0 - 8.5 % | 2.0 - 2.2 % |
| no face dropped (diagnostic switch) | 0 | 0 | 0.00 - 0.02 % | 0.01 - 0.03 % |

The dropped faces (kept as evidence in `out/mesh_leak/culled_faces_before_fix.csv` and `.obj`, not in the
repository): 235 vertical and 50 horizontal; seating 172, structuredPlaster 66, plaster 25, stagePanels 18, floor
4; width (2 × area / longest edge) median 5.9 cm, 90 % below 9.0 cm. 140 are vertical seating faces below 1.5 m
(step risers). Half of the rays ended behind faces started within 0.5 m of a dropped face (62 % within 1 m).

Voxel size (before the fix): 6.53 cm 285 faces dropped, 8.0 - 8.5 % found no surface; 4 cm 218 faces, 4.6 - 5.0 %;
3 cm 97 faces, 0.5 - 0.7 %. Welding the vertices (0.1 mm, 1230 → 1211) changed nothing (285 faces, same rays).
Python (`geometry.build_mesh`) and JavaScript (`buildMesh`) give the same counts before and after (now, 5 cm: 2598
room faces, 279 narrow, 0 dropped, 3319.3 m³ in both; 6.53 cm: 293 narrow, 3310.2 m³ in both). `engine_js.py` runs
the JavaScript engine itself, so the page and the Python tools share the ray tracer.

## Fix

1. A face with no room voxel at 2.5 voxels is looked at again: room voxels within 3 voxels of its own points make it
   a narrow face, kept as a two-sided face. Only a face with none is left out (`keepAll` / `keep_all` keeps those too).
2. The two sides of a two-sided face lie in one plane. Before, the back was 2 mm behind the front; where the voxel
   vote took the room side for the back, a slit of up to 2 mm opened at the edge towards the next face (model of 24
   steps with 6 cm risers at 10 cm voxels: 0.24 % of the rays lost with fix 1 alone, 0 with both).
3. Volume: free voxels + 1.5 voxels of the surface band next to them (before 0.5): CR3 at 6.53 cm 3124 → 3293 m³
   (5 cm: 3188 → 3319 m³; BRAS documentation 3330.6 m³). The divergence theorem over the file's own winding is not
   used: for the CR3 OBJ the area vectors do not sum to zero (15.5 m² along x), so that value depends on where the
   origin is (3330.6 m³ in the file's frame, 3278 m³ with the origin at the model's corner). The engine uses it only
   when its oriented one-sided faces close (sum of area vectors below 0.1 % of their area) and it agrees with the
   voxel count within 3 %.
4. Page: the share of lost rays is always shown for a 3D model; above 0.1 % a warning says that the values are not
   valid, and the saved config and the SOFA comment carry the value. Names can be set to "Not part of the room".

## Result

`node validation/check_mesh_leak.js <files>` (source at the model centre, α 0.2, scattering 0.3, automatic voxel
size, 3 seeds × 20 000 rays). "Unreached space": the ray entered a space that the room fill did not reach, i.e. one
joined to the room only by openings narrower than about 3 voxels (a ceiling cavity behind slotted panels, the inside
of a thin slab); the engine ends it there, so such a space acts as an absorber.

| model | rays lost before | rays lost now | of which through gaps | of which in unreached space | faces: narrow kept / left out |
|---|---|---|---|---|---|
| steps model (built in the script; 5, 6.5, 10 cm voxels) | 44.5 - 50.6 % | 0.000 % | 0.000 % | 0.000 % | 20 - 24 / 0 |
| BRAS CR3 | 11.3 % | 0.015 % | 0.015 % | 0.000 % | 285 / 0 |
| BRAS CR4 | 38.7 % | 25.1 % | 3.2 % | 21.8 % | 1306 / 55 |
| Fratoni DUS | 38.2 % | 2.2 % | 1.3 % | 0.9 % | 2494 / 41 |
| Fratoni TCB | 10.1 % | 2.6 % | 2.4 % | 0.2 % | 1207 / 1 |
| Fratoni ULH | not run | 3.1 % | 0.2 % | 2.9 % | 257 / 38 |
| Fratoni STC | not run | 0.007 % | 0.007 % | 0.000 % | 312 / 29 |
| Arni model (`arni_model.py`, 5 cm) | 8.5 % | 0.007 % | 0.007 % | 0.000 % | 106 / 0 |
| OperaRIR model without / with seat rows (`opera_model.py`, 12 cm) | 1.3 % / 1.5 % | 0.000 % / 0.003 % | | 0.000 % | 3 / 0, 5 / 0 |

CR3 with the page's four source positions and three further ones (stage, mid-hall, near a side wall, balcony
height), 50 000 rays, 3 seeds at the first: 0.012 - 0.018 % at the two positions run after fix 2 (0.05 - 0.07 % at all
positions with fix 1 alone).

**Open.** CR4, DUS, TCB and ULH are above the 0.1 % limit after the fix. In CR4 almost all of it is rays that
enter the space above the ceiling panels through the slots between them; the room fill does not reach that space at
9.4 cm voxels, the faces that bound only that space are left out, and the rays are ended. This is not the dropped-face
error; it is how the engine treats a space behind narrow openings, and it needs its own decision (make such spaces
part of the room, or keep them as absorbers and say so). The rest ("through gaps", 1 - 3 % in CR4, DUS, TCB) has not
been traced to its cause.

## Effect on the results

Same rays and seeds, engine before (`1e911b9`) and now (`validation/check_leak_effect.py`; page set-up: the script
of this check in the session, not in the repository).

- CR3, the page's set-up (page default materials, α about 0.25 - 0.3; 4 sources × 3 seats, 50 000 rays, ray-traced
  part only): T30 +0.2 % on average (largest +0.9 %), EDT +0.4 % (largest +0.8 %).
- CR3 with the BRAS fitted absorption and scattering, not calibrated (`out/bras_shape_CR3/config.json`, LS1 ×
  MP1 - 5, 8 cm voxels, 50 000 rays, image sources + rays as on the page):

| criterion | engine | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz |
|---|---|---|---|---|---|---|---|
| T30 (s) | before | 1.69 | 1.47 | 1.37 | 1.41 | 1.39 | 1.12 |
| | now | 1.72 | 1.50 | 1.39 | 1.44 | 1.42 | 1.14 |
| | change, mean (%) | +2.0 | +2.1 | +2.1 | +2.1 | +2.1 | +1.9 |
| | change, largest of a pair (%) | +3.0 | +4.2 | +4.3 | +4.0 | +4.2 | +4.1 |
| EDT (s) | before | 1.71 | 1.42 | 1.34 | 1.41 | 1.36 | 1.13 |
| | now | 1.74 | 1.44 | 1.36 | 1.42 | 1.38 | 1.14 |
| | change, mean (%) | +1.7 | +1.3 | +1.2 | +1.2 | +1.3 | +1.3 |
| C80 (dB) | before | 0.08 | 1.30 | 1.65 | 1.27 | 1.47 | 2.87 |
| | now | -0.02 | 1.22 | 1.57 | 1.19 | 1.39 | 2.80 |

  So the holes shortened T30 by about 2 % and EDT by about 1.3 % in CR3 with its real materials, and raised C80
  by 0.1 dB. The documented comparison with the measurement (`validation/bras_CR3.md`, Python engine, not rerun)
  had the simulated T30 4 - 14 % longer than measured before calibration; without the holes it is about 2 % longer
  still, and the calibration factors fitted there are about 2 % too small for the same reason.
- CR4 with the BRAS fitted absorption and scattering, not calibrated (`out/bras_shape_CR4/config.json`, LS1 ×
  MP1 - 5, 50 000 rays): T30 +3.8 / +4.1 / +3.9 / +3.7 / +3.2 / +2.5 % at 125 Hz - 4 kHz (largest of a pair +6.1 %),
  EDT +1.9 … +2.6 %, C80 −0.2 dB. CR4 still loses 25 % of the rays after the fix (see *Open*).
- Fratoni DUS and TCB, rerun with `validation/check_fratoni_js.py` (20 000 rays; `validation/fratoni_DUS.md`,
  `fratoni_TCB.md`): DUS T30 +0.9 % on average (single zone and band −5.0 … +5.3 %), EDT +0.4 %, C80 within 0.2 dB;
  TCB T30 0.0 % (−3.0 … +6.7 %), EDT +3.1 %, C80 −0.2 dB. Mean absolute error at 500 Hz - 1 kHz, before → now:
  DUS EDT 2.7 → 2.8, T30 1.2 → 1.0, C80 1.2 → 1.2, Ts 0.9 → 0.8 JND; TCB EDT 8.2 → 7.9, T30 4.0 → 4.0, C80 2.7 → 2.5,
  Ts 3.5 → 3.4 JND. The single-zone changes are of the size of the ray noise at 20 000 rays
  (`validation/ray_noise.md`).

Why 8 - 24 % of lost rays change T30 by 0 - 2 % only: the rays are counted over their whole life. In CR3 a ray makes
about 100 - 180 reflections in 2.5 s (mean free path 4V/S = 4.8 m), so 10 % lost over the run is below 0.1 % per
reflection, against a mean absorption of 10 - 30 % per reflection. The dropped faces of CR3 were 8.1 m² of 2763 m².

In the Arni model the 106 dropped faces were the side faces of the panels (90.3 m² of 351 m²), which face each
other across the slots between neighbouring panels; rays that entered a slot were lost. They are now kept.

Not rerun: `validation/bras_CR3.md`, `bras_CR4.md`, the BRIR checks of CR3 / CR4, `fratoni_STC.md`, `fratoni_ULH.md`
(Python engine, hours of run time), `arni_check.md`, `opera_check.md`, the Arvedi records (excluded from use) and the
calibrations built on them. Their numbers are from the engine with the dropped faces. Detmold and the Fratoni 2.5D
runs use drawn halls, which have no voxel step, and are not affected.

## The `.skp` reader

- CR3: the `.skp` gives 2596 triangles, the Blender OBJ 2598. No face is missing: the area per material is the same
  to 0.01 m² (structuredPlaster 1171.93 m² in both, total 2763.0 m²); about 1200 triangles of each file have no
  counterpart in the other, because the two programs cut the same polygons into triangles differently. 75 of the
  `.skp` triangles have no area and are skipped.
- `CR3_RIR_Genelec8020c.skp`: 9256 faces are not room surfaces (`no_material` 7552, `colour_255_84_84` 1416,
  `[Color_A08]` 288). With these three names set to "Not part of the room" the model has the same area per material
  as `CR3.skp`.
