// Boleta: un presidente, un gobernador, un intendente y hasta cinco legisladores.
const MAX_LEG = 5;
const TOTAL_SLOTS = 8;
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
  b.push({ i: cid, c: cargo, j: jur || jurDe(cid, cargo) });
  guardar(b);
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
    btn.textContent = en ? '✓ En tu boleta' : 'Agregar a la boleta';
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
      html += it ? avatar(MV.c[it.i], 'mb-s') : '<span class="mb-s vacio" title="' + CARGO_N[cg] + '">' + CARGO_N[cg][0] + '</span>';
    });
    const legs = b.filter(x => x.c === 'legislador');
    for (let k = 0; k < MAX_LEG; k++) html += legs[k] ? avatar(MV.c[legs[k].i], 'mb-s leg') : '<span class="mb-s leg vacio">L</span>';
    document.getElementById('mb-slots').innerHTML = html;
    document.getElementById('mb-n').textContent = b.length + ' de ' + TOTAL_SLOTS;
    const falta = orden.find(cg => !b.some(x => x.c === cg));
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
  ['presidencial', 'gobernador', 'intendente'].forEach(cg => {
    if (b.some(x => x.c === cg)) return;
    const ops = MV.k.filter(k => k[1] === cg && !usados.has(k[0]));
    if (!ops.length) return;
    const k = azar(ops); usados.add(k[0]); b.push({ i: k[0], c: cg, j: k[2] });
  });
  while (b.filter(x => x.c === 'legislador').length < MAX_LEG) {
    const ops = MV.k.filter(k => k[1] === 'legislador' && !usados.has(k[0]));
    if (!ops.length) break;
    const k = azar(ops); usados.add(k[0]); b.push({ i: k[0], c: 'legislador', j: k[2] });
  }
  guardar(b);
}

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
