#!/usr/bin/env python3
"""gen-breeding.py: breeding-sequence cues (heart, egg, hatch, inch, swim, grow), procedurally synthesized (numpy + ffmpeg).
Original work by Michael (sound design) for John Hall's natural-selection demo. No samples. Deterministic (fixed seeds,
bit-exact OGG serials). Reuses the DSP helpers of ../gen-sounds.py so the palette matches the predator/stamp sounds.
Run:  python3 gen-breeding.py   -> wav/*.wav (16-bit masters) + *.mp3 (96 kbps) + *.ogg (Vorbis q4), mono 44.1 kHz.

Overlap rule: many offspring play staggered, so every TONAL cue is tuned to the same C-major pentatonic
(C D E G A), all sounds are low-passed below ~7 kHz with soft (>=2 ms) attacks and no hard noise bursts, so stacked
copies blend into a chord / soft texture instead of beating or turning harsh."""
import sys; sys.dont_write_bytecode = True   # no __pycache__ next to gen-sounds.py
import numpy as np, subprocess, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('gs', os.path.join(HERE, '..', 'gen-sounds.py'))
gs = importlib.util.module_from_spec(spec); spec.loader.exec_module(gs)      # helpers only (its main is guarded)
SR, t_, place, osc, lp, hp, bp, write_wav = gs.SR, gs.t_, gs.place, gs.osc, gs.onepole_lp, gs.onepole_hp, gs.biquad_bp, gs.write_wav
WAV = os.path.join(HERE, 'wav'); os.makedirs(WAV, exist_ok=True)

# pentatonic note table (Hz)
N = {'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.0, 'A4': 440.0, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
     'G5': 783.99, 'A5': 880.0, 'C6': 1046.5, 'D6': 1174.66, 'E6': 1318.5, 'G6': 1568.0}

def env_ad(n, att, dec):   # soft attack (att s), exponential decay (dec s)
    t = np.arange(n) / SR; return (1 - np.exp(-t / att)) * np.exp(-t / dec)
def tone(f, dur, att=.003, dec=.08, harm=(1, .18, .05), bend=0.0, vib=0.0):
    """rounded sine 'pluck'. bend = relative pitch rise over the note (0.1 = +10 %), vib = vibrato depth."""
    t = t_(dur); u = t / dur
    fc = f * (1 + bend * (1 - (1 - u) ** 2)) * (1 + vib * np.sin(2 * np.pi * 6.5 * t))
    return env_ad(len(t), att, dec) * sum(a * osc(fc * (k + 1)) for k, a in enumerate(harm))
def soft_noise(rng, dur, fc, q, att, dec):
    t = t_(dur); return bp(rng.standard_normal(len(t)), fc, q) * env_ad(len(t), att, dec)
def water_bubble(f0, rng, gain=1.0, d=.025, rise=.8):   # soft bubble "plip" (sine with upward chirp)
    t = t_(d * 4); f = f0 * (1 + rise * t / (d * 4)); return gain * osc(f) * env_ad(len(t), .0015, d)

# ---------------- 1. heart: a soft rising two-note "bloom" (land) / a rising bubble "plip-plop" (water) ----------------
def heart(n1='E5', n2='A5'):
    b = np.zeros(int(SR * .32))
    place(b, .8 * tone(N[n1], .14, .004, .045, bend=.03), 0)
    place(b, tone(N[n2], .22, .004, .07, bend=.02, vib=.004), .075)
    return b
def heart_water(f1='E5', f2='A5', seed=101):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * .32))
    place(b, .8 * water_bubble(N[f1], rng, 1, .03, .5), 0)
    place(b, water_bubble(N[f2], rng, 1, .045, .45), .08)
    for k in range(3): place(b, water_bubble(rng.uniform(1800, 2600), rng, .12, .01), rng.uniform(.04, .2))
    return b

# ---------------- 2. egg: little "tok" of a shell set down + tiny wobble (land) / a round "blup" (water) ----------------
def egg(n='C5', seed=201):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * .22))
    body = tone(N[n], .2, .002, .03, harm=(1, .3, .12, .05))                   # hollow shell resonance
    knock = lp(soft_noise(rng, .03, 1800, 1.2, .0008, .005), 4000) * .6          # soft contact, no hard click
    place(b, body + np.pad(knock, (0, len(body) - len(knock))), 0)
    place(b, .25 * tone(N[n] * 1.5, .08, .002, .02), .06)                        # wobble re-tap (a fifth up)
    return b
def egg_water(n='G4', seed=211):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * .26))
    place(b, lp(water_bubble(N[n], rng, 1, .05, .35), 2500), 0)
    place(b, .35 * water_bubble(N[n] * 2, rng, 1, .02, .5), .05)
    return b

# ---------------- 3. hatch: two delicate shell cracks + a tiny "peep" (land) / cracks + a bubble burst (water) ----------------
def crack(rng, gain=1.0):
    t = t_(.025); x = bp(rng.standard_normal(len(t)), rng.uniform(2600, 3400), 2.5) * env_ad(len(t), .0006, .004)
    return lp(x, 6000) * gain
def hatch(peep='E6', seed=301):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * .48))
    place(b, crack(rng, .7), 0); place(b, crack(rng, .5), .07); place(b, crack(rng, .9), .15)
    place(b, .35 * tone(N['C5'], .1, .002, .02, harm=(1, .3)), .15)             # shell halves fall apart
    place(b, .9 * tone(N[peep], .16, .01, .06, harm=(1, .12), bend=.06, vib=.01), .23)   # the baby's "peep"
    return b
def hatch_water(n='E5', seed=311):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * .5))
    place(b, lp(crack(rng, .6), 3500), 0); place(b, lp(crack(rng, .8), 3500), .09)
    for k in range(7): place(b, water_bubble(N[n] * rng.choice([1, 1.5, 2]), rng, rng.uniform(.25, .55), rng.uniform(.012, .025)), .12 + .035 * k + rng.uniform(0, .01))
    return b

# ---------------- 4a. inch: caterpillar inching, 3 soft scrunch-steps ----------------
def inch(steps=3, gap=.28, pitch='G4', seed=401):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * (gap * steps + .2)))
    for k in range(steps):
        t = t_(.16); u = t / .16
        squish = lp(soft_noise(rng, .16, 900, .9, .02, .05), 1800) * .5           # body bunching up (soft, low)
        boing = tone(N[pitch] * (1 + .06 * k), .16, .01, .05, harm=(1, .15), bend=-.12) * .7   # tiny rubbery "bwip" down
        place(b, (squish + boing) * (1 - .12 * k), k * gap)
        place(b, .18 * tone(N['D6'], .05, .002, .012, harm=(1,)), k * gap + .1)   # little foot "pat"
    return b

# ---------------- 4b. swim: baby squid jets: 3 soft jet pulses + trailing bubbles ----------------
def swim(pulses=3, gap=.3, seed=501, f_lo=250, f_hi=1100):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * (gap * pulses + .25)))
    for k in range(pulses):
        d = .2; t = t_(d); u = t / d
        n = rng.standard_normal(len(t)); fc = f_lo + (f_hi - f_lo) * np.sin(np.pi * u ** .5)
        y = np.zeros(len(t)); s1 = s2 = 0.0
        for i, v in enumerate(n):
            a = np.exp(-2 * np.pi * fc[i] / SR); s1 = (1 - a) * v + a * s1; s2 = (1 - a) * s1 + a * s2; y[i] = s2
        y = hp(y, 120) * np.sin(np.pi * u ** .45) ** 1.5 * 4
        place(b, y * (1 - .15 * k), k * gap)
        for j in range(2): place(b, water_bubble(N[rng.choice(['C6', 'D6', 'E6', 'G6'])], rng, .22, .012), k * gap + .12 + .04 * j)
    return b

# ---------------- 5. grow: soft rising pentatonic shimmer (land: ends with a light wing flutter / water: bubbly) ----------------
def grow(notes=('C5', 'E5', 'G5', 'C6'), seed=601):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * 1.25))
    for k, n in enumerate(notes):
        place(b, (.55 + .12 * k) * tone(N[n], .45, .006, .16, harm=(1, .2, .06), vib=.003), .12 * k)
    place(b, .08 * gs.sparkle(.5, rng, 5, 4500, 6500, 1.0), .35)               # gentle glints (kept below 7 kHz)
    place(b, .45 * lp(gs.flutter(.36, 15.0, seed), 3000), .62)                   # new wings open: soft flutter
    return b
def grow_water(notes=('C5', 'E5', 'G5', 'C6'), seed=611):
    rng = np.random.default_rng(seed); b = np.zeros(int(SR * 1.25))
    for k, n in enumerate(notes):
        place(b, (.5 + .12 * k) * tone(N[n], .42, .006, .14, harm=(1, .15), vib=.004), .12 * k)
        place(b, .4 * water_bubble(N[n] * 2, rng, 1, .02, .6), .12 * k + .01)
    for j in range(8): place(b, water_bubble(rng.uniform(900, 2200), rng, rng.uniform(.12, .3), .015), .5 + .05 * j)
    return b

SOUNDS = {   # base names (Ken's play('<name>')) first; optional variants after
    'heart':          lambda: heart('E5', 'A5'),
    'egg':            lambda: egg('C5', 201),
    'hatch':          lambda: hatch('E6', 301),
    'inch':           lambda: inch(3, .28, 'G4', 401),
    'swim':           lambda: swim(3, .3, 501),
    'grow':           lambda: grow(('C5', 'E5', 'G5', 'C6'), 601),
    'heart-2':        lambda: heart('D5', 'G5'),
    'egg-2':          lambda: egg('D5', 202),
    'hatch-2':        lambda: hatch('D6', 302),
    'inch-2':         lambda: inch(3, .25, 'A4', 402),
    'swim-2':         lambda: swim(3, .27, 502, 300, 1300),
    'grow-2':         lambda: grow(('D5', 'G5', 'A5', 'D6'), 602),
    'heart-water':    lambda: heart_water('E5', 'A5', 101),
    'heart-water-2':  lambda: heart_water('D5', 'G5', 102),
    'egg-water':      lambda: egg_water('G4', 211),
    'egg-water-2':    lambda: egg_water('A4', 212),
    'hatch-water':    lambda: hatch_water('E5', 311),
    'hatch-water-2':  lambda: hatch_water('D5', 312),
    'grow-water':     lambda: grow_water(('C5', 'E5', 'G5', 'C6'), 611),
    'grow-water-2':   lambda: grow_water(('D5', 'G5', 'A5', 'D6'), 612),
}

if __name__ == '__main__':
    for name, fn in SOUNDS.items():
        x = gs.norm(fn().astype(float))
        x = gs.trim(x, thr_db=-50)                                   # no leading silence (0.5 ms pre-roll), tail trimmed at -50 dB
        x = gs.norm(gs.fade(gs.norm(x), fin=0.002, fout=0.03))       # 2 ms soft attack (no click when stacked), 30 ms tail fade
        wp = os.path.join(WAV, name + '.wav'); write_wav(wp, x)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-c:a', 'libmp3lame', '-b:a', '96k', os.path.join(HERE, name + '.mp3')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-fflags', '+bitexact', '-c:a', 'libvorbis', '-q:a', '4', os.path.join(HERE, name + '.ogg')], check=True)
        print(f'{name:15s} {len(x) / SR * 1000:6.0f} ms')
