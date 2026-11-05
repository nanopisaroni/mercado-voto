// POST /api/voto  {id, b: [{i, c}]}
// Cuenta una boleta finalizada para el ranking de los más elegidos. Anónimo: el id es aleatorio y vive
// en el navegador. Si la misma boleta se vuelve a finalizar, se descuenta lo anterior y se suma lo nuevo.
import MV from './_data.js';
import { pipeline, hayRedis, json, limitado } from './_redis.js';

const CARGOS = ['presidencial', 'gobernador', 'intendente', 'legislador'];
const jurDe = (cid, cargo) => (MV.k.find(k => k[0] === cid && k[1] === cargo) || [])[2];

function limpiar(b) {
  if (!Array.isArray(b)) return null;
  const vistos = new Set(), out = [];
  for (const x of b.slice(0, 8)) {
    const jur = x && CARGOS.includes(x.c) && jurDe(x.i, x.c);
    if (!jur || vistos.has(x.i)) continue;
    if (x.c !== 'legislador' && out.some(y => y.c === x.c)) continue;
    if (x.c === 'legislador' && out.filter(y => y.c === 'legislador').length >= 5) continue;
    vistos.add(x.i);
    out.push({ i: x.i, c: x.c, j: jur });
  }
  return out;
}
const miembro = x => `${x.i}|${x.j}`;

export async function POST(request) {
  if (process.env.RANKING_OFF) return json({ off: true });
  if (!hayRedis) return json({ ok: false, motivo: 'sin-redis' }, 503);
  let body;
  try { body = await request.json(); } catch (e) { return json({ ok: false }, 400); }
  const id = String(body.id || '');
  const b = limpiar(body.b);
  if (!/^[a-z0-9]{10,40}$/.test(id) || !b || !b.length) return json({ ok: false }, 400);
  if (await limitado(request, 'voto', 15)) return json({ ok: false, motivo: 'limite' }, 429);

  const [prevTxt] = await pipeline([['GET', 'bol:' + id]]);
  const prev = prevTxt ? JSON.parse(prevTxt) : null;
  const antes = new Set((prev || []).map(x => x.c + ':' + miembro(x)));
  const ahora = new Set(b.map(x => x.c + ':' + miembro(x)));
  const cmds = [];
  (prev || []).forEach(x => { if (!ahora.has(x.c + ':' + miembro(x))) cmds.push(['ZINCRBY', 'rk:' + x.c, -1, miembro(x)]); });
  b.forEach(x => { if (!antes.has(x.c + ':' + miembro(x))) cmds.push(['ZINCRBY', 'rk:' + x.c, 1, miembro(x)]); });
  if (!prev) cmds.push(['INCR', 'stats:boletas']);
  cmds.push(['SET', 'bol:' + id, JSON.stringify(b)]);
  await pipeline(cmds);
  return json({ ok: true, nueva: !prev });
}
