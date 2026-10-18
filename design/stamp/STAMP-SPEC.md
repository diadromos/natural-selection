# Random-death mark: black rubber stamp

Replaces the yellow outline skull (`marks[i]=='random'` branch) with the same skull-and-crossbones art, now as a black rubber stamp inside a rough ring. The size is unchanged (viewBox `0 0 80 80`, 80x80), so it drops into the existing `.mark` overlay.

## Files (design/stamp/)
- `stamp.svg`: textured version (SVG filter). The filter id is `sfSTAMP_ID` and the bone mask is `smSTAMP_ID`; replace `STAMP_ID` with something unique per stamp (the cell index).
- `stamp-static.svg`: filter-free fallback. It has hand-jittered edges, about 15 fixed irregular ink voids plus 40 pinholes and two lighter patches, all in one mask (`stSv`), and a bone-gap mask (`stSb`).
- `stamp-svgs.js`: provides `window.STAMP_SVG(i)` (textured; ids `sf<i>`/`sm<i>`; seeds cycle through 3/17/41/88 by `i%4`) and `window.STAMP_STATIC` (string).
  - The SVG strings use single quotes only, with no backticks or `${`.
  - The static ids are fixed. Identical copies on one page are harmless because every reference resolves to an identical definition.
- `preview.png`: real size on white, mid-gray, black, red and green over a sample creature (textured, static, 3 seed variants), plus a 3x copy.
- `stamp-gen.py`: regenerates everything.

**Ink:** `#111`.

**How the filter works:**
- Two `feDisplacementMap` passes give rough edges: a low-frequency wobble (0.09, scale 2.4) and a fine grain (0.8, scale 1.3).
- Two thresholded `feTurbulence` alphas are multiplied together:
  - one gives low-frequency lighter patches (0.07);
  - one gives fine speckled voids (0.6).
- Voids are truly transparent, so the creature or background shows through them.

**Legibility:** a crisp, fully opaque white outline about 1px wide at 80px. The existing `.mark` `drop-shadow(0 0 3px #000)` still works with it. It reads on white, #888, #333, #111, navy #1a237e, deep red #8b0000 and green.
- Textured: the outline comes from the distressed ink alpha before the voids are cut (`feMorphology` dilate 1.1, then an `feFuncA` steepen for a hard edge, then the ink is cut out, white flood). So it hugs the rough edges and rims the eye/nose/teeth holes, while the speckled voids stay transparent instead of turning into white noise.
- Static: the same jittered shapes are stroked first in #fff, 2.3px with round joins, under the ink.

## Plug-in
```html
<script src="design/stamp/stamp-svgs.js"></script>
```
```js
// in render(): replace the random-mark SVG
marks[i]=='random' ? `<div class='mark stamp'>${STAMP_SVG(i)}</div>` : ...
// or the filter-free default:  `<div class='mark stamp'>${STAMP_STATIC}</div>`
```

## Slam animation (Web Animations API)
Set the tilt and offset once per stamp; they stay after the animation. Stagger the 8 stamps by 70 ms.
```js
function slamStamps(grid, randomIdx) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const anims = [];
  randomIdx.slice().sort((a,b)=>a-b).forEach((i, n) => {
    const cell = grid.children[i], svg = cell.querySelector('.mark.stamp svg');
    if (!svg) return;
    const rot = (Math.random()*24 - 12).toFixed(1);                      // -12..+12 deg
    const dx = (Math.random()*8 - 4).toFixed(1), dy = (Math.random()*8 - 4).toFixed(1); // ±4px
    const base = `translate(${dx}px,${dy}px) rotate(${rot}deg)`;
    svg.style.transform = base;                                          // kept after the animation
    svg.style.transformOrigin = '50% 50%';
    const delay = n * 70;
    if (reduce) {                                                        // fallback: plain fade-in
      anims.push(svg.animate([{opacity:0},{opacity:1}], {duration:200, delay, fill:'backwards'}));
      return;
    }
    anims.push(svg.animate([
      { transform: `${base} translateY(-18px) scale(1.8)`, opacity: 0, filter: 'none',
        easing: 'cubic-bezier(.55,0,1,.45)', offset: 0 },                 // drop, accelerating: 180 ms
      { transform: `${base} scale(1)`, opacity: 1, offset: 180/360 },
      { transform: `${base} scale(1.08,.92)`, opacity: 1,                 // squash + tiny ink spread: 60 ms
        filter: 'drop-shadow(0 0 .6px #111)', easing: 'ease-out', offset: 240/360 },
      { transform: `${base} scale(1)`, opacity: 1, filter: 'none', offset: 1 } // settle: 120 ms ease-out
    ], { duration: 360, delay, fill: 'backwards' }));
    // optional impact shake of the cell (1-2 px), starting at impact
    cell.animate([{transform:'translate(0,0)'},{transform:'translate(1.5px,-1px)'},
                  {transform:'translate(-1.5px,1px)'},{transform:'translate(0,0)'}],
                 {duration: 90, delay: delay + 180, easing: 'linear'});
  });
  return Promise.all(anims.map(a => a.finished));   // ~0.85 s for 8 stamps (7*70 + 360)
}
```
- `fill:'backwards'` keeps each stamp hidden (opacity 0) until its turn. After the animation the inline `transform` (tilt + offset) stays.
- Only transform, opacity and the stamp's own filter are animated. No creature or background color is touched.
- Order: run it right after `render(marks)`. It can overlap the predator run (`animatePredator`); both together still fit the ~3 s budget.

## Performance
- Eight filtered 80px SVGs render fine on desktop and mid-range phones. Each filter is rasterized once per stamp.
- Animating `transform` on a filtered element can re-rasterize it every frame on weak GPUs. If Ken sees jank (low-end Android, old iPhones), use `STAMP_STATIC` as the default; it looks close and has no filter cost.
- A cheap heuristic: `navigator.hardwareConcurrency <= 4` or reduced motion means static.
- The ink-spread `drop-shadow` keyframe is optional. Drop it first if frames are tight.
