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
| [`mono.html`](mono.html) (Monochrome) | Gray moths, drawn as a peppered moth (*Biston betularia*; [`design/moth.svg`](design/moth.svg)) | One 32-bit number (`00000000`–`FFFFFFFF`), drawn as gray | High 16 bits from one parent; low 16 bits from the other | Gene shifted by up to ±2²⁶ |
| [`spots.html`](spots.html) (Spots) | White moths with gray spots, using the same peppered moth drawing | Two 32-bit genes: **spot shade** (base gray) and **spot pattern** (seed for 4–12 mirrored spots: positions, sizes, and per-spot shade offsets of up to ±70 gray levels). Spot centers are redrawn until they land inside the moth outline. | Shade from one parent; pattern from the other | 70% chance to shift the shade by up to ±2²⁶; 70% chance to flip 1–3 random bits of the pattern |
| [`squirts.html`](squirts.html) (Squirts) | Full-color squid | 24-bit RGB color (same as Color) | Same as Color | Same as Color |

Extra controls:

- **Spots:** a **Background gray** slider (`#bgs`, 0–255) and a **Random background** button (`#rbg`). Both change the background live, without resetting the population.
- **Squirts:** **Hue** (`#hue`, 0–360, rainbow track) and **Value** (`#val`, 0–100: white at 0, full hue at 50, black at 100) sliders. Both change the background live, without a reset.

## How to use it

| Control | What it does |
|---|---|
| **Next generation** | Runs one generation. The eaten get a red bird outline (a red fish on Squirts) and the randomly killed get a yellow skull and crossbones. After 1.5 s the survivors' children replace the grid. |
| **N** (number box, default 10) | How many generations **Run N generations** runs. |
| **Run N generations** | Runs N generations at once with no marks, then shows the result. |
| **Reset** | Starts over with a new random background, a new random population, and generation 0. |
| **Mutation** (on by default) | Turns mutation on or off. |
| Version links | Switch pages. Each page starts fresh. |

**% match labels.** Under each creature is its match to the background, rounded to one decimal place. **100% means identical.**

- Color and Squirts: `100 × (1 − d / (255·√3))`, where `d` is the Euclidean RGB distance.
- Monochrome: `100 × (1 − |gene − bgGene| / 0xFFFFFFFF)`.
- Spots: `100 × (1 − |area-weighted average moth gray − background gray| / 255)`, averaged over the wings and body.

**Background label.** `Background: #RRGGBB` on Color and Squirts. On Monochrome and Spots it shows the background's 32-bit gene as eight hex digits.

**Stats line.** `Generation N | Avg distance from background: X`. **Lower is better camouflage.** On Color and Squirts, X is the average RGB distance (0 to about 441.7). On Monochrome it is shown in hex plus a percentage, and on Spots as `X / 255` plus a percentage.

## How selection, breeding, and mutation work

Each generation, on every page:

1. **Predation:** the creatures are ranked by distance from the background, and the **8 most distant** are eaten.
2. **Random death:** **8 more** of the remaining 24 die at random.
3. **Breeding:** the **16 survivors** are shuffled into 8 pairs. Each pair (A, B) has **4 children**: two take gene 1 from A and gene 2 from B, and two the other way around. That brings the population back to 32, and it is shuffled again before display.
4. **Mutation:** if **Mutation** is checked, each child has a **30% chance** of a small random change (see the table above).

On the Spots page the predator judges only the **area-weighted average gray** of the moth. That average is sampled over the whole moth outline (wings and body, but not the legs and antennae), using the topmost spot (or white) at each point. Each spot's center is drawn on the left half (y 20–62) and redrawn, up to 50 tries, until it falls inside the moth outline; the spot is then mirrored onto the right half. Very different patterns can therefore be equally well hidden.

## The real-world case: Kettlewell's peppered moths

The demo is a toy version of one of the best-known field studies of natural selection. In the 1950s H. B. D. Kettlewell ran mark-release-recapture experiments on the peppered moth, *Biston betularia*. He compared the pale *typica* form with the black *carbonaria* form in a polluted wood near Birmingham (the Christopher Cadbury Bird Reserve, near Rubery) and an unpolluted, lichen-covered wood in Dorset (Deanend Wood). In each wood the form that showed up against the bark came back in smaller numbers. In Birmingham in 1953 he recaptured 123 of 447 marked *carbonaria* (27.5%) but only 18 of 137 *typica* (about 13%) [[1]](#references). In Dorset in 1955 it went the other way: 62 of 496 *typica* (12.5%) against 30 of 473 *carbonaria* (6.3%) [[2]](#references). He and the ethologist Niko Tinbergen also watched birds take the moths from tree trunks, and Tinbergen filmed them. In Dorset, five bird species were seen to eat 164 *carbonaria* and 26 *typica*. In Birmingham, a family of redstarts took 43 *typica* and 15 *carbonaria* [[2]](#references).

| ![Pale peppered moth, form typica: white wings finely speckled with black, resting on a light textured surface](docs/images/peppered-moth-typica.jpg) | ![Black peppered moth, form carbonaria: uniformly sooty-black wings and body, resting on a light textured surface](docs/images/peppered-moth-carbonaria.jpg) |
|:---:|:---:|
| *Biston betularia* f. *typica*, the pale, speckled form | *Biston betularia* f. *carbonaria*, the black (melanic) form |

<sub>Photos: [Olaf Leillinger](https://de.wikipedia.org/wiki/Benutzer:Olei) (Wikimedia Commons user Olei), cropped by Chiswick Chap, via Wikimedia Commons: [*typica*](https://commons.wikimedia.org/wiki/File:Biston.betularia.7200.jpg) and [*carbonaria*](https://commons.wikimedia.org/wiki/File:Biston.betularia.f.carbonaria.7209.jpg). Licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); resized to 600 px wide for this guide.</sub>

**How the demo maps onto it.** On the Monochrome and Spots pages the creatures are drawn as peppered moths ([`design/moth.svg`](design/moth.svg)). The predator here plays the part of the birds: it removes the creatures that differ most from the background, and over the generations the population shifts toward the background color. **Where it simplifies:** the predator kills exactly 8 creatures per generation, ranked strictly by distance, and exactly 8 more die at random; real predation is probabilistic and varies from year to year. Color in the demo comes from several recombined parts (hue versus saturation and value, or high versus low bits), and that behaves much like blending inheritance. In the real moth, *carbonaria* is controlled by a single dominant allele at one locus [[3]](#references), caused by a transposable-element insertion in the gene *cortex* [[4]](#references). The demo also has no migration, and its environment never changes on its own. The background stays fixed until you press Reset or move a slider (Spots and Squirts only).

**Criticism and confirmation.** Kettlewell's methods were later questioned. Moths were placed on tree trunks, which were argued to be unusual resting sites, and they were released at much higher densities than occur in the wild [[3]](#references). Judith Hooper's 2002 book *Of Moths and Men* went further, accusing Kettlewell of fraud [[5]](#references); Cook et al. call that claim groundless [[3]](#references). To answer the critics, Michael Majerus of Cambridge ran a large experiment from 2001 to 2007 in a 1-hectare garden near Coton, Cambridgeshire. He released 4,864 moths at low densities onto natural resting sites, and he recorded where wild moths actually rest: 35% of 135 were on trunks. Majerus died in 2009 before publishing the work. Cook, Grant, Saccheri and Mallet analyzed and published it in 2012. They found significant bird predation against *carbonaria*, with a daily selection coefficient of about 0.09, enough to explain the decline of melanic moths since industrial pollution fell [[3]](#references).

For the fuller account, see [docs/README.md](docs/README.md#the-real-world-case-kettlewells-peppered-moths).

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
├── index.html                # Color version (full-color butterflies)
├── mono.html                 # Monochrome version (gray peppered moths, 32-bit gray genes)
├── spots.html                # Spots version (white peppered moths, gray spots)
├── squirts.html              # Squirts version (full-color squid)
├── README.md                 # This file
├── LICENSE                   # CC BY 4.0 (photos in docs/images/ excepted)
├── .nojekyll                 # Tells GitHub Pages to serve the files as-is
├── design/
│   ├── mobile.css            # Shared responsive stylesheet linked by all four pages
│   ├── MARKUP-NOTES.md       # Notes on how the pages hook into mobile.css
│   ├── moth.svg              # Peppered moth (Biston betularia) drawing, inlined into mono.html and spots.html
│   ├── moth-gen.py           # Python script that generated the moth paths
│   ├── MOTH-NOTES.md         # Notes for Ken on using the moth drawing
│   ├── moth-preview.html     # Preview page for the moth on several fills
│   ├── moth-preview.png      # Rendered moth preview
│   ├── moth-vs-photo.png     # Moth drawing compared with a photo of the real moth
│   ├── mockup-*.png          # Mobile design mockups (index, spots, squirts)
│   ├── mockup-desktop-*.png  # Desktop design mockups (index, spots, squirts)
│   └── shots/                # Screenshots of each page at 390px and desktop widths, before and after % labels and the moth
├── docs/
│   ├── README.md             # Full user guide
│   ├── tooltips.json         # Tooltip text for each UI element, by page
│   └── images/
│       ├── peppered-moth-typica.jpg      # Photo of the pale form (CC BY-SA 3.0)
│       ├── peppered-moth-carbonaria.jpg  # Photo of the dark form (CC BY-SA 3.0)
│       └── ATTRIBUTION.md                # Photo credits and license
├── squirt.svg                # Standalone squid artwork (earlier shape; squirts.html inlines its own)
├── squirt-preview.html       # Standalone preview of an earlier squid shape
└── *.png                     # Development screenshots (final-state, overlay-screenshot, squirt-preview3–5)
```

Each page is self-contained: its HTML, inline CSS, and inline JavaScript are all in one file, and the only shared asset is `design/mobile.css`.

## License

This project is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may share and adapt it for any purpose, as long as you give credit. See [LICENSE](LICENSE).

The two peppered moth photos in `docs/images/` are an exception: they are by Olaf Leillinger via Wikimedia Commons and remain under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). See [docs/images/ATTRIBUTION.md](docs/images/ATTRIBUTION.md).

## References

1. Kettlewell, H. B. D. (1955). Selection experiments on industrial melanism in the Lepidoptera. *Heredity*, 9(3), 323–342. [doi:10.1038/hdy.1955.36](https://doi.org/10.1038/hdy.1955.36)
2. Kettlewell, H. B. D. (1956). Further selection experiments on industrial melanism in the Lepidoptera. *Heredity*, 10(3), 287–301. [doi:10.1038/hdy.1956.28](https://doi.org/10.1038/hdy.1956.28)
3. Cook, L. M., Grant, B. S., Saccheri, I. J., & Mallet, J. (2012). Selective bird predation on the peppered moth: the last experiment of Michael Majerus. *Biology Letters*, 8(4), 609–612. [doi:10.1098/rsbl.2011.1136](https://doi.org/10.1098/rsbl.2011.1136)
4. van't Hof, A. E., Campagne, P., Rigden, D. J., Yung, C. J., Lingley, J., Quail, M. A., Hall, N., Darby, A. C., & Saccheri, I. J. (2016). The industrial melanism mutation in British peppered moths is a transposable element. *Nature*, 534(7605), 102–105. [doi:10.1038/nature17951](https://doi.org/10.1038/nature17951)
5. Hooper, J. (2002). *Of Moths and Men: Intrigue, Tragedy and the Peppered Moth*. London: Fourth Estate. (US edition: *Of Moths and Men: An Evolutionary Tale*. New York: W. W. Norton.)
