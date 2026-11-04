// Genera la imagen de la boleta (post 4:5 o historia 9:16) y la comparte o descarga.
const FMT = { post: [1080, 1350], story: [1080, 1920] };
const FONT = 'Inter, system-ui, -apple-system, sans-serif';

function rrect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function cargarFoto(src) {
  return new Promise(res => {
    if (!src) return res(null);
    const img = new Image();
    img.onload = () => res(img);
    img.onerror = () => res(null);
    img.src = src;
  });
}

// Escribe texto achicando la fuente hasta que entre en el ancho, en hasta dos líneas.
function texto(ctx, t, x, y, ancho, peso, tam, min, lh) {
  for (let s = tam; s >= min; s -= 2) {
    ctx.font = peso + ' ' + s + 'px ' + FONT;
    if (ctx.measureText(t).width <= ancho) { ctx.fillText(t, x, y); return y + s * (lh || 1.15); }
  }
  // dos líneas
  ctx.font = peso + ' ' + min + 'px ' + FONT;
  const p = t.split(' ');
  let a = '', k = 0;
  while (k < p.length && ctx.measureText((a + ' ' + p[k]).trim()).width <= ancho) a = (a + ' ' + p[k++]).trim();
  let b = p.slice(k).join(' ');
  while (b && ctx.measureText(b).width > ancho) b = b.slice(0, -2) + '…';
  ctx.fillText(a, x, y);
  ctx.fillText(b, x, y + min * 1.12);
  return y + min * 1.12 * 2;
}

function circulo(ctx, img, it, cx, cy, r) {
  ctx.save();
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.closePath(); ctx.clip();
  if (img) {
    const s = Math.max((2 * r) / img.width, (2 * r) / img.height);
    ctx.drawImage(img, cx - img.width * s / 2, cy - img.height * s * 0.38, img.width * s, img.height * s);
  } else {
    ctx.fillStyle = it ? it.color : '#eee'; ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    if (it) { ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.font = '800 ' + Math.round(r * .7) + 'px ' + FONT; ctx.fillText(it.i, cx, cy + r * .25); }
  }
  ctx.restore();
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.lineWidth = Math.max(4, r * .06); ctx.strokeStyle = it ? it.color : '#ddd'; ctx.stroke();
}

function vacio(ctx, cx, cy, r) {
  ctx.save();
  ctx.setLineDash([10, 8]); ctx.lineWidth = 4; ctx.strokeStyle = '#ccc';
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
  ctx.fillStyle = '#bbb'; ctx.textAlign = 'center'; ctx.font = '700 ' + Math.round(r * .55) + 'px ' + FONT;
  ctx.fillText('?', cx, cy + r * .2);
}

function corto(n) {
  const p = n.split(' ');
  return p.length > 1 ? p[0][0] + '. ' + p.slice(1).join(' ') : n;
}

async function tarjetaBoleta(items, pf, formato) {
  try { await document.fonts.ready; } catch (e) {}
  const [W, H] = FMT[formato] || FMT.post;
  const st = formato === 'story';
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  const fotos = await Promise.all(items.map(it => cargarFoto(it.f ? '/' + it.f : '')));
  const fotoDe = it => fotos[items.indexOf(it)];

  // fondo
  ctx.fillStyle = '#f2f2f2'; ctx.fillRect(0, 0, W, H);
  const hdr = st ? 230 : 150;
  ctx.fillStyle = '#ffe600'; ctx.fillRect(0, 0, W, hdr);

  // marca
  const my = st ? 128 : 92;
  ctx.fillStyle = '#2d2d2d'; rrect(ctx, 64, my - 42, 60, 60, 14); ctx.fill();
  ctx.fillStyle = '#ffe600'; ctx.font = '900 40px ' + FONT; ctx.textAlign = 'center'; ctx.fillText('✓', 94, my + 2);
  ctx.textAlign = 'left'; ctx.fillStyle = '#2d2d2d';
  ctx.font = '500 46px ' + FONT; ctx.fillText('mercado', 142, my + 4);
  const wm = ctx.measureText('mercado ').width;
  ctx.font = '900 46px ' + FONT; ctx.fillText('voto', 142 + wm, my + 4);
  ctx.textAlign = 'right'; ctx.font = '800 26px ' + FONT;
  const et = 'MI BOLETA';
  const ew = ctx.measureText(et).width + 44;
  ctx.fillStyle = '#2d2d2d'; rrect(ctx, W - 64 - ew, my - 36, ew, 52, 26); ctx.fill();
  ctx.fillStyle = '#ffe600'; ctx.textAlign = 'center'; ctx.fillText(et, W - 64 - ew / 2, my - 1);

  // tarjeta blanca principal
  const top = hdr + (st ? 70 : 34);
  const pie = st ? 330 : 150;
  const alto = H - top - pie;
  ctx.fillStyle = '#fff'; rrect(ctx, 40, top, W - 80, alto, 28); ctx.fill();

  // ejecutivos
  const col = (W - 80) / 3;
  const r = st ? 150 : 116;
  const ey = top + (st ? 110 : 46) + r;
  [['presidencial', 'PRESIDENTE'], ['gobernador', 'GOBERNADOR'], ['intendente', 'INTENDENTE']].forEach(([cg, etq], k) => {
    const cx = 40 + col * k + col / 2;
    const it = items.find(x => x.c === cg);
    it ? circulo(ctx, fotoDe(it), it, cx, ey, r) : vacio(ctx, cx, ey, r);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#3483fa'; ctx.font = '800 21px ' + FONT;
    ctx.fillText(etq + (it && it.j && it.j !== 'Nacional' ? ' · ' + it.j.toUpperCase() : ''), cx, ey + r + 46);
    ctx.fillStyle = it ? '#222' : '#bbb';
    const y2 = texto(ctx, it ? it.n : 'Sin elegir', cx, ey + r + 90, col - 30, '800', st ? 38 : 34, 26);
    if (it) { ctx.fillStyle = '#888'; texto(ctx, it.p, cx, y2 + 2, col - 30, '500', 22, 17); }
  });

  // legisladores
  const ly = ey + r + (st ? 340 : 228);
  ctx.strokeStyle = '#eee'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(90, ly - 40); ctx.lineTo(W - 90, ly - 40); ctx.stroke();
  const legs = items.filter(x => x.c === 'legislador');
  ctx.textAlign = 'center'; ctx.fillStyle = '#3483fa'; ctx.font = '800 21px ' + FONT;
  ctx.fillText('LEGISLADORES · ' + legs.length + ' DE 5', W / 2, ly);
  const lr = st ? 86 : 66;
  const lc = (W - 120) / 5;
  for (let k = 0; k < 5; k++) {
    const cx = 60 + lc * k + lc / 2, cy = ly + 34 + lr;
    const it = legs[k];
    it ? circulo(ctx, fotoDe(it), it, cx, cy, lr) : vacio(ctx, cx, cy, lr);
    ctx.fillStyle = it ? '#333' : '#bbb'; ctx.textAlign = 'center';
    texto(ctx, it ? corto(it.n) : 'Libre', cx, cy + lr + 38, lc - 12, '700', 22, 16);
  }

  // perfil
  const py = top + alto - (st ? 250 : 170);
  if (pf) {
    ctx.fillStyle = '#fff8cc'; rrect(ctx, 80, py, W - 160, st ? 190 : 130, 22); ctx.fill();
    ctx.textAlign = 'left';
    ctx.font = (st ? 96 : 72) + 'px ' + FONT; ctx.fillText(pf.emoji, 110, py + (st ? 128 : 92));
    const tx = st ? 240 : 200;
    ctx.fillStyle = '#7a5c00'; ctx.font = '700 22px ' + FONT; ctx.fillText('MI BOLETA ES', tx, py + (st ? 62 : 44));
    ctx.fillStyle = '#222'; ctx.font = '900 ' + (st ? 60 : 48) + 'px ' + FONT; ctx.fillText(pf.tipo, tx, py + (st ? 124 : 94));
    if (pf.rasgos.length) { ctx.fillStyle = '#7a5c00'; ctx.font = '500 ' + (st ? 28 : 22) + 'px ' + FONT; ctx.fillText('Tirando a ' + pf.rasgos.join(' y ').toLowerCase(), tx, py + (st ? 164 : 120)); }
  }

  // pie
  ctx.textAlign = 'center';
  ctx.fillStyle = '#2d2d2d'; ctx.font = '900 ' + (st ? 52 : 38) + 'px ' + FONT;
  ctx.fillText('¿Y vos qué comprarías?', W / 2, H - pie + (st ? 130 : 62));
  ctx.fillStyle = '#3483fa'; ctx.font = '700 ' + (st ? 36 : 28) + 'px ' + FONT;
  ctx.fillText('Armá la tuya en ' + location.host, W / 2, H - pie + (st ? 196 : 108));
  return cv;
}

async function entregar(cv, nombre) {
  const blob = await new Promise(r => cv.toBlob(r, 'image/png'));
  const file = new File([blob], nombre, { type: 'image/png' });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], title: 'Mi boleta en Mercado Voto' }); return; } catch (e) { if (e.name === 'AbortError') return; }
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  if (typeof aviso === 'function') aviso('Imagen descargada. Subila a tus redes.');
}

async function descargarBoleta(items, pf, formato) {
  const cv = await tarjetaBoleta(items, pf, formato);
  await entregar(cv, formato === 'story' ? 'mi-boleta-historia.png' : 'mi-boleta.png');
}
