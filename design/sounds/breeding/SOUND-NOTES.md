# Breeding sequence sounds

These are by Michael (sound design) for John Hall. Every sound is **original and procedurally synthesized** by `gen-breeding.py`
(numpy + ffmpeg, fixed seeds, bit-exact OGG). It reuses the DSP helpers from `../gen-sounds.py`, so the palette matches the
predator, stamp and reward sounds: the same rounded chirp syllables, Minnaert-style bubbles, swoosh filter and flutter.
No samples were used, so no CC0 or other attribution is needed. **License:** original work made for John Hall, free to use, modify and redistribute in this project.

Ken's hooks call `play('<name>')`, which loads `design/sounds/breeding/<name>.ogg`, or `.mp3` on Safari.
**Only the 6 base names are needed.** The variants are optional extras.

## Files
All files are mono, 44.1 kHz. The MP3s are 96 kbps CBR and the OGGs are Vorbis q4. The masters are 16-bit WAVs in `wav/`.
- **Peaks:** every master peaks at **-1.0 dBFS**. Decoded peaks fall between -1.6 and -0.6 dBFS, so nothing clips.
- **Leading silence:** none. Each file reaches -40 dB of its peak within 1.7 ms.
- **Attack:** a soft 2 ms attack, so stacked copies don't click. Tails get a 30 ms fade-out.

| file | dur | mp3 / ogg | LUFS (master) | suggested vol | what |
|---|---|---|---|---|---|
| **`heart`** | 299 ms | 4.3 / 5.1 KB | -14.9 | 0.3 | soft rising two-note "bloom" (E5 → A5, slight bend), like a tiny happy chirp |
| **`egg`** | 181 ms | 2.8 / 4.9 KB | -18.4 | 0.35 | little hollow shell "tok" (C5 + partials) + a soft wobble re-tap a fifth up |
| **`hatch`** | 394 ms | 5.6 / 5.9 KB | -13.2 | 0.25 | three delicate shell cracks, the halves falling apart, then a tiny rising "peep" (E6) |
| **`inch`** | 724 ms | 9.2 / 8.0 KB | -15.8 | 0.3 | caterpillar: 3 soft scrunch-steps (low squish + rubbery "bwip" down + tiny foot pat), 280 ms apart |
| **`swim`** | 804 ms | 10.1 / 9.4 KB | -19.4 | 0.4 | baby squid: 3 small jet pulses (soft filtered water push) + trailing bubbles, 300 ms apart |
| **`grow`** | 935 ms | 11.7 / 9.5 KB | -13.1 | 0.25 | gentle rising C-E-G-C shimmer + soft glints, then new wings open (light flutter at about 620 ms) |
| `heart-2` | 299 ms | 4.3 / 4.9 KB | -15.0 | 0.3 | variant (D5 → G5) |
| `egg-2` | 181 ms | 2.8 / 4.8 KB | -18.2 | 0.35 | variant (D5) |
| `hatch-2` | 394 ms | 5.6 / 5.7 KB | -13.6 | 0.25 | variant (peep D6, different cracks) |
| `inch-2` | 664 ms | 8.6 / 8.1 KB | -15.7 | 0.3 | variant (A4, 250 ms steps) |
| `swim-2` | 743 ms | 9.5 / 9.5 KB | -19.3 | 0.4 | variant (brighter, 270 ms pulses) |
| `grow-2` | 936 ms | 11.7 / 10.0 KB | -12.9 | 0.25 | variant (D-G-A-D) |
| `heart-water`, `heart-water-2` | 264 ms | 4.0 / 5.2, 4.9 KB | -15.8 / -16.4 | 0.3 | squirts option: rising bubble "plip-plop" on the same notes |
| `egg-water`, `egg-water-2` | 204 ms | 3.1 / 4.5, 4.4 KB | -15.8 | 0.3 | squirts option: round low "blup" (G4 / A4) |
| `hatch-water`, `hatch-water-2` | 391 / 416 ms | 5.2, 5.6 / 6.0, 6.3 KB | -15.5 / -14.1 | 0.25 | squirts option: muffled cracks + a little burst of bubbles |
| `grow-water`, `grow-water-2` | 911 / 908 ms | 11.4 / 8.5, 8.6 KB | -13.9 / -13.7 | 0.25 | squirts option: rising shimmer with a bubble on each note + a bubbly fizz |

- **Limits:** heart, egg and hatch are all **≤ 416 ms** (limit 600 ms). Inch, swim and grow are **≤ 936 ms** (limit 1.5 s).
- **Size:** the 6 base pairs come to **86 KB**, and all 20 pairs to 268 KB. The masters are 872 KB.
- **Suggested volumes:** these are loudness-matched, so a single play lands at about -25 to -27 LUFS, a little softer than the predator chirps.
  Ken's current `BREED_VOL` (0.4–0.55) is about 4–6 dB louder. That still doesn't clip, but **I'd use the values above**, because John wants breeding soft.

## Why overlaps stay soft (not harsh)
- **One key:** every tonal cue is tuned to the same **C-major pentatonic** (C D E G A). Stacked hearts, peeps and grow shimmers form a chord instead of beating or clashing.
- **No hard top end:** under 0.6% of the energy sits above 6 kHz, everything is low-passed to 7 kHz or lower, there are no hard noise transients (the shell cracks are soft band-passed ticks), and every file has a 2 ms attack.
- **Stress test,** using the suggested volumes × master 0.8, with base and -2 files alternating:
  - **Ken's throttle on** (180 ms gap per cue): 24 creatures staggered 40 ms apart give 6 plays per cue. Mixed peaks are -13 to -8.5 dBFS.
  - **No throttle at all:** all 24 plays peak between -12 and -6 dBFS, except `grow`, which reaches -0.8. Keep the throttle, or at least a per-cue gap, on `grow`.

## Trigger mapping
**What Ken's code has now** (`design/hearts/hearts.js`, uncommitted on `breeding-hearts`). `HEART = {stagger:40, pop:320, eggDelay:380, eggPop:280, hold:600}`.
`breedMarks()` starts after the predator run and stamps, about 5440 ms after the click. Parent k (k = 0..15, all 16 survivors) has `--d = 40·k` ms.

| cue | play at (ms after `breedMarks()` starts) | why |
|---|---|---|
| `heart` | **40·k + 0** | `heartPop` is 320 ms with an overshoot ease, and reaches full size at about 55% (176 ms). The heart's soft attack and rise match the pop starting, so don't delay it |
| `egg` | **40·k + 380 + 168 = 40·k + 548** | the egg drops in (`eggPop`) and lands at the 60% keyframe (168 ms). The "tok" is the shell touching down |

**Assumed steps (not in the code yet). Ken, adjust these to the real timings:**

| cue | play at | assumption |
|---|---|---|
| `hatch` | when the egg-crack animation **starts** | the cracks are at 0 / 70 / 150 ms and the peep at about 230 ms, so the baby should appear about 230 ms in |
| `inch` (finch pages) | at the start of the crawl to the child's new cell | 3 steps 280 ms apart (0.72 s). For a longer crawl, start it again or let it end early; it's fine to cut |
| `swim` (squirts) | at the start of the swim | 3 jet pulses 300 ms apart (0.8 s) |
| `grow` | at the start of the grow-up morph | the shimmer rises over about 360 ms, and the "wings open" flutter is at about 620 ms (the moment the adult shape completes) |

**Counts:** up to about 24 creatures (16 parents and their offspring), staggered, with Ken's throttle (`BREED_GAP` 180 ms per cue, `BREED_CAP` 8 per second) letting only a few overlap.
Hearts and eggs play at the code's 40 ms stagger, so the 180 ms gap lets roughly every 5th through, about 4 audible per cue per round. That's intended: it reads as a few at a time, not 16.

## Optional extras (only if Ken wants them; his `play()` currently accepts only the 6 base names)
- **Round-robin:** alternate `<name>` / `<name>-2` per play, plus ±3% random pitch, so repeats don't sound mechanical.
- **Squirts:** the base heart, egg, hatch and grow are soft enough for both settings. For a wetter squirts page, play `heart-water`, `egg-water`, `hatch-water` and `grow-water` (and their -2 versions) there instead. `swim` is already the water cue.
- **Silence rules:** follow the existing ones: sound off by default behind `#sound`, nothing in Run N or under reduced motion, and muted when the tab is hidden. Ken's `play()` path should follow them too.

## Regenerating
Run `cd design/sounds/breeding && python3 gen-breeding.py`. It rewrites `wav/`, `*.mp3` and `*.ogg` and is byte-identical on re-run, because OGG uses `-fflags +bitexact`.
It imports `../gen-sounds.py` for its helpers only and writes nothing outside `breeding/`.
