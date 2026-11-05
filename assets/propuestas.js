// Página de propuestas: filtros en la columna izquierda, detalle y carrito.
(function () {
  const grid = document.getElementById('pgrid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.prop'));
  const estado = { esp: '', eje: '', tipo: 'propuesta', est: '', q: '' };
  const cuenta = document.getElementById('p-cuenta');
  const vacio = document.getElementById('pvacio');
  const titulo = document.getElementById('p-titulo');

  const TIPO_TITULO = { propuesta: 'Todas las propuestas', vision: 'Visiones de país', futuro: 'Futuros posibles' };

  function aplicar() {
    let n = 0;
    for (const c of cards) {
      const ok = (!estado.esp || c.dataset.esp === estado.esp)
        && (!estado.eje || c.dataset.eje === estado.eje)
        && (!estado.tipo || c.dataset.tipo === estado.tipo)
        && (!estado.est || c.dataset.estado === estado.est)
        && (!estado.q || c.dataset.busca.includes(estado.q));
      c.hidden = !ok;
      if (ok) n++;
    }
    cuenta.textContent = n + (n === 1 ? ' resultado' : ' resultados');
    vacio.hidden = n > 0;
    if (titulo) titulo.textContent = TIPO_TITULO[estado.tipo] || 'Propuestas';

    // conteos por eje según espacio y tipo (sin aplicar el eje)
    const base = cards.filter(c => (!estado.esp || c.dataset.esp === estado.esp)
      && (!estado.tipo || c.dataset.tipo === estado.tipo));
    const cnt = {};
    base.forEach(c => { cnt[c.dataset.eje] = (cnt[c.dataset.eje] || 0) + 1; });
    document.querySelectorAll('.cat-item').forEach(b => {
      const v = b.dataset.v;
      const k = b.querySelector('b');
      if (k) k.textContent = v ? (cnt[v] || 0) : base.length;
    });
  }

  document.addEventListener('click', e => {
    const el = e.target.closest('[data-f]');
    if (!el) return;
    e.preventDefault();
    const f = el.dataset.f;
    estado[f] = el.dataset.v;
    document.querySelectorAll('[data-f="' + f + '"]').forEach(o => o.classList.toggle('on', o === el));
    aplicar();
  });

  document.querySelectorAll('.pcat').forEach(cat => {
    cat.addEventListener('click', () => {
      const t = cat.dataset.tipo;
      estado.tipo = t;
      document.querySelectorAll('.pcat').forEach(o => o.classList.toggle('on', o === cat));
      document.querySelectorAll('[data-f="tipo"]').forEach(o => o.classList.toggle('on', o.dataset.v === t));
      aplicar();
    });
  });

  // parámetros de la URL: ?tipo=vision&esp=lla&eje=economia
  const qs = new URLSearchParams(location.search);
  ['tipo', 'esp', 'eje', 'est'].forEach(k => {
    const v = qs.get(k);
    if (!v) return;
    estado[k] = v;
    document.querySelectorAll('[data-f="' + k + '"]').forEach(o => o.classList.toggle('on', o.dataset.v === v));
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

  aplicar();
})();
