# Natural Selection: Camouflage — A Field Guide

*A demonstration by Ken Thompson, in four pages.*

## What the Demonstration Shows

There is, in every patch of ground and every reach of open water, a quiet and unending trial. The creature that stands out against its surroundings is seen, and what is seen is eaten. The creature that blends in lives a little longer, long enough to breed, and its children inherit the coloring that hid it.

This app stages that trial. A **population of 32 creatures** is laid out in a grid of 4 rows by 8 columns, set against a colored **background**. Each generation:

1. **A predator eats the 8 most visible creatures**, the ones whose coloring lies farthest from the background. They are marked with a **red circle and white fangs**.
2. **8 more die at random**, whatever their color, because fortune keeps no ledger of merit. They are marked with a **yellow skull and crossbones**.
3. **The 16 survivors are shuffled and paired.** Each pair has four children, so the population is back to 32. Each child takes one gene from one parent and the other gene from the other parent (what those genes are depends on the page; see below).
4. **Mutation** (if it is on): each child has a 30% chance of a small random change to its genes.

Over the generations the population drifts toward the background color. Nobody steers it; selection does the work. That is the whole lesson.

## The Four Pages

All four pages live in `/workspace/natural-selection/` and link to one another through the links near the foot of each page.

| Page | Creatures | Genes | Distance measured as |
|---|---|---|---|
| `index.html` (Color) | Butterflies in full color | 24-bit RGB color, shown as `#RRGGBB`. Child takes the **hue** of one parent and the **saturation and value** of the other. | Straight-line distance in RGB space (0 to about 441.7) |
| `mono.html` (Monochrome) | Gray butterflies | One 32-bit number (`00000000`–`FFFFFFFF`) drawn as a shade of gray. Child takes the **high 16 bits** of one parent and the **low 16 bits** of the other. | Absolute difference of the 32-bit numbers, shown in hex and as a percentage |
| `spots.html` (Spots) | White butterflies with gray spots | Two 32-bit genes: a **spot shade** (base gray of the spots) and a **spot pattern** (seed for how many spots, their sizes, positions and per-spot shade offsets). Child takes the shade of one parent and the pattern of the other. | Difference between the wing's area-weighted average gray and the background gray, out of 255 and as a percentage |
| `squirts.html` (Squirts) | Squid in full color | Same as the Color page: hue from one parent, saturation and value from the other. | RGB distance, as on the Color page |

On the Spots page a mutation changes the shade gene (70% chance) and flips 1–3 random bits of the pattern gene (70% chance). On the Monochrome page it shifts the 32-bit gene by a small amount. On Color and Squirts it nudges hue by up to ±20° and saturation and value by up to ±0.075.

## Getting Under Way

1. Serve the folder (it is served now at `http://127.0.0.1:8766/`) and open `index.html`, or whichever page you want.
2. On load, the app gives you a random background and 32 random creatures, at **Generation 0**.
3. Press **Next generation** and watch it happen: the marks appear for about one and a half seconds, then the survivors' children take their places.
4. Once you have seen the mechanism, set a number in the box and press **Run N generations** to go much faster.
5. Watch the **Avg distance from background** number below the grid fall.

## The Controls

### On every page

- **Next generation** (`#step`): Runs one generation with the marks shown. The eaten are marked with red fangs, the unlucky with a yellow skull, for 1.5 seconds; then the grid is redrawn with the new brood and the generation count goes up by one. Wait for the redraw before pressing again.
- **Generation count box** (`#n`): A number field, set to **10** by default (minimum 1). It sets how many generations the next button runs. An empty or zero value counts as 1.
- **Run N generations** (`#multi`): Runs that many generations at once with no marks and no pause, then shows only the final population. Very large numbers can make the page pause for a moment, especially on the Spots page.
- **Reset** (`#reset`): Starts over: a new random background, 32 new random creatures, generation back to 0.
- **Mutation** (`#mut`): A checkbox, **on** by default. When on, each child has a 30% chance of a small random change to its genes. When off, children only recombine their parents' genes, so the population can never get closer than the best mix of genes already present.
- **Version links**: Links to the other pages (Color, Monochrome, Spots, Squirts). Each page starts fresh; nothing carries over.

### Spots page only

- **Background gray slider** (`#bgs`): A range from 0 (black) to 255 (white). Dragging it changes the background gray **right away, without resetting** the population or generation count, so you can change the creatures' environment mid-run and watch them adapt.
- **Random background** (`#rbg`): Picks a new random gray background straight away, also without a reset. The slider moves to match.

### Squirts page only

- **Hue slider** (`#hue`, labelled *Hue*): A range from 0 to 360 over a rainbow track. It sets the background's hue live, without a reset.
- **Value slider** (`#val`, labelled *Value*): A range from 0 to 100. Its track goes from **white at 0**, through the **full hue at 50**, to **black at 100**; the track updates to show the current hue. It changes the background live, without a reset.

On Reset, both sliders move to match the new random background.

## What You See

- **Background label** (`#bglabel`): Shows `Background: ` followed by the background gene: `#RRGGBB` on the Color and Squirts pages, and the 32-bit gene as eight hex digits on the Monochrome and Spots pages.
- **The grid** (`#grid`): The background color itself, with the 32 creatures (`#grid > div.org`) arranged in 4 rows of 8. Under each creature is its **% match to the background**, rounded to one decimal place, where 100% means identical. The label text turns black or white, whichever is easier to read against the background. The match is computed per page:
  - **Color and Squirts:** 100 × (1 − *d* / (255 × √3)), where *d* is the straight-line (Euclidean) distance between the creature's and the background's RGB colors.
  - **Monochrome:** 100 × (1 − |gene − background gene| / `0xFFFFFFFF`).
  - **Spots:** a single number, 100 × (1 − |area-weighted average wing gray − background gray| / 255).
- **Statistics line** (`#stats`): `Generation N | Avg distance from background: X`. **Lower is better camouflage.** The Monochrome page shows it in hex and as a percentage; the Spots page shows it out of 255 and as a percentage.

## What to Watch For

- **The fall of the distance figure.** It usually drops quickly over the first few dozen generations, then levels off as the creatures get close to the background.
- **The fangs at work.** In single steps, notice that the fanged ones are always the most conspicuous, while the skulls fall anywhere, sometimes on the best-hidden creatures. Selection works on averages, not on individuals.
- **Mutation turned off.** Reset, uncheck Mutation, and run a hundred generations. The population gets stuck at the best combination its starting genes allow. Turn mutation back on and it starts creeping closer again.
- **A change of scene.** On the Spots or Squirts pages, let a population adapt, then move the background slider. The distance figure jumps, and the population has to adapt again.
- **Spots that hide by average.** On the Spots page the predator judges only the overall average gray of the wings, so very different spot patterns can be equally well hidden.

## Tips

- Use **Next generation** to see how it works, and **Run N generations** to see the result over time.
- Start with N around 10–50; raise it once you know how fast your browser handles it.
- A mid-gray or mid-tone background makes the convergence easiest to see; on near-black or near-white backgrounds the creatures may already be close.
- The demo is random: two runs with the same settings will go differently. Run it a few times before drawing conclusions.
- Nothing is saved. Reloading the page is the same as pressing Reset.
