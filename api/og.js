// Imagen de preview (1200x630) para links compartidos.
//   /api/og                     portada genérica
//   /api/og?c=<id>              ficha de un candidato
//   /api/og?p=..&g=..&i=..&l=a,b boleta compartida
import { ImageResponse } from '@vercel/og';
import { readFileSync } from 'node:fs';
import MV from './_data.js';

const FONTS = [400, 500, 600, 700, 800, 900].map(weight => ({
  name: 'Inter', weight, style: 'normal',
  data: readFileSync(new URL(`./_fonts/inter-${weight}.woff`, import.meta.url)),
}));

// Las fotos se leen del disco (no por HTTP): así funciona también en previews protegidos.
const cacheFotos = new Map();
function foto(ruta) {
  if (!cacheFotos.has(ruta)) {
    let uri = null;
    try {
      const buf = readFileSync(new URL('../' + ruta, import.meta.url));
      const tipo = buf[0] === 0x89 ? 'image/png' : buf[0] === 0x52 ? 'image/webp' : 'image/jpeg';
      uri = `data:${tipo};base64,${buf.toString('base64')}`;
    } catch (e) {}
    cacheFotos.set(ruta, uri);
  }
  return cacheFotos.get(ruta);
}

const AZUL = '#3483fa', AMARILLO = '#ffe600', OSCURO = '#2d2d2d';

function h(type, style, ...children) {
  const kids = children.flat().filter(x => x !== null && x !== undefined && x !== false);
  return { type, props: { style: { display: 'flex', ...style }, children: kids.length === 1 ? kids[0] : kids } };
}
const img = (src, style) => ({ type: 'img', props: { src, style } });

function avatar(c, size, borde = 6) {
  const st = { width: size, height: size, borderRadius: size, border: `${borde}px solid ${c.col}`, objectFit: 'cover', objectPosition: 'center 18%' };
  if (c.f && foto(c.f)) return img(foto(c.f), st);
  return h('div', { ...st, background: c.col, color: '#fff', fontSize: size * 0.36, fontWeight: 800, alignItems: 'center', justifyContent: 'center' }, c.i);
}
const hueco = size => h('div', { width: size, height: size, borderRadius: size, border: '5px dashed #ccc', alignItems: 'center', justifyContent: 'center', color: '#bbb', fontSize: size * 0.4, fontWeight: 800 }, '?');

const svg = s => 'data:image/svg+xml;base64,' + Buffer.from(s).toString('base64');
const MARK = svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 132 120"><ellipse cx="66" cy="60" rx="58" ry="46" stroke="#00368C" stroke-width="4" fill="none"/><g stroke="#00368C" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"><path d="M56 62h44v28H56z" fill="#fff"/><g transform="rotate(-15 64 44)"><rect x="52" y="24" width="23" height="36" rx="2" fill="#fff"/><path d="M57 40l4 4 8.5-9" fill="none" stroke-width="4"/></g><path d="M56 62l8-8h44l-8 8z" fill="#fff"/><path d="M70 58h24" stroke-width="5.5"/><g fill="#fff"><rect x="14" y="28" width="26" height="30" rx="11"/><rect x="30" y="27" width="20" height="9" rx="4.5"/><rect x="30" y="37" width="20" height="9" rx="4.5"/><rect x="30" y="47" width="18" height="9" rx="4.5"/><rect x="24" y="55" width="20" height="9" rx="4.5" transform="rotate(18 34 59)"/></g></g></svg>');
const estrella = lleno => svg(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z" fill="${lleno ? AZUL : 'none'}" stroke="${AZUL}" stroke-width="1.6" stroke-linejoin="round"/></svg>`);

function marca(tam = 40) {
  return h('div', { alignItems: 'center', gap: 14 },
    img(MARK, { width: tam * 1.35, height: tam * 1.22 }),
    h('div', { fontSize: tam, color: '#00368C', letterSpacing: -2, flexDirection: 'column', lineHeight: 0.95 },
      h('span', { fontWeight: 800 }, 'mercado'), h('span', { fontWeight: 800 }, 'voto')));
}

const POLOS = MV.polos;
const TIPOS = [[9, '🐎', 'Pura sangre'], [15, '🧭', 'Coherente'], [21, '🥗', 'Ensalada mixta'], [99, '🧟', 'Frankenstein']];
function perfil(ids) {
  const ejes = ids.map(id => MV.c[id].e);
  if (ejes.length < 2) return null;
  const media = [0, 1, 2, 3, 4, 5].map(k => ejes.reduce((s, e) => s + e[k], 0) / ejes.length);
  const disp = [0, 1, 2, 3, 4, 5].map(k => Math.sqrt(ejes.reduce((s, e) => s + (e[k] - media[k]) ** 2, 0) / ejes.length)).reduce((a, b) => a + b, 0) / 6;
  const t = TIPOS.find(t => disp < t[0]);
  const rasgos = media.map((v, k) => [Math.abs(v - 50), k, v]).filter(r => r[0] >= 12).sort((a, b) => b[0] - a[0]).slice(0, 2).map(([, k, v]) => POLOS[k][v > 50 ? 2 : 1]);
  return { emoji: t[1], tipo: t[2], rasgos };
}

function boleta(q) {
  const id = k => (MV.c[q.get(k)] ? q.get(k) : null);
  const ej = [['p', 'PRESIDENTE'], ['g', 'GOBERNADOR'], ['i', 'INTENDENTE']].map(([k, et]) => [id(k), et]);
  const legs = (q.get('l') || '').split(',').filter(x => MV.c[x]).slice(0, 5);
  const todos = [...ej.map(e => e[0]).filter(Boolean), ...legs];
  const pf = perfil(todos);
  return h('div', { width: '100%', height: '100%', flexDirection: 'column', background: '#ededed', fontFamily: 'Inter' },
    h('div', { height: 96, background: AMARILLO, alignItems: 'center', justifyContent: 'space-between', padding: '0 48px' },
      marca(38),
      h('div', { background: OSCURO, color: AMARILLO, fontSize: 24, fontWeight: 800, padding: '10px 22px', borderRadius: 30, letterSpacing: 1 }, 'MI BOLETA')),
    h('div', { flex: 1, margin: '24px 40px 0', background: '#fff', borderRadius: '24px 24px 0 0', padding: '28px 30px 0', flexDirection: 'column' },
      h('div', { justifyContent: 'space-around' },
        ej.map(([cid, et]) => {
          const c = cid && MV.c[cid];
          return h('div', { flexDirection: 'column', alignItems: 'center', width: 330 },
            c ? avatar(c, 170) : hueco(170),
            h('div', { color: AZUL, fontSize: 18, fontWeight: 800, marginTop: 12, letterSpacing: 1 }, et),
            h('div', { fontSize: c && c.n.length > 20 ? 27 : 32, fontWeight: 800, color: c ? '#222' : '#bbb', marginTop: 2, textAlign: 'center' }, c ? c.n : 'Sin elegir'));
        })),
      h('div', { marginTop: 26, alignItems: 'center', justifyContent: 'space-between', borderTop: '2px solid #eee', paddingTop: 20 },
        h('div', { alignItems: 'center', gap: 10 },
          h('div', { color: AZUL, fontSize: 18, fontWeight: 800, letterSpacing: 1, marginRight: 8 }, 'LEGISLADORES'),
          legs.length ? legs.map(x => avatar(MV.c[x], 64, 4)) : h('div', { color: '#bbb', fontSize: 24 }, 'Sin elegir')),
        pf ? h('div', { alignItems: 'center', gap: 12, background: '#fff8cc', padding: '10px 22px', borderRadius: 18 },
          h('div', { fontSize: 46 }, pf.emoji),
          h('div', { flexDirection: 'column' },
            h('div', { fontSize: 15, color: '#7a5c00', fontWeight: 700, letterSpacing: 1 }, 'BOLETA'),
            h('div', { fontSize: 32, fontWeight: 900, color: '#222', lineHeight: 1 }, pf.tipo))) : null)),
    h('div', { height: 64, background: OSCURO, color: '#fff', alignItems: 'center', justifyContent: 'center', fontSize: 26, fontWeight: 700, gap: 14 },
      '¿Y vos qué comprarías?', h('span', { color: AMARILLO }, 'Armá la tuya →')));
}

function candidato(c) {
  const n = Math.max(1, Math.round((c.cu / (c.to || 1)) * 5));
  return h('div', { width: '100%', height: '100%', background: '#fff', fontFamily: 'Inter' },
    c.f && foto(c.f) ? img(foto(c.f), { width: 560, height: 630, objectFit: 'cover', objectPosition: 'center 15%' })
      : h('div', { width: 560, height: 630, background: c.col, color: '#fff', fontSize: 200, fontWeight: 800, alignItems: 'center', justifyContent: 'center' }, c.i),
    h('div', { flex: 1, flexDirection: 'column', padding: '44px 48px', justifyContent: 'space-between', borderTop: `14px solid ${AMARILLO}` },
      h('div', { flexDirection: 'column' },
        h('div', { fontSize: 22, color: '#999' }, c.p),
        h('div', { fontSize: c.n.length > 22 ? 50 : 60, fontWeight: 800, color: '#222', lineHeight: 1.05, marginTop: 6, letterSpacing: -2 }, c.n),
        h('div', { fontSize: 26, color: '#666', marginTop: 14, fontStyle: 'italic', lineHeight: 1.3 }, c.g),
        c.to ? h('div', { alignItems: 'center', marginTop: 18, gap: 4 }, [0, 1, 2, 3, 4].map(k => img(estrella(k < n), { width: 30, height: 30 })), h('span', { color: '#999', fontSize: 20, marginLeft: 10 }, `${c.cu} de ${c.to} promesas cumplidas`)) : null),
      h('div', { flexDirection: 'column' },
        h('div', { fontSize: 72, fontWeight: 400, color: '#222', letterSpacing: -2 }, '1 voto'),
        h('div', { fontSize: 24, color: '#00a650', fontWeight: 600 }, 'Envío gratis a tu urna'),
        h('div', { marginTop: 22, justifyContent: 'space-between', alignItems: 'center' },
          marca(30),
          c.le ? h('div', { fontSize: 20, color: '#c8102e', fontWeight: 700, background: '#ffe3e5', padding: '6px 14px', borderRadius: 20 }, `⚠ ${c.le} crítica${c.le > 1 ? 's' : ''} letal${c.le > 1 ? 'es' : ''}`) : null))));
}

function portada() {
  const caras = ['milei', 'cristina', 'kicillof', 'bullrich', 'macri', 'bregman', 'massa', 'villarruel'].filter(id => MV.c[id]);
  return h('div', { width: '100%', height: '100%', background: AMARILLO, fontFamily: 'Inter', padding: '56px 64px', flexDirection: 'column', justifyContent: 'space-between' },
    marca(48),
    h('div', { flexDirection: 'column' },
      h('div', { fontSize: 76, fontWeight: 900, color: OSCURO, lineHeight: 1, letterSpacing: -3 }, 'Armá tu boleta'),
      h('div', { fontSize: 76, fontWeight: 900, color: OSCURO, lineHeight: 1.05, letterSpacing: -3 }, 'como si fuera un carrito'),
      h('div', { fontSize: 28, color: '#5a4f00', marginTop: 16 }, 'Lo bueno, lo malo y las críticas de cada candidato.')),
    h('div', { alignItems: 'center' },
      caras.map((id, k) => h('div', { marginLeft: k ? -22 : 0 }, avatar(MV.c[id], 96, 5))),
      h('div', { marginLeft: 26, background: OSCURO, color: '#fff', fontSize: 28, fontWeight: 700, padding: '16px 28px', borderRadius: 40 }, '1 voto c/u · envío gratis')));
}

export async function GET(request) {
  const url = new URL(request.url);
  const q = url.searchParams;
  let el;
  if (q.get('c') && MV.c[q.get('c')]) el = candidato(MV.c[q.get('c')]);
  else if (['p', 'g', 'i', 'l'].some(k => q.get(k))) el = boleta(q);
  else el = portada();
  return new ImageResponse(el, {
    width: 1200, height: 630, emoji: 'twemoji', fonts: FONTS,
    headers: { 'Cache-Control': 'public, max-age=86400, s-maxage=604800, immutable' },
  });
}
