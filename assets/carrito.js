function pintarContador() {
  const b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  document.querySelectorAll('.mi-boleta .n').forEach(e => e.textContent = b.length);
}

function agregar(id, ir) {
  let b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  if (!b.includes(id)) b.push(id);
  localStorage.setItem('mv_boleta', JSON.stringify(b));
  pintarContador();
  if (ir) { location.href = '/boleta'; return; }
  const t = document.createElement('div');
  t.textContent = 'Agregado a tu boleta';
  t.style.cssText = 'position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#2d2d2d;color:#fff;padding:11px 20px;border-radius:6px;font-size:13.5px;z-index:99;box-shadow:0 6px 20px rgba(0,0,0,.2)';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 1800);
}

document.addEventListener('DOMContentLoaded', pintarContador);
