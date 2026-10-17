# Markup notes for mobile.css (minimal)
1. In each page's <head>, AFTER the existing <style> block:
   <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
   <link rel="stylesheet" href="design/mobile.css">
2. Nothing else is required. The CSS overrides the inline styles it needs to (#n width, #bglabel font, slider widths, link colors) with !important, and it never touches #grid's background or color, .org, or any creature SVG fill.
3. Optional cleanup: remove the inline `style="width:60px"` on #n, the `style="color:#9cf"` on nav links, and the inline font on #bglabel. Also remove the `|` separators in the nav <p> (they're already hidden with font-size:0).
4. Optional: add class="controls" to the control <div>s and class="nav" to the links <p>. The CSS currently targets them structurally (`body>h2+div`, `body>p:has(a)`), so if the structure changes, those classes keep the styling stable.
5. squirts.html: #hue and #val already sit inside <label>Hue …</label> and <label>Value …</label>, so no change is needed. The CSS keeps their inline/JS gradient backgrounds visible.
6. The grid becomes 4 columns × 8 rows at phone width through grid-template-columns. The JS doesn't need to change.
