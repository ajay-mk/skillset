'use strict';
// Page logic: KaTeX typesetting, mobile menu, scroll progress, and demos.
// A demo is an element with data-demo="<name>" holding an <input type=range>
// and an <output>; window.DEMOS[name](root, value) redraws it. Define DEMOS in
// assets/demos.js and load it before this file on pages that use demos.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.equation,.math').forEach(el => {
    try { katex.render(el.textContent, el, {displayMode: el.classList.contains('equation'), throwOnError: true}); }
    catch (e) { el.classList.add('math-error'); console.error('KaTeX', el.textContent, e.message); }
  });
  document.querySelectorAll('[data-demo]').forEach(root => {
    const draw = (window.DEMOS || {})[root.dataset.demo];
    if (!draw) { console.error('no demo named', root.dataset.demo); return; }
    const input = root.querySelector('input'), out = root.querySelector('output');
    const run = () => { if (out) out.textContent = input.value; draw(root, Number(input.value)); };
    input.addEventListener('input', run); run();
  });
  const menu = document.getElementById('menu');
  if (menu) menu.addEventListener('click', () => {
    const open = document.getElementById('sidebar').classList.toggle('is-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  const bar = document.querySelector('.scroll-progress');
  const prog = () => { const m = document.documentElement.scrollHeight - innerHeight; bar.style.width = (m > 0 ? scrollY / m : 0) * (innerWidth - bar.offsetLeft) + 'px'; };
  addEventListener('scroll', prog, {passive: true}); prog();
});
