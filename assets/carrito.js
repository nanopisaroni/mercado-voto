// Boleta: un presidente, un gobernador, un intendente y hasta cinco legisladores.
const MAX_LEG = 5;

function leer() {
  try { return JSON.parse(localStorage.getItem('mv_boleta_v2') || '[]'); } catch (e) { return []; }
}
function guardar(b) {
  localStorage.setItem('mv_boleta_v2', JSON.stringify(b));
  pintarContador();
}
function pintarContador() {
  const n = leer().length;
  document.querySelectorAll('.mi-boleta .n').forEach(e => e.textContent = n);
}
function aviso(txt) {
  const t = document.createElement('div');
  t.textContent = txt;
  t.style.cssText = 'position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#2d2d2d;color:#fff;padding:11px 20px;border-radius:6px;font-size:13.5px;z-index:999;box-shadow:0 6px 20px rgba(0,0,0,.25)';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2000);
}
function agregar(cid, cargo, jur, ir) {
  const b = leer();
  if (b.some(x => x.i === cid)) { aviso('Ya está en tu boleta'); return; }
  if (cargo !== 'legislador') {
    const i = b.findIndex(x => x.c === cargo);
    if (i >= 0) b.splice(i, 1);
  } else if (b.filter(x => x.c === 'legislador').length >= MAX_LEG) {
    aviso('Tu boleta ya tiene 5 legisladores'); return;
  }
  b.push({ i: cid, c: cargo, j: jur });
  guardar(b);
  if (ir) { location.href = '/boleta'; return; }
  aviso('Sumado a tu boleta');
}
function quitar(idx) {
  const b = leer();
  b.splice(idx, 1);
  guardar(b);
  if (typeof renderBoleta === 'function') renderBoleta();
}
document.addEventListener('DOMContentLoaded', pintarContador);
