// /b?p=..&g=..&i=..&l=a,b  Link corto de una boleta compartida.
// Devuelve un HTML con las etiquetas Open Graph de esa boleta (para WhatsApp, X, etc.)
// y redirige a la persona a /boleta con los mismos parámetros.
import MV from './_data.js';

const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function GET(request) {
  const url = new URL(request.url);
  const q = new URLSearchParams();
  ['p', 'g', 'i'].forEach(k => { const v = url.searchParams.get(k); if (v && MV.c[v]) q.set(k, v); });
  const legs = (url.searchParams.get('l') || '').split(',').filter(x => MV.c[x]).slice(0, 5);
  if (legs.length) q.set('l', legs.join(','));
  const qs = q.toString().replace(/%2C/g, ',');
  const dest = '/boleta' + (qs ? '?' + qs : '');

  const nombres = ['p', 'g', 'i'].map(k => q.get(k)).filter(Boolean).map(id => MV.c[id].n);
  const titulo = nombres.length ? 'Mi boleta: ' + nombres.join(' · ') : 'Mi boleta en Mercado Voto';
  const desc = (legs.length ? 'Y ' + legs.length + ' legislador' + (legs.length > 1 ? 'es' : '') + '. ' : '') + '¿Y vos qué comprarías? Armá la tuya en Mercado Voto.';
  const img = url.origin + '/api/og' + (qs ? '?' + qs : '');

  const html = `<!DOCTYPE html><html lang="es-AR"><head><meta charset="utf-8">
<title>${esc(titulo)}</title>
<meta name="description" content="${esc(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Mercado Voto">
<meta property="og:title" content="${esc(titulo)}"><meta property="og:description" content="${esc(desc)}">
<meta property="og:image" content="${esc(img)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="${esc(url.origin + '/b' + (qs ? '?' + qs : ''))}">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url=${esc(dest)}">
<link rel="canonical" href="${esc(url.origin + dest)}">
</head><body><script>location.replace(${JSON.stringify(dest)})</script><a href="${esc(dest)}">Ver la boleta</a></body></html>`;
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=0, s-maxage=86400' } });
}
