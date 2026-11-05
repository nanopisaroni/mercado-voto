// POST /api/evento  {e, p}
// Embudo propio y anónimo: cuenta cuántas veces pasa cada paso, por día y en total.
// No guarda IPs ni identificadores, sólo contadores.
import { pipeline, hayRedis, json, limitado } from './_redis.js';

export const EVENTOS = [
  'visita', 'elige_lugar', 'pide_lugar', 'empieza_guia', 'agrega', 'completa', 'finaliza',
  'comparte', 'descarga_imagen', 'abre_compartida', 'usa_compartida', 'azar',
  'ver_ficha', 'ver_prop', 'ver_campana',
];

export async function POST(request) {
  if (!hayRedis) return new Response(null, { status: 204 });
  let body;
  try { body = JSON.parse(await request.text()); } catch (e) { return json({ ok: false }, 400); }
  const e = String(body.e || '');
  if (!EVENTOS.includes(e)) return json({ ok: false }, 400);
  if (await limitado(request, 'evento', 120)) return new Response(null, { status: 204 });
  const dia = 'funnel:' + new Date().toISOString().slice(0, 10);
  const cmds = [['HINCRBY', 'funnel:total', e, 1], ['HINCRBY', dia, e, 1], ['EXPIRE', dia, 60 * 60 * 24 * 120]];
  const p = String(body.p || '').slice(0, 40);
  if (e === 'pide_lugar' && p) cmds.push(['HINCRBY', 'pedidos', p, 1]);
  if (e === 'comparte' && p) cmds.push(['HINCRBY', 'funnel:redes', p, 1]);
  // Vistas por ficha: serie diaria de 10 días para el ranking de tendencia.
  if ((e === 'ver_ficha' || e === 'ver_prop' || e === 'ver_campana') && p) {
    const hoy = new Date().toISOString().slice(0, 10);
    cmds.push(['ZINCRBY', 'v:d:' + hoy, 1, p]);
    cmds.push(['EXPIRE', 'v:d:' + hoy, 60 * 60 * 24 * 10]);
  }
  await pipeline(cmds);
  return new Response(null, { status: 204 });
}
