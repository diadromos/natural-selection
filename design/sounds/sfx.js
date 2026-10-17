// sfx.js: sound scheduler for the predator run + rubber stamps (see SOUND-NOTES.md).
// Loaded by all four pages after stamp.js:  <script src="design/sounds/sfx.js"></script>
// API:  SFX.setEnabled(true|false)   -> called from the #sound toggle's click (unlocks audio; autoplay policy)
//       SFX.scheduleRun(kind, nEaten, nStamps, STAMP)  -> called in step() right before stampMarks()/animatePredator()
//       SFX.lastRun                   -> log of the last scheduleRun (name, ms, vol, rate per event; used by tests/mixes)
// Timing is computed from the same constants the animations use, on the Web Audio clock (sample-accurate,
// not throttled like setTimeout). Predator timing is read from window.PREDATOR_T (exported by
// design/predator-anim/predator-anim.js), so there is one source of truth; P below is only a fallback.
(function () {
  const BASE = (document.currentScript && document.currentScript.src.replace(/[^/]*$/, '')) || 'design/sounds/';
  const NAMES = ['bird-chirp-a', 'bird-chirp-b', 'bird-flutter', 'stamp-thump-1', 'stamp-thump-2', 'stamp-thump-3',
    'stamp-thump-water', 'water-swoosh-a', 'water-swoosh-b', 'water-bubbles'];
  const VOL = { thump: 0.8, chirp: 0.45, flutter: 0.35, bubbles: 0.5, swooshHop: 0.3, swooshEnd: 0.35 };
  const MASTER = 0.8;
  const THUMPS = ['stamp-thump-1', 'stamp-thump-2', 'stamp-thump-3'];
  const P = { entry: 600, hop: 480, grab: 120, exit: 520 };   // fallback only; real values come from window.PREDATOR_T
  const LATE = 0.03;                                            // s: drop an event rather than play it >30 ms late
  let ctx = null, master = null, loading = null, on = false, rr = 0;
  const bufs = {}, live = new Set();
  const ext = () => (new Audio().canPlayType('audio/ogg; codecs="vorbis"') ? 'ogg' : 'mp3'); // Safari -> mp3
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load() {
    if (loading) return loading;
    const e = ext();
    loading = Promise.all(NAMES.map(n => fetch(BASE + n + '.' + e).then(r => r.arrayBuffer())
      .then(a => new Promise((res, rej) => ctx.decodeAudioData(a, res, rej))).then(b => { bufs[n] = b; })
      .catch(err => console.warn('sfx: could not load', n, err))));
    return loading;
  }
  function unlock() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain(); master.gain.value = MASTER; master.connect(ctx.destination);
    }
    if (ctx.state !== 'running' && !document.hidden) ctx.resume();
    return load();
  }
  function stopAll() { live.forEach(s => { try { s.stop(); } catch (e) {} }); live.clear(); }
  // pause audio while the tab is hidden; cancel pending events so nothing plays out of sync on return
  document.addEventListener('visibilitychange', () => {
    if (!ctx) return;
    if (document.hidden) { stopAll(); ctx.suspend(); } else if (on) ctx.resume();
  });
  function play(log, name, ms, t0, vol, vary = true) {
    const b = bufs[name]; if (!b) return;
    const when = t0 + ms / 1000;
    if (when < ctx.currentTime - (ctx.outputLatency || ctx.baseLatency || 0) - LATE) return; // missed (e.g. still loading): skip
    const s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = b;
    const rate = vary ? 1 + (Math.random() - 0.5) * 0.08 : 1;              // +-4% pitch
    const gain = vol * (vary ? 1 - Math.random() * 0.15 : 1);              // 0..-1.4 dB
    s.playbackRate.value = rate; g.gain.value = gain;
    s.connect(g); g.connect(master);
    s.onended = () => live.delete(s); live.add(s);
    s.start(Math.max(when, ctx.currentTime));
    log.push({ name, ms, when, vol: gain, master: MASTER, rate });
  }
  function schedule(kind, nEaten, nStamps, STAMP, t0, log) {
    const T = window.PREDATOR_T || P;
    // stamps: thump on CONTACT (end of the drop), not on the start of the stamp animation
    const water = kind === 'fish' && window.SFX.waterStamp;
    for (let n = 0; n < nStamps; n++)
      play(log, water ? 'stamp-thump-water' : THUMPS[rr++ % 3], STAMP.start + n * STAMP.gap + STAMP.drop, t0, VOL.thump);
    if (!nEaten) return;                                                   // animatePredator does nothing -> no predator sounds
    const grab = n => T.entry + n * (T.grab + T.hop);                      // grab n starts (gulp starts)
    const exit = grab(nEaten - 1) + T.grab;                                // exit flight starts
    if (kind === 'bird') {
      play(log, 'bird-flutter', 0, t0, VOL.flutter);
      for (let n = 0; n < nEaten; n++) play(log, n % 2 ? 'bird-chirp-b' : 'bird-chirp-a', grab(n), t0, VOL.chirp);
      play(log, 'bird-flutter', exit, t0, VOL.flutter);
    } else {                                                               // perch: underwater swooshes + bubbles, no chirps
      play(log, 'water-swoosh-a', 0, t0, VOL.swooshEnd);
      for (let n = 0; n < nEaten; n++) {
        play(log, 'water-bubbles', grab(n), t0, VOL.bubbles);
        if (n < nEaten - 1) play(log, n % 2 ? 'water-swoosh-a' : 'water-swoosh-b', grab(n) + T.grab, t0, VOL.swooshHop);
      }
      play(log, 'water-swoosh-b', exit, t0, VOL.swooshEnd);
    }
  }
  window.SFX = {
    waterStamp: true,                            // muffled stamp-thump-water on squirts.html (John: underwater sounds)
    lastRun: null,
    get enabled() { return on; },
    get context() { return ctx; },
    setEnabled(v) {
      on = !!v; try { localStorage.setItem('ns-sfx', on ? '1' : '0'); } catch (e) {}
      if (on) return unlock();
      if (ctx) { stopAll(); ctx.suspend(); } return Promise.resolve();
    },
    // kind: 'bird' | 'fish'; nEaten = eaten.length; nStamps = randomIdx.length; STAMP = the page's STAMP const
    scheduleRun(kind, nEaten, nStamps, STAMP) {
      if (!on || !ctx || document.hidden) return;
      if (reduced()) return;                                               // no animation -> no sound
      if (!nEaten && !nStamps) return;
      const perf0 = performance.now(), log = [];
      const run = { kind, nEaten, nStamps, perf0, events: log };
      window.SFX.lastRun = run;
      const go = () => {
        if (!on || document.hidden || window.SFX.lastRun !== run) return;
        const lat = ctx.outputLatency || ctx.baseLatency || 0;
        // t0 = context time of the click; corrects for any wait for resume()/decoding
        const t0 = ctx.currentTime - lat - (performance.now() - perf0) / 1000;
        run.t0 = t0; run.lat = lat;
        schedule(kind, nEaten, nStamps, STAMP, t0, log);
      };
      // still unlocking or decoding (e.g. Sound was clicked just before Next generation): schedule once ready
      if (ctx.state === 'running' && Object.keys(bufs).length === NAMES.length) go();
      else Promise.all([ctx.state === 'running' ? 0 : ctx.resume(), load()]).then(go);
    }
  };
})();
