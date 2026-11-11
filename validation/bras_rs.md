# BRAS reference scenes RS1 - RS4, RS6, RS7: the engine against the measurements and the round robin (2026-11-10)

Data: BRAS (Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0), scene drawings and SOFA
positions; materials from the BRAS surface descriptions (initial estimates). Script: `validation/bras_rs.py`
(geometry of each scene in its docstring); RS5 is in `validation/bras_rs5_engine.md`. The round-robin comparison uses the
curves of SuppPub2 of Brinkmann et al. (2019), https://doi.org/10.1121/1.5096178, read from the PDF's vector
graphics (`validation/rr_extract.py`, `validation/rr_compare.py`).

Method: the arrivals the engine produces for each scene (direct sound, image sources with the material reflection
factor, the (1 - s) loss and the Kirchhoff-Fresnel finite-reflector factor, UTD edge diffraction) are summed
coherently and processed like the measured RIR: Hann window from -6 / -3 ms before the direct sound to the
round-robin fade-out of the scene, then 1/3-octave levels. Shape error: rms of the band differences after removing
their mean; mean abs. difference: absolute levels (source: flat point source with the documented calibration,
0.4 Pa at 1 m). The Genelec 8020c response and directivity are not modelled (not in the downloaded data); the
round-robin participants had them.

## 1. Per scene (current engine, 125 Hz - 4 kHz, medians over the pairs)

| scene | pairs | shape error | mean abs. difference | note |
|---|---|---|---|---|
| RS1 rigid floor | 10 | 2.3 dB | 2.3 dB | |
| RS1 absorber (RockFon) | 9 | 3.1 dB | 3.2 dB | |
| RS1 diffusor | 10 | 3.6 dB | 3.4 dB | the diffusor modelled as a plane with its measured specular loss; scattered sound not in the discrete part |
| RS2 1 m plate, rigid / absorbing | 15 / 15 | 1.3 / 1.5 dB | 1.3 / 1.3 dB | incl. 6 pairs behind the plate |
| RS2 2 m plate, rigid / absorbing | 15 / 9 | 1.6 / 1.5 dB | 1.4 / 1.5 dB | one pair 7 cm inside the shadow boundary is 7 dB louder measured (positioning tolerance 5.5 cm, BRAS documentation) |
| RS3 two parallel plates, 600 ms | 1 | 1.8 dB | 2.6 dB | see section 3 |
| RS4 reflector array, on / off centre | 9 / 9 | 1.8 / 1.5 dB | 2.4 / 1.2 dB | |
| RS6 body 0.72 x 0.72 m | 9 | 4.1 dB | - | **4 of 8 positions behind the body get no sound**; with second-order diffraction 3.2 / 2.7 dB (section 4) |
| RS7 15 blocks (seat dip) | 8 | 5.6 dB | 6.0 dB | in sight of the source -0.7 ... -4.7 dB (5 - 20 dB too loud before the fix of section 5); behind the first block 5 - 11 dB too loud |

## 2. Against the round-robin simulators (shape error on the 15 figures of SuppPub2)

| figure | scene | pair | reading check | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|---|---|---|
| S2-1 | RS1 rigid | LS2-MP2 | 0.3 | 2.8 | 0.8 | 3.0 | 0.8 | 1.6 | 2.9 |
| S2-2 | RS1 rigid | LS3-MP3 | 0.2 | 2.0 | 0.9 | 3.1 | 0.7 | 0.9 | 1.9 |
| S2-3 | RS1 absorber | LS2-MP2 | 0.3 | 2.3 | 0.7 | 2.7 | 0.7 | 1.6 | 1.3 |
| S2-4 | RS1 absorber | LS3-MP3 | 0.2 | 1.9 | 0.7 | 2.8 | 0.7 | 0.9 | 1.5 |
| S2-5 | RS1 diffusor | LS2-MP2 | 0.2 | 4.2 | 4.4 | 3.3 | 2.8 | 2.9 | 2.8 |
| S2-6 | RS1 diffusor | LS3-MP3 | 0.2 | 2.1 | 2.4 | 3.9 | 1.3 | 1.4 | 2.4 |
| S2-10 | RS2 1 m rigid | LS2-MP2 | 0.1 | - | 0.8 | 2.5 | 2.5 | 2.0 | 2.0 |
| S2-11 | RS2 2 m rigid | LS2-MP2 | 0.2 | - | 1.5 | 4.6 | 3.1 | 2.6 | 1.4 |
| S2-12 | RS2 1 m absorbing | LS2-MP2 | 0.1 | - | 1.0 | 2.4 | 1.7 | 1.4 | 2.3 |
| S2-13 | RS2 2 m absorbing | LS2-MP2 | 0.2 | - | 2.3 | 3.9 | 2.6 | 2.3 | 1.3 |
| S2-14 | RS2 1 m rigid | LS5-MP4 | 0.1 | - | 1.1 | 1.7 | 1.2 | 1.0 | 1.1 |
| S2-15 | RS2 2 m rigid | LS5-MP4 | 0.2 | - | 1.4 | 2.3 | 1.4 | 1.4 | 1.1 |
| S2-19 | RS3 | LS1-MP1 | 0.9 | 1.7 | 0.6 | 1.3 | 0.7 | 0.7 | 0.8 |
| S2-22 | RS4 on centre | LS2-MP2 | 0.5 | 3.0 | 0.8 | 2.7 | - | - | 2.3 |
| S2-23 | RS4 off centre | LS5-MP5 | 0.2 | 4.5 | 1.1 | 2.8 | - | - | 1.4 |
| **median** | | | | **2.3** (9) | **1.0** (15) | **2.8** (15) | **1.3** (13) | **1.4** (13) | **1.5** (15) |

All values in dB. The shape error is defined here; the paper compares the spectra only as figures (sec. III.A)
and gives no error measure. Reading check: the round-robin measured curve against the measured RIR processed here (0.1 -
0.9 dB, so the reading and the windowing agree). The round robin is anonymous; the letters are its own.

AuralPaths ranks between the two groups: better than A and D, close to E and F (1.3 / 1.4), worse than C. (Before
the fix of section 5 the median was 1.9 dB.) In RS1 (rigid floor, direct
sound 30 - 60 degrees off the loudspeaker axis) the gap to C / E is largest; the loudspeaker directivity, which the
participants modelled and this comparison does not, is the most likely cause (not tested: the Genelec 8020c data
are a separate 1.17 GB BRAS archive).

## 3. What the engine variants change

| | RS2 (4 configs) | RS3 | RS4 on / off | round-robin figures |
|---|---|---|---|---|
| before 2026-11-10 (no thin-plate edges) | 1.3 - 1.7 | 2.0 | 1.7 / 1.7 | 1.9 |
| current engine (thin-plate edges, one boundary edge in sight of the source, section 5) | 1.3 - 1.6 | 1.8 | 1.8 / 1.5 | 1.5 |
| as current, without the Kirchhoff factor, with diffraction + reflection (`diffraction_refl` 1) | 1.3 - 1.6 | 0.9 | 1.7 / 1.5 | 1.5 |

Shape error in dB. Free-standing plates get both the Kirchhoff-Fresnel factor on the specular reflection and UTD
at their edges, which counts the edge effect twice in principle; the measured differences between the variants are
small and not consistent in sign (better without the factor for the 2 m plate and RS3, worse for the 1 m plate), so
the engine is not changed. RS3 arrival by arrival (octave bands, energy within +-1.5 ms of each path): at 250 Hz
the arrivals with paths of 44 m and more are 14 - 63 dB stronger measured than with the Kirchhoff factor and 15 - 39
dB weaker than without it: for repeated reflections between two finite plates the Kirchhoff-Fresnel factor of
each reflection (with a1, a2 along the unfolded path) removes far too much at low frequencies, plain image sources
too little. At 1 and 4 kHz the arrival-by-arrival differences scatter by +-10 - 40 dB without a clear pattern
(overlapping arrivals of the two image series; not analysed further). The whole-window spectrum is dominated by the
first arrivals, hence the small shape errors above.

## 4. Thick obstacles (RS6): second-order diffraction (added 2026-11-10)

Before, the engine had first-order diffraction only: behind the 0.72 m body 4 of the 8 positions got no sound
(the path needs both top edges in sequence), the others were 1.4 - 6 dB off. New: `diffraction.diffract2` /
`GEOM.diffract2` (opt-in, `"geometry": {"diffraction_order": 2}`), UTD applied to the sequence of two edges with
the hard-face coefficient halved at grazing incidence on the second edge (Kouyoumjian & Pathak, NASA CR-2401,
1974, https://ntrs.nasa.gov/api/citations/19740020597/downloads/19740020597.pdf, sec. III.A). Variant `d2` of
`validation/bras_rs.py` (second order, diffraction with one floor reflection before / after, no Kirchhoff factor):

| pairs | level bias meas - sim | mean abs. difference | shape error |
|---|---|---|---|
| 8 behind the body | -0.6 ... +1.6 dB | 2.3 - 2.8 dB | 3.0 - 3.5 dB |
| 1 with line of sight 8 cm above the top | +0.3 dB | 2.7 dB (3.4 dB before) | 4.0 dB |

Checks of the method:
- Without the grazing factor 1/2 the four positions with source and receiver below the top are 5 - 6.5 dB too
  loud, as the factor predicts.
- With the Kirchhoff factor on the specular reflection off the 0.72 m top, the pair with line of sight drops to
  -5.0 dB (both the factor and the UTD reflection terms account for the finite face); without it +0.3 dB. The
  engine default keeps the factor (section 3); for scenes like this, `d2` drops it.
- The RS5 partition given as a 25 mm box with second-order diffraction over its two top edges (instead of one
  thin-plate edge; `validation/bras_rs5.py --variant box+floor+d2`) is 4 - 10 dB too loud behind it: the product
  of two UTD coefficients does not reduce to one knife edge when the edges are much closer than a wavelength (the
  w -> 0 limit discussed by Chu, Stanton & Pierce 2007, https://doi.org/10.1121/1.2783001). Plates thinner than
  5 cm therefore stay thin-plate edges; between 5 cm and a few tenths of a metre the second-order result has not
  been checked.
- Cost: in the drawn fan-hall example 0.5 s per source-receiver pair in Python (105 arrivals), 38 s with
  `diffraction_refl` 1 as well (2549 arrivals).

## 5. Grazing incidence over rows (RS7): fixed in sight of the source, not behind the rows

Source and receivers just above the tops of 15 blocks 0.12 m deep (a seat-dip set-up). Measured against the free
field (same window): with the source in sight (LS2) the level above 1 kHz is within +-2 dB of the free field, with a
dip of -7 ... -13 dB around 500 Hz (the seat dip) and +5 dB at 250 Hz; behind the first block (LS1) it is 8 - 17 dB
below the free field above 500 Hz.

The engine added one first-order diffraction term for each of the 30 block edges. Each lies near its edge's
boundary, where the UTD term reaches half the direct sound, and terms of independent edges add up: 5 - 20 dB too
loud. First-order UTD has no interaction between edges, so the engine now keeps, when the source is in sight, the
boundary diffraction of one edge only (`diffraction._lit_single` / `litSingle` in engine_geom.js, both engines): among
the plain paths whose receiver lies within 20 degrees of a boundary of its edge, the nearest one, plus the edges of a
face that reflects specularly to the receiver (a finite reflector). Engineering rule. Effect:

| | RS7 in sight (4 pairs) | RS7 behind the first block (4) | other scenes |
|---|---|---|---|
| level bias meas - sim, before | -7.9 ... -19.8 dB | -5.3 ... -11.0 dB | |
| level bias meas - sim, now | -0.7 ... -4.7 dB | unchanged | RS1, RS2, RS3, RS5, RS6 unchanged within 0.1 dB; RS4 on centre shape 2.1 -> 1.8 dB but mean abs. difference 2.0 -> 2.4 dB, off centre 1.6 -> 1.2 dB; round-robin median 1.9 -> 1.5 dB |

The remaining errors: the 500 Hz seat dip in sight of the source is not produced (no model for it), and behind the
first block the simulation is still 5 - 11 dB too loud (the attenuation over the following rows needs diffraction
over many edges in sequence). Second-order diffraction does not help over rows: with it the simulation is 7 - 31
dB too loud (pairs of near-grazing edges add up the same way); use it for isolated thick obstacles only. In the
drawn fan-hall example the rule reduces the diffracted arrivals of the 12 source-receiver pairs from 132 to 98.
**Behind seat rows, balcony fronts or riser steps seen at grazing incidence the simulation is still too loud.**

Update 2026-11-11: an optional seat-dip model (`"geometry": {"seat_dip": {"on": true}}`, `seatdip.py`; 2-D boundary
elements over generic seat rows, multiplied onto the direct sound) gives, with its settings scaled to this 1:3.2
set-up, 1.8 - 2.5 dB mean absolute difference in sight of the source and 3.3 - 6.2 dB behind the first block (median
measured - simulated -0.9 ... +0.3 and -5.6 ... +0.4 dB); the 400 - 500 Hz dip within 3 dB, but 315 Hz 5 - 7 dB too
quiet (the simulated dip starts about a third octave low). Before T was computed on 5.9 Hz bins (full scale) these were
3.0 - 3.3 and 3.4 - 6.7 dB, with 200 Hz 8 - 9 dB too loud from wrap-around of the rows' response
(`validation/rs7_seatdip_bem.py`; docs/MODEL_en.md, *Seat dip*).
The deep notch the model puts at 260 - 330 Hz is not explained: a converged 3-D calculation, the documented block
dimensions, absorbing block surfaces and MDF walls on the box cavity all keep it (`validation/rs7_seatdip_diag.py`;
docs/MODEL_en.md, *Seat dip*, lower edge of the dip).
