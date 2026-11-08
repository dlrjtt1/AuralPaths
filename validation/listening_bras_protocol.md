# Listening test: AuralPaths BRIRs against measured BRIRs (BRAS CR3 / CR4) — protocol draft

Status: draft, not run. Stimuli: `validation/listening_bras.py`. Objective comparison of the same BRIRs:
`validation/bras_brir_CR3_FABIAN_K8data.md`, `_CR4_FABIAN_K8data.md`.

## Question

Do listeners judge AuralPaths auralizations of two real rooms as plausible, and how do they differ from auralizations
with the measured BRIRs of the same source and listener positions, attribute by attribute? This tests the room model
only: head (FABIAN), loudspeaker (QSC K8 directivity and on-axis response), positions and dry signal are the same in
both versions.

## Model for the design

The perceptual part of the BRAS round robin (Brinkmann et al. 2019, *J. Acoust. Soc. Am.* 145(4), 2746–2760,
[doi:10.1121/1.5096178](https://doi.org/10.1121/1.5096178)) evaluated simulations of these rooms against the
measured BRIRs with (i) authenticity, a double-blind 2I/2AFC test, (ii) plausibility, a yes/no question "Was this an
audio example from a real room?" analysed with signal detection theory, and (iii) difference ratings on ten
attributes of the Spatial Audio Quality Inventory (SAQI; Lindau et al. 2014, *Acta Acust. united Ac.* 100(5),
[doi:10.3813/AAA.918778](https://doi.org/10.3813/AAA.918778)) with the measured auralization as reference. None of
the algorithms in the round robin was authentic; three of four were mostly plausible; tone colour, followed by source
position and localizability, contributed most to the differences. This test uses (ii) and (iii), so that AuralPaths
can be placed next to those results, with the differences listed below.

## Stimuli

- Rooms and positions: CR3 and CR4, listener MP6, loudspeakers LS3–LS7 (10 position pairs).
- Versions: measured BRIR (BRAS, FABIAN, head-above-torso orientation 0°) and AuralPaths BRIR (FABIAN HRIRs of the
  BRAS release, head-above-torso orientation 0°; measured K8 directivity and on-axis response; BRAS fitted materials,
  not calibrated). 20 BRIRs.
- Dry signal: anechoic guitar (excerpt of Flamenco2_U89.wav, TH Köln Audio Group, CC BY-SA; as distributed with
  pyfar, `pyfar.signals.files.guitar`), 6.7 s.
- Processing: both BRIRs cut to 2.5 s with a 50 ms fade, onsets aligned to the sample, every stimulus set to the same
  integrated loudness (ITU-R BS.1770, −26 LUFS) so that level is not a cue. No headphone compensation (one headphone
  model plays both versions; for plausibility judgements a FABIAN-based compensation would be better and is not
  available here).

## Procedure

1. Listener information and consent; headphone model and playback level fixed for all listeners (set once with
   the loudest stimulus at a comfortable level; record the level).
2. Familiarisation: a few stimuli of both versions from a room not used later, or the same rooms with another source,
   without feedback.
3. Plausibility block: all 20 stimuli, each presented N times (N to be fixed; the round robin used 100 trials with 20
   different contents), random order, one question: "Was this an audio example from a real room?" (yes / no).
   Listeners are not told that some examples are simulated beforehand only if the ethics approval allows this.
4. Attribute block: for each of the 10 position pairs, the measured version as the reference and the simulated
   version as the test item, switchable at will; a slider per attribute for the difference (test − reference),
   centre = no difference. Attributes: a subset of SAQI chosen for the differences found objectively, with the exact
   SAQI names, scale end labels and definitions to be taken from Lindau et al. (2014) before use — candidates: tone
   colour (bright–dark), horizontal source position, distance, localizability, reverberation, envelopment.
   One hidden reference (measured vs measured) per room as a check.
5. Short debriefing (what differences were noticed).

## Analysis

- Plausibility: hit rate (simulated judged real) and false-alarm rate (measured judged real) per listener; d′ as in
  the round robin; per room and pooled.
- Attributes: mean and confidence interval of the difference per attribute, room and source; linear mixed-effects
  model with listener as random intercept and room / source as fixed factors; check the hidden references are rated
  near zero.
- Relate attribute differences to the objective ones (spectrum, C80, IACC_E3 per source).

## Differences from the round robin (state them in any report)

- Static binaural synthesis: one head orientation (0°). BRAS also provides BRIRs for head orientations ±44° in 2°
  steps (BRAS documentation) for dynamic synthesis; this test does not use them.
- One dry signal instead of 20 contents for plausibility; one source per trial.
- AuralPaths was not run blind: the room model is the BRAS geometry and fitted materials, and the loudspeaker data
  were added after the objective comparison. The round-robin participants received the same scene descriptions.
- Laboratory test with simulated and measured BRIRs of two rooms: the result is about the auralization, not about
  sound reinforcement in these or other halls.

## Before running

- Ethics approval and consent form of the institution.
- Number of listeners: decide from the precision needed for d′ and the attribute means (power analysis); the round
  robin had 29 listeners, seven per algorithm for authenticity and plausibility.
- Check the stimuli: `out/listening_bras/stimuli.csv` (loudness, peaks, onset shift, SHA-256) and listen to every
  pair once for artefacts (clicks at the cut, noise floor of the measured BRIRs).
