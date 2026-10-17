# Natural Selection: Camouflage

**Live demo:** https://diadromos.github.io/natural-selection/

A small, dependency-free browser demo of natural selection. Thirty-two creatures sit on a colored background; a predator eats the ones that stand out, chance takes a few more, and the survivors breed. Watch long enough and the population fades into its surroundings.

> Against a plain field of color, the conspicuous are found out and the inconspicuous endure. No hand guides the change. Generation by generation, the creatures take on the color of the ground they live on, as though the world itself had colored them.

For the full user guide (every control, what to watch for, and tips), see **[docs/README.md](docs/README.md)**.

## What it demonstrates

- **Selection:** the predator always takes the creatures farthest from the background color, so better-camouflaged creatures are more likely to survive.
- **Chance:** an equal number die at random, whatever their color, so luck and fitness both play a part.
- **Inheritance and recombination:** each child mixes genes from two parents.
- **Mutation:** small random changes add variation that selection can act on. Turn it off and the population stalls at the best mix of its starting genes.

## The four versions

| Page | Creatures | Genes | Child inherits | Mutation (30% of children, when on) |
|---|---|---|---|---|
| [`index.html`](index.html) (Color) | Full-color butterflies | 24-bit RGB color | Hue from one parent; saturation and value from the other | Hue ±20°, saturation and value ±0.075 each |
| [`mono.html`](mono.html) (Monochrome) | Gray butterflies | One 32-bit number (`00000000`–`FFFFFFFF`), drawn as gray | High 16 bits from one parent; low 16 bits from the other | Gene shifted by up to ±2²⁶ |
| [`spots.html`](spots.html) (Spots) | White butterflies with gray spots | Two 32-bit genes: **spot shade** (base gray) and **spot pattern** (seed for 4–12 mirrored spots: positions, sizes, and per-spot shade offsets of up to ±70 gray levels) | Shade from one parent; pattern from the other | 70% chance to shift the shade by up to ±2²⁶; 70% chance to flip 1–3 random bits of the pattern |
| [`squirts.html`](squirts.html) (Squirts) | Full-color squid | 24-bit RGB color (same as Color) | Same as Color | Same as Color |

Extra controls:

- **Spots:** a **Background gray** slider (`#bgs`, 0–255) and a **Random background** button (`#rbg`). Both change the background live, without resetting the population.
- **Squirts:** **Hue** (`#hue`, 0–360, rainbow track) and **Value** (`#val`, 0–100: white at 0, full hue at 50, black at 100) sliders. Both change the background live, without a reset.

## How to use it

| Control | What it does |
|---|---|
| **Next generation** | Runs one generation. The eaten get a red circle with fangs and the randomly killed get a yellow skull and crossbones. After 1.5 s the survivors' children replace the grid. |
| **N** (number box, default 10) | How many generations **Run N generations** runs. |
| **Run N generations** | Runs N generations at once with no marks, then shows the result. |
| **Reset** | Starts over with a new random background, a new random population, and generation 0. |
| **Mutation** (on by default) | Turns mutation on or off. |
| Version links | Switch pages. Each page starts fresh. |

**% match labels.** Under each creature is its match to the background, rounded to one decimal place. **100% means identical.**

- Color and Squirts: `100 × (1 − d / (255·√3))`, where `d` is the Euclidean RGB distance.
- Monochrome: `100 × (1 − |gene − bgGene| / 0xFFFFFFFF)`.
- Spots: `100 × (1 − |area-weighted average wing gray − background gray| / 255)`.

**Background label.** `Background: #RRGGBB` on Color and Squirts. On Monochrome and Spots it shows the background's 32-bit gene as eight hex digits.

**Stats line.** `Generation N | Avg distance from background: X`. **Lower is better camouflage.** On Color and Squirts, X is the average RGB distance (0 to about 441.7). On Monochrome it is shown in hex plus a percentage, and on Spots as `X / 255` plus a percentage.

## How selection, breeding, and mutation work

Each generation, on every page:

1. **Predation:** the creatures are ranked by distance from the background, and the **8 most distant** are eaten.
2. **Random death:** **8 more** of the remaining 24 die at random.
3. **Breeding:** the **16 survivors** are shuffled into 8 pairs. Each pair (A, B) has **4 children**: two take gene 1 from A and gene 2 from B, and two the other way around. That brings the population back to 32, and it is shuffled again before display.
4. **Mutation:** if **Mutation** is checked, each child has a **30% chance** of a small random change (see the table above).

On the Spots page the predator judges only the **area-weighted average gray** of the wings. That average is sampled over the wing shape, using the topmost spot (or white) at each point. Very different patterns can therefore be equally well hidden.

## Running locally

These are plain static files: no build step, no dependencies, no network requests.

```sh
git clone https://github.com/USERNAME/REPO.git
cd REPO
python3 -m http.server 8000
# then open http://localhost:8000/index.html
```

Or just open `index.html` directly in a browser. The pages also work from `file://`.

To publish, enable **GitHub Pages** for the repository (Settings → Pages → deploy from the default branch, root folder). `index.html` is the landing page.

## File layout

```
.
├── index.html            # Color version (full-color butterflies)
├── mono.html             # Monochrome version (32-bit gray genes)
├── spots.html            # Spots version (white butterflies, gray spots)
├── squirts.html          # Squirts version (full-color squid)
├── README.md             # This file
├── design/
│   ├── mobile.css        # Shared responsive stylesheet linked by all four pages
│   ├── MARKUP-NOTES.md   # Notes on how the pages hook into mobile.css
│   ├── mockup-*.png      # Design mockups (index, spots, squirts)
│   └── shots/            # 390px-wide screenshots of each page, before and after % labels
├── docs/
│   ├── README.md         # Full user guide
│   └── tooltips.json     # Tooltip text for each UI element, by page
├── squirt.svg            # Standalone squid artwork (earlier shape; squirts.html inlines its own)
├── squirt-preview.html   # Standalone preview of an earlier squid shape
└── *.png                 # Development screenshots (final-state, overlay-screenshot, squirt-preview3–5)
```

Each page is self-contained: its HTML, inline CSS, and inline JavaScript are all in one file, and the only shared asset is `design/mobile.css`.
