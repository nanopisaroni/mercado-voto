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

  document.querySelectorAll('.share-row [data-share]').forEach(b => b.addEventListener('click', () => {
    const url = location.origin + '/c/' + F.slug;
    compartirLink(b.dataset.share, F.nombre + ' en Mercado Voto: “' + F.gancho + '” Mirá lo bueno, lo malo y las críticas 👇', url);
  }));
  pintar();
})();
