// GET /api/ranking
// Los más elegidos por cargo (acumulado), los más vendidos de la semana y lo que está en tendencia
// por visitas de las últimas 48 horas.
// Respuesta: {total, r:{...}, sem:{...}, semTotal, tend:[[id, vistas], ...], desde, hasta}
// Con RANKING_OFF (por ejemplo, durante la veda) devuelve {off: true} y el sitio oculta el ranking.
import { pipeline, hayRedis, json } from './_redis.js';

const CARGOS = ['presidencial', 'gobernador', 'intendente', 'legislador'];
const CACHE = 'public, max-age=0, s-maxage=60, stale-while-revalidate=600';

// [hoy, ayer, anteayer, ...]
function dias(n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(new Date(Date.now() - i * 864e5).toISOString().slice(0, 10));
  return out;
}

function desarmar(plano) {
  const out = [];
  for (let i = 0; i < (plano || []).length; i += 2) {
    const n = Math.round(+plano[i + 1]);
    if (n <= 0) continue;
    out.push([plano[i], n]);
  }
  return out;
}

function porCargo(plano) {
  const out = [];
  for (let i = 0; i < (plano || []).length; i += 2) {
    const n = Math.round(+plano[i + 1]);
    if (n <= 0) continue;
    const [id, jur] = plano[i].split('|');
    out.push([id, jur, n]);
  }
  return out;
}

export async function GET() {
  if (process.env.RANKING_OFF) return json({ off: true }, 200, CACHE);
  if (!hayRedis) return json({ off: true, motivo: 'sin-redis' }, 200, 'no-store');
  const d7 = dias(7);
  const d2 = dias(2);
  try {
    const [totTxt, ...rks] = await pipeline([
      ['GET', 'stats:boletas'],
      ...CARGOS.map(c => ['ZRANGE', 'rk:' + c, 0, -1, 'REV', 'WITHSCORES']),
    ]);
    const r = {};
    CARGOS.forEach((c, k) => { r[c] = porCargo(rks[k]); });

    // Semana: se suman los buckets diarios de los últimos siete días.
    const sem = {};
    for (const c of CARGOS) {
      const keys = d7.map(d => `rk:d:${c}:${d}`);
      const res = await pipeline([
        ['ZUNIONSTORE', 'tmp:w:' + c, keys.length, ...keys],
        ['ZRANGE', 'tmp:w:' + c, 0, 19, 'REV', 'WITHSCORES'],
        ['DEL', 'tmp:w:' + c],
      ]);
      sem[c] = porCargo(res[1]);
    }

    // Tendencia: visitas a fichas en las últimas 48 horas.
    const tv = await pipeline([
      ['ZUNIONSTORE', 'tmp:v', 2, ...d2.map(d => 'v:d:' + d)],
      ['ZRANGE', 'tmp:v', 0, 14, 'REV', 'WITHSCORES'],
      ['DEL', 'tmp:v'],
    ]);
    const tend = desarmar(tv[1]);

    // Boletas finalizadas esta semana.
    const bd = await pipeline(d7.map(d => ['GET', 'stats:boletas:d:' + d]));
    const semTotal = bd.reduce((s, x) => s + (+x || 0), 0);

    return json({
      total: +totTxt || 0, r, sem, semTotal, tend,
      desde: d7[d7.length - 1], hasta: d7[0],
    }, 200, CACHE);
  } catch (e) {
    return json({ off: true, motivo: 'error' }, 200, 'no-store');
  }
}
