/* filtros y catálogo */
const state = { cargo: '', jur: '', partido: '', badge: '', eco: 0, q: '', orden: '' };
const TITULOS = { presidencial: 'Candidatos a Presidente', gobernador: 'Candidatos a Gobernador', intendente: 'Candidatos a Intendente', legislador: 'Candidatos a Legislador' };

const $ = id => document.getElementById(id);
const tarjetas = () => [...document.querySelectorAll('.card')];
let ordenOriginal = [];

function llenarJurisdicciones() {
  const sel = $('f-jur');
  const vals = new Set();
  tarjetas().forEach(t => {
    if (state.cargo && t.dataset.cargo !== state.cargo) return;
    if (t.dataset.jur && t.dataset.jur !== 'Nacional') vals.add(t.dataset.jur);
  });
  sel.innerHTML = '<option value="">Todas</option>' + [...vals].sort().map(v => `<option value="${v}">${v}</option>`).join('');
  sel.value = vals.has(state.jur) ? state.jur : '';
  state.jur = sel.value;
}

function sinAcentos(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, ''); }

function aplicar() {
  let n = 0;
  const q = sinAcentos(state.q);
  tarjetas().forEach(t => {
    const d = t.dataset;
    const texto = sinAcentos((d.nombre + ' ' + d.partido + ' ' + d.jur).toLowerCase());
    const ok = (!state.cargo || d.cargo === state.cargo)
      && (!state.jur || d.jur === state.jur)
      && (!state.partido || d.partido === state.partido)
      && (!state.badge || d.badge === state.badge)
      && (!q || texto.includes(q))
      && (state.eco === 0 || Math.abs(+d.eco - state.eco) <= 20);
    t.hidden = !ok;
    if (ok) n++;
  });
  const grid = $('grid');
  let arr = [...ordenOriginal];
  if (state.orden === 'cumplimiento') arr.sort((a, b) => (+b.dataset.cum) - (+a.dataset.cum));
  if (state.orden === 'letales') arr.sort((a, b) => (+b.dataset.let) - (+a.dataset.let));
  if (state.orden === 'ruptura') arr.sort((a, b) => (+b.dataset.rupt) - (+a.dataset.rupt));
  if (state.orden === 'nombre') arr.sort((a, b) => a.dataset.nombre.localeCompare(b.dataset.nombre));
  arr.forEach(x => grid.appendChild(x));
  $('cuenta').textContent = n + (n === 1 ? ' resultado' : ' resultados');
  $('vacio').hidden = n > 0;
  $('titulo-cat').textContent = state.q ? 'Resultados para “' + state.q + '”' : (TITULOS[state.cargo] || (state.badge === 'NUEVO' ? 'Outsiders' : 'Todos los candidatos'));
  document.querySelectorAll('.cat[data-cargo]').forEach(c => c.classList.toggle('on', c.dataset.cargo === state.cargo));
  $('f-eco-v').textContent = state.eco === 0 ? 'Sin filtro' : (state.eco < 50 ? 'Cerca de más Estado' : state.eco > 50 ? 'Cerca de más mercado' : 'Centro');
  chips();
  sincronizarURL();
}

function chips() {
  const lista = [];
  if (state.cargo) lista.push(['cargo', TITULOS[state.cargo].replace('Candidatos a ', '')]);
  if (state.jur) lista.push(['jur', state.jur]);
  if (state.partido) lista.push(['partido', state.partido]);
  if (state.badge) lista.push(['badge', state.badge.charAt(0) + state.badge.slice(1).toLowerCase()]);
  if (state.eco) lista.push(['eco', 'Economía ' + state.eco]);
  if (state.q) lista.push(['q', '“' + state.q + '”']);
  $('chips').innerHTML = lista.map(([k, v]) => `<button type="button" class="chip-f" data-k="${k}">${v} <span aria-hidden="true">✕</span></button>`).join('');
}

function sincronizarURL() {
  const q = new URLSearchParams();
  ['cargo', 'jur', 'partido', 'badge', 'orden', 'q'].forEach(k => { if (state[k]) q.set(k, state[k]); });
  const s = q.toString();
  history.replaceState(null, '', s ? '/?' + s + location.hash : '/' + location.hash);
}

function marcarRadios() {
  document.querySelectorAll('input[name=cargo]').forEach(r => r.checked = r.value === state.cargo);
  document.querySelectorAll('input[name=badge]').forEach(r => r.checked = r.value === state.badge);
  $('f-partido').value = state.partido;
  $('f-eco').value = state.eco;
  $('orden').value = state.orden;
  $('q').value = state.q;
}

function limpiar(k) {
  if (!k) { Object.assign(state, { cargo: '', jur: '', partido: '', badge: '', eco: 0, q: '' }); }
  else state[k] = k === 'eco' ? 0 : '';
  if (k === 'cargo' || !k) state.jur = '';
  marcarRadios(); llenarJurisdicciones(); aplicar();
}

function abrirFiltros(si) {
  $('filtros').classList.toggle('abierto', si);
  document.body.classList.toggle('sin-scroll', si);
}

function slider() {
  const cont = $('slides'), dots = $('dots');
  if (!cont) return;
  const n = cont.children.length;
  dots.innerHTML = [...Array(n)].map((_, i) => `<button type="button" aria-label="Destacado ${i + 1}"></button>`).join('');
  const ir = i => cont.scrollTo({ left: i * cont.clientWidth, behavior: 'smooth' });
  const actual = () => Math.round(cont.scrollLeft / cont.clientWidth);
  const marcar = () => [...dots.children].forEach((d, i) => d.classList.toggle('on', i === actual()));
  dots.addEventListener('click', e => { const i = [...dots.children].indexOf(e.target); if (i >= 0) ir(i); });
  cont.addEventListener('scroll', () => requestAnimationFrame(marcar), { passive: true });
  marcar();
  let pausa = false;
  cont.addEventListener('pointerenter', () => pausa = true);
  cont.addEventListener('pointerleave', () => pausa = false);
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches)
    setInterval(() => { if (!pausa && !document.hidden) ir((actual() + 1) % n); }, 6000);
}

document.addEventListener('DOMContentLoaded', () => {
  ordenOriginal = tarjetas();
  const q = new URLSearchParams(location.search);
  ['cargo', 'jur', 'partido', 'badge', 'orden', 'q'].forEach(k => { if (q.get(k)) state[k] = q.get(k); });
  if (state.q) state.q = state.q.toLowerCase().trim();
  marcarRadios();
  llenarJurisdicciones();
  aplicar();
  slider();

  document.querySelectorAll('input[name=cargo]').forEach(r => r.addEventListener('change', () => { state.cargo = r.value; state.jur = ''; llenarJurisdicciones(); aplicar(); }));
  document.querySelectorAll('input[name=badge]').forEach(r => r.addEventListener('change', () => { state.badge = r.value; aplicar(); }));
  $('f-jur').addEventListener('change', e => { state.jur = e.target.value; aplicar(); });
  $('f-partido').addEventListener('change', e => { state.partido = e.target.value; aplicar(); });
  $('f-eco').addEventListener('input', e => { state.eco = +e.target.value; aplicar(); });
  $('orden').addEventListener('change', e => { state.orden = e.target.value; aplicar(); });
  $('q').addEventListener('input', e => { state.q = e.target.value.toLowerCase().trim(); aplicar(); });
  document.querySelector('.buscador').addEventListener('submit', e => { e.preventDefault(); $('catalogo').scrollIntoView({ behavior: 'smooth' }); });
  $('chips').addEventListener('click', e => { const b = e.target.closest('.chip-f'); if (b) limpiar(b.dataset.k); });
  $('limpiar').addEventListener('click', () => { limpiar(); abrirFiltros(false); });
  $('abrir-filtros').addEventListener('click', () => abrirFiltros(true));
  $('cerrar-filtros').addEventListener('click', () => abrirFiltros(false));
  document.addEventListener('click', e => {
    if ($('filtros').classList.contains('abierto') && !e.target.closest('#filtros, #abrir-filtros')) abrirFiltros(false);
  });
  $('filtros').addEventListener('change', () => { if (matchMedia('(max-width: 860px)').matches) setTimeout(() => abrirFiltros(false), 150); });
  document.querySelectorAll('.cat[data-cargo]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault(); state.cargo = a.dataset.cargo; state.jur = ''; state.badge = '';
    marcarRadios(); llenarJurisdicciones(); aplicar(); $('catalogo').scrollIntoView({ behavior: 'smooth' });
  }));
  $('sorpresa').addEventListener('click', () => { completarAzar(); location.href = '/boleta'; });
});
