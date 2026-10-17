# Predator "eaten" mark replacement

The yellow random-death skull is untouched. Only the SVG inside `<div class='mark'>` on the `marks[i]=='eaten'` branch changes. All strings use single quotes only (no backticks, no `${}`), so they drop straight into the template literal.

The OLD substring is identical in all four pages and occurs exactly once in each (verified).

## OLD (index.html, mono.html, spots.html, squirts.html)
```
<svg viewBox='0 0 80 80' width='80' height='80'><circle cx='40' cy='40' r='34' fill='none' stroke='#e00' stroke-width='3'/><path d='M14 22 Q40 34 66 22' stroke='#e00' stroke-width='2.5' fill='none'/><path d='M24 26 L29 50 L34 30 M46 30 L51 50 L56 26' fill='none' stroke='#fff' stroke-width='2.5' stroke-linejoin='round'/></svg>
```

## NEW for index.html, mono.html, spots.html: red finch outline (design/predator-bird.svg)
```
<svg viewBox='0 0 80 80' width='80' height='80'><g fill='none' stroke='#000' stroke-opacity='.55' stroke-width='6.5' stroke-linejoin='round' stroke-linecap='round'><path d='M62 22 C58 13 46 13 43 22 C38 30 29 36 21 45 L7 54 L13 57 L8 63 L24 56 C33 62 49 61 57 50 C61 44 63 39 63 35 M62 22 L74 29 L63 35 M64 28.8 L71 29.2 M45 31 C37 34 29 42 25 51 C35 50 44 45 49 38 M38 60 L36 69 M46 58 L46 69 M28 70 L56 70'/><circle cx='53.5' cy='25' r='3.6' fill='#000' fill-opacity='.55' stroke='none'/></g><g fill='none' stroke='#e00' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'><path d='M62 22 C58 13 46 13 43 22 C38 30 29 36 21 45 L7 54 L13 57 L8 63 L24 56 C33 62 49 61 57 50 C61 44 63 39 63 35 M62 22 L74 29 L63 35 M64 28.8 L71 29.2 M45 31 C37 34 29 42 25 51 C35 50 44 45 49 38 M38 60 L36 69 M46 58 L46 69 M28 70 L56 70'/><circle cx='53.5' cy='25' r='2' fill='#e00' stroke='none'/></g></svg>
```

## NEW for squirts.html: red perch outline (design/predator-fish.svg)
```
<svg viewBox='0 0 80 80' width='80' height='80'><g fill='none' stroke='#000' stroke-opacity='.55' stroke-width='6.5' stroke-linejoin='round' stroke-linecap='round'><path d='M8 41 C13 30 26 24 40 24 C52 24 60 31 64 38 L75 28 L71 40.5 L75 53 L64 43 C59 50 48 56 36 56 C22 56 12 50 8 41 M8 41 L14 42 M24 30 C28 36 28 45 24 51 M27 26 L29 15 L33 25 L36 13 L39 24 L42 14.5 L45 24.5 M48 25 C51 16 58 18 60 31 M30 43 C34 47 38 47 41 44 M30 55 L27 63 L36 56 M47 54 C49 61 55 61 59 49'/><circle cx='17' cy='36' r='3.6' fill='#000' fill-opacity='.55' stroke='none'/></g><g fill='none' stroke='#e00' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'><path d='M8 41 C13 30 26 24 40 24 C52 24 60 31 64 38 L75 28 L71 40.5 L75 53 L64 43 C59 50 48 56 36 56 C22 56 12 50 8 41 M8 41 L14 42 M24 30 C28 36 28 45 24 51 M27 26 L29 15 L33 25 L36 13 L39 24 L42 14.5 L45 24.5 M48 25 C51 16 58 18 60 31 M30 43 C34 47 38 47 41 44 M30 55 L27 63 L36 56 M47 54 C49 61 55 61 59 49'/><circle cx='17' cy='36' r='2' fill='#e00' stroke='none'/></g></svg>
```

Notes
- Each mark is drawn twice: first a dark halo (#000, 55% opacity, 6.5px stroke), then the red outline (#e00, 3px, round joins/caps). The existing `.mark{filter:drop-shadow(0 0 3px #000)}` adds extra separation. There's no body fill, so each mark is an outline only.
- The eye is a small filled red dot with a halo, so it stays legible at 80px.
- The `design/*.svg` files are the same markup plus `xmlns` so they open standalone; use the strings above (without xmlns) in the pages.
