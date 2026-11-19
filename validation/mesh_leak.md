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
Python (`geometry.build_mesh`) and JavaScript (`buildMesh`) give the same counts before and after (2026-11-19, 5 cm:
2576 room faces, 258 of them narrow, 22 behind the room's faces, 0 dropped, 3319.3 m³ in both; 6.53 cm: 2574 / 270 /
24, 3310.2 m³ in both; see *Faces behind the room's faces* below). `engine_js.py` runs
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
size, 3 seeds × 20 000 rays). Three states of the engine: before (commit `1e911b9`), with fixes 1 - 3 only (commit
`82158f3`), and now, with the spaces behind narrow openings counted as room and the rays behind faces followed (5, 6
below).

| model | rays lost before | fixes 1 - 3 | now | now: through gaps / in space that is not room | space added | rays followed behind faces |
|---|---|---|---|---|---|---|
| steps model (built in the script; 5, 6.5, 10 cm voxels) | 44.5 - 50.6 % | 0.000 % | 0.000 % | 0 / 0 | 0 | 0 |
| BRAS CR3 | 11.3 % | 0.015 % | 0.000 % | 0 / 0 | 0 | 0.01 % |
| BRAS CR4 | 38.7 % | 25.1 % | 0.000 % | 0 / 0 | 16.1 m³ (11 spaces and pockets) | 5.82 % |
| Fratoni ULH | not run | 3.1 % | 0.000 % | 0 / 0 | 1.3 m³ | 0.01 % |
| Fratoni STC | not run | 0.007 % | 0.000 % | 0 / 0 | 0 | 0.01 % |
| Arni model (`arni_model.py`, 5 cm) | 8.5 % | 0.007 % | 0.000 % | 0 / 0 | not read | not read |
| OperaRIR model without / with seat rows (`opera_model.py`, 12 cm) | 1.3 % / 1.5 % | 0.000 % / 0.003 % | 0.000 % / 0.000 % | 0 / 0 | not read | not read |
| Fratoni DUS | 38.2 % | 2.2 % | 1.40 % | 0.35 % / 1.05 % | 2.6 m³ | 1.44 % |
| Fratoni TCB | 10.1 % | 2.6 % | 0.29 % | 0.11 % / 0.19 % | 0.6 m³ | 2.33 % |

5. Spaces behind narrow openings are part of the room (`docs/MODEL_*`, mesh rule): pockets of up to 64 free voxels
   closed in by surface bands, and larger free spaces that at least 5 of 10 000 probe rays enter and that are not
   joined to the outside. In CR4 this is the air between the ceiling panels and the ceiling (16 m³).
6. A ray between the backs of one-sided faces is followed instead of ended. In CR4 these are rays in the 4 cm slot
   between the two skins of the ceiling panels, which are open at the rim (5.8 % of the rays over the run).

**Still above the 0.1 % limit: DUS and TCB.** In DUS the free space that the remaining lost rays enter is joined to
the border of the voxel grid, i.e. to the outside, and 0.35 % of the rays find no surface at all: the model has
openings to the outside at 10 cm voxels. Where they are has not been determined. TCB: the same kind, smaller.

## Faces behind the room's faces (2026-11-19)

Found while rerunning the validations: the second look of fix 1 also kept faces that do not bound the room, because
"room voxels within 3 voxels" does not ask whether another face lies in between. Fratoni ULH: the slab under the
raked floor (it touches the steps along their inner edges), the outer sides of the walls and the walls below the
rake, 252 m², so the surface was 1197 m² instead of 945 m². No ray reaches such a face, so the ray-traced results
were not affected, but the surface areas, the Sabine estimates printed with the checks and the 2.5D conversion
(`obj_to_hall.py` takes the absorption area per group from the mesh) were. The first look had the same weakness,
since before 2026-11-18, for a second skin a few centimetres behind a wall (BRAS CR4: the layers behind the stage
wall, 122 m²).

7. A face must have a free line to a room voxel. First look: from a point of the face to the room voxel 2.5 voxels
   in front of or behind it. Second look: from the points with room voxels within 3 voxels to the 8 nearest of
   them. The lines are tested against the triangles of the other faces within 4 voxels; a point within 1 mm of
   another face is not used (a slab touching the steps), and faces in the plane of the face do not block (two
   copies of one face). A face with no free line stays in the model as a two-sided face, so that no ray passes where
   it closes a slit, and is marked hidden: it is not counted in the areas, the room faces and the volume
   (`nHidden`, `aHidden` / `n_hidden`, `a_hidden`; `exposure: false` skips the test). If no point of a face can be
   tested in the first look, its count stands.

`node validation/check_mesh_leak.js <files>` as above, engine of commit `be5bc48` (before) and now:

| model | faces behind the room's faces | their area | surface counted, before → now | rays lost, before → now | relative change of the summed ray energy |
|---|---|---|---|---|---|
| double shell (built in the script: a box with a second skin 6 cm outside; 5, 6.5, 10 cm voxels) | 6 | 314.6 m² | 618.6 → 304.0 m² (exact 304) | 0 → 0 % | not read |
| BRAS CR3 | 24 | 0.7 m² | 2763.0 → 2762.3 m² | 0 → 0 % | 4 × 10⁻⁷ |
| BRAS CR4 | 140 | 126.7 m² | 5851.3 → 5724.6 m² | 0 → 0 % | 1 × 10⁻⁶ |
| Fratoni ULH | 241 | 249.7 m² | 1197.4 → 947.7 m² | 0 → 0 % | 3 × 10⁻¹⁰ |
| Fratoni STC | 176 | 18.6 m² | 631.1 → 612.4 m² | 0 → 0 % | 0 |
| Arni model | 105 | 89.4 m² | 441.7 → 352.4 m² | 0 → 0 % | 0 |
| OperaRIR model without / with seat rows | 1 / 1 | 0.0 m² | 6531.4 / 6915.2 m², unchanged | 0 → 0 % | 0 |
| Fratoni DUS | 1627 | 437.1 m² | 7626.6 → 7189.5 m² | 1.40 → 1.42 % | 5 × 10⁻⁷ |
| Fratoni TCB | 711 | 798.8 m² | 11995.4 → 11196.6 m² | 0.29 → 0.29 % | 0 |

(Single material and automatic voxel size, so the areas differ slightly from those of the validation runs.) The
ray energy changes where a face that was one-sided became a two-sided narrow face (its back moves from 2 mm behind
it into its plane). Python and JavaScript give the same counts on CR3, CR4, ULH and STC (`docs/MODEL_*`, *3D models
in the browser*). In the Arni model the faces behind are the panel sides, which face each other across the slots
between neighbouring panels: they keep the rays that enter a slot in the room and are not surface of the room.

Limits: a face seen from the room only through a slit narrower than about a voxel counts as behind the room's
faces (its area is not counted, the rays still reflect from it); a face smaller than 2 mm across has no point that
can be tested and is treated the same way.

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
  by 0.1 dB; in CR4 the holes and the rays ended above the ceiling panels shortened T30 by 3 - 5 %. The documented comparison with the measurement (`validation/bras_CR3.md`, Python engine, not rerun)
  had the simulated T30 4 - 14 % longer than measured before calibration; without the holes it is about 2 % longer
  still, and the calibration factors fitted there are about 2 % too small for the same reason.
- CR4 with the BRAS fitted absorption and scattering, not calibrated (`out/bras_shape_CR4/config.json`, LS1 ×
  MP1 - 5, 50 000 rays), engine now against before: T30 +4.7 / +5.2 / +4.8 / +4.4 / +4.0 / +2.9 % at 125 Hz - 4 kHz
  (largest of a pair +6.9 %), EDT +2.6 … +3.7 %, C80 −0.2 … −0.3 dB. With fixes 1 - 3 only (25 % of the rays still
  lost): T30 +3.8 / +4.1 / +3.9 / +3.7 / +3.2 / +2.5 %, EDT +1.9 … +2.6 %, C80 −0.2 dB. CR3 is the same with and
  without fixes 5, 6 (no space added).
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
other across the slots between neighbouring panels; rays that entered a slot were lost. They are kept in the model
now; since 2026-11-19 they are not counted in the surface (352 m², as before the fix; 442 m² in the runs of
2026-11-18 / 19 before that change), because they have no free line to the room.

Not rerun: the BRIR checks of CR3 / CR4 (Python engine), `arni_check.md`, `opera_check.md`, the Arvedi records (excluded from use) and the
calibrations built on them. Their numbers are from the engine with the dropped faces. Detmold and the Fratoni 2.5D
runs use drawn halls, which have no voxel step, and are not affected.

Rerun 2026-11-19 with the final rules: `fratoni_STC.md`, `fratoni_ULH.md`, `bras_CR3.md`, `bras_CR4.md` (notes at their tops; the BRAS tables in `docs/MODEL_*` still show the runs before).

## The `.skp` reader

- CR3: the `.skp` gives 2596 triangles, the Blender OBJ 2598. No face is missing: the area per material is the same
  to 0.01 m² (structuredPlaster 1171.93 m² in both, total 2763.0 m²); about 1200 triangles of each file have no
  counterpart in the other, because the two programs cut the same polygons into triangles differently. 75 of the
  `.skp` triangles have no area and are skipped.
- `CR3_RIR_Genelec8020c.skp`: 9256 faces are not room surfaces (`no_material` 7552, `colour_255_84_84` 1416,
  `[Color_A08]` 288). With these three names set to "Not part of the room" the model has the same area per material
  as `CR3.skp`.
