// Cliente mínimo de Redis por REST (Upstash). Sin dependencias.
// Lee las variables que crea la integración de Vercel Marketplace (KV_REST_API_* o UPSTASH_REDIS_REST_*).
// Sin variables y con MV_REDIS_MEMORIA=1 usa un Redis en memoria, sólo para desarrollo local.

const URL_ = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

export const hayRedis = Boolean((URL_ && TOKEN) || process.env.MV_REDIS_MEMORIA);

// Ejecuta varios comandos en un solo viaje. Devuelve el resultado de cada uno.
export async function pipeline(cmds) {
  if (!cmds.length) return [];
  if (!URL_ || !TOKEN) return memoria(cmds);
  const r = await fetch(URL_ + '/pipeline', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds.map(c => c.map(String))),
  });
  if (!r.ok) throw new Error('Redis ' + r.status);
  const out = await r.json();
  return out.map(x => { if (x.error) throw new Error(x.error); return x.result; });
}

// ---------- Redis en memoria (desarrollo) ----------
const M = globalThis.__mvRedis || (globalThis.__mvRedis = new Map());
function memoria(cmds) {
  if (!process.env.MV_REDIS_MEMORIA) throw new Error('Redis no configurado');
  return cmds.map(([cmd, k, ...a]) => {
    cmd = cmd.toUpperCase();
    if (cmd === 'GET') return M.get(k) ?? null;
    if (cmd === 'SET') { M.set(k, a[0]); return 'OK'; }
    if (cmd === 'INCR') { const v = (+M.get(k) || 0) + 1; M.set(k, String(v)); return v; }
    if (cmd === 'EXPIRE') return 1;
    if (cmd === 'HINCRBY') { const h = M.get(k) || new Map(); h.set(a[0], (h.get(a[0]) || 0) + +a[1]); M.set(k, h); return h.get(a[0]); }
    if (cmd === 'HGETALL') { const h = M.get(k); return h ? [...h].flatMap(([f, v]) => [f, String(v)]) : []; }
    if (cmd === 'HSET') { let h = M.get(k); if (!(h instanceof Map)) { h = new Map(); M.set(k, h); } for (let i = 0; i < a.length; i += 2) h.set(a[i], String(a[i + 1])); return a.length / 2; }
    if (cmd === 'LPUSH') { const l = M.get(k) || []; l.unshift(a[0]); M.set(k, l); return l.length; }
    if (cmd === 'ZINCRBY') { const z = M.get(k) || new Map(); z.set(a[1], (z.get(a[1]) || 0) + +a[0]); M.set(k, z); return String(z.get(a[1])); }
    if (cmd === 'ZRANGE') { // ZRANGE k 0 -1 REV WITHSCORES
      const z = M.get(k); if (!z) return [];
      return [...z].filter(([, s]) => s > 0).sort((x, y) => y[1] - x[1]).flatMap(([m, s]) => [m, String(s)]);
    }
    if (cmd === 'ZUNIONSTORE') { // ZUNIONSTORE dest n k1 k2 ...
      const n = +a[0], claves = a.slice(1, 1 + n), out = new Map();
      claves.forEach(kk => { const z = M.get(kk); if (z) [...z].forEach(([m, s]) => { if (s > 0) out.set(m, (out.get(m) || 0) + s); }); });
      M.set(k, out); return out.size;
    }
    if (cmd === 'DEL') { return M.delete(k) ? 1 : 0; }
    throw new Error('Comando no soportado en memoria: ' + cmd);
  });
}

// IP del visitante, para limitar abusos.
export function ip(request) {
  return (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'local';
}

export function json(data, status = 200, cache = 'no-store') {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': cache } });
}

// Devuelve true si la IP superó `max` pedidos en el minuto actual.
export async function limitado(request, clave, max) {
  const k = `rl:${clave}:${ip(request)}:${Math.floor(Date.now() / 60000)}`;
  const [n] = await pipeline([['INCR', k], ['EXPIRE', k, 120]]);
  return n > max;
}
