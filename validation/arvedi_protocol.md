# Arvedi Auditorium: blind check protocol (fixed 2026-11-11, before any measured RIR was opened)

Purpose: one check of AuralPaths on a hall that played no part in its development, with the procedure fixed before
the measurements are seen, so that the result is a prediction and not a fit.

Data: "The Sound of the Violin's Home: A Higher-Order Room Impulse Response Dataset of the Arvedi Auditorium in
Cremona", Politecnico di Milano, https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0): 65 receivers, 5 stage sources
(one omnidirectional at the stage centre, four directional loudspeakers), 8-capsule spherical array, 48 kHz.
Derived outputs stay in `out/` (not in the repository).

## Fixed before the measurements are opened

1. **Code.** Engine as of commit `983daf2` (2026-11-11). Any change to the engine after the measured RIRs have been
   opened is reported separately as "after seeing the data"; the blind result is the one with this commit.
2. **Geometry.** A simplified 3-D model (`validation/arvedi_model.py`) drawn only from published drawings and facts:
   plans and sections on ArchDaily (ARKPABI, https://www.archdaily.com/870937), dimensions, volume, stage, materials
   and reverberation time in Arketipo (https://www.arketipomagazine.it/auditorium-giovanni-arvedi-del-museo-del-violino-di-cremona-studio-arkpabi-e-nagata-acoustics/),
   Beckmann Acoustics poster and the Museo del Violino page. The model is finished before any RIR is opened. The
   dataset's source and receiver coordinates may be read to place the model in the measurement frame (an offset and
   a rotation only; the hall shape is not changed to fit them).
3. **Initial materials.** BRAS CR3 (chamber music hall) "fitted" estimates by analogy (plaster, floor, seating,
   windows, stage), Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3 (CC BY-SA 4.0).
4. **Calibration.** Only absorption, scaled per octave band (125 Hz - 4 kHz) with `calibrate.py` so that the
   simulated T30 matches the measured T30 of the omnidirectional source averaged over all receivers. Nothing else is
   fitted. Scattering stays as initialised.
5. **Compared (omnidirectional source, omnidirectional pressure of the array).** Per receiver and octave band
   (125 Hz - 4 kHz): EDT, T20, C80, D50, Ts (ISO 3382-1); reported as bias and as the share of receivers within one
   JND (ISO 3382-1:2009 Annex A: EDT 5 %, C80 1 dB, D50 5 %, Ts 10 ms) and the mean error in JND, as for Detmold and
   the round robin. T30 is the calibration target and is shown only as a check of the fit.
6. **Settings.** As the Detmold check (`validation/detmold_kh.py`): image-source order 3, 20 000 rays, edge diffraction
   off, seat dip off, binaural settings unused (omnidirectional comparison). Pre-declared secondary runs: seat dip on (default
   seats), and the four directional sources with the generic loudspeaker directivity.
7. **One run.** The comparison is computed once and reported as it comes out, including failures.

## Added 2026-11-11, after reading the position files only (no RIR opened)

8. **Placement.** The dataset's origin is the stage centre (S0 at z = 1.45 m, S1 - S4 at 1.18 m) and its axes are
   parallel to the model's. The 65 receivers (rows A1 - A5) are on one side of the stage; on the low-end side all of
   them lie 0.5 - 1.4 m above the model floor, on the high-end side 11 of them would lie at or below it. Placement:
   model = dataset + (22.05, 7.0, 0) m, no rotation.
9. **Metrics, both sides with the same functions.** Octave-band energy histograms (measured: `validate_bras_cr.
   measured_hist` of each of the 8 capsules, energies averaged over the capsules; simulated: `brir_proto.energy_hists`
   at the array centre), then `validate_fratoni.criteria` (EDT, T30, C80, C50 -> D50, Ts) and T20 (-5 ... -25 dB) the
   same way. Direct sound at the geometric distance / c.
10. **Materials.** BRAS CR3 fitted values (examples/bras_cr3): seating (aud) <- mat_CR3_seating, plaster walls <-
    mat_CR3_plaster, ceiling <- mat_CR3_ceiling, windows <- mat_CR3_windows, walkway and stage floors <-
    mat_CR3_floor, wood shells <- mat_CR3_stagePanels; their scattering as given there.
11. **Secondary run, directional sources.** S1 - S4 with the generic loudspeaker model (90 degree coverage), aimed
    horizontally along +x (towards the measured audience); the aim is not documented in the dataset.

## Deviation, 2026-11-11, before any result (computation time only)

12. **Image-source order 2 instead of 3** (item 6). On this mesh (232 faces, each kept two-sided) order 3 takes about
    85 s per receiver for the image sources alone (order 2: about 11 s), i.e. some 17 hours for the calibration and the
    six comparison runs. Higher orders are left to the ray tracing (20 000 rays), as in the other mesh-hall checks
    (BRAS CR3 / CR4 use order 1). No result had been computed when this was changed; only the measured T30 means
    (calibration targets, 1.38 - 1.63 s, 125 Hz - 4 kHz) had been printed.

## The blind run is void: receivers placed on the wrong side (found 2026-11-11, after its results)

13. The dataset's documentation (README of https://github.com/polimi-ispl/arverir, which could not be reached from
    this session; the figure and the loudspeaker models were provided by the user after the blind results had been
    printed) shows the 65 receivers in rows A1 - A5 in front of the HIGH end, the dataset's +x pointing to it. Item 8
    placed them on the low-end side: the model's floor in front of the high end had been read too high from the
    section, so the height test chose the wrong side. The blind results (out/arvedi; EDT 21 - 36 % long, C80 0.5 -
    2.2 dB low at 250 Hz - 4 kHz for S0) compare the wrong seats and are void. Sources per the documentation: S0 B&K
    OmniPower 4292-L, S1 - S4 Genelec 8020C (quartet positions; photo: facing the audience on the +x side).
    **Post hoc run** (`validation/arvedi_check.py --posthoc`, out/arvedi_posthoc), not blind: dataset turned by
    180 deg (model = (22.05 - x, 7 - y, z)); ring-row floors in front of the high end set from the receiver heights
    (microphone 1.2 m above the floor; validation/arvedi_model.py PROF_POSTHOC); everything else as items 1 - 12, plus
    S0 with the 4292-L horizontal directivity from the B&K data sheet (BP 1689). These results are reported as
    post hoc and do not count as a blind check.

14. **Loudspeaker data for the post hoc run (2026-11-11, before it was started).** S1 - S4: Genelec 8020A
    manufacturer data (CLF2 file by Genelec Oy, measured 2009-09-21, anechoic, 1.6 m) as a stand-in for the 8020C of
    the dataset (same family and size; whether the C version radiates the same is not checked; the user judges the
    difference in sound to be small, which is a judgement, not a measurement). The horizontal and
    vertical polars (1/3-octave bands 125 Hz - 16 kHz) were read off the CLF Viewer plots by colour (`--genelec <csv>`;
    the CSV and the reading scripts stay in out/arvedi_posthoc, not in the repository). Aim: horizontal, towards the
    measured audience (dataset +x), as in the photo of the measurement. S0: as item 13 (omnidirectional, and the
    4292-L horizontal polars as a second run). Everything else as items 1 - 13; all results post hoc.

15. **Detailed diagnostic run (2026-11-12, after the post hoc results; `--posthoc --detail`, out/arvedi_detail).**
    Question: do the early-decay errors come from the simplified model and the uniform calibration? (a) Geometry:
    wooden parapets 1.1 m high and 0.25 m thick on the walkway edge along both sides (x 14.6 - 32 m) and a 1 m lip on
    the front of the high block, as in the photo and the sections; the pit walls under the walkway (x 15 - 29 m) as
    textured panels. (b) Materials per surface, with sources, instead of CR3 by analogy: seating = medium-upholstered
    unoccupied chairs (Gade, Springer Handbook of Acoustics ch. 9, table 9.3, after Beranek: 0.54 0.62 0.68 0.70 0.68
    0.66); plaster walls and ceiling = BRAS mat_CR2_plaster, windows = mat_CR3_windows, walkway and stage = mat_CR4_
    parquet, wood shells = mat_CR3_stagePanels, pit walls = mat_CR4_brickwall (BRAS initial estimates, i.e. before
    the uniform fit; scattering from the same files, seating scattering from mat_CR3_seating). (c) Reported first
    without any calibration (prediction from these values), then with only the seating absorption scaled to the
    measured T30 of S0 (`calibrate.py --adjust aud`). Sources as in item 14. Results are diagnostic, not a check.

Results of the post hoc runs: [arvedi_check.md](arvedi_check.md).
