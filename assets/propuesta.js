// Página de una propuesta: compartir la ficha.
(() => {
  const P = window.PROP;
  document.querySelectorAll('.share-row [data-share]').forEach(b => b.addEventListener('click', () => {
    track('comparte', 'propuesta-' + b.dataset.share);
    compartirLink(b.dataset.share, '“' + P.titulo + '” (' + P.esp + '). Cómo funcionaría, quién paga y las fuentes, en Mercado Voto 👇', location.origin + '/p/' + P.slug);
  }));
})();
