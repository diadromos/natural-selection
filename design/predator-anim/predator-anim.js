// predator-anim.js: Web Animations API predator run (bird or fish).
// Usage: await animatePredator(gridEl, eatenIdx, 'bird'|'fish');
// Needs predator-svgs.js loaded first (window.PREDATOR_SVGS). No colors on creatures/background are changed;
// it only animates transform/opacity of the creature <svg> and the .mark overlay inside eaten cells.
(function () {
  const T = { entry: 300, hop: 240, grab: 60, exit: 260, gulp: 150 };   // ms; total for 8 targets ~2.7 s
  const SWOOP = [0.45, 0, 0.2, 1];          // cubic-bezier for each hop (ease-in-out, quick swoop)
  const FRAME = { bird: 80, fish: 100 };     // frame swap period (ms)
  const CYCLE = { bird: ['f1', 'f2', 'f3', 'f2'], fish: ['f1', 'f2', 'f3', 'f2'] };
  const MOUTH = window.PREDATOR_ANCHORS || { bird: [74, 36.5], fish: [8, 41] }; // beak tip / mouth in the 80x80 viewBox (from predator-svgs.js)
  const FACES = { bird: 1, fish: -1 };       // +1 = drawn facing right, -1 = facing left

  // cubic-bezier easing solver (same math as CSS)
  function bez(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = t => ((ax * t + bx) * t + cx) * t, Y = t => ((ay * t + by) * t + cy) * t, dX = t => (3 * ax * t + 2 * bx) * t + cx;
    return x => { let t = x; for (let i = 0; i < 8; i++) { const e = X(t) - x, d = dX(t); if (Math.abs(e) < 1e-5 || !d) break; t -= e / d; } return Y(Math.min(1, Math.max(0, t))); };
  }
  const ease = bez(...SWOOP);
  const q = (a, c, b, u) => (1 - u) * (1 - u) * a + 2 * (1 - u) * u * c + u * u * b; // quadratic bezier

  window.animatePredator = function (grid, eatenIdx, kind = 'bird') {
    if (!eatenIdx.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return Promise.resolve(); // static marks stay
    const cells = [...grid.children], vw = innerWidth;
    const targets = [...eatenIdx].sort((a, b) => a - b).map(i => {   // reading order
      const r = cells[i].getBoundingClientRect(); return { i, x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width };
    });
    const size = Math.min(96, targets[0].w * 0.95), k = size / 80;
    const [mx, my] = MOUTH[kind].map(v => v * k);
    const g = grid.getBoundingClientRect();
    const start = { x: -size, y: Math.max(-size, g.top - size * 1.5) };          // offscreen top-left
    const last = targets[targets.length - 1];
    const end = { x: last.x > vw / 2 ? vw + size : -size, y: last.y - size * 2 };  // off the far edge

    // overlay + predator element
    const layer = document.createElement('div');
    layer.id = 'predator-layer'; // Ken: an id keeps mobile.css's body>div:not([id]) panel style (opaque background) off the overlay
    layer.style.cssText = 'position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:50';
    const el = document.createElement('div');
    el.style.cssText = `position:absolute;left:0;top:0;width:${size}px;height:${size}px;transform-origin:0 0`;
    el.innerHTML = window.PREDATOR_SVGS[kind];
    el.firstElementChild.setAttribute('width', size); el.firstElementChild.setAttribute('height', size);
    layer.appendChild(el); document.body.appendChild(layer);

    // ---- build one timeline: segments (move) and holds (grab)
    const pts = [start, ...targets, end], kf = [], frames = [], gulps = [];
    let t = 0, face = 1;
    const push = (x, y, rot, s, time) => kf.push({ time, transform:
      `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) rotate(${rot.toFixed(1)}deg) scale(${(s * face * FACES[kind]).toFixed(3)},${s}) translate(${-mx}px,${-my}px)` });
    for (let s = 0; s < pts.length - 1; s++) {
      const a = pts[s], b = pts[s + 1], dur = s === 0 ? T.entry : s === pts.length - 2 ? T.exit : T.hop;
      const dx = b.x - a.x, dy = b.y - a.y, dist = Math.hypot(dx, dy) || 1;
      face = dx >= 0 ? 1 : -1;
      const dip = kind === 'bird' ? 0.25 * dist + 20 * k : 0.08 * dist;              // swoop below the straight line
      const cx = (a.x + b.x) / 2, cy = Math.max(a.y, b.y) + dip;
      const N = 12; let px = a.x, py = a.y;
      for (let n = 0; n <= N; n++) {
        const u = ease(n / N);
        let x = q(a.x, cx, b.x, u), y = q(a.y, cy, b.y, u);
        if (kind === 'fish') { const w = 6 * k * Math.sin(2 * Math.PI * u) * Math.sin(Math.PI * u); x += -dy / dist * w; y += dx / dist * w; }
        let ang = n ? Math.atan2(y - py, x - px) * 180 / Math.PI : Math.atan2(dy, dx) * 180 / Math.PI;
        if (face < 0) ang -= 180; ang = ((ang + 540) % 360) - 180;
        const rot = Math.max(-25, Math.min(25, ang * (kind === 'bird' ? 0.3 : 1)));
        if (n || s === 0) push(x, y, rot, 1, t + dur * n / N);
        px = x; py = y;
      }
      t += dur;
      if (s < pts.length - 2) {                         // grab at target s+1
        const tg = t; gulps.push({ i: b.i, t: tg });
        push(b.x, b.y, 0, 1.15, tg + T.grab * 0.5); push(b.x, b.y, 0, 1, tg + T.grab);
        frames.push([tg, tg + T.grab]); t += T.grab;
      }
    }
    const total = t;
    const anims = [];
    anims.push(el.animate(kf.map(f => ({ transform: f.transform, offset: f.time / total })), { duration: total, fill: 'both' }));

    // ---- frame swaps (step keyframes per frame group); bird shows .perch during grabs
    const sched = []; let n = 0;
    for (let ft = 0; ft < total; ft += FRAME[kind]) {
      const grab = frames.find(([a, b]) => ft >= a && ft < b);
      sched.push([ft, grab ? (kind === 'bird' ? 'perch' : 'f2') : CYCLE[kind][n++ % 4]]);
    }
    ['f1', 'f2', 'f3', 'perch'].forEach(cls => {
      const grp = el.querySelector('.' + cls); if (!grp) return;
      const k2 = sched.map(([ft, f]) => ({ opacity: f === cls ? 1 : 0, offset: ft / total, easing: 'step-end' }));
      k2.push({ opacity: k2[k2.length - 1].opacity, offset: 1 });
      anims.push(grp.animate(k2, { duration: total, fill: 'both' }));
    });

    // ---- creatures: shrink into the beak; static .mark fades in after the grab
    gulps.forEach(({ i, t: tg }) => {
      const cell = cells[i], cr = cell.querySelector(':scope > svg'), mark = cell.querySelector('.mark');
      if (cr) anims.push(cr.animate([{ transform: 'scale(1)', opacity: 1 }, { transform: 'scale(.2)', opacity: 0 }],
        { delay: tg, duration: T.gulp, easing: 'ease-in', fill: 'both' }));
      if (mark) anims.push(mark.animate([{ opacity: 0 }, { opacity: 1 }],
        { delay: tg + T.gulp, duration: 150, fill: 'both' }));       // hidden until gulped, then fades in
    });
    return anims[0].finished.then(() => { layer.remove(); }, () => layer.remove()).then(() => total);
  };
})();
