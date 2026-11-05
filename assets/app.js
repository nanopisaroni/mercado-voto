// Boleta: un presidente, un gobernador, un intendente y hasta cinco legisladores.
const MAX_LEG = 5;
const CARGO_N = { presidencial: 'Presidente', gobernador: 'Gobernador', intendente: 'Intendente', legislador: 'Legislador' };
const CARGO_Q = { presidencial: 'p', gobernador: 'g', intendente: 'i', legislador: 'l' };
const KEY = 'mv_boleta_v2';

function leer() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
}
function guardar(b) {
  try { localStorage.setItem(KEY, JSON.stringify(b)); } catch (e) {}
  pintarEstado();
}
function jurDe(cid, cargo) {
  const k = MV.k.find(x => x[0] === cid && x[1] === cargo);
  return k ? k[2] : 'Nacional';
}

// Agrega una candidatura. Devuelve {ok, msg}. Si el cargo ya estaba ocupado, reemplaza.
function agregar(cid, cargo, jur) {
  const b = leer();
  const c = MV.c[cid];
  const ya = b.findIndex(x => x.i === cid && x.c === cargo);
  if (ya >= 0) return { ok: false, msg: c.n + ' ya está en tu boleta' };
  const otro = b.findIndex(x => x.i === cid);
  if (otro >= 0) b.splice(otro, 1);
  let msg = c.n + ' sumado como ' + CARGO_N[cargo];
  if (cargo !== 'legislador') {
    const i = b.findIndex(x => x.c === cargo);
    if (i >= 0) { msg = c.n + ' reemplazó a ' + MV.c[b[i].i].n; b.splice(i, 1); }
  } else if (b.filter(x => x.c === 'legislador').length >= MAX_LEG) {
    return { ok: false, msg: 'Ya tenés 5 legisladores. Sacá uno para sumar otro.' };
  }
  const j = jur || jurDe(cid, cargo);
  b.push({ i: cid, c: cargo, j });
  guardar(b);
  const L = leerLugar();
  if (L && !candidaturaTeToca(cargo, j)) msg += '. Ojo: es de ' + j + ' y vos votás en ' + (cargo === 'intendente' ? (L.ciudad || L.prov) : L.prov);
  track('agrega', cargo);
  if (completa(b)) trackUnaVez('completa', 'mv_completa_' + boletaQuery(b));
  document.dispatchEvent(new CustomEvent('mv:agregado', { detail: { cid, cargo } }));
  return { ok: true, msg };
}
function quitarCand(cid, cargo) {
  guardar(leer().filter(x => !(x.i === cid && x.c === cargo)));
}

// ---------- UI común ----------
let toastT;
function aviso(txt, accion) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.innerHTML = '';
  const s = document.createElement('span'); s.textContent = txt; t.appendChild(s);
  if (accion) {
    const a = document.createElement('a'); a.href = accion.href; a.textContent = accion.txt; t.appendChild(a);
  }
  t.classList.add('on');
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove('on'), 3200);
}

function avatar(c, cls) {
  if (c.f) return '<img class="' + cls + '" src="/' + c.f + '" alt="">';
  return '<span class="' + cls + ' ini" style="--c:' + c.col + '">' + c.i + '</span>';
}

function pintarEstado() {
  const b = leer();
  document.querySelectorAll('.mi-boleta .n').forEach(e => { e.textContent = b.length; e.classList.toggle('lleno', b.length > 0); });
  // botones de agregar
  document.querySelectorAll('.btn.add').forEach(btn => {
    const en = b.some(x => x.i === btn.dataset.cid && x.c === btn.dataset.cargo);
    btn.classList.toggle('en', en);
    const corto = btn.closest('.rk-lista');
    btn.textContent = en ? (corto ? '✓ En boleta' : '✓ En tu boleta') : (corto ? 'Agregar' : 'Agregar a la boleta');
    btn.setAttribute('aria-pressed', en);
  });
  // barra inferior
  const mb = document.getElementById('minibar');
  if (mb) {
    mb.hidden = b.length === 0;
    const orden = ['presidencial', 'gobernador', 'intendente'];
    let html = '';
    orden.forEach(cg => {
      const it = b.find(x => x.c === cg);
      if (!it && !cargosDisponibles().includes(cg)) return;
      html += it ? avatar(MV.c[it.i], 'mb-s') : '<span class="mb-s vacio" title="' + CARGO_N[cg] + '">' + CARGO_N[cg][0] + '</span>';
    });
    const legs = b.filter(x => x.c === 'legislador');
    for (let k = 0; k < MAX_LEG; k++) html += legs[k] ? avatar(MV.c[legs[k].i], 'mb-s leg') : '<span class="mb-s leg vacio">L</span>';
    document.getElementById('mb-slots').innerHTML = html;
    document.getElementById('mb-n').textContent = b.length + ' de ' + totalSlots();
    const falta = cargosDisponibles().find(cg => cg !== 'legislador' && !b.some(x => x.c === cg));
    document.getElementById('mb-hint').textContent = falta ? 'Te falta ' + CARGO_N[falta].toLowerCase() : (legs.length < MAX_LEG ? 'Sumá legisladores' : '¡Completa!');
  }
}

document.addEventListener('click', e => {
  const btn = e.target.closest('.btn.add');
  if (!btn) return;
  const { cid, cargo, jur } = btn.dataset;
  if (btn.classList.contains('en')) {
    quitarCand(cid, cargo);
    aviso(MV.c[cid].n + ' salió de tu boleta');
    return;
  }
  const r = agregar(cid, cargo, jur);
  aviso(r.msg, r.ok ? { href: '/boleta', txt: 'Ver boleta' } : null);
  if (r.ok) {
    const mb = document.getElementById('minibar');
    if (mb) { mb.classList.remove('pop'); void mb.offsetWidth; mb.classList.add('pop'); }
  }
});

// ---------- compartir ----------
function boletaQuery(b) {
  const q = new URLSearchParams();
  ['presidencial', 'gobernador', 'intendente'].forEach(cg => { const it = b.find(x => x.c === cg); if (it) q.set(CARGO_Q[cg], it.i); });
  const legs = b.filter(x => x.c === 'legislador').map(x => x.i);
  if (legs.length) q.set('l', legs.join(','));
  return q.toString().replace(/%2C/g, ',');
}
function boletaDeQuery(search) {
  const q = new URLSearchParams(search);
  const b = [];
  ['presidencial', 'gobernador', 'intendente'].forEach(cg => {
    const id = q.get(CARGO_Q[cg]);
    if (id && MV.c[id]) b.push({ i: id, c: cg, j: jurDe(id, cg) });
  });
  (q.get('l') || '').split(',').filter(id => MV.c[id]).slice(0, MAX_LEG)
    .forEach(id => { if (!b.some(x => x.i === id)) b.push({ i: id, c: 'legislador', j: jurDe(id, 'legislador') }); });
  return b;
}

async function copiar(txt) {
  try { await navigator.clipboard.writeText(txt); return true; }
  catch (e) {
    const t = document.createElement('textarea'); t.value = txt; document.body.appendChild(t); t.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (e2) {}
    t.remove(); return ok;
  }
}

// red: wa | x | tg | link | native
async function compartirLink(red, texto, url) {
  const enc = encodeURIComponent;
  if (red === 'wa') return window.open('https://wa.me/?text=' + enc(texto + '\n' + url), '_blank', 'noopener');
  if (red === 'x') return window.open('https://x.com/intent/post?text=' + enc(texto) + '&url=' + enc(url), '_blank', 'noopener');
  if (red === 'tg') return window.open('https://t.me/share/url?url=' + enc(url) + '&text=' + enc(texto), '_blank', 'noopener');
  if (red === 'native' && navigator.share) { try { await navigator.share({ title: 'Mercado Voto', text: texto, url }); } catch (e) {} return; }
  aviso(await copiar(url) ? 'Link copiado. Pegalo donde quieras.' : 'No se pudo copiar el link');
}

document.addEventListener('DOMContentLoaded', () => {
  pintarEstado();
  document.querySelectorAll('[data-share="native"]').forEach(b => { if (navigator.share) b.hidden = false; });
});
window.addEventListener('storage', e => { if (e.key === KEY) pintarEstado(); });

// Completa los lugares vacíos con candidaturas al azar.
function completarAzar() {
  const b = leer();
  const usados = new Set(b.map(x => x.i));
  const azar = arr => arr[Math.floor(Math.random() * arr.length)];
  const L = leerLugar();
  const opciones = cg => MV.k.filter(k => k[1] === cg && !usados.has(k[0]) && candidaturaTeToca(cg, k[2], L));
  track('azar');
  ['presidencial', 'gobernador', 'intendente'].forEach(cg => {
    if (b.some(x => x.c === cg)) return;
    const ops = opciones(cg);
    if (!ops.length) return;
    const k = azar(ops); usados.add(k[0]); b.push({ i: k[0], c: cg, j: k[2] });
  });
  while (b.filter(x => x.c === 'legislador').length < MAX_LEG) {
    const ops = opciones('legislador');
    if (!ops.length) break;
    const k = azar(ops); usados.add(k[0]); b.push({ i: k[0], c: 'legislador', j: k[2] });
  }
  guardar(b);
}

// ---------- dónde votás ----------
// {prov, ciudad}. ciudad es una de las ciudades con candidatos a intendente, o '' si es otra localidad.
const KEY_LUGAR = 'mv_lugar';
function leerLugar() {
  try { return JSON.parse(localStorage.getItem(KEY_LUGAR) || 'null'); } catch (e) { return null; }
}
function guardarLugar(l) {
  try { localStorage.setItem(KEY_LUGAR, JSON.stringify(l)); } catch (e) {}
  pintarLugar();
  document.dispatchEvent(new CustomEvent('mv:lugar', { detail: l }));
}
// ¿Esta candidatura es de la jurisdicción del usuario? Sin lugar elegido, todo le toca.
function candidaturaTeToca(cargo, jur, L) {
  L = L === undefined ? leerLugar() : L;
  if (!L || cargo === 'presidencial') return true;
  if (cargo === 'gobernador') return jur === L.prov;
  if (cargo === 'intendente') return Boolean(L.ciudad) && jur === L.ciudad;
  return jur === 'Nacional' || jur === L.prov;
}
// Cargos que el usuario puede completar según dónde vota (si no hay candidatos cargados, no cuenta).
function cargosDisponibles() {
  const L = leerLugar();
  return ['presidencial', 'gobernador', 'intendente', 'legislador']
    .filter(cg => MV.k.some(k => k[1] === cg && candidaturaTeToca(cg, k[2], L)));
}
function totalSlots() {
  return cargosDisponibles().reduce((n, cg) => n + (cg === 'legislador' ? MAX_LEG : 1), 0);
}
function completa(b) {
  return cargosDisponibles().every(cg => cg === 'legislador'
    ? b.filter(x => x.c === cg).length >= MAX_LEG
    : b.some(x => x.c === cg));
}
function pintarLugar() {
  const L = leerLugar();
  document.querySelectorAll('.lugar-txt').forEach(e => {
    e.textContent = L ? (L.ciudad && L.ciudad !== L.prov ? L.ciudad + ', ' + L.prov : L.prov) : '¿Dónde votás?';
  });
}

let alElegirLugar = null;
function pedirLugar(cb) {
  alElegirLugar = cb || null;
  const m = document.getElementById('m-lugar');
  if (!m) return cb && cb(leerLugar());
  const L = leerLugar() || {};
  const conGob = new Set(MV.k.filter(k => k[1] === 'gobernador').map(k => k[2]));
  const sel = document.getElementById('ml-prov');
  sel.innerHTML = '<option value="">Elegí tu provincia</option>' +
    MV.lugar.provs.map(p => '<option value="' + p + '">' + p + (conGob.has(p) || p === 'CABA' ? '' : ' (pronto)') + '</option>').join('');
  sel.value = L.prov || '';
  pintarCiudades(L.ciudad);
  m.hidden = false;
  document.body.classList.add('sin-scroll');
  setTimeout(() => sel.focus(), 50);
}
function pintarCiudades(actual) {
  const prov = document.getElementById('ml-prov').value;
  const ciudades = Object.entries(MV.lugar.ciudades).filter(([, p]) => p === prov).map(([c]) => c);
  const w = document.getElementById('ml-ciudad-w');
  w.hidden = !prov || prov === 'CABA' || !ciudades.length;
  document.getElementById('ml-ciudades').innerHTML = ciudades.map(c =>
    '<label><input type="radio" name="ml-ciudad" value="' + c + '"' + (actual === c ? ' checked' : '') + '> ' + c + '</label>').join('') +
    '<label><input type="radio" name="ml-ciudad" value=""' + (prov && !ciudades.includes(actual) ? ' checked' : '') + '> Otra localidad</label>';
  const conGob = MV.k.some(k => k[1] === 'gobernador' && k[2] === prov);
  const aviso = document.getElementById('ml-aviso');
  aviso.hidden = !prov || conGob || prov === 'CABA';
  aviso.textContent = 'Todavía no cargamos candidatos de ' + prov + '. Igual podés armar presidente y legisladores, y anotamos que la pediste.';
  document.getElementById('ml-ok').disabled = !prov;
}
function cerrarLugar() {
  const m = document.getElementById('m-lugar');
  if (m) m.hidden = true;
  if (!document.querySelector('.modal:not([hidden])')) document.body.classList.remove('sin-scroll');
}
document.addEventListener('DOMContentLoaded', () => {
  pintarLugar();
  const m = document.getElementById('m-lugar');
  if (!m) return;
  document.getElementById('ml-prov').addEventListener('change', () => pintarCiudades(''));
  document.getElementById('ml-ok').addEventListener('click', () => {
    const prov = document.getElementById('ml-prov').value;
    if (!prov) return;
    const r = document.querySelector('input[name=ml-ciudad]:checked');
    const ciudad = prov === 'CABA' ? 'CABA' : (r ? r.value : '');
    guardarLugar({ prov, ciudad });
    track('elige_lugar', prov);
    if (!MV.k.some(k => k[1] === 'gobernador' && k[2] === prov) && prov !== 'CABA') track('pide_lugar', prov);
    cerrarLugar();
    const cb = alElegirLugar; alElegirLugar = null;
    if (cb) cb({ prov, ciudad });
  });
  m.querySelectorAll('[data-cerrar-lugar]').forEach(b => b.addEventListener('click', () => {
    cerrarLugar();
    const cb = alElegirLugar; alElegirLugar = null;
    if (cb) cb(leerLugar());
  }));
  m.addEventListener('click', e => { if (e.target === m) cerrarLugar(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !m.hidden) cerrarLugar(); });
});
document.addEventListener('click', e => { if (e.target.closest('[data-lugar]')) pedirLugar(); });

// ---------- métricas ----------
// Vercel Web Analytics (si está activado en el proyecto) y un embudo propio y anónimo en /api/evento.
function track(e, p) {
  try { if (window.va) window.va('event', { name: e, ...(p ? { p: String(p) } : {}) }); } catch (err) {}
  try {
    const body = JSON.stringify({ e, p: p || '' });
    if (!(navigator.sendBeacon && navigator.sendBeacon('/api/evento', new Blob([body], { type: 'text/plain' }))))
      fetch('/api/evento', { method: 'POST', body, keepalive: true }).catch(() => {});
  } catch (err) {}
}
function trackUnaVez(e, clave, p) {
  try { if (localStorage.getItem(clave)) return; localStorage.setItem(clave, '1'); } catch (err) {}
  track(e, p);
}
document.addEventListener('DOMContentLoaded', () => {
  try { if (!sessionStorage.getItem('mv_visita')) { sessionStorage.setItem('mv_visita', '1'); track('visita'); } } catch (e) {}
});

// ---------- ranking ----------
const MIN_RANKING = 20; // boletas mínimas antes de mostrar números, para no exhibir un ranking vacío
let rankingP = null;
function ranking() {
  if (!rankingP) rankingP = fetch('/api/ranking').then(r => r.ok ? r.json() : null).then(d => (d && !d.off ? d : null)).catch(() => null);
  return rankingP;
}
// Posición y cantidad de un candidato en su cargo (y en su jurisdicción, para gobernador e intendente).
function posicion(rk, cid, cargo, jur) {
  if (!rk) return null;
  const lista = (rk.r[cargo] || []).filter(x => cargo === 'gobernador' || cargo === 'intendente' ? x[1] === jur : true);
  const i = lista.findIndex(x => x[0] === cid);
  return i < 0 ? null : { pos: i + 1, n: lista[i][2], de: lista.length };
}
function boletaId() {
  try {
    let id = localStorage.getItem('mv_bid');
    if (!id) { id = (Date.now().toString(36) + Math.random().toString(36).slice(2, 12)).toLowerCase(); localStorage.setItem('mv_bid', id); }
    return id;
  } catch (e) { return ''; }
}
function enviarBoleta(b) {
  const id = boletaId();
  if (!id || !b.length) return Promise.resolve(null);
  return fetch('/api/voto', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, b: b.map(x => ({ i: x.i, c: x.c })) }) })
    .then(r => r.ok ? r.json() : null).catch(() => null);
}
const fmt = n => n.toLocaleString('es-AR');

// ---------- propuestas ----------
const KEY_P = 'mv_propuestas_v1';
function leerProps() { try { return JSON.parse(localStorage.getItem(KEY_P) || '[]'); } catch (e) { return []; } }
function guardarProps(a) { try { localStorage.setItem(KEY_P, JSON.stringify(a)); } catch (e) {} pintarProps(); }
function propEnCarrito(id) { return leerProps().some(x => x.id === id); }
function agregarProp(o) {
  if (!o || !o.id) return { ok: false, msg: 'No pudimos agregar esa propuesta' };
  const a = leerProps();
  if (a.some(x => x.id === o.id)) return { ok: false, msg: 'Esa propuesta ya está en tu carrito' };
  a.push(o); guardarProps(a);
  return { ok: true, msg: 'Sumaste: ' + o.titulo };
}
function quitarProp(id) { guardarProps(leerProps().filter(x => x.id !== id)); }
function pintarProps() {
  document.querySelectorAll('.add-p').forEach(b => {
    const on = propEnCarrito(b.dataset.id);
    b.classList.toggle('on', on);
    b.textContent = on ? 'En el carrito ✓' : 'Agregar';
  });
  const n = leerProps().length;
  const bar = document.getElementById('pbar');
  if (bar) { bar.hidden = n === 0; const x = document.getElementById('pbar-n'); if (x) x.textContent = n; }
  const rc = document.getElementById('rc-props');
  if (rc) rc.textContent = n;
}
document.addEventListener('click', e => {
  const b = e.target.closest('.add-p');
  if (!b) return;
  e.preventDefault();
  let o = {};
  try { o = JSON.parse(b.dataset.prop || '{}'); } catch (err) {}
  const r = agregarProp(o);
  aviso(r.msg, r.ok ? { href: '/boleta', txt: 'Ver carrito' } : null);
});
document.addEventListener('DOMContentLoaded', pintarProps);
