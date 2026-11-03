/* Breeding hearts + eggs (feature branch breeding-hearts).
   After the predator run and the stamps, every creature that breeds this generation gets a small heart
   in the top-right corner of its cell; shortly after each heart pops, a small cream egg appears over it.
   Overlays live inside each .org cell (inside #grid), like the stamps, so they scroll with the grid.
   Never touches creature colors: the heart and egg are separate elements with their own fixed fills.
   Placeholder strings (final wording from Joseph Conrad): aria-label "Parent", aria-label "Egg". */
(function(){
const HEART={stagger:40,pop:320,eggDelay:380,eggPop:280,hold:600};
const EGG_LAND=Math.round(HEART.eggPop*.6); // egg 'tok' when it lands: the 60% keyframe of eggPop (168 ms) -> 40k+548 ms (SOUND-NOTES.md)
const STR={parent:'Parent',egg:'Egg'};
const css=`
#grid .org .breed{position:absolute;top:2%;right:2%;width:26%;aspect-ratio:1/1;pointer-events:none;z-index:3}
#grid .org .breed svg{position:absolute;inset:0;width:100%!important;height:100%!important;max-height:none!important;filter:drop-shadow(0 0 1.5px rgba(0,0,0,.6))}
#grid .org .breed .egg{position:absolute;left:30%;top:40%;width:40%;height:50%;pointer-events:none}
#grid .org .breed .egg svg{filter:drop-shadow(0 0 1px rgba(0,0,0,.55))}
@keyframes heartPop{0%{transform:scale(0);opacity:0}55%{transform:scale(1.35);opacity:1}75%{transform:scale(.9)}100%{transform:scale(1)}}
@keyframes eggPop{0%{transform:translateY(-35%) scale(.2);opacity:0}60%{transform:translateY(4%) scale(1.12);opacity:1}100%{transform:none;opacity:1}}
#grid .org .breed.anim .heart{transform-origin:50% 60%;animation:heartPop ${HEART.pop}ms cubic-bezier(.3,1.4,.6,1) both;animation-delay:var(--d,0ms)}
#grid .org .breed.anim .egg{transform-origin:50% 80%;animation:eggPop ${HEART.eggPop}ms cubic-bezier(.3,1.4,.6,1) both;animation-delay:calc(var(--d,0ms) + ${HEART.eggDelay}ms)}
`;
const st=document.createElement('style');st.id='breed-hearts-css';st.textContent=css;document.head.appendChild(st);
const heartSVG=`<svg class="heart" viewBox="0 0 32 30" aria-hidden="true"><path d="M16 28 C7 21 1.5 15.5 1.5 9.5 C1.5 4.8 5 1.5 9.2 1.5 C12.2 1.5 14.6 3.2 16 5.6 C17.4 3.2 19.8 1.5 22.8 1.5 C27 1.5 30.5 4.8 30.5 9.5 C30.5 15.5 25 21 16 28 Z" fill="#ff3d7f" stroke="#7a0f33" stroke-width="1.6" stroke-linejoin="round"/><path d="M7 7.5 C8 5.6 10 5 11.6 5.4" stroke="#fff" stroke-opacity=".75" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>`;
const eggSVG=`<svg viewBox="0 0 20 26" aria-hidden="true"><path d="M10 1.5 C15 1.5 18.5 9 18.5 15 C18.5 21 14.8 24.5 10 24.5 C5.2 24.5 1.5 21 1.5 15 C1.5 9 5 1.5 10 1.5 Z" fill="#fbf4e2" stroke="#7d6b4a" stroke-width="1.4"/><ellipse cx="7" cy="9.5" rx="1.8" ry="3" fill="#fff" opacity=".8"/></svg>`;
/* breedMarks(grid, idx, {reduced}) -> Promise resolved when every heart and egg has finished appearing.
   idx = indices (DOM order of .org cells) of the creatures that breed. */
window.breedMarks=function(grid,idx,opt){opt=opt||{};const rm=!!opt.reduced,cells=grid.querySelectorAll('.org');
 idx.forEach((i,k)=>{const c=cells[i];if(!c)return;const b=document.createElement('div');b.className='breed'+(rm?'':' anim');
  b.setAttribute('role','img');b.setAttribute('aria-label',STR.parent);b.dataset.idx=i;b.style.setProperty('--d',(k*HEART.stagger)+'ms');
  b.innerHTML=heartSVG+`<span class="egg" role="img" aria-label="${STR.egg}">${eggSVG}</span>`;c.appendChild(b)});
 // Sounds (design/sounds/sfx.js; off unless #sound is on; silent under reduced motion): one call per heart and per egg,
 // throttled inside SFX.play (one per cue every 180 ms, max 8 breeding cues per second), so 16 parents give ~4 hearts + ~4 eggs.
 if(!rm&&window.SFX&&SFX.play){window.SFX.lastBreed=[];const q=[];idx.forEach((i,k)=>{q.push(['heart',k*HEART.stagger],['egg',k*HEART.stagger+HEART.eggDelay+EGG_LAND])});q.sort((x,y)=>x[1]-y[1]).forEach(([n,d])=>SFX.play(n,{delay:d}))}
 const total=rm||!idx.length?0:(idx.length-1)*HEART.stagger+HEART.eggDelay+HEART.eggPop;
 return new Promise(r=>setTimeout(r,total))};
window.BREED_HEART=HEART;window.BREED_STRINGS=STR;
})();
