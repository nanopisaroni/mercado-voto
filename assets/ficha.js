// Página de candidato: compra con el cargo elegido y botones para compartir la ficha.
(() => {
  const F = window.FICHA;
  const cargoElegido = () => {
    const sel = document.getElementById('sel-cargo');
    return F.cargos[sel ? +sel.value : 0];
  };
  const pintar = () => {
    const [cargo] = cargoElegido() || [];
    const en = leer().some(x => x.i === F.id && x.c === cargo);
    const btn = document.getElementById('agregar');
    btn.textContent = en ? '✓ En tu boleta' : 'Agregar a la boleta';
    btn.classList.toggle('en', en);
  };

  document.getElementById('comprar').addEventListener('click', () => {
    const [cargo, jur] = cargoElegido();
    agregar(F.id, cargo, jur);
    location.href = '/boleta';
  });
  document.getElementById('agregar').addEventListener('click', e => {
    const [cargo, jur] = cargoElegido();
    if (e.currentTarget.classList.contains('en')) { quitarCand(F.id, cargo); aviso(F.nombre + ' salió de tu boleta'); }
    else { const r = agregar(F.id, cargo, jur); aviso(r.msg, r.ok ? { href: '/boleta', txt: 'Ver boleta' } : null); }
    pintar();
  });
  const sel = document.getElementById('sel-cargo');
  if (sel) sel.addEventListener('change', pintar);

  // Vista de la ficha, una vez por sesión, para el ranking de tendencia.
  try {
    if (!sessionStorage.getItem('mv_vf_' + F.id)) { sessionStorage.setItem('mv_vf_' + F.id, '1'); track('ver_ficha', F.id); }
  } catch (e) {}

  document.querySelectorAll('.share-row [data-share]').forEach(b => b.addEventListener('click', () => {
    const url = location.origin + '/c/' + F.slug;
    track('comparte', 'ficha-' + b.dataset.share);
    compartirLink(b.dataset.share, F.nombre + ' en Mercado Voto: “' + F.gancho + '” Mirá lo bueno, lo malo y las críticas 👇', url);
  }));
  pintar();
})();

// Videos: se carga el iframe recién al hacer clic.
document.addEventListener('click', e => {
  const v = e.target.closest('.vid');
  if (!v || v.dataset.done) return;
  v.dataset.done = '1';
  const id = v.dataset.vid;
  v.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id +
    '?autoplay=1&rel=0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="Video del candidato"></iframe>';
});
