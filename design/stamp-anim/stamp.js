// stamp.js: black rubber-stamp skull for random (chance) deaths, stamped on with the Web Animations API.
// Loaded by all four pages before the page script. Pages call:
//   stampMark(i)                    -> HTML for the .mark overlay of random-death cell i (render())
//   stampMarks(gridEl, idx, timing) -> animate the stamps in (step()); returns a Promise
// Selection, breeding, creature colours and the predator run are not touched.
(function () {
  // ======================================================================
  // ART SOURCE (in priority order):
  //   1. window.STAMP_SVG(i)  - Henri's final art, design/stamp/stamp-svgs.js (full <svg>, own ink filter + light halo)
  //   2. window.STAMP_STATIC  - Henri's filter-free fallback (same file)
  //   3. PLACEHOLDER_ART below + this file's ink filter + CSS halo (used only if design/stamp/ is missing)
  // To swap art: replace design/stamp/stamp-svgs.js (keep viewBox 0 0 80 80, 80x80, single quotes).
  // ======================================================================
  // PLACEHOLDER_ART: placeholder stamp artwork.
  // Inner SVG markup for viewBox 0 0 80 80 (same size/box as the old yellow skull mark).
  // Draw in solid #000; the ink filter below roughens edges and adds uneven ink.
  // Placeholder: the old skull path filled black (eyes, nose, teeth knocked out with evenodd)
  // plus heavy crossbones.
  // ======================================================================
  const PLACEHOLDER_ART =
    "<path fill-rule='evenodd' d='M40 12 C24 12 18 24 18 34 C18 42 24 46 26 48 L26 56 L54 56 L54 48 C56 46 62 42 62 34 C62 24 56 12 40 12Z" +
    " M27 34 A5 5 0 1 0 37 34 A5 5 0 1 0 27 34Z M43 34 A5 5 0 1 0 53 34 A5 5 0 1 0 43 34Z M40 40 L37 46 L43 46Z" +
    " M33 50 h2 v6 h-2Z M39 50 h2 v6 h-2Z M45 50 h2 v6 h-2Z'/>" +
    "<path d='M12 61 L68 75 M68 61 L12 75' stroke='#000' stroke-width='6' stroke-linecap='round' fill='none'/>" +
    "<g><circle cx='9' cy='58.5' r='3.6'/><circle cx='11.5' cy='63.5' r='3.6'/><circle cx='71' cy='58.5' r='3.6'/><circle cx='68.5' cy='63.5' r='3.6'/>" +
    "<circle cx='9' cy='77.5' r='3.6'/><circle cx='11.5' cy='72.5' r='3.6'/><circle cx='71' cy='77.5' r='3.6'/><circle cx='68.5' cy='72.5' r='3.6'/></g>";

  // Ink look (tunable). ROUGH = edge displacement (viewBox units), WARP_FREQ = edge wobble scale,
  // GRAIN = ink-dropout noise frequency, VOIDS = dropout threshold (0.30 = almost none, 0.45 = very worn),
  // VARIANTS = number of filters with different noise seeds (cell i uses variant i % VARIANTS).
  const INK = { ROUGH: 2, WARP_FREQ: 0.12, GRAIN: 0.16, VOIDS: 0.27, VARIANTS: 4 };
  // Thin light "paper" halo so black ink stays readable on dark backgrounds.
  const HALO = 'drop-shadow(0 0 .7px rgba(246,240,226,.95)) drop-shadow(0 0 1.6px rgba(246,240,226,.55))';
  function filterDefs() {
    let f = '';
    for (let v = 0; v < INK.VARIANTS; v++) {
      f += `<filter id='stamp-ink-${v}' x='-15%' y='-15%' width='130%' height='130%' color-interpolation-filters='sRGB'>` +
        `<feTurbulence type='fractalNoise' baseFrequency='${INK.WARP_FREQ}' numOctaves='2' seed='${3 + v * 11}' result='warp'/>` +
        `<feDisplacementMap in='SourceGraphic' in2='warp' scale='${INK.ROUGH}' xChannelSelector='R' yChannelSelector='G' result='rough'/>` +
        `<feTurbulence type='fractalNoise' baseFrequency='${INK.GRAIN}' numOctaves='2' seed='${7 + v * 13}' result='grain'/>` +
        // alpha = 9*(R - VOIDS): mostly solid ink, soft-edged dropouts where the noise is low
        `<feColorMatrix in='grain' type='matrix' values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  9 0 0 0 ${(-9 * INK.VOIDS).toFixed(2)}' result='ink'/>` +
        `<feComposite in='rough' in2='ink' operator='in'/></filter>`;
    }
    return f;
  }
  function install() {
    if (document.getElementById('stamp-defs')) return;
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.id = 'stamp-defs'; s.setAttribute('aria-hidden', 'true');
    s.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
    s.innerHTML = filterDefs();
    document.body.prepend(s);
    const st = document.createElement('style'); st.id = 'stamp-style';
    // Henri's art keeps the stock .mark drop-shadow (per STAMP-SPEC); the placeholder gets a light paper halo instead.
    st.textContent = `.mark.stamp.ph{filter:${HALO}!important}`;
    document.head.appendChild(st);
  }
  if (document.body) install(); else document.addEventListener('DOMContentLoaded', install);

  // deterministic per-cell pseudo-random in [-1,1) (does not consume Math.random, so selection RNG is untouched)
  const h = (i, k) => { let x = Math.imul(i + 1, 374761393) + Math.imul(k, 668265263); x = Math.imul(x ^ (x >>> 13), 1274126177); return (((x ^ (x >>> 16)) >>> 0) / 2147483648) - 1; };
  // Every keyframe uses the same function list (translate rotate translateY scale) so the browser interpolates
  // each function directly instead of falling back to matrix interpolation.
  const tf = (p, lift, sx, sy) => `translate(${p.dx}px,${p.dy}px) rotate(${p.r}deg) translateY(${-lift}px) scale(${sx},${sy})`;

  // stampMark(i): overlay HTML for random-death cell i (pose is applied by stampMarks right after render()).
  window.stampMark = function (i) {
    const art = typeof window.STAMP_SVG === 'function' ? window.STAMP_SVG(i) : window.STAMP_STATIC;
    if (typeof art === 'string' && art.indexOf('<svg') === 0) return `<div class='mark stamp'>${art}</div>`;
    install();
    return `<div class='mark stamp ph'><svg viewBox='0 0 80 80' width='80' height='80'>` +
      `<g fill='#000' filter='url(#stamp-ink-${Math.abs(i) % INK.VARIANTS})'>${PLACEHOLDER_ART}</g></svg></div>`;
  };

  // stampMarks(grid, idx, T): Henri's slamStamps (STAMP-SPEC.md) with page-tunable timing T:
  //   {start, gap, drop, squash, settle, scale, lift, tilt, offset, shake, spread, dropEase}
  // Reduced motion: stamps get their pose and appear instantly (static, no animation).
  // Resolves when every stamp has settled.
  window.stampMarks = function (grid, idx, T) {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const dur = T.drop + T.squash + T.settle, anims = [];
    [...idx].sort((a, b) => a - b).forEach((i, n) => {
      const cell = grid.children[i], svg = cell && cell.querySelector('.mark.stamp > svg'); if (!svg) return;
      const p = { r: (h(i, 1) * T.tilt).toFixed(1), dx: (h(i, 2) * T.offset).toFixed(1), dy: (h(i, 3) * T.offset).toFixed(1) };
      svg.style.transformOrigin = '50% 50%';
      svg.style.transform = tf(p, 0, 1, 1);                       // final pose, kept after the animation
      if (reduce) return;
      const delay = T.start + n * T.gap, ink = T.spread ? 'drop-shadow(0 0 .6px #111)' : 'none';
      anims.push(svg.animate([
        { transform: tf(p, T.lift, T.scale, T.scale), opacity: 0, filter: 'none', easing: T.dropEase, offset: 0 }, // drop
        { transform: tf(p, 0, 1, 1), opacity: 1, filter: 'none', offset: T.drop / dur },                             // contact
        { transform: tf(p, 0, 1.08, 0.92), opacity: 1, filter: ink, easing: 'ease-out', offset: (T.drop + T.squash) / dur }, // squash + ink spread
        { transform: tf(p, 0, 1, 1), opacity: 1, filter: 'none', offset: 1 }                                         // settle
      ], { duration: dur, delay, fill: 'backwards' }));
      if (T.shake) cell.animate([{ transform: 'translate(0,0)' }, { transform: `translate(${T.shake}px,${-T.shake / 1.5}px)` },
        { transform: `translate(${-T.shake}px,${T.shake / 1.5}px)` }, { transform: 'translate(0,0)' }],
        { duration: 90, delay: delay + T.drop, easing: 'linear' });  // impact shake of the cell
    });
    return Promise.all(anims.map(a => a.finished.catch(() => {}))).then(() => anims.length);
  };
})();
