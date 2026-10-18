# Predator run: motion spec

Note: the branch `animate-predators` did not exist when I checked (`git branch -a` lists only main and origin/main). I designed this against main's current `step()`: `render(marks)`, then `setTimeout(next generation, 1500)`. Nothing in git or in the pages was touched.

## Files (design/predator-anim/)
| file | what |
|---|---|
| `bird-fly-up.svg`, `bird-fly-mid.svg`, `bird-fly-down.svg`, `bird-perch.svg` | finch frames. The perch frame = `design/predator-bird.svg`, used for the grab. |
| `fish-tail-left.svg`, `fish-tail-center.svg`, `fish-tail-right.svg` | perch frames; the tail rotates ±22° about the peduncle |
| `bird-anim.svg`, `fish-anim.svg` | all frames in one SVG: `<g class='f1'>`, `f2`, `f3` (+ `perch` for the bird) |
| `predator-svgs.js` | `window.PREDATOR_SVGS = {bird, fish}`: the combined SVGs as single-quoted strings |
| `predator-anim.js` | `animatePredator(gridEl, eatenIdx, kind)`: the whole recipe below, ready to use |
| `demo.html` | standalone looping demo (`?kind=bird|fish&t=1200` freezes at t ms) |
| `frames-preview.png`, `demo-*.png` | renders |
| `frames-gen.py` | regenerates all SVGs + predator-svgs.js |

Style: same as the static marks. Red `#e00` 3px outline, dark halo (`#000` @ .55, 6.5px) drawn first, viewBox `0 0 80 80`, single quotes, no fills except the eye dot.

**Frame method chosen: frame-group swap.** The combined SVG has one `<g>` per frame, and each group's `opacity` is animated with `step-end` keyframes on the same WAAPI timeline. This is simpler and more legible than a CSS transform flap (a single wing can't convincingly go from up to down by rotation), and it stays in sync with pause/seek because everything is one timeline.

## Timing (8 targets: about 2.72 s)
| phase | ms | notes |
|---|---|---|
| entry | 300 | from offscreen top-left (`x=-size`, `y=grid.top-1.5*size`) to target 1 |
| grab | 60 | at each target: scale 1 → 1.15 (30 ms) → 1 (30 ms); bird shows `.perch` |
| hop | 240 | target n → n+1, in reading order (sorted index) |
| gulp | 150 | creature `scale(1)→scale(.2)`, `opacity 1→0`, `ease-in`, starts at grab start |
| mark | 150 | the static `.mark` of that cell fades 0→1 right after the gulp |
| exit | 260 | last target → off the far edge (`x = vw+size` if last target is right of center, else `-size`; `y = last.y - 2*size`) |

Total = 300 + 8×60 + 7×240 + 260 = **2720 ms**. With 1500 ms in `step()` today, change the timeout so it waits for the run (see Plug-in).

- **Hop easing:** `cubic-bezier(.45, 0, .2, 1)` (ease-in-out with a quick swoop). It's applied to the path parameter, and the position is sampled into 12 keyframes per hop, so the curve and the easing are both exact.
- **Path:** a quadratic bezier from A to B, with control point `((Ax+Bx)/2, max(Ay,By) + dip)`.
  - Bird: `dip = 0.25*dist + 20*k`, which swoops below the straight line.
  - Fish: `dip = 0.08*dist`, plus a sine wobble perpendicular to travel: `w = 6k·sin(2πu)·sin(πu)`. That's one S-curve per hop, zero at both ends.
  - `k = size/80`, and `size = min(96, cell width × .95)`.
- **Facing:** `face = sign(Bx - Ax)` per segment.
  - The bird is drawn facing right, so it gets `scale(face)`.
  - The fish is drawn facing left, so it gets `scale(-face)`.
  - The flip happens during the grab hold, so it's never visible mid-flight.
- **Rotation:** the tangent angle of the sampled path. If the creature is facing left, subtract 180°, then clamp to ±25°. The fish uses the full angle (it banks along the sine); the bird uses 0.3× of it (a slight tilt).
- **Anchor:** the beak tip / mouth lands exactly on the cell center. The transform is
  `translate(x,y) rotate(r) scale(sx,sy) translate(-mx,-my)` with `transform-origin:0 0`.
  - The anchor `(mx,my)` is the mouth point × k, read from `window.PREDATOR_ANCHORS` in predator-svgs.js: bird `(73.53,37.53)`, fish `(4.55,43)`.
  - The frames are auto-fitted inside the viewBox, with a 4.5-unit margin so the halo never clips. Bird: scale .986, fish: shifted 3.45 left. Each kind uses one transform for all its frames, so the anchor is identical across frames.
- **Frames:**
  - Bird: `f1 up → f2 mid → f3 down → f2 mid`, every **80 ms**, with `perch` shown during each 60 ms grab.
  - Fish: `f1 tail-left → f2 center → f3 tail-right → f2`, every **100 ms**, with `f2` held during grabs.

## WAAPI core (excerpt of predator-anim.js)
```js
// one predator element in a fixed, overflow-hidden overlay (no scrollbars when offscreen)
const layer = Object.assign(document.createElement('div'), {style:'position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:50'});
el.style.cssText = `position:absolute;left:0;top:0;width:${size}px;height:${size}px;transform-origin:0 0`;
el.innerHTML = PREDATOR_SVGS[kind];

// targets from getBoundingClientRect (viewport coords, matches position:fixed)
const targets = eatenIdx.slice().sort((a,b)=>a-b).map(i => { const r = cells[i].getBoundingClientRect();
  return { i, x: r.left + r.width/2, y: r.top + r.height/2 }; });

// path keyframes: for each segment sample n=0..12: u = ease(n/12); p = quad(A, C, B, u) (+ fish wobble)
kf.push({ offset: time/total, transform:
  `translate(${x}px,${y}px) rotate(${rot}deg) scale(${s*face*FACES[kind]},${s}) translate(${-mx}px,${-my}px)` });
// grab hold: two extra keyframes at B: scale 1.15 at +30 ms, 1 at +60 ms
el.animate(kf, { duration: total, fill: 'both' });

// frame swap: one step animation per <g class=f1|f2|f3|perch>
grp.animate(schedule.map(([t, f]) => ({ opacity: f === cls ? 1 : 0, offset: t/total, easing: 'step-end' })),
            { duration: total, fill: 'both' });

// gulp + static mark reveal, both delayed on the same clock
creatureSvg.animate([{transform:'scale(1)',opacity:1},{transform:'scale(.2)',opacity:0}],
                    { delay: tGrab, duration: 150, easing: 'ease-in', fill: 'both' });
markDiv.animate([{opacity:0},{opacity:1}], { delay: tGrab + 150, duration: 150, fill: 'both' });
```
Everything shares t=0, so `document.getAnimations().forEach(a => { a.pause(); a.currentTime = T; })` freezes the whole run at T (that's how `demo.html?t=` works).

**Reduced motion:** if `matchMedia('(prefers-reduced-motion: reduce)').matches`, `animatePredator` returns a resolved promise immediately. The static marks stay exactly as they are today.

**Colors:** the code animates only `transform`/`opacity` on the creature `<svg>` (first child `svg` of `.org`) and on `.mark`. It never sets fill, color or background, so the grid background and the creature genes are untouched. The overlay is removed when the run finishes.

## Plug-in for Ken (per page)
1. Load the scripts before the page script:
   `<script src="design/predator-anim/predator-svgs.js"></script><script src="design/predator-anim/predator-anim.js"></script>`
2. Make `step()` wait for the run:
```js
async function step(){
  const {marks,next} = generation(); render(marks);
  const eaten = Object.keys(marks).filter(i => marks[i]=='eaten').map(Number);
  await animatePredator(document.getElementById('grid'), eaten, 'bird');   // 'fish' on squirts.html
  setTimeout(() => { pop = shuffle(next); gen++; render(); }, 500);        // short pause to read the marks
}
```
3. Optional: disable #step/#multi while the run is going, to avoid double clicks.
The existing static eaten-mark markup stays as it is; the script hides each one until its creature is gulped.
