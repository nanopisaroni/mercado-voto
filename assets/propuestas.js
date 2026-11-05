// Página de propuestas: filtros, detalle y carrito.
(function () {
  const grid = document.getElementById('pgrid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.prop'));
  const estado = { esp: '', eje: '', tipo: 'propuesta', q: '' };
  const cuenta = document.getElementById('p-cuenta');
  const vacio = document.getElementById('pvacio');

  function aplicar() {
    let n = 0;
    for (const c of cards) {
      const ok = (!estado.esp || c.dataset.esp === estado.esp)
        && (!estado.eje || c.dataset.eje === estado.eje)
        && (!estado.tipo || c.dataset.tipo === estado.tipo)
        && (!estado.q || c.dataset.busca.includes(estado.q));
      c.hidden = !ok;
      if (ok) n++;
    }
    cuenta.textContent = n + (n === 1 ? ' resultado' : ' resultados');
    vacio.hidden = n > 0;
  }

  document.querySelectorAll('.chip[data-f]').forEach(chip => {
    chip.addEventListener('click', () => {
      const f = chip.dataset.f;
      estado[f] = chip.dataset.v;
      document.querySelectorAll('.chip[data-f="' + f + '"]').forEach(o => o.classList.toggle('on', o === chip));
      aplicar();
    });
  });

  document.querySelectorAll('.pcat').forEach(cat => {
    cat.addEventListener('click', () => {
      const t = cat.dataset.tipo;
      estado.tipo = t;
      document.querySelectorAll('.pcat').forEach(o => o.classList.toggle('on', o === cat));
      document.querySelectorAll('.chip[data-f="tipo"]').forEach(o => o.classList.toggle('on', o.dataset.v === t));
      aplicar();
    });
  });

  // parámetros de la URL: ?tipo=vision&esp=lla&eje=economia
  const qs = new URLSearchParams(location.search);
  ['tipo', 'esp', 'eje'].forEach(k => {
    const v = qs.get(k);
    if (!v) return;
    estado[k] = v;
    document.querySelectorAll('.chip[data-f="' + k + '"]').forEach(o => o.classList.toggle('on', o.dataset.v === v));
    if (k === 'tipo') document.querySelectorAll('.pcat').forEach(o => o.classList.toggle('on', o.dataset.tipo === v));
  });

  const q = document.getElementById('pq');
  if (q) {
    let t;
    q.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(() => { estado.q = q.value.trim().toLowerCase(); aplicar(); }, 160);
    });
  }

  // ---------- modal de detalle ----------
  const modal = document.getElementById('pm');
  const cuerpo = document.getElementById('pm-body');
  function abrir(id) {
    const p = (window.MVP || {})[id];
    if (!p) return;
    const det = (p.detalle || []).map(d => '<li>' + esc(d) + '</li>').join('');
    const cands = (p.candidatos || []).map(c =>
      '<a class="pm-cand" href="/c/' + c.s + '">' + esc(c.n) + '</a>').join('');
    cuerpo.innerHTML =
      '<div class="pm-top"><span class="p-eje">' + esc(p.eje) + '</span>'
      + '<span class="p-esp" style="--c:' + p.color + '">' + esc(p.esp) + '</span>'
      + '<span class="p-tipo t-' + (p.tipo === 'Visión de país' ? 'vision' : p.tipo === 'Futuro posible' ? 'futuro' : 'propuesta') + '">' + esc(p.tipo) + '</span></div>'
      + '<h2>' + esc(p.titulo) + '</h2>'
      + '<p class="pm-cuerpo">' + esc(p.cuerpo) + '</p>'
      + (det ? '<ul class="pm-det">' + det + '</ul>' : '')
      + (cands ? '<div class="pm-cands"><b>Quién lo sostiene</b><div>' + cands + '</div></div>' : '')
      + '<div class="pm-fuente"><b>Fuente</b> <a href="' + p.fuente.u + '" target="_blank" rel="noopener">' + esc(p.fuente.t) + '</a></div>'
      + '<div class="pm-ficha"><span>Costo fiscal: <b>' + esc(p.costo || '—') + '</b></span><span>Alcance: <b>' + esc(p.alcance || '—') + '</b></span></div>'
      + '<button class="btn grande add-p" data-id="' + id + '" data-prop=\'' + JSON.stringify({ id: id, titulo: p.titulo, esp: p.esp, eje: p.eje, tipo: p.tipo }).replace(/'/g, '&#39;') + '\'>Agregar al carrito</button>';
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function cerrar() { modal.hidden = true; document.body.style.overflow = ''; }
  document.addEventListener('click', e => {
    const v = e.target.closest('.ver-p');
    if (v) { e.preventDefault(); abrir(v.dataset.id); }
  });
  document.getElementById('pm-cerrar').addEventListener('click', cerrar);
  modal.addEventListener('click', e => { if (e.target === modal) cerrar(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) cerrar(); });

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  aplicar();
})();
