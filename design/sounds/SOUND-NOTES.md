# Sound notes: predator run + rubber stamps

Michael (sound design) for John Hall. Every sound here is **original and procedurally synthesized** by
`gen-sounds.py` (numpy + ffmpeg). No samples, recordings or third-party sounds were used, so no CC0 or other
attribution is needed. License: original work made by Michael for John Hall, free to use, modify and
redistribute in this project (same terms as the repo).

## Files
All files are mono, 44.1 kHz. MP3 is 96 kbps CBR (LAME, gapless tag). OGG is Vorbis q4. Masters are 16-bit WAV in `wav/`.
Every master peaks at **-1.0 dBFS** (decoded MP3/OGG peaks are between -2.1 and -0.02 dBFS, so nothing clips).
Silence is trimmed at both ends. Thumps have no fade-in, so the transient is at sample 0 (onset 0.0 ms, peak at about 2 ms). Everything else has a 2 ms fade-in, and every file has a 15 ms fade-out, so there are no clicks.

| file (.mp3 / .ogg) | dur | size mp3 / ogg | loudness | vol (0–1) | what |
|---|---|---|---|---|---|
| `bird-chirp-a` | 163 ms | 2.8 / 5.1 KB | ≈ -14 LUFS | 0.45 | finch "tsee-tsip", two down-swept notes at 4–6 kHz |
| `bird-chirp-b` | 247 ms | 3.7 / 5.8 KB | ≈ -13 LUFS | 0.45 | "chi-chi-tweet", two ticks + an upswept note |
| `bird-flutter` | 306 ms | 4.3 / 7.4 KB | ≈ -18 LUFS | 0.35 | wing-beat noise bursts (about 17 Hz), swell and fade |
| `stamp-thump-1` | 217 ms | 3.4 / 5.4 KB | ≈ -17 LUFS | 0.8 | rubber stamp: 150→52 Hz thud + 1.8 kHz slap + sticky "tk" at +85 ms |
| `stamp-thump-2` | 181 ms | 2.8 / 5.2 KB | ≈ -18 LUFS | 0.8 | tighter and a bit higher (175→60 Hz, 2.3 kHz slap) |
| `stamp-thump-3` | 250 ms | 3.7 / 5.4 KB | ≈ -17 LUFS | 0.8 | heavier and longer (130→46 Hz, 1.5 kHz slap) |
| `water-swoosh-a` | 338 ms | 4.6 / 6.6 KB | ≈ -18 LUFS | 0.3 hop / 0.35 entry-exit | low filtered water push (160→850 Hz sweep) + 8 bubbles |
| `water-swoosh-b` | 299 ms | 4.3 / 6.2 KB | ≈ -17 LUFS | 0.3 / 0.35 | brighter and quicker (200→1000 Hz) + 11 bubbles |
| `water-bubbles` | 239 ms | 3.7 / 5.9 KB | ≈ -18 LUFS | 0.5 | a short cluster of 14 bubbles (the gulp) |
| `stamp-thump-water` | 287 ms | 4.0 / 4.8 KB | ≈ -17 LUFS | 0.8 | muffled (700 Hz low-pass) stamp, used on squirts.html (`SFX.waterStamp = true`) |
| `reward-chirp` | 307 ms | 4.3 / 6.0 KB | ≈ -12.5 LUFS | 0.55 | **easter egg**, finch: bright RISING two-note "tu-WEET" (≈3.5 kHz held, then 5.2→6.0 kHz sweep up) + high sparkle glints (7–10 kHz) |
| `reward-pop` | 340 ms | 4.9 / 6.6 KB | ≈ -12.3 LUFS | 0.6 | **easter egg**, perch: big rising "bloop" bubble (380→1280 Hz) → bright pop → fizz of small bubbles + sparkle |

Total: about 158 KB for all 24 web files (largest 7.4 KB). LUFS figures are approximate because the clips are this short.
Leading silence: none. Swooshes and bubbles start at sample 0 but swell softly (reaching -20 dB of peak by 6–17 ms) because they are pushes, not hits. Their audible peak is at 80–170 ms.

## Timeline (ms from the click on "Next generation", i.e. the `step()` call)
Sources: `T = {entry:600, hop:480, grab:120, exit:520}` in `design/predator-anim/predator-anim.js`, and
`STAMP = {start:150, gap:600, drop:240, squash:80, settle:160}` in index/mono/spots/squirts.html.
`stampMarks()` and `animatePredator()` are started in the same synchronous block of `step()`, so they share t=0.

- **Predator:** entry flight 0–600 → grab #0 at **600** (gulp starts) → hop to the next target 720–1200 → grab #1 at 1200 …
  So **grab n = 600 + 600·n** (n = 0..7: 600 … 4800), **hop n starts at 720 + 600·n** (n = 0..6, i.e. 7 hops between the 8 targets).
  Exit 4920–5440. Then STEP_PAUSE is 800 ms, and breeding happens at about 6240 ms.
  (Ken's summary says "8 hops of 480 ms". In the code, the first approach is the 600 ms entry, and after that there are 7 hops of 480 ms + 120 ms grabs. The grab times above follow the code.)
- **Stamp k (k = 0..7, in sorted cell order):** the animation starts at 150 + 600k, and the stamp **contacts at 390 + 600k** (offset `drop/dur` of the keyframes). That is also when the 90 ms cell shake starts. Squash peaks at +80 (470 + 600k) and settles by 630 + 600k.
  **The thump hits on contact: 390, 990, 1590, 2190, 2790, 3390, 3990, 4590.** Contact is the end of the drop. Don't fire it at the start (150 + 600k), which would be 240 ms early.
  The sticky "tk" built into the thump at about +85 ms matches the squash → settle.
- Check against the recording `design/shots/slow-index-1280.mp4`, using a frame-difference analysis: the run starts about 40 ms into the video. The perch-frame pops show up at about 640 + 600n, and the stamp-drop motion peaks end at about 1020 / 1620 / … These match the numbers above within one frame (33 ms).

## Trigger mapping
| event | page | sound | at (ms) | vol |
|---|---|---|---|---|
| stamp contact k=0..7 | all pages | `stamp-thump-1/2/3`, round-robin | 390 + 600k | 0.8 |
| predator entry | finch pages (index, mono, spots) | `bird-flutter` | 0 | 0.35 |
| **grab n** (gulp) n=0..7 | finch pages | `bird-chirp-a` / `-b`, alternating | 600 + 600n | 0.45 |
| exit | finch pages | `bird-flutter` | 4920 | 0.35 |
| predator entry | squirts | `water-swoosh-a` | 0 | 0.35 |
| grab n (gulp) n=0..7 | squirts | `water-bubbles` | 600 + 600n | 0.5 |
| hop n n=0..6 | squirts | `water-swoosh-b` / `-a`, alternating | 720 + 600n | 0.3 |
| exit | squirts | `water-swoosh-b` | 4920 | 0.35 |
| (optional) stamp contact | squirts | `stamp-thump-water` instead of 1/2/3 | 390 + 600k | 0.8 |

### Easter egg: reward note on the last stamp (John)
| event | page | sound | at (ms) | vol |
|---|---|---|---|---|
| contact of the **last stamp that lands** (the 8th: k=7) | finch pages | `reward-chirp`, layered on that stamp's thump | 390 + 600·7 **+ 15 = 4605** | 0.55, no random pitch |
| same | squirts | `reward-pop` | 4605 | 0.6, no random pitch |
- **+15 ms offset:** the thump's transient and body (first ~15 ms, 46–175 Hz) come through clean, and the reward note (3–10 kHz / rising bloop) sits on top as a separate event. Both are clearly heard. 0 ms also works; above +30 ms it starts to sound like a flam.
- **Distinct from regular chirps:** the regular chirps are down-swept (a) or short ticks (b). The reward holds a low first note and then jumps up about a fifth and keeps rising, it is longer, and it has sparkle glints. It also plays without random pitch, so it sounds identical every round (a recognizable "ding").
- **Collision rule:** grab #7 (4800) would chirp/bubble 195 ms into the reward. So a regular grab chirp/bubbles that starts within 300 ms after the reward is **skipped**, and the reward stands in for it. The thump, flutter and swooshes are unaffected.
- **Fewer than 8 stamps:** today `generation()` always kills exactly Q = N/4 = 8 at random, so there are always 8 stamps. If that ever changes (or a cell has no stamp svg), the reward fires on the **last stamp that actually lands**, at 390 + 600·(nStamps−1) + 15 (sfx.js uses `randomIdx.length`). John said "8th", and in the current code the last stamp is always the 8th. If he wants it strictly on the 8th only, change the `if (nStamps)` condition in sfx.js to `if (nStamps >= 8)`. With 0 stamps there is no reward. With 0 eaten (no predator) the reward still plays on the last stamp.

**Chirps go on the grab, not on the hop start.** The grab is the event (the bird lands and the creature disappears), and each chirp then sits 210 ms after a thump, so the result is a steady thump · chirp · thump · chirp pattern. The thump tails (≤ 250 ms) overlap the start of the chirp by 40 ms at most, which is inaudible. If John prefers chirps on take-off, use 720 + 600n: the chirp (≤ 250 ms) still ends before the next thump at 990 + 600n.
`preview/preview-mix-index.ogg` and `preview/preview-mix-squirts.ogg` are full 6.3 s renders of exactly this schedule, including the reward note and the water thump on squirts. Mixed peaks are -2.9 and -2.1 dBFS, so nothing stacks too loud. `preview/slow-index-1280-with-sound.mp4` is the recording with the index mix laid on top, so you can watch the sync.

## Integration tips (for Ken)
- **Use Web Audio and schedule from one clock.** The `sfx.js` in this folder does exactly that (now wired in; see Ken's section below).
  Call `SFX.scheduleRun('bird'|'fish', eaten.length, randomIdx.length, STAMP)` in `step()` on the line just before `stampMarks(...)`.
  It computes every trigger from the constants above on `AudioContext.currentTime` and subtracts `outputLatency`. This keeps the sound sample-accurate and in sync even if the main thread hiccups, which per-event `setTimeout` would not do.
  Keep its `P` in sync with `T` if the predator timing changes, or export `T` from predator-anim.js.
- **Autoplay policy.** No sound can start without a user gesture. Add a small "🔊 Sound" toggle, **off by default**, and call `SFX.setEnabled(true)` from its click handler (this creates/resumes the AudioContext and preloads and decodes all 10 clips, about 50 KB). Remember the choice in localStorage. Even then, resume the context on the next click on "Next generation", because browsers only allow it inside a gesture.
- **Format choice.** `canPlayType('audio/ogg; codecs="vorbis"')` picks OGG, otherwise MP3. Safari gets MP3. Older Safari may not trim the MP3 encoder delay (about 25 ms of silence at the start) when decoding. If the sync feels late on Safari, start the buffer with `start(when, 0.025)`.
- **Variation.** Round-robin the 3 thumps, and alternate the chirps and swooshes. Add ±4% playbackRate and 0 to -1.4 dB random gain per hit (sfx.js does this), so 8 identical thumps don't sound like a machine gun.
- **Levels.** All clips are peak-normalized to the same level. Use the vol column as gain, and put a master gain of about 0.8 on top. At most 2–3 clips ever overlap, so there's no need for a limiter.
- **Reduced motion.** When `prefers-reduced-motion` is on, the animations don't run, so don't play the sounds either (sfx.js skips them). The same goes for `multi()` (step N generations), which renders without animation.
- **Mobile.** iOS mutes Web Audio while the ring/silent switch is set to silent. That's expected, so don't fight it. Use Web Audio rather than `<audio>` elements: iOS plays only one `<audio>` at a time and adds latency. Keep the toggle large enough to tap. Suspend the context on `visibilitychange` → hidden.
- **Regenerating.** Run `python3 gen-sounds.py`. It is deterministic (fixed seeds) and rewrites `wav/`, all mp3/ogg files and the `preview/` mixes. `USE_WATER_STAMP = True` (default, matches `SFX.waterStamp`) puts the muffled stamp in the squirts preview, and `REWARD_OFFSET` (15 ms) sets the reward offset in the previews. Note: Vorbis writes a random stream serial, so re-rendering changes OGG bytes even when the audio is identical. Restore unchanged files with `git checkout` to avoid noise.

## Integration (Ken, animate-predators)
- Wired into all four pages: `sfx.js` loads after `stamp.js`; `step()` calls `SFX.scheduleRun(kind, eaten.length, randomIdx.length, STAMP)` just before `stampMarks(...)` (`'bird'` on index/mono/spots, `'fish'` on squirts).
- Predator timing has one source of truth: `predator-anim.js` exports `window.PREDATOR_T` (frozen copy of `T`); `sfx.js` reads it at schedule time and falls back to its own `P`.
- Squirts uses the underwater set (swooshes + bubbles, no chirps) and the muffled `stamp-thump-water` (`SFX.waterStamp = true`, was `WATER_STAMP = false`).
- `#sound` toggle in the controls: off on every page load ("Sound off", `aria-pressed="false"`); the stored localStorage choice is written but not restored, because audio cannot start without a click anyway.
- If Sound was just clicked and the clips are still decoding (or the context is resuming), the run is scheduled once ready, measured from the click; events more than 30 ms late are dropped instead of played out of sync.
- Background (John): `visibilitychange` → hidden and `pagehide` (incl. bfcache) stop every queued source, cancel a run still waiting to be scheduled, and suspend the context. `visibilitychange` → visible and `pageshow` (incl. `persisted`) resume it only if the #sound toggle is still on and the page is visible. The toggle's state, label and `aria-pressed` are never changed by this. Sounds left in the interrupted run are dropped (no backlog replay); the next Next generation schedules normally. Muting also stops pending sources.
- `SFX.lastRun` logs every scheduled event (name, ms, gain, playbackRate) for tests and offline mixes.
