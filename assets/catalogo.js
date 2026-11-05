/* filtros, catálogo, armado guiado y ranking */
const state = { cargo: '', jur: '', partido: '', badge: '', eco: 0, q: '', orden: '', verTodo: false, guia: false };
const TITULOS = { presidencial: 'Candidatos a Presidente', gobernador: 'Candidatos a Gobernador', intendente: 'Candidatos a Intendente', legislador: 'Candidatos a Legislador' };

const $ = id => document.getElementById(id);
const tarjetas = () => [...document.querySelectorAll('.card')];
let ordenOriginal = [];
let RK = null; // ranking, si hay suficientes boletas

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
const filtraLugar = () => leerLugar() && !state.verTodo && !state.jur && !state.q;

function aplicar() {
  let n = 0;
  const q = sinAcentos(state.q);
  const L = filtraLugar() ? leerLugar() : null;
  tarjetas().forEach(t => {
    const d = t.dataset;
    const texto = sinAcentos((d.nombre + ' ' + d.partido + ' ' + d.jur).toLowerCase());
    const ok = (!state.cargo || d.cargo === state.cargo)
      && (!state.jur || d.jur === state.jur)
      && (!state.partido || d.partido === state.partido)
      && (!state.badge || d.badge === state.badge)
      && (!q || texto.includes(q))
      && (state.eco === 0 || Math.abs(+d.eco - state.eco) <= 20)
      && (!L || candidaturaTeToca(d.cargo, d.jur, L));
    t.hidden = !ok;
    if (ok) n++;
  });
  const grid = $('grid');
  let arr = [...ordenOriginal];
  const orden = state.orden || (RK ? 'elegidos' : '');
  if (orden === 'elegidos') arr.sort((a, b) => (+b.dataset.rk || 0) - (+a.dataset.rk || 0));
  if (orden === 'cumplimiento') arr.sort((a, b) => (+b.dataset.cum) - (+a.dataset.cum));
  if (orden === 'letales') arr.sort((a, b) => (+b.dataset.let) - (+a.dataset.let));
  if (orden === 'ruptura') arr.sort((a, b) => (+b.dataset.rupt) - (+a.dataset.rupt));
  if (orden === 'nombre') arr.sort((a, b) => a.dataset.nombre.localeCompare(b.dataset.nombre));
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
  const L = leerLugar();
  if (L && filtraLugar()) lista.push(['lugar', '📍 Candidatos de ' + (L.ciudad && L.ciudad !== L.prov ? L.ciudad + ', ' : '') + L.prov]);
  if (state.cargo && !state.guia) lista.push(['cargo', TITULOS[state.cargo].replace('Candidatos a ', '')]);
  if (state.jur) lista.push(['jur', state.jur]);
  if (state.partido) lista.push(['partido', state.partido]);
  if (state.badge) lista.push(['badge', state.badge.charAt(0) + state.badge.slice(1).toLowerCase()]);
  if (state.eco) lista.push(['eco', 'Economía ' + state.eco]);
  if (state.q) lista.push(['q', '“' + state.q + '”']);
  $('chips').innerHTML = lista.map(([k, v]) => `<button type="button" class="chip-f" data-k="${k}" title="Quitar filtro">${v} <span aria-hidden="true">✕</span></button>`).join('');
}

function sincronizarURL() {
  const q = new URLSearchParams();
  ['cargo', 'jur', 'partido', 'badge', 'orden', 'q'].forEach(k => { if (state[k]) q.set(k, state[k]); });
  if (state.guia) q.set('guia', '1');
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
  else if (k === 'lugar') state.verTodo = true;
  else state[k] = k === 'eco' ? 0 : '';
  if (k === 'cargo' || !k) state.jur = '';
  marcarRadios(); llenarJurisdicciones(); aplicar();
}

function abrirFiltros(si) {
  $('filtros').classList.toggle('abierto', si);
  document.body.classList.toggle('sin-scroll', si);
}

function irAlCatalogo() { $('catalogo').scrollIntoView({ behavior: 'smooth' }); }

// ---------- armado guiado ----------
const saltados = new Set();
function pasoActual() {
  const b = leer();
  return cargosDisponibles().find(cg => !saltados.has(cg) && (cg === 'legislador'
    ? b.filter(x => x.c === cg).length < MAX_LEG
    : !b.some(x => x.c === cg)));
}
function pintarGuia() {
  const g = $('guia');
  g.hidden = !state.guia;
  if (!state.guia) return;
  const paso = pasoActual();
  if (!paso) { location.href = '/boleta'; return; }
  const pasos = cargosDisponibles();
  const b = leer();
  const L = leerLugar();
  $('guia-pasos').innerHTML = pasos.map((cg, i) => {
    const hecho = cg === 'legislador' ? b.filter(x => x.c === cg).length >= MAX_LEG : b.some(x => x.c === cg);
    return `<span class="gp${cg === paso ? ' on' : ''}${hecho ? ' ok' : ''}">${hecho ? '✓' : i + 1}</span>`;
  }).join('');
  const nLeg = b.filter(x => x.c === 'legislador').length;
  const donde = paso === 'gobernador' ? ' de ' + L.prov : paso === 'intendente' ? ' de ' + L.ciudad : '';
  $('guia-tit').textContent = 'Paso ' + (pasos.indexOf(paso) + 1) + ' de ' + pasos.length + ' · ' +
    (paso === 'legislador' ? 'Elegí hasta 5 legisladores (' + nLeg + '/5)' : 'Elegí tu ' + CARGO_N[paso].toLowerCase() + donde);
  $('guia-sub').textContent = paso === 'legislador' ? 'Sumá los que quieras y seguí cuando estés.' : 'Leé las fichas y tocá “Agregar” en el que compres.';
  $('guia-saltar').hidden = paso === 'legislador';
  $('guia-sig').hidden = paso !== 'legislador';
  $('guia-sig').textContent = nLeg ? 'Ver mi boleta →' : 'Saltar y ver mi boleta →';
  if (state.cargo !== paso) { state.cargo = paso; state.jur = ''; marcarRadios(); llenarJurisdicciones(); aplicar(); }
}
function empezarGuia() {
  const arrancar = () => {
    state.guia = true; state.verTodo = false; state.q = ''; state.badge = ''; state.partido = '';
    saltados.clear();
    track('empieza_guia');
    pintarGuia(); irAlCatalogo();
  };
  leerLugar() ? arrancar() : pedirLugar(arrancar);
}

// ---------- ranking ----------
function pintarRanking(rk) {
  if (!rk || rk.total < MIN_RANKING) return;
  RK = rk;
  $('hero-cont').textContent = '🔥 ' + fmt(rk.total) + ' boletas armadas';
  document.querySelectorAll('[data-rk]').forEach(o => o.hidden = false);
  tarjetas().forEach(t => {
    const p = posicion(rk, t.querySelector('.btn.add').dataset.cid, t.dataset.cargo, t.dataset.jur);
    t.dataset.rk = p ? p.n : 0;
    if (!p || p.pos > 3) return;
    const linea = document.createElement('div');
    linea.className = 'rk-linea';
    linea.textContent = (p.pos === 1 ? '🔥 Más elegido' : '#' + p.pos + ' más elegido') + (t.dataset.cargo === 'gobernador' || t.dataset.cargo === 'intendente' ? ' en ' + t.dataset.jur : '');
    t.querySelector('.race').after(linea);
    if (p.pos === 1) t.querySelector('.card-foto').insertAdjacentHTML('beforeend', '<span class="badge-rk">MÁS VENDIDO</span>');
  });
  $('ranking').hidden = false;
  $('rk-sub').textContent = fmt(rk.total) + ' boletas finalizadas';
  const L = leerLugar();
  const tabs = [['presidencial', 'Presidente']];
  if (L && rk.r.gobernador.some(x => x[1] === L.prov)) tabs.push(['gobernador', 'Gobernador · ' + L.prov]);
  if (L && L.ciudad && rk.r.intendente.some(x => x[1] === L.ciudad)) tabs.push(['intendente', 'Intendente · ' + L.ciudad]);
  tabs.push(['legislador', 'Legisladores']);
  $('rk-tabs').innerHTML = tabs.map(([k, v], i) => `<button type="button" role="tab" data-rk-tab="${k}" aria-selected="${i === 0}">${v}</button>`).join('');
  listaRanking('presidencial');
  aplicar();
}
function listaRanking(cargo) {
  const L = leerLugar();
  const lista = RK.r[cargo].filter(x => cargo === 'gobernador' ? x[1] === L.prov : cargo === 'intendente' ? x[1] === L.ciudad : true).slice(0, 5);
  $('rk-lista').innerHTML = lista.map(([id, jur, n], i) => {
    const c = MV.c[id];
    return `<li><span class="rk-pos">${i + 1}</span>${avatar(c, 'rk-f')}<div class="rk-info"><a href="/c/${c.s}"><b>${c.n}</b></a><span>${c.p}</span>
      <div class="rk-barra"><i style="width:${Math.round(100 * n / lista[0][2])}%"></i></div></div>
      <div class="rk-n"><b>${Math.round(100 * n / RK.total)}%</b><small>${fmt(n)} boletas</small></div>
      <button class="btn add sec" data-cid="${id}" data-cargo="${cargo}" data-jur="${jur}">Agregar</button></li>`;
  }).join('');
  document.querySelectorAll('[data-rk-tab]').forEach(t => t.setAttribute('aria-selected', t.dataset.rkTab === cargo));
  pintarEstado();
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
  if (q.get('guia')) empezarGuia();
  ranking().then(pintarRanking);

  document.querySelectorAll('input[name=cargo]').forEach(r => r.addEventListener('change', () => { state.cargo = r.value; state.jur = ''; state.guia = false; pintarGuia(); llenarJurisdicciones(); aplicar(); }));
  document.querySelectorAll('input[name=badge]').forEach(r => r.addEventListener('change', () => { state.badge = r.value; aplicar(); }));
  $('f-jur').addEventListener('change', e => { state.jur = e.target.value; aplicar(); });
  $('f-partido').addEventListener('change', e => { state.partido = e.target.value; aplicar(); });
  $('f-eco').addEventListener('input', e => { state.eco = +e.target.value; aplicar(); });
  $('orden').addEventListener('change', e => { state.orden = e.target.value; aplicar(); });
  $('q').addEventListener('input', e => { state.q = e.target.value.toLowerCase().trim(); aplicar(); });
  document.querySelector('.buscador').addEventListener('submit', e => { e.preventDefault(); irAlCatalogo(); });
  $('chips').addEventListener('click', e => { const b = e.target.closest('.chip-f'); if (b) limpiar(b.dataset.k); });
  $('limpiar').addEventListener('click', () => { limpiar(); abrirFiltros(false); });
  $('abrir-filtros').addEventListener('click', () => abrirFiltros(true));
  $('cerrar-filtros').addEventListener('click', () => abrirFiltros(false));
  document.addEventListener('click', e => {
    if ($('filtros').classList.contains('abierto') && !e.target.closest('#filtros, #abrir-filtros')) abrirFiltros(false);
  });
  $('filtros').addEventListener('change', () => { if (matchMedia('(max-width: 860px)').matches) setTimeout(() => abrirFiltros(false), 150); });
  document.querySelectorAll('.cat[data-cargo]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault(); state.cargo = a.dataset.cargo; state.jur = ''; state.badge = ''; state.guia = false; pintarGuia();
    marcarRadios(); llenarJurisdicciones(); aplicar(); irAlCatalogo();
  }));
  $('sorpresa').addEventListener('click', () => {
    const ir = () => { completarAzar(); location.href = '/boleta'; };
    leerLugar() ? ir() : pedirLugar(ir);
  });
  document.querySelectorAll('[data-guia]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); empezarGuia(); }));
  $('guia-saltar').addEventListener('click', () => { saltados.add(pasoActual()); pintarGuia(); irAlCatalogo(); });
  $('guia-sig').addEventListener('click', () => { location.href = '/boleta'; });
  $('guia-salir').addEventListener('click', () => { state.guia = false; pintarGuia(); aplicar(); });
  $('rk-tabs').addEventListener('click', e => { const t = e.target.closest('[data-rk-tab]'); if (t) listaRanking(t.dataset.rkTab); });
  document.addEventListener('mv:agregado', e => {
    if (!state.guia || e.detail.cargo !== state.cargo) return;
    setTimeout(() => { pintarGuia(); irAlCatalogo(); }, e.detail.cargo === 'legislador' ? 0 : 700);
  });
  document.addEventListener('mv:lugar', () => {
    state.verTodo = false;
    if (state.guia) { saltados.clear(); pintarGuia(); }
    aplicar();
    if (RK) { $('ranking').hidden = true; RK = null; ranking().then(pintarRanking); document.querySelectorAll('.rk-linea, .badge-rk').forEach(x => x.remove()); }
  });
});
