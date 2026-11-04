// Genera el comprobante del voto como PNG y lo comparte o descarga.
const W = 1080, H = 1350;

function rrect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function wrap(ctx, texto, x, y, ancho, alto) {
  const palabras = String(texto).split(' ');
  let linea = '', lineas = [];
  palabras.forEach(p => {
    const t = linea ? linea + ' ' + p : p;
    if (ctx.measureText(t).width > ancho && linea) { lineas.push(linea); linea = p; }
    else linea = t;
  });
  if (linea) lineas.push(linea);
  lineas.forEach((l, i) => ctx.fillText(l, x, y + i * alto));
  return y + lineas.length * alto;
}

function cargarFoto(src) {
  return new Promise(res => {
    if (!src) return res(null);
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => res(img);
    img.onerror = () => res(null);
    img.src = src;
  });
}

async function tarjetaVoto(c, extra) {
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  const color = c.color || '#3483fa';

  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#ffe600'; ctx.fillRect(0, 0, W, 190);

  // marca
  ctx.fillStyle = '#2d2d2d';
  ctx.font = '700 54px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('mercado', 90, 118);
  ctx.font = '800 54px Inter, system-ui, sans-serif';
  ctx.fillText('voto', 330, 118);
  ctx.textAlign = 'right';
  ctx.font = '500 30px Inter, system-ui, sans-serif';
  ctx.fillText('SIMULADOR', 990, 112);

  ctx.fillStyle = color; ctx.fillRect(0, 190, W, 10);

  // foto circular
  const img = await cargarFoto(c.foto ? '/' + c.foto : '');
  const cx = W / 2, cy = 470, r = 190;
  ctx.save();
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.closePath(); ctx.clip();
  if (img) {
    const s = Math.max((2 * r) / img.width, (2 * r) / img.height);
    ctx.drawImage(img, cx - img.width * s / 2, cy - img.height * s / 2 - 20, img.width * s, img.height * s);
  } else {
    ctx.fillStyle = color; ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center';
    ctx.font = '700 120px Inter, system-ui, sans-serif';
    ctx.fillText(c.iniciales || '', cx, cy + 42);
  }
  ctx.restore();
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.strokeStyle = color; ctx.lineWidth = 8; ctx.stroke();

  // nombre, con ajuste de tamaño para que entre en una línea
  ctx.textAlign = 'center'; ctx.fillStyle = '#222';
  let tam = 62;
  for (const t of [62, 54, 46, 40]) { tam = t; ctx.font = '700 ' + t + 'px Inter, system-ui, sans-serif'; if (ctx.measureText(c.nombre).width <= 900) break; }
  ctx.fillText(c.nombre, cx, 742);

  ctx.font = '500 34px Inter, system-ui, sans-serif';
  ctx.fillStyle = '#777';
  ctx.fillText(c.partido + (c.jur && c.jur !== 'Nacional' ? ' · ' + c.jur : ''), cx, 800);

  // cargo
  const etiqueta = (c.cargo || 'presidencial').toUpperCase();
  ctx.font = '600 26px Inter, system-ui, sans-serif';
  const anchoEt = ctx.measureText(etiqueta).width + 60;
  ctx.fillStyle = '#f2f2f2';
  rrect(ctx, cx - anchoEt / 2, 838, anchoEt, 54, 27); ctx.fill();
  ctx.fillStyle = '#666';
  ctx.fillText(etiqueta, cx, 874);

  // precio
  ctx.fillStyle = '#222';
  ctx.font = '700 96px Inter, system-ui, sans-serif';
  ctx.fillText('1 voto', cx, 1032);
  ctx.font = '500 30px Inter, system-ui, sans-serif';
  ctx.fillStyle = '#00a650';
  ctx.fillText('por período de 4 años', cx, 1082);

  // pie
  ctx.fillStyle = '#f5f5f5'; ctx.fillRect(0, H - 150, W, 150);
  ctx.fillStyle = '#666'; ctx.font = '500 28px Inter, system-ui, sans-serif';
  ctx.fillText('mercado-voto.vercel.app', cx, H - 92);
  ctx.fillStyle = '#999'; ctx.font = '400 22px Inter, system-ui, sans-serif';
  ctx.fillText('Simulador. No es una encuesta ni un voto real.', cx, H - 52);

  return cv;
}

async function entregar(cv, nombre) {
  const blob = await new Promise(r => cv.toBlob(r, 'image/png'));
  const file = new File([blob], nombre, { type: 'image/png' });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], title: 'Mi voto en Mercado Voto' }); return; } catch (e) {}
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

async function descargarVoto() {
  const b = document.querySelectorAll('.btn');
  const cv = await tarjetaVoto(window.CAND);
  await entregar(cv, 'mi-voto-' + window.CAND.slug + '.png');
}


// ---------- boleta completa ----------
async function tarjetaBoleta(items) {
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');

  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#ffe600'; ctx.fillRect(0, 0, W, 170);
  ctx.fillStyle = '#2d2d2d'; ctx.textAlign = 'left';
  ctx.font = '800 46px Inter, system-ui, sans-serif';
  ctx.fillText('mercado voto', 80, 100);
  ctx.textAlign = 'right'; ctx.font = '600 28px Inter, system-ui, sans-serif';
  ctx.fillText('MI BOLETA', 1000, 97);
  ctx.fillStyle = '#2d2d2d'; ctx.fillRect(0, 170, W, 8);

  const buscar = c => items.find(x => x.c === c);
  const linea = (etiqueta, it, y) => {
    ctx.textAlign = 'left';
    ctx.fillStyle = '#999'; ctx.font = '600 22px Inter, system-ui, sans-serif';
    ctx.fillText(etiqueta.toUpperCase(), 80, y);
    ctx.fillStyle = it ? '#222' : '#ccc';
    ctx.font = '700 46px Inter, system-ui, sans-serif';
    ctx.fillText(it ? it.n : 'Sin elegir', 80, y + 52);
    if (it) {
      ctx.fillStyle = '#777'; ctx.font = '500 26px Inter, system-ui, sans-serif';
      ctx.fillText(it.p + (it.j && it.j !== 'Nacional' ? ' · ' + it.j : ''), 80, y + 92);
    }
    ctx.strokeStyle = '#eee'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(80, y + 122); ctx.lineTo(1000, y + 122); ctx.stroke();
  };

  linea('Presidente', buscar('presidencial'), 250);
  linea('Gobernador', buscar('gobernador'), 420);
  linea('Intendente', buscar('intendente'), 590);

  const legs = items.filter(x => x.c === 'legislador');
  ctx.fillStyle = '#999'; ctx.font = '600 22px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('LEGISLADORES  ·  ' + legs.length + ' DE 5', 80, 760);
  if (!legs.length) {
    ctx.fillStyle = '#ccc'; ctx.font = '700 40px Inter, system-ui, sans-serif';
    ctx.fillText('Sin elegir', 80, 812);
  } else {
    legs.forEach((l, i) => {
      const y = 812 + i * 62;
      ctx.fillStyle = l.color || '#3483fa';
      ctx.beginPath(); ctx.arc(96, y - 12, 9, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#222'; ctx.font = '600 32px Inter, system-ui, sans-serif';
      ctx.fillText(l.n, 125, y);
      ctx.fillStyle = '#999'; ctx.font = '400 22px Inter, system-ui, sans-serif';
      ctx.textAlign = 'right'; ctx.fillText(l.j || '', 1000, y); ctx.textAlign = 'left';
    });
  }

  ctx.fillStyle = '#f5f5f5'; ctx.fillRect(0, H - 150, W, 150);
  ctx.textAlign = 'center'; ctx.fillStyle = '#333'; ctx.font = '700 30px Inter, system-ui, sans-serif';
  ctx.fillText('Armé mi boleta de candidatos', W / 2, H - 92);
  ctx.fillStyle = '#999'; ctx.font = '400 24px Inter, system-ui, sans-serif';
  ctx.fillText('mercado-voto.vercel.app · simulador', W / 2, H - 52);

  return cv;
}

async function descargarBoleta(items) {
  const cv = await tarjetaBoleta(items);
  await entregar(cv, 'mi-boleta.png');
}
