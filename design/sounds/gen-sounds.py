#!/usr/bin/env python3
"""gen-sounds.py: procedurally synthesizes every sound in this folder (numpy only, no samples).
Original work by Michael (sound design) for John Hall's natural-selection demo.
Run:  python3 gen-sounds.py   -> writes wav/ (masters), *.mp3, *.ogg   (needs ffmpeg with libmp3lame + libvorbis)
Deterministic: fixed RNG seeds, so re-running gives the same files."""
import numpy as np, subprocess, os, wave, tempfile
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(HERE, 'wav'); os.makedirs(WAV, exist_ok=True)

def t_(dur): return np.arange(int(SR * dur)) / SR
def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y
def onepole_hp(x, fc): return x - onepole_lp(x, fc)
def biquad_bp(x, f0, q):
    w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
    b0, b1, b2, a0, a1, a2 = al, 0, -al, 1 + al, -2 * c, 1 - al
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2, x1, y2, y1 = x1, v, y1, o; y[i] = o
    return y
def osc(freq_curve):  # phase-accumulating sine for a per-sample frequency array
    return np.sin(2 * np.pi * np.cumsum(freq_curve) / SR)
def place(buf, x, at):
    i = int(at * SR); n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n]; return buf
def fade(x, fin=0.0005, fout=0.012):
    x = x.copy(); a, b = int(fin * SR), int(fout * SR)
    if a: x[:a] *= np.linspace(0, 1, a)
    if b: x[-b:] *= np.linspace(1, 0, b) ** 2
    return x
def trim(x, thr_db=-48, keep_head=False):
    thr = 10 ** (thr_db / 20) * np.max(np.abs(x)); idx = np.where(np.abs(x) > thr)[0]
    s = 0 if keep_head else max(0, idx[0] - int(0.0005 * SR)); e = min(len(x), idx[-1] + int(0.004 * SR))
    return x[s:e]
def norm(x, peak_db=-1.0): return x / np.max(np.abs(x)) * 10 ** (peak_db / 20)

# ---------------- birds ----------------
def syllable(dur, f_start, f_peak, f_end, rng, harm=(1, .25, .08)):
    t = t_(dur); u = t / dur
    f = np.where(u < .35, f_start + (f_peak - f_start) * np.clip(u / .35, 0, 1) ** .7, f_peak + (f_end - f_peak) * np.clip((u - .35) / .65, 0, 1) ** 1.3)
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 95 * t))          # tiny trill
    env = np.sin(np.pi * u) ** 1.6 * (1 + .3 * np.sin(2 * np.pi * 160 * t))
    return env * sum(a * osc(f * (k + 1)) for k, a in enumerate(harm))

def chirp_a():   # finch "tsee-tsip": two quick down-swept notes, ~200 ms
    rng = np.random.default_rng(1); b = np.zeros(int(SR * .26))
    place(b, syllable(.075, 4200, 6300, 3900, rng), 0)
    place(b, .8 * syllable(.055, 4700, 5600, 3300, rng), .105)
    return b
def chirp_b():   # "chi-chi-tweet": two clicks + an upswept note, ~270 ms
    rng = np.random.default_rng(2); b = np.zeros(int(SR * .32))
    place(b, .7 * syllable(.03, 5200, 6000, 4800, rng), 0)
    place(b, .7 * syllable(.03, 5400, 6200, 5000, rng), .055)
    place(b, syllable(.12, 3300, 5200, 6100, rng, (1, .2, .05)), .125)
    return b
def flutter(dur=.36, rate=17.0, seed=3):  # wing-beat noise bursts, swelling then fading
    rng = np.random.default_rng(seed); t = t_(dur); u = t / dur
    n = onepole_lp(onepole_hp(rng.standard_normal(len(t)), 350), 2600)
    beat = (0.5 + 0.5 * np.cos(2 * np.pi * rate * t + np.pi)) ** 3
    env = np.sin(np.pi * np.clip(u * 1.15, 0, 1)) ** 0.8
    return n * beat * env

def sparkle(dur, rng, n=7, f_lo=7000, f_hi=10500, gain=.18):  # tiny high glints
    b = np.zeros(int(SR * dur))
    for k in range(n):
        f = rng.uniform(f_lo, f_hi); t = t_(.03)
        place(b, gain * osc(np.full(len(t), f)) * np.exp(-t / .006) * (1 - np.exp(-t / .0004)), rng.uniform(.02, dur * .8))
    return b
def reward_chirp():  # easter egg: bright RISING two-note "tu-WEET" (a 5th up), clearly unlike the down-swept regular chirps
    rng = np.random.default_rng(31); b = np.zeros(int(SR * .36))
    place(b, syllable(.085, 3000, 3500, 3700, rng, (1, .45, .2, .08)), 0)          # note 1 ~3.5 kHz, flat-rising
    place(b, syllable(.16, 4600, 5400, 6600, rng, (1, .4, .15)), .1)               # note 2 ~5.3 kHz, sweeping up
    return b + sparkle(.36, rng)
def reward_pop():    # easter egg: big upward "bloop" bubble + bright pop + small sparkly bubbles
    rng = np.random.default_rng(32); dur = .34; t = t_(dur); b = np.zeros(len(t))
    tb = t_(.16); f = 380 + 900 * (tb / .16) ** 1.4                               # big bubble rising 380 -> 1280 Hz
    place(b, osc(f) * np.sin(np.pi * np.clip(tb / .16, 0, 1)) ** .5 * (1 - np.exp(-tb / .002)), 0)
    tp = t_(.05); place(b, .6 * osc(1600 + 2200 * tp / .05) * np.exp(-tp / .012), .15)   # the "pop"
    for k in range(9): place(b, bubble(rng.uniform(.45, 1.2), rng, rng.uniform(.2, .45)), rng.uniform(.17, .28))
    return b + sparkle(dur, rng, 5, 5000, 8000, .12)

# ---------------- rubber stamp ----------------
def thump(seed, f0=150, f1=52, body_ms=110, slap_fc=1800, slap_q=1.4, slap_gain=.55, peel=True, muffle=None):
    rng = np.random.default_rng(seed); dur = .30; t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / .018)                        # fast pitch drop = weight
    body = osc(f) * np.exp(-t / (body_ms / 1000 / 3.2))
    click = onepole_lp(rng.standard_normal(len(t)), 5000) * np.exp(-t / .0012) * .3   # contact tick at t=0
    slap = biquad_bp(rng.standard_normal(len(t)), slap_fc, slap_q) * np.exp(-t / .009) * slap_gain * 2.2
    rub = osc(np.full(len(t), 230 + 40 * rng.random())) * np.exp(-t / .03) * .22        # rubbery wobble
    x = body + click + slap + rub
    x = np.tanh(1.6 * x) / np.tanh(1.6)                          # gentle saturation: denser, punchier thud
    if peel:  # tiny sticky "tk" ~85 ms later = the squash->settle release of the rubber
        p = biquad_bp(rng.standard_normal(len(t)), 2600, 2.0) * np.exp(-t / .004) * .5
        x = place(x, p, .085 + .01 * rng.random())
    if muffle: x = onepole_lp(onepole_lp(x, muffle), muffle * 1.5)
    return x

# ---------------- underwater ----------------
def bubble(r_mm, rng, gain=1.0):  # Minnaert resonance ~3.26 kHz/mm, rising chirp as it nears the surface
    f0 = 3260 / r_mm; d = .012 + .03 * r_mm / 3; t = t_(d * 4)
    f = f0 * (1 + 0.9 * t / (d * 4))
    return gain * osc(f) * np.exp(-t / d) * (1 - np.exp(-t / .0008))
def swoosh(dur, seed, f_lo=180, f_hi=900, n_bub=9):
    rng = np.random.default_rng(seed); t = t_(dur); u = t / dur
    n = rng.standard_normal(len(t))
    fc = f_lo + (f_hi - f_lo) * np.sin(np.pi * u ** .6) ** 1.5           # filter sweep up/down = water push
    y = np.zeros_like(n); s1 = s2 = 0.0
    for i, v in enumerate(n):
        a = np.exp(-2 * np.pi * fc[i] / SR); s1 = (1 - a) * v + a * s1; s2 = (1 - a) * s1 + a * s2; y[i] = s2
    y = onepole_hp(y, 90) * np.sin(np.pi * u ** .6) ** 1.2 * 3.0   # fast swell (peak ~1/3 in), long wash out
    b = y
    for _ in range(n_bub):
        place(b, bubble(rng.uniform(.9, 3.2), rng, rng.uniform(.25, .6)), rng.uniform(.008, dur * .7))
    return b

SOUNDS = {
    'bird-chirp-a':        lambda: chirp_a(),
    'bird-chirp-b':        lambda: chirp_b(),
    'bird-flutter':        lambda: flutter(),
    'stamp-thump-1':       lambda: thump(11, 150, 52, 115, 1800, 1.4, .55),
    'stamp-thump-2':       lambda: thump(12, 175, 60, 95, 2300, 1.8, .45),
    'stamp-thump-3':       lambda: thump(13, 130, 46, 135, 1500, 1.2, .62),
    'water-swoosh-a':      lambda: swoosh(.34, 21, 160, 850, 8),
    'water-swoosh-b':      lambda: swoosh(.30, 22, 200, 1000, 11),
    'water-bubbles':       lambda: swoosh(.24, 23, 120, 400, 14) * .6,
    'reward-chirp':        lambda: reward_chirp(),
    'reward-pop':          lambda: reward_pop(),
    'stamp-thump-water':   lambda: thump(14, 120, 44, 150, 900, 1.0, .35, peel=False, muffle=700),
}
THUMPS = {k for k in SOUNDS if k.startswith('stamp')}

def write_wav(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())

# ---------------- preview mixes: one full generation, same schedule as SOUND-NOTES.md ----------------
def load(n):
    with wave.open(os.path.join(WAV, n + '.wav')) as w: return np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32767
def preview():
    # predator (predator-anim.js T): entry 600, grab 120, hop 480, exit 520 -> grab n at 600+600n, hop n at 720+600n, exit 4920
    # stamps (page STAMP): start 150, gap 600, drop 240 -> slam n at 390+600n
    for page, kind in (('index', 'bird'), ('squirts', 'fish')):
        b = np.zeros(int(SR * 6.3)); thumps = ['stamp-thump-1', 'stamp-thump-2', 'stamp-thump-3']
        for n in range(8):
            th = 'stamp-thump-water' if (kind == 'fish' and USE_WATER_STAMP) else thumps[n % 3]
            place(b, .8 * load(th) * (1 - .08 * (n % 2)), (390 + 600 * n) / 1000)
            if n == 7:
                place(b, (.55 if kind == 'bird' else .6) * load('reward-chirp' if kind == 'bird' else 'reward-pop'), (390 + 600 * n + REWARD_OFFSET) / 1000)
                continue                                    # last grab (4800) is covered by the reward, no regular chirp/bubbles
            if kind == 'bird':
                place(b, .45 * load('bird-chirp-a' if n % 2 == 0 else 'bird-chirp-b'), (600 + 600 * n) / 1000)
            else:
                place(b, .5 * load('water-bubbles'), (600 + 600 * n) / 1000)
                if n < 7: place(b, .3 * load('water-swoosh-a' if n % 2 else 'water-swoosh-b'), (720 + 600 * n) / 1000)
        if kind == 'bird':
            place(b, .35 * load('bird-flutter'), 0.0); place(b, .35 * load('bird-flutter'), 4.92)
        else:
            place(b, .35 * load('water-swoosh-a'), 0.0); place(b, .35 * load('water-swoosh-b'), 4.92)
        pk = np.max(np.abs(b)); b = b / max(pk, 1) * .89  # never clip the preview
        os.makedirs(os.path.join(HERE, 'preview'), exist_ok=True)
        wp = os.path.join(tempfile.gettempdir(), f'preview-{page}.wav'); write_wav(wp, b)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-c:a', 'libvorbis', '-q:a', '4', os.path.join(HERE, 'preview', f'preview-mix-{page}.ogg')], check=True)
        print(f'preview-{page}: raw mix peak {20*np.log10(pk):+.1f} dBFS')
USE_WATER_STAMP = True    # matches sfx.js SFX.waterStamp = true (squirts uses the muffled thump)
REWARD_OFFSET = 15   # ms after the last stamp's contact, so the thump's attack stays clean

if __name__ == '__main__':
    for name, fn in SOUNDS.items():
        x = fn().astype(float)
        x = trim(x, keep_head=name in THUMPS)                # thumps: transient stays at sample 0
        x = fade(norm(x), fin=0.0 if name in THUMPS else 0.002, fout=0.015)
        x = norm(x)
        wp = os.path.join(WAV, name + '.wav'); write_wav(wp, x)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '96k', os.path.join(HERE, name + '.mp3')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-ac', '1', '-c:a', 'libvorbis', '-q:a', '4', os.path.join(HERE, name + '.ogg')], check=True)
        print(f'{name:20s} {len(x)/SR*1000:6.0f} ms')
    preview()
