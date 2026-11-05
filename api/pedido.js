// POST /api/pedido  {plan, addons, espacio, nombre, contacto, notas}
// Registra un pedido de campaña digital. No cobra nada: guarda el pedido, le da un código
// y avisa por Telegram si están las variables del bot. El pago se coordina aparte.
import { createRequire } from 'module';
import { pipeline, hayRedis, json, limitado } from './_redis.js';

const require = createRequire(import.meta.url);
let CATALOGO = { planes: [], addons: [] };
try { CATALOGO = require('../data/campanas.json'); } catch (e) {}

const PLANES = new Map((CATALOGO.planes || []).map(p => [p.id, p]));
const ADDONS = new Map((CATALOGO.addons || []).map(a => [a.id, a]));

const recorte = (v, n) => String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const plata = n => '$' + n.toLocaleString('es-AR');

export async function POST(request) {
  if (!hayRedis) return json({ ok: false, motivo: 'sin-redis' }, 503);
  let body;
  try { body = await request.json(); } catch (e) { return json({ ok: false, motivo: 'formato' }, 400); }
  if (await limitado(request, 'pedido', 6)) return json({ ok: false, motivo: 'limite' }, 429);

  const plan = PLANES.get(String(body.plan || ''));
  if (!plan) return json({ ok: false, motivo: 'plan' }, 400);
  const addons = (Array.isArray(body.addons) ? body.addons : []).slice(0, 6).filter(id => ADDONS.has(String(id)));
  const nombre = recorte(body.nombre, 80);
  const contacto = recorte(body.contacto, 120);
  const espacio = recorte(body.espacio, 80);
  const notas = recorte(body.notas, 500);
  if (nombre.length < 2) return json({ ok: false, motivo: 'nombre' }, 400);
  if (contacto.length < 5) return json({ ok: false, motivo: 'contacto' }, 400);

  const total = plan.precio + addons.reduce((s, id) => s + ADDONS.get(id).precio, 0);
  const codigo = 'MV-' + Date.now().toString(36).toUpperCase().slice(-5) + Math.random().toString(36).slice(2, 5).toUpperCase();
  const cuando = new Date().toISOString();

  try {
    await pipeline([
      ['HSET', 'pedido:' + codigo, 'codigo', codigo, 'cuando', cuando, 'plan', plan.id,
        'addons', addons.join(','), 'espacio', espacio, 'nombre', nombre, 'contacto', contacto,
        'notas', notas, 'total', String(total)],
      ['EXPIRE', 'pedido:' + codigo, 60 * 60 * 24 * 365],
      ['LPUSH', 'pedidos', codigo],
    ]);
  } catch (e) {
    return json({ ok: false, motivo: 'guardado' }, 500);
  }

  // Aviso al dueño del sitio. Si no hay variables, el pedido queda igual en Redis.
  const tok = process.env.TELEGRAM_BOT_TOKEN, chat = process.env.TELEGRAM_CHAT_ID;
  if (tok && chat) {
    const texto = [
      '🛒 Pedido ' + codigo,
      'Plan: ' + plan.nombre + ' (' + plata(plan.precio) + ')',
      addons.length ? 'Extras: ' + addons.map(id => ADDONS.get(id).nombre + ' (' + plata(ADDONS.get(id).precio) + ')').join(', ') : '',
      'Espacio: ' + (espacio || 'sin especificar'),
      'Nombre: ' + nombre,
      'Contacto: ' + contacto,
      notas ? 'Notas: ' + notas : '',
      'Total: ' + plata(total),
    ].filter(Boolean).join('\n');
    fetch('https://api.telegram.org/bot' + tok + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chat, text: texto, disable_web_page_preview: true }),
    }).catch(() => {});
  }

  return json({ ok: true, codigo, total, plan: plan.nombre, moneda: 'ARS' });
}
