// GET /api/ranking  Los más elegidos por cargo, con la cantidad de boletas que los incluyen.
// Respuesta: {total, r: {presidencial: [[id, jur, n], ...], gobernador: [...], ...}}
// Con RANKING_OFF (por ejemplo, durante la veda) devuelve {off: true} y el sitio oculta el ranking.
import { pipeline, hayRedis, json } from './_redis.js';

const CARGOS = ['presidencial', 'gobernador', 'intendente', 'legislador'];
const CACHE = 'public, max-age=0, s-maxage=60, stale-while-revalidate=600';

export async function GET() {
  if (process.env.RANKING_OFF) return json({ off: true }, 200, CACHE);
  if (!hayRedis) return json({ off: true, motivo: 'sin-redis' }, 200, 'no-store');
  try {
    const res = await pipeline([['GET', 'stats:boletas'], ...CARGOS.map(c => ['ZRANGE', 'rk:' + c, 0, -1, 'REV', 'WITHSCORES'])]);
    const r = {};
    CARGOS.forEach((c, k) => {
      const plano = res[k + 1] || [];
      r[c] = [];
      for (let i = 0; i < plano.length; i += 2) {
        const n = Math.round(+plano[i + 1]);
        if (n <= 0) continue;
        const [id, jur] = plano[i].split('|');
        r[c].push([id, jur, n]);
      }
    });
    return json({ total: +res[0] || 0, r }, 200, CACHE);
  } catch (e) {
    return json({ off: true, motivo: 'error' }, 200, 'no-store');
  }
}
