// GET /api/metricas  (header Authorization: Bearer <METRICAS_TOKEN>)
// Embudo total, últimos 14 días, redes por las que se comparte y provincias que piden los usuarios.
import { pipeline, hayRedis, json } from './_redis.js';

const obj = plano => { const o = {}; for (let i = 0; i < (plano || []).length; i += 2) o[plano[i]] = +plano[i + 1]; return o; };

export async function GET(request) {
  const token = process.env.METRICAS_TOKEN;
  const auth = (request.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  if (!token || auth !== token) return json({ ok: false }, 401);
  if (!hayRedis) return json({ ok: false, motivo: 'sin-redis' }, 503);
  const dias = [...Array(14)].map((_, k) => new Date(Date.now() - k * 864e5).toISOString().slice(0, 10)).reverse();
  const res = await pipeline([
    ['GET', 'stats:boletas'], ['HGETALL', 'funnel:total'], ['HGETALL', 'funnel:redes'], ['HGETALL', 'pedidos'],
    ...dias.map(d => ['HGETALL', 'funnel:' + d]),
  ]);
  return json({
    ok: true, boletas: +res[0] || 0, total: obj(res[1]), redes: obj(res[2]), pedidos: obj(res[3]),
    dias: dias.map((d, k) => ({ d, ...obj(res[4 + k]) })),
  });
}
