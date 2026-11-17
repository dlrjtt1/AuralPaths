# Where the computing time goes (2026-11-15, diagnostic)

Machine: 2 cores (cloud container); absolute times differ on other machines, the shares and ratios are the result.
Scripts: `validation/timing.py` (Python engine, wall-clock timers around the stages, exclusive times),
`validation/timing_js.py` (browser engine `engine_geom.js` in Node, one thread, `--prof` for Node's CPU profile).
Halls: Detmold (drawn hall, 34 receivers, image sources to order 3) and Arvedi (OBJ mesh, 65 receivers, order 2),
the calibrated configurations of the hall checks, one source.

## Python engine

| run | wall | ray tracing (pyroomacoustics, C++) | image-source factors, emission directions (Python) | image sources (C++) | rest |
|---|---|---|---|---|---|
| Detmold, criteria path, 34 receivers, 20000 rays | 79 s | 67.7 s (86 %) | 8.7 s (11 %) | 2.2 s | 0.5 s |
| Detmold, BRIR path, 3 receivers, 20000 rays | 17.8 s | 11.5 s (65 %) | 1.3 s | 0.4 s | early residual binaural 2.5 s, direction tracer 0.9 s, room set-up 0.9 s, late noise 0.3 s |
| Arvedi, criteria path, 65 receivers, 5000 rays | 220 s | 191.9 s (87 %) | 3.0 s | 16.7 s | room set-up 8.5 s |

The time is in pyroomacoustics' ray tracer, which is already compiled code. It grows with the number of receivers
(Detmold: 11.5 s for 3, 67.7 s for 34 receivers at the same ray count).

## Browser engine (Node, one thread)

| run | build | image sources | ray tracing, energy only | ray tracing with early / late directions |
|---|---|---|---|---|
| Detmold, 34 receivers, 20000 rays | 0.0 s | 1.0 s | 4.2 s | 4.4 s |
| Detmold, 3 receivers, 20000 rays | 0.0 s | 0.2 s | 2.6 s | 2.4 s |
| Detmold, 34 receivers, 80000 / 320000 rays | | | 13 s / 57 s | |
| Arvedi, 65 receivers, 5000 rays | 4.8 s (voxel room 3.5 s) | 0.7 s | 2.3 s | 2.5 s |

Own time (Detmold): `rays` 70 %, `inPoly2` 10 %, garbage collector 5 %. Arvedi: `voxelRoom` 34 %, `bvhWalk` 20 %,
`rays` 18 %, garbage collector 9 %.

Same ray count and receivers, ray tracing only: the browser engine on one thread is about 16 times faster than
pyroomacoustics in the drawn hall (4.2 s against 67.7 s) and about 80 times in the mesh hall (2.3 s against 192 s).
Not a like-for-like algorithm comparison: the browser tracer ends a ray at -70 dB of its start energy (pyroomacoustics
runs every ray to 2.5 s), uses a BVH in meshes and the analytic walls of the drawn hall.

Page, first computation after loading `index.html` (default hall, headless Chromium, main thread, CPU profile):
4.8 s, of which 6 % idle (waiting for the workers); `fftAny` 23 %, `gauss` 14 %, `fullHist` 10 %, `coherentPair`
10 %, `runBiquad` 5 %: the late-noise rendering on the main thread, not the tracing. A page run with a drawn or mesh
hall was not profiled.

## Ray noise of the browser tracer (Detmold, 34 receivers, 1 kHz, two seeds, ray histogram only)

| rays | time | EDT: RMS over receivers / hall mean | C80 | T30 |
|---|---|---|---|---|
| 20000 | 4 s | 8.0 % / +0.7 % | 1.00 dB / -0.08 dB | 9.6 % / +1.7 % |
| 80000 | 13 s | 3.0 % / +0.3 % | 0.48 dB / 0.00 dB | 4.2 % / -0.7 % |
| 320000 | 57 s | 2.2 % / -0.5 % | 0.19 dB / +0.04 dB | 2.6 % / -0.3 % |

Python (`validation/ray_noise.md`, full histogram): EDT 11.1 / 8.0 / 2.9 %, C80 0.93 / 0.47 / 0.27 dB, T30 22.8 /
12.1 / 6.0 % at 75 s / about 5 min / 18 min. Similar noise per ray, 15 - 20 times less time.

## Found on the way: the two engines differ in drawn halls

`validation/check_drawn_pyjs.py` (Detmold, calibrated materials of the Python run, every 6th receiver, 20000 rays,
mean over 6 receivers):

| band | browser T30 / EDT / C80 | Python T30 / EDT / C80 |
|---|---|---|
| 250 Hz | 1.86 s / 1.90 s / -0.9 dB | 1.50 s / 1.55 s / -0.1 dB |
| 500 Hz | 1.89 s / 1.95 s / -1.1 dB | 1.54 s / 1.58 s / +0.8 dB |
| 1 kHz | 1.94 s / 1.99 s / -1.2 dB | 1.51 s / 1.62 s / +2.3 dB |
| 2 kHz | 1.73 s / 1.78 s / -0.5 dB | 1.39 s / 1.57 s / +4.4 dB |

Same surfaces (59, same materials) in both. For orientation at 1 kHz (areas of the model, volume 4221 m3, air as in
the engines): Sabine 2.03 s, Eyring 1.87 s. The scattering model differs: in drawn halls the browser reflects a ray
either specularly or by Lambert's law with probability s, pyroomacoustics sends every reflection in the direction
s * Lambert + (1 - s) * specular. In mesh halls the browser uses the mixed direction too and the engines agree
(`check_mesh_pyjs.py`: T30 within 2 %). In this hall the absorption sits on the floor (seating 0.53, s 0.6) and the
walls and ceiling are hard (0.035, s 0.3); the mixed direction turns every wall reflection a little towards the
floor, the either-or model keeps 70 % of them specular. `validation/detmold_js.md`: calibrated on T30 separately, the two models agree with the measurement about equally. Consequence:
absorption calibrated with one engine does not carry over to the other in a drawn hall; the Detmold check
(`detmold_kh.md`) is a check of the Python engine.

## Page with a drawn hall (fan hall example, 12 paths, 50000 rays; added 2026-11-15)

Loading `examples/fan_hall_config.json` into the page, headless Chromium, 2 cores: 55 - 64 s. Main thread before the
change below: 34 % idle (waiting for the ray-tracing worker), `lateDir` 24 %, `fftAny` 13 %, the Gaussian random
numbers of `lateDir` 22 % (`gs`, `rn`), `runBiquad` 3 %: about 3 s per path for the four noise-pair sets of the
directional late field and the early windows. These are now computed in a pool of workers; the main thread is 97 %
idle, the BRIRs are identical, the total time on 2 cores is the same (57 - 66 s, one worker). With more cores the
pool has up to 6 workers; not measured.

## Faster page computation (2026-11-17)

Two changes, measured on the fan hall example (`examples/fan_hall_config.json`, 4 sources x 3 seats, 50000 rays,
headless Chromium, 2 cores, so one ray-tracing worker and one late-noise worker):

| step | before | after |
|---|---|---|
| loading the config (all 12 paths) | 55 - 63 s | 27 s |
| moving one PA (3 paths) | 13.5 s | 6.7 s |
| moving one seat (4 paths) | 39 s | 14 s |
| changing ITDG / level ratio (no new paths) | 0.06 - 0.15 s | unchanged |
| first load of the page (default shoebox) | 5 s | unchanged |

1. Ray tracer (`engine_geom.js`, `GEOM.rays`): the planes of the surfaces are read from one flat array, the
   point-in-surface test takes coordinates instead of a new array per test, and the Lambert frame of a surface is
   computed once. Same arithmetic in the same order: the histograms and direction records are bit-identical
   (Node benchmark of the page's worker message, 4 sources x 50000 rays: 15.1 s -> 10.2 s; all arrays identical;
   page BRIRs identical). Python's `engine_js.py` uses the same file and gets the same speed-up.
2. Early-window noise (`viewer_template.html`, `lateDir` with a length): the three noise pairs of the early
   scattered energy (0 - 20, 20 - 50 ms, rest of the early part) are used only up to the end of the early part, but
   were generated over the full length of the late field (76800 samples). They are now generated up to the first
   arrival + early part + cross-fade + 0.2 s (band-filter edges), about 16384 samples in this hall. The late field is
   unchanged (bit-identical after the early part). Inside the early part this is a new noise realization: against
   the old page, energy in the windows 0 - 20 / 20 - 50 / 50 - 110 ms RMS 0.18 / 0.19 / 0.25 dB over the 12 paths,
   IACC_E3 (500 Hz - 2 kHz) mean difference 0.000, RMS 0.048; the old page with other noise seeds gives 0.23 / 0.13 /
   0.22 dB and RMS 0.050, so the change is within seed-to-seed variation.

With more cores both pools grow (up to 8 ray-tracing and 6 noise workers); not measured here.

First load of the page (default shoebox, same machine): the late-noise bank (8 templates of coherent noise pairs, one
generator stream) was built on the main thread before the first computation (2.5 s). Each template is now made only
when used (the default hall uses 4 of the 8), from the generator state it has in the stream (found by stepping the
generator without the arithmetic, 0.13 s), so the numbers are those of the whole stream; the templates needed at
start-up are made in workers (up to 4). Default page BRIRs bit-identical; after changing the HRIR set the templates
are made again on first use. Script blocking the page: 5.3 s -> 0.7 s; until the first computation is done:
5.4 s -> 3.7 s (2 cores: one bank worker; the main thread then waits about 1.9 s for it).

## 3D (OBJ) halls: image sources (2026-11-17)

Loading the DUS model of the Fratoni data (14082 room triangles after voxelisation, 4 sources x 3 seats, page defaults:
image sources to order 2 plus ray-guided specular paths to order 3, 10000 rays) took 205 s in headless Chromium on
2 cores, almost all in the ray-tracing worker: per source the exhaustive image-source search took 42 s and the rays
10.5 s (Node benchmark of the page's worker message). The search tests about 10^8 second-order candidate images per
source; each was rejected with several `Math.hypot` calls. The rejection tests now use squared distances and the
packed surface planes, and the back-trace allocates nothing until a point is on its surface. The same candidates are
accepted, in the same order: the image-source arrivals of all 12 paths are identical (DUS and the fan hall, compared
as JSON). Image sources of 4 sources: DUS 181 s -> 70 s, fan hall 1.7 s -> 0.8 s. Loading the DUS model in the page:
205 s -> 128 s on 2 cores (the image sources of the sources are spread over the workers, up to 4 in 3D halls, so a
larger machine runs them in parallel; not measured here). The model has no coplanar duplicate triangles (14063
distinct planes of 14082), so grouping by plane would not help.
