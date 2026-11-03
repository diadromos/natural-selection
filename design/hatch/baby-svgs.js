/* Swappable baby creature drawings for the hatch step (design/hatch/hatch.js).
   Each entry is a function (tint) -> SVG markup string. tint = {body: css color, spots?: css color}.
   body is the child's own gene color (pages pass it in); outlines, eyes and legs are fixed dark ink, so the
   tint is the only gene-driven color. Replace either function to restyle the babies; keep the root <svg>
   and its viewBox aspect (the hatch code sizes the baby by width and orients it by `heading`).
   heading: direction the drawing faces, in degrees (0 = right, -90 = up). */
(function(){
const INK='#1a1a1a';
window.BABY_SVGS={
 // Caterpillar, facing right, 6 body segments + head. viewBox 64 x 30.
 caterpillar:{heading:0,aspect:30/64,svg:t=>{
  const seg=[[10,17,6],[18,15,6.6],[26,14,7],[34,14,7],[42,15,6.8],[50,13,7.6]];
  const legs=seg.slice(0,5).map(([x,y,r])=>`<path d='M${x-2} ${y+r-1} l-1 4 M${x+2} ${y+r-1} l1 4' stroke='${INK}' stroke-width='1.4' stroke-linecap='round'/>`).join('');
  const body=seg.map(([x,y,r],i)=>`<circle class='seg seg${i}' cx='${x}' cy='${y}' r='${r}' fill='${t.body}' stroke='${INK}' stroke-width='1.3'/>`).join('');
  const spots=t.spots?seg.slice(0,5).map(([x,y,r],i)=>`<circle cx='${x+(i%2?1.5:-1.5)}' cy='${y-r*.35}' r='${r*.38}' fill='${t.spots}'/>`).join(''):'';
  return `<svg viewBox='0 0 64 30' aria-hidden='true'>${legs}${body}${spots}<circle cx='53' cy='11' r='1.6' fill='${INK}'/><circle cx='53.5' cy='10.5' r='.5' fill='#fff'/><path d='M55.5 16 q1.5 1.2 3 0' stroke='${INK}' stroke-width='1' fill='none' stroke-linecap='round'/><path d='M49 6 q-1 -4 -3 -5 M53 6 q1 -4 3 -5' stroke='${INK}' stroke-width='1.1' fill='none' stroke-linecap='round'/></svg>`}},
 // Baby squid, mantle up (facing up), big eyes, short tentacles. viewBox 40 x 50.
 squid:{heading:-90,aspect:50/40,svg:t=>
  `<svg viewBox='0 0 40 50' aria-hidden='true'><path class='mantle' d='M20 2 C30 2 35 10 34 20 C33 26 30 29 29 31 L11 31 C10 29 7 26 6 20 C5 10 10 2 20 2 Z' fill='${t.body}' stroke='${INK}' stroke-width='1.6' stroke-linejoin='round'/>`+
  `<g class='arms' fill='${t.body}' stroke='${INK}' stroke-width='1.4' stroke-linejoin='round'><path d='M11 30 C9 37 7 42 8 46 C10 47 12 42 14 31Z'/><path d='M15 31 C15 38 14 44 16 47 C18 46 18 39 18.5 31Z'/><path d='M21.5 31 C22 39 22 46 24 47 C26 44 25 38 25 31Z'/><path d='M26 31 C28 42 30 47 32 46 C33 42 31 37 29 30Z'/></g>`+
  `<ellipse cx='14.5' cy='25' rx='3' ry='3.8' fill='${INK}'/><ellipse cx='25.5' cy='25' rx='3' ry='3.8' fill='${INK}'/><circle cx='14' cy='24' r='1' fill='#fff'/><circle cx='25' cy='24' r='1' fill='#fff'/></svg>`}
};
})();
