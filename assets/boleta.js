// Página de la boleta: armado, perfil, compra y compartir. También muestra boletas compartidas por link.
const $b = id => document.getElementById(id);
const SLOTS = [['presidencial', 'Presidente'], ['gobernador', 'Gobernador'], ['intendente', 'Intendente']];
const COMPARTIDA = boletaDeQuery(location.search);
let usada = false;
const modoCompartida = () => COMPARTIDA.length > 0 && !usada;
const boletaActual = () => modoCompartida() ? COMPARTIDA : leer();

// ---------- perfil ----------
const TIPOS = [
  [9, '🐎', 'Pura sangre', 'Todos tiran para el mismo lado. Coherencia total: o sabés lo que querés, o elegiste por el color del afiche.'],
  [15, '🧭', 'Coherente', 'Hay matices, pero la boleta tiene una dirección clara.'],
  [21, '🥗', 'Ensalada mixta', 'Un poco de cada cosa. Tu boleta es un asado con invitados de todos los partidos.'],
  [99, '🧟', 'Frankenstein', 'Elegiste candidatos que no se pondrían de acuerdo ni para pedir una pizza. Prepará el pochoclo para el primer gabinete.'],
];
function perfil(b) {
  const ejes = b.map(x => MV.c[x.i].e);
  if (ejes.length < 2) return null;
  const media = [0, 1, 2, 3, 4, 5].map(k => ejes.reduce((s, e) => s + e[k], 0) / ejes.length);
  const disp = [0, 1, 2, 3, 4, 5].map(k => Math.sqrt(ejes.reduce((s, e) => s + (e[k] - media[k]) ** 2, 0) / ejes.length))
    .reduce((a, b) => a + b, 0) / 6;
  const t = TIPOS.find(t => disp < t[0]);
  const rasgos = media.map((v, k) => [Math.abs(v - 50), k, v]).filter(r => r[0] >= 12).sort((a, b) => b[0] - a[0]).slice(0, 2)
    .map(([, k, v]) => MV.polos[k][v > 50 ? 2 : 1]);
  return { media, disp, emoji: t[1], tipo: t[2], desc: t[3], rasgos };
}

function radarSVG(media, b) {
  const cx = 130, cy = 118, R = 82;
  const pt = (k, v) => { const a = (-90 + k * 60) * Math.PI / 180, r = 8 + v / 100 * (R - 8); return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
  let s = '';
  [0.33, 0.66, 1].forEach(f => s += '<polygon class="ra" points="' + [0, 1, 2, 3, 4, 5].map(k => pt(k, f * 100).join(',')).join(' ') + '"/>');
  b.forEach(x => {
    const c = MV.c[x.i];
    s += '<polygon points="' + c.e.map((v, k) => pt(k, v).join(',')).join(' ') + '" fill="none" stroke="' + c.col + '" stroke-opacity=".35" stroke-width="1.2"/>';
  });
  s += '<polygon points="' + media.map((v, k) => pt(k, v).join(',')).join(' ') + '" fill="#3483fa" fill-opacity=".18" stroke="#3483fa" stroke-width="2.5"/>';
  MV.polos.forEach((p, k) => {
    const a = (-90 + k * 60) * Math.PI / 180, x = cx + (R + 14) * Math.cos(a), y = cy + (R + 14) * Math.sin(a);
    const anc = Math.abs(Math.cos(a)) < .3 ? 'middle' : Math.cos(a) < 0 ? 'end' : 'start';
    const dy = a < -1 ? -4 : Math.sin(a) > .9 ? 12 : 3;
    s += '<text class="rl" x="' + x.toFixed(1) + '" y="' + (y + dy).toFixed(1) + '" text-anchor="' + anc + '">' + p[media[k] >= 50 ? 2 : 1] + '</text>';
  });
  return '<svg class="radar" viewBox="-42 0 344 235" role="img" aria-label="Perfil promedio de la boleta">' + s + '</svg>';
}

// ---------- render ----------
function itemHTML(it, editable) {
  const c = MV.c[it.i];
  const sub = c.p + (it.j && it.j !== 'Nacional' ? ' · ' + it.j : '');
  const ajeno = editable && leerLugar() && !candidaturaTeToca(it.c, it.j);
  const est = c.to ? '<span class="estrellas"><i>' + '★'.repeat(Math.max(1, Math.round(c.cu / c.to * 5))) + '☆'.repeat(5 - Math.max(1, Math.round(c.cu / c.to * 5))) + '</i></span>' : '';
  return '<div class="slot-item">' + avatar(c, 'slot-f') +
    '<div class="slot-txt"><a href="/c/' + c.s + '"><b>' + c.n + '</b></a><span>' + sub + '</span>' + est +
    (c.le ? '<span class="slot-alerta">⚠ ' + c.le + ' crítica' + (c.le > 1 ? 's' : '') + ' letal' + (c.le > 1 ? 'es' : '') + '</span>' : '') +
    (ajeno ? '<span class="slot-ajeno">📍 No se vota donde vos votás</span>' : '') + '</div>' +
    (editable ? '<div class="slot-acc"><a href="/?cargo=' + it.c + '#catalogo" class="link-btn">Cambiar</a><button class="link-btn quitar" data-i="' + it.i + '" data-c="' + it.c + '">Quitar</button></div>' : '') +
    '</div>';
}
function vacioHTML(cargo, txt, editable) {
  if (editable && !cargosDisponibles().includes(cargo)) {
    const L = leerLugar();
    const donde = cargo === 'intendente' ? (L.ciudad || 'tu localidad') : L.prov;
    const txt = cargo === 'gobernador' && L.prov === 'CABA' ? 'En CABA no se elige gobernador: el jefe de Gobierno va en Intendente.'
      : 'Todavía no cargamos candidatos a ' + CARGO_N[cargo].toLowerCase() + ' de ' + donde + '.';
    return '<div class="slot-vacio no-aplica"><span>' + txt + '</span><button type="button" class="link-btn" data-lugar>Cambiar lugar</button></div>';
  }
  return editable
    ? '<a class="slot-vacio" href="/?cargo=' + cargo + '#catalogo"><span>' + txt + '</span><b>+ Elegir</b></a>'
    : '<div class="slot-vacio"><span>' + txt + '</span></div>';
}

function render() {
  const comp = modoCompartida();
  const b = boletaActual();
  const editable = !comp;
  $b('compartida').hidden = !comp;
  $b('vaciar').hidden = comp || !b.length;
  $b('b-titulo').textContent = comp ? 'Boleta compartida' : 'Tu boleta';
  $b('pasos').hidden = comp;
  $b('perfil-h').textContent = comp ? 'Perfil de esta boleta' : 'Perfil de tu boleta';
  let html = '';
  SLOTS.forEach(([cg, etq]) => {
    const it = b.find(x => x.c === cg);
    html += '<div class="slot"><div class="slot-label">' + etq + '</div>' + (it ? itemHTML(it, editable) : vacioHTML(cg, 'Sin elegir todavía', editable)) + '</div>';
  });
  const legs = b.filter(x => x.c === 'legislador');
  html += '<div class="slot"><div class="slot-label">Legisladores <span>' + legs.length + ' de ' + MAX_LEG + '</span></div>';
  legs.forEach(it => html += itemHTML(it, editable));
  for (let k = legs.length; k < MAX_LEG; k++) html += vacioHTML('legislador', 'Lugar ' + (k + 1) + ' libre', editable);
  html += '</div>';
  $b('slots').innerHTML = html;

  // resumen
  const n = b.length;
  const cu = b.reduce((s, x) => s + MV.c[x.i].cu, 0), to = b.reduce((s, x) => s + MV.c[x.i].to, 0);
  const le = b.reduce((s, x) => s + MV.c[x.i].le, 0);
  $b('rc-n').textContent = n;
  $b('rc-votos').textContent = $b('rc-total').textContent = n + (n === 1 ? ' voto' : ' votos');
  $b('rc-prom').textContent = to ? Math.round(100 * cu / to) + '%' : '-';
  $b('rc-let').textContent = le;
  $b('rc-let').classList.toggle('rojo', le > 0);
  $b('finalizar').disabled = !n;
  const total = totalSlots(), lleno = completa(b);
  $b('finalizar').textContent = comp ? 'Compartir esta boleta' : (lleno ? 'Finalizar compra' : 'Finalizar compra (' + n + '/' + total + ')');
  $b('sorpresa').hidden = comp || lleno;
  const pasos = [...$b('pasos').children];
  pasos.forEach((p, i) => p.classList.toggle('on', i <= (lleno ? 1 : 0)));
  const L = leerLugar();
  $b('b-sub').innerHTML = comp ? 'Un presidente, un gobernador, un intendente y hasta cinco legisladores.'
    : L ? '📍 Votás en ' + (L.ciudad && L.ciudad !== L.prov ? L.ciudad + ', ' : '') + L.prov + '. <button type="button" class="link-btn" data-lugar>Cambiar</button>'
      : 'Un presidente, un gobernador, un intendente y hasta cinco legisladores. <button type="button" class="link-btn" data-lugar>Decinos dónde votás</button>';

  const pf = perfil(b);
  $b('perfil').hidden = !pf;
  if (pf) {
    $b('perfil-tipo').innerHTML = '<span class="pt-e">' + pf.emoji + '</span><div><small>' + (comp ? 'Esta boleta es' : 'Tu boleta es') + '</small><b>' + pf.tipo + '</b>' +
      (pf.rasgos.length ? '<span>Tirando a ' + pf.rasgos.join(' y ').toLowerCase() + '</span>' : '<span>Centro en todo</span>') + '</div>';
    $b('perfil-radar').innerHTML = radarSVG(pf.media, b);
    $b('perfil-desc').textContent = pf.desc;
  }
}

// ---------- compartir ----------
function textoShare(b) {
  const pf = perfil(b);
  const nombre = id => MV.c[id].n;
  const lineas = [];
  SLOTS.forEach(([cg, etq]) => { const it = b.find(x => x.c === cg); if (it) lineas.push('• ' + etq + ': ' + nombre(it.i)); });
  const legs = b.filter(x => x.c === 'legislador');
  if (legs.length) lineas.push('• Legisladores: ' + legs.map(x => nombre(x.i)).join(', '));
  const cab = modoCompartida() ? 'Mirá esta boleta en Mercado Voto 🛒🗳️' : 'Armé mi boleta en Mercado Voto 🛒🗳️';
  return cab + '\n' + lineas.join('\n') + (pf ? '\nResultado: ' + pf.emoji + ' boleta ' + pf.tipo.toLowerCase() + '.' : '') + '\n¿Y vos qué comprarías?';
}
function urlShare(b) { return location.origin + '/b?' + boletaQuery(b); }

function itemsImagen(b) {
  return b.map(x => { const c = MV.c[x.i]; return { c: x.c, j: x.j, n: c.n, p: c.p, f: c.f, i: c.i, color: c.col }; });
}

async function compartir(red) {
  const b = boletaActual();
  if (!b.length) return;
  if (red === 'post' || red === 'story') {
    const pf = perfil(b);
    aviso('Generando la imagen…');
    track('descarga_imagen', red);
    await descargarBoleta(itemsImagen(b), pf, red);
    return;
  }
  track('comparte', red);
  compartirLink(red, textoShare(b), urlShare(b));
}

async function finalizar() {
  const b = boletaActual();
  if (!b.length) return;
  $b('modal').hidden = false;
  document.body.classList.add('sin-scroll');
  [...$b('pasos').children].forEach(p => p.classList.add('on'));
  const comp = modoCompartida();
  $b('m-tit').textContent = comp ? 'Compartí esta boleta' : (completa(b) ? '¡Listo! Compraste tu boleta' : '¡Compra parcial confirmada!');
  const pf = perfil(b);
  $b('m-sub').textContent = pf ? 'Tu boleta salió ' + pf.emoji + ' ' + pf.tipo.toLowerCase() + '. Mandala al grupo y que empiece el debate.' : 'Mandala al grupo y que empiece el debate.';
  $b('m-rk').hidden = true;
  if (!comp) {
    confeti();
    track('finaliza');
    enviarBoleta(b).then(() => ranking()).then(rk => mostrarComparacion(rk, b));
  }
  const img = $b('m-img');
  img.removeAttribute('src');
  const cv = await tarjetaBoleta(itemsImagen(b), pf, 'post');
  img.src = cv.toDataURL('image/jpeg', .85);
}
// "3 de cada 10 eligió el mismo presidente que vos": prueba social para empujar a compartir.
function mostrarComparacion(rk, b) {
  if (!rk || rk.total < MIN_RANKING) return;
  const pres = b.find(x => x.c === 'presidencial');
  if (!pres) return;
  const p = posicion(rk, pres.i, 'presidencial', pres.j);
  if (!p) return;
  const pct = Math.round(100 * p.n / rk.total);
  $b('m-rk').innerHTML = (pct >= 1 ? '<b>' + pct + '%</b> de las boletas eligió a ' : 'Pocas boletas eligieron a ') + MV.c[pres.i].n +
    ' como presidente. Está <b>#' + p.pos + '</b> entre los más elegidos.';
  $b('m-rk').hidden = false;
}
function cerrarModal() { $b('modal').hidden = true; document.body.classList.remove('sin-scroll'); render(); }

// ---------- confeti ----------
function confeti() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const cv = $b('confeti'), ctx = cv.getContext('2d');
  cv.width = innerWidth; cv.height = innerHeight; cv.style.display = 'block';
  const cols = ['#ffe600', '#3483fa', '#00a650', '#ff7733', '#2d2d2d'];
  const ps = [...Array(140)].map(() => ({ x: Math.random() * cv.width, y: -20 - Math.random() * cv.height * .5, vx: (Math.random() - .5) * 3, vy: 2 + Math.random() * 4, r: Math.random() * 6.3, s: 6 + Math.random() * 6, c: cols[Math.floor(Math.random() * cols.length)] }));
  let t = 0;
  (function paso() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    ps.forEach(p => { p.x += p.vx; p.y += p.vy; p.r += .1; ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); ctx.restore(); });
    if (++t < 200) requestAnimationFrame(paso); else { ctx.clearRect(0, 0, cv.width, cv.height); cv.style.display = 'none'; }
  })();
}

// ---------- eventos ----------
document.addEventListener('DOMContentLoaded', () => {
  render();
  $b('slots').addEventListener('click', e => {
    const q = e.target.closest('.quitar');
    if (q) { quitarCand(q.dataset.i, q.dataset.c); render(); }
  });
  $b('vaciar').addEventListener('click', () => { if (confirm('¿Vaciar toda la boleta?')) { guardar([]); render(); } });
  $b('sorpresa').addEventListener('click', () => { completarAzar(); render(); aviso('Completamos los lugares vacíos al azar 🎲'); });
  $b('finalizar').addEventListener('click', finalizar);
  $b('m-cerrar').addEventListener('click', cerrarModal);
  $b('modal').addEventListener('click', e => { if (e.target.id === 'modal') cerrarModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$b('modal').hidden) cerrarModal(); });
  document.querySelectorAll('.modal [data-share]').forEach(b => b.addEventListener('click', () => compartir(b.dataset.share)));
  if (modoCompartida()) track('abre_compartida');
  document.addEventListener('mv:lugar', render);
  $b('copiar-boleta').addEventListener('click', () => {
    track('usa_compartida');
    guardar(COMPARTIDA.slice());
    usada = true;
    history.replaceState(null, '', '/boleta');
    render();
    aviso('Ahora es tu boleta. Cambiá lo que quieras.');
  });
});

// ---------- propuestas compradas ----------
function pintarPropsBoleta() {
  const cont = $b('b-props');
  if (!cont) return;
  const ids = leerProps();
  if (!ids.length) {
    cont.innerHTML = '<p class="sub">Todavía no sumaste propuestas. Podés elegir ideas, visión de país y futuro posible.</p>';
    return;
  }
  cont.innerHTML = ids.map(p => '<div class="bp-item"><span class="bp-eje">' + p.eje + '</span><b>' + p.titulo +
    '</b><span class="bp-esp">' + p.esp + '</span><button class="link-btn" data-quitar="' + p.id + '">Quitar</button></div>').join('');
  cont.querySelectorAll('[data-quitar]').forEach(b => b.addEventListener('click', () => {
    quitarProp(b.dataset.quitar);
    pintarPropsBoleta();
    aviso('Propuesta quitada del carrito');
  }));
}
document.addEventListener('DOMContentLoaded', pintarPropsBoleta);
