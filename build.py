#!/usr/bin/env python3
"""Genera el sitio Mercado Voto desde data/candidatos.json."""
import json, os, html, re, math

BASE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(f"{BASE}/data/candidatos.json"))
CANDS = D["candidatos"]
EJES = D["ejes"]

CATS = [("presidencial", "Presidenciales"), ("gobernador", "Gobernadores"),
        ("diputado", "Diputados"), ("senador", "Senadores"), ("municipal", "Municipales")]

POLOS = [("Economía", "Estado", "Mercado"), ("Sociedad", "Conservador", "Progresista"),
         ("Poder", "Institucional", "Personalista"), ("Federalismo", "Centralista", "Federal"),
         ("Cambio", "Continuidad", "Ruptura"), ("Exterior", "Autonomía", "Occidente")]


def esc(s):
    return html.escape(s or "", quote=True)


def limpia(s):
    s = (s or "").replace("—", ",").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip()


def ini(nombre):
    partes = [p for p in re.split(r"\s+", nombre) if p]
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()


def estrellas(c):
    tot = c["cumplidas"] + c["incumplidas"]
    if not tot:
        return '<span class="estrellas">sin registro<span> de promesas</span></span>'
    pct = c["cumplidas"] / tot
    llenas = max(1, min(5, round(pct * 5)))
    return f'<span class="estrellas">{"★" * llenas}{"☆" * (5 - llenas)}<span>{c["cumplidas"]} de {tot} promesas</span></span>'


def foto(c, clase="foto"):
    if c["foto"]:
        return f'<div class="{clase}"><img src="/{c["foto"]}" alt="{esc(c["nombre"])}" loading="lazy"></div>'
    return f'<div class="{clase}"><div class="ini" style="background:{c["color"]}">{ini(c["nombre"])}</div></div>'


def radar(c):
    cx, cy, rmax = 110, 110, 78
    pts, labels = [], []
    for i, (v) in enumerate(c["ejes"]):
        ang = math.radians(-90 + i * 60)
        r = 16 + (v / 100) * (rmax - 16)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        lx, ly = cx + (rmax + 20) * math.cos(ang), cy + (rmax + 20) * math.sin(ang)
        anchor = "middle" if abs(math.cos(ang)) < 0.3 else ("end" if math.cos(ang) < 0 else "start")
        labels.append(f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="{anchor}" '
                      f'font-size="9.5" fill="#888" font-weight="600">{esc(POLOS[i][0])}</text>')
    anillos = ""
    for frac in (0.25, 0.5, 0.75, 1.0):
        p = " ".join(f"{cx + rmax*frac*math.cos(math.radians(-90+i*60)):.1f},{cy + rmax*frac*math.sin(math.radians(-90+i*60)):.1f}" for i in range(6))
        anillos += f'<polygon points="{p}" fill="none" stroke="#e8e8e8" stroke-width="1"/>'
    radios = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx+rmax*math.cos(math.radians(-90+i*60)):.1f}" '
        f'y2="{cy+rmax*math.sin(math.radians(-90+i*60)):.1f}" stroke="#eee"/>' for i in range(6))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    puntos = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{c["color"]}"/>' for x, y in pts)
    return f'''<svg class="radar" viewBox="0 0 220 220" role="img" aria-label="Perfil ideológico estimado de {esc(c["nombre"])}">
{anillos}{radios}
<polygon points="{poly}" fill="{c["color"]}" fill-opacity="0.18" stroke="{c["color"]}" stroke-width="2"/>
{puntos}{"".join(labels)}
</svg>'''


def miga(cats_txt="", extra=""):
    return f'<div class="miga"><a href="/">Inicio</a> › {cats_txt}{extra}</div>'


NAV_JS = """
function pintarContador(){
  const b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  document.querySelectorAll('.mi-boleta .n').forEach(e => e.textContent = b.length);
}
function agregar(id, ir){
  let b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  if(!b.includes(id)) b.push(id);
  localStorage.setItem('mv_boleta', JSON.stringify(b));
  pintarContador();
  if(ir) location.href = '/boleta';
  else {
    const t = document.createElement('div');
    t.textContent = 'Agregado a tu boleta';
    t.style.cssText='position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:11px 20px;border-radius:6px;font-size:13.5px;z-index:99';
    document.body.appendChild(t); setTimeout(()=>t.remove(), 1800);
  }
}
document.addEventListener('DOMContentLoaded', pintarContador);
"""


def header(activo=""):
    nav = "".join(
        f'<a href="/?cat={k}" class="{"on" if activo == k else ""}">{v}</a>' for k, v in CATS)
    return f'''<header class="top"><div class="wrap">
  <a class="logo" href="/">Mercado <b>Voto</b></a>
  <div class="buscador"><input id="q" type="text" placeholder="Buscá un candidato, un partido o una provincia" autocomplete="off"><button aria-label="Buscar">⌕</button></div>
  <a class="mi-boleta" href="/boleta">🛒 Mi boleta <span class="n">0</span></a>
</div></header>
<nav class="nav"><div class="wrap">{nav}<a href="/?orden=ruptura">Más disruptivos</a><a href="/?orden=cumplimiento">Mejor reputación</a></div></nav>'''


def footer():
    return '''<footer><div class="wrap">
  <div>Mercado Voto · simulador. No se compra nada, no se vota nada.</div>
  <div>Perfiles y críticas: proyecto A Quién Criticás. Fotos: Wikimedia Commons.</div>
</div></footer>'''


# ---------------- tarjetas ----------------
def card(c):
    chips = f'<span class="chip partido">{esc(c["partido"])}</span>'
    return f'''<div class="card" data-cats="{" ".join(c["categorias"])}" data-prov="{esc(c["provincia"])}" data-partido="{esc(c["partido"])}" data-eco="{c["ejes"][0]}" data-nombre="{esc(c["nombre"].lower())}">
  {foto(c)}
  <div class="cuerpo">
    <a class="nom" href="/c/{c["slug"]}">{esc(c["nombre"])}</a>
    <div class="meta">{esc(c["provincia"])} · {esc(limpia(c["tag"]))[:42]}</div>
    <div>{chips}</div>
    <div class="precio">1 voto <small>por período</small></div>
    <div class="envio">Asume en diciembre</div>
    {estrellas(c)}
    <button class="btn" onclick="agregar('{c["id"]}', true)">Comprar</button>
  </div>
</div>'''


# ---------------- index ----------------
def build_index():
    cards = "\n".join(card(c) for c in sorted(CANDS, key=lambda x: -x["ejes"][4]))
    provs = sorted({c["provincia"] for c in CANDS})
    partidos = sorted({c["partido"] for c in CANDS})
    opt_p = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in provs)
    opt_pa = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in partidos)
    filtros = f'''<aside class="filtros">
  <h3>Categoría</h3>
  <label><input type="radio" name="cat" value="" checked> Todas</label>
  {"".join(f'<label><input type="radio" name="cat" value="{k}"> {v}</label>' for k, v in CATS)}
  <h3>Provincia</h3>
  <select id="f-prov"><option value="">Todas</option>{opt_p}</select>
  <h3>Espacio político</h3>
  <select id="f-partido"><option value="">Todos</option>{opt_pa}</select>
  <h3>Eje económico</h3>
  <input type="range" id="f-eco" min="0" max="100" value="0" step="10">
  <div class="rango"><span>Estado</span><span>Mercado</span></div>
  <h3>Promesas</h3>
  <label><input type="checkbox" id="f-cumpl"> Solo con promesas verificadas</label>
</aside>'''
    js = '''
const tarjetas = [...document.querySelectorAll('.card')];
const cuenta = document.getElementById('cuenta');
function aplicar(){
  const cat = document.querySelector('input[name=cat]:checked').value;
  const prov = document.getElementById('f-prov').value;
  const par = document.getElementById('f-partido').value;
  const eco = +document.getElementById('f-eco').value;
  const cumpl = document.getElementById('f-cumpl').checked;
  const q = (document.getElementById('q').value || '').toLowerCase().trim();
  const orden = document.getElementById('orden').value;
  let n = 0;
  tarjetas.forEach(t => {
    const ok = (!cat || t.dataset.cats.split(' ').includes(cat))
      && (!prov || t.dataset.prov === prov)
      && (!par || t.dataset.partido === par)
      && (!q || t.dataset.nombre.includes(q) || t.dataset.partido.toLowerCase().includes(q))
      && (!cumpl || t.querySelector('.estrellas').textContent.includes('de'));
    const e = +t.dataset.eco;
    const okEco = eco === 0 || Math.abs(e - eco) <= 25;
    const ver = ok && okEco;
    t.style.display = ver ? '' : 'none';
    if(ver) n++;
  });
  const grid = document.getElementById('grid');
  const arr = [...grid.children].filter(x => x.style.display !== 'none');
  if(orden === 'cumplimiento') arr.sort((a,b) => (b.dataset.cum||0) - (a.dataset.cum||0));
  if(orden === 'ruptura') arr.sort((a,b) => (b.dataset.rupt||0) - (a.dataset.rupt||0));
  if(orden === 'nombre') arr.sort((a,b) => a.dataset.nombre.localeCompare(b.dataset.nombre));
  arr.forEach(x => grid.appendChild(x));
  cuenta.textContent = n + (n === 1 ? ' resultado' : ' resultados');
}
['f-prov','f-partido','f-eco','f-cumpl','orden'].forEach(id => {
  const el = document.getElementById(id); if(el) el.addEventListener('input', aplicar);
});
document.querySelectorAll('input[name=cat]').forEach(r => r.addEventListener('change', aplicar));
document.getElementById('q').addEventListener('input', aplicar);
const cat0 = new URLSearchParams(location.search).get('cat');
if(cat0){ const r = document.querySelector(`input[name=cat][value="${cat0}"]`); if(r){ r.checked = true; } }
const ord0 = new URLSearchParams(location.search).get('orden');
if(ord0){ document.getElementById('orden').value = ord0; }
aplicar();
'''
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mercado Voto · elegí antes de votar</title>
<meta name="description" content="Los candidatos de las elecciones argentinas, con su perfil, su historial de votos y las críticas que no responden.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header()}
<main class="main"><div class="wrap">
  <div class="cols">
    {filtros}
    <div>
      <div class="resumen">
        <div class="cuenta" id="cuenta">25 resultados</div>
        <select id="orden">
          <option value="">Más relevantes</option>
          <option value="cumplimiento">Mejor reputación</option>
          <option value="ruptura">Más disruptivos</option>
          <option value="nombre">Nombre, A a Z</option>
        </select>
      </div>
      <div class="grid" id="grid">
{cards}
      </div>
    </div>
  </div>
</div></main>
{footer()}
<script>{NAV_JS}{js}</script>
</body></html>'''


# ---------------- ficha ----------------
def build_ficha(c):
    cat_txt = " › ".join(v for k, v in CATS if k in c["categorias"])
    crit = ""
    for cr in c["criticas"]:
        f = (cr.get("fuerza") or "").replace(" ", "-")
        crit += f'''<div class="critica">
  <div class="cab"><span class="area">{esc(limpia(cr.get("area", "")))} · {esc(limpia(cr.get("tipo", "")))}</span>
  <span class="fuerza {f}">{esc(cr.get("fuerza", ""))}</span></div>
  <div class="tesis">{esc(limpia(cr.get("tesis", "")))}</div>
  <div class="cuerpo">{esc(limpia(cr.get("cuerpo", "")))}</div>
  <details><summary>Ver la evidencia</summary><div class="evid">{esc(limpia(cr.get("evidencia", "")))}</div></details>
</div>'''
    qa = ""
    for cr in c["criticas"][:3]:
        qa += f'''<div class="qa">
  <div class="p">{esc(limpia(cr.get("tesis", "")))}</div>
  <div class="r"><b>Lo que respondería:</b> {esc(limpia(cr.get("respuesta_esperada", "")))}</div>
  <div class="r" style="margin-top:8px"><b>Por qué no alcanza:</b> {esc(limpia(cr.get("refutacion", "")))}</div>
</div>'''
    cum = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_cumplidas"]) or "<li>Sin promesas registradas</li>"
    inc = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_incumplidas"]) or "<li>Sin promesas registradas</li>"
    tray = "".join(f'<li><span class="f">{esc(t.get("fecha",""))}</span><span>{esc(limpia(t.get("evento","")))}</span></li>' for t in c["trayectoria"])
    vuln = "".join(f"<li>{esc(limpia(v))}</li>" for v in c["vulnerabilidades"])
    polos = "".join(f'<div><b>{a}</b><br>{b} ↔ {d}</div>' for a, b, d in POLOS)
    rel = [x for x in CANDS if x["id"] != c["id"] and (x["partido"] == c["partido"] or set(x["categorias"]) & set(c["categorias"]))][:4]
    rel_html = "".join(f'<a href="/c/{x["slug"]}" style="display:block;padding:10px 0;border-bottom:1px solid #f2f2f2">'
                       f'<b style="font-size:13.5px;color:#333">{esc(x["nombre"])}</b><br>'
                       f'<span style="font-size:12px;color:#999">{esc(x["partido"])}</span></a>' for x in rel)

    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(c["nombre"])} · Mercado Voto</title>
<meta name="description" content="{esc(limpia(c["bio"]))[:150]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header(c["categorias"][0])}
<main class="main"><div class="wrap">
  {miga(cat_txt, f' › <a href="/c/{c["slug"]}">{esc(c["nombre"])}</a>')}
  <div class="ficha">
    {foto(c)}
    <div>
      <h1>{esc(c["nombre"])}</h1>
      <div class="rol">{esc(limpia(c["rol"]))}</div>
      <div class="tagline"><span class="chip partido">{esc(c["partido"])}</span><span class="chip">{esc(c["provincia"])}</span></div>
      <div class="precio-grande">1 voto <small>por período de 4 años</small></div>
      <div class="cuotas">12 cuotas de 0 votos · envío gratis a todo el país</div>
      <div class="caja-partido">
        <div>Espacio: <b>{esc(c["partido"])}</b></div>
        <div>Distrito: <b>{esc(c["provincia"])}</b></div>
        <div style="margin-top:8px">{estrellas(c)}</div>
      </div>
      <button class="btn" onclick="agregar('{c["id"]}', true)">Comprar ahora</button>
      <button class="btn sec" onclick="agregar('{c["id"]}', false)">Agregar a mi boleta</button>
      <div class="aviso">Simulador. No se registra ningún voto ni se envía nada a ningún lado.</div>
    </div>
  </div>

  <div class="bloques">
    <div>
      <div class="panel">
        <h2>Quién es</h2>
        <p>{esc(limpia(c["bio"]))}</p>
        <h3>Trayectoria</h3>
        <ul class="timeline">{tray}</ul>
      </div>

      <div class="panel">
        <h2>A quién criticás</h2>
        <div class="sub">Las {len(c["criticas"])} críticas más fuertes contra este candidato, con la evidencia y lo que respondería.</div>
        {crit}
      </div>

      <div class="panel">
        <h2>Preguntas y respuestas</h2>
        <div class="sub">Cada crítica puesta en formato de pregunta, con la respuesta esperada del candidato y por qué no cierra.</div>
        {qa}
      </div>
    </div>

    <div>
      <div class="panel">
        <h2>Composición ideológica</h2>
        <div class="sub">Estimación editorial sobre seis ejes. No es una medición.</div>
        {radar(c)}
        <div class="leyenda">{polos}</div>
      </div>

      <div class="panel">
        <h2>Promesas</h2>
        <h3 style="color:var(--ml-green)">Cumplidas</h3>
        <ul class="limpia si">{cum}</ul>
        <h3 style="color:#c33">Incumplidas</h3>
        <ul class="limpia no">{inc}</ul>
      </div>

      <div class="panel">
        <h2>Puntos débiles</h2>
        <ul class="limpia">{vuln}</ul>
      </div>

      <div class="panel">
        <h2>Quizás te interese</h2>
        {rel_html}
      </div>
    </div>
  </div>
</div></main>
{footer()}
<script>{NAV_JS}</script>
</body></html>'''


# ---------------- boleta ----------------
def build_boleta():
    data = json.dumps({c["id"]: {"n": c["nombre"], "s": c["slug"], "p": c["partido"], "pr": c["provincia"],
                                 "f": c["foto"], "i": ini(c["nombre"]), "col": c["color"]} for c in CANDS},
                      ensure_ascii=False)
    js = f'''
const DATA = {data};
function render(){{
  const b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  const cont = document.getElementById('lista');
  const tot = document.getElementById('tot');
  document.querySelectorAll('.mi-boleta .n').forEach(e => e.textContent = b.length);
  if(!b.length){{
    cont.innerHTML = '<div class="vacio">Todavía no elegiste a nadie.<br><a href="/">Ver candidatos</a></div>';
    tot.textContent = '0'; return;
  }}
  cont.innerHTML = b.map(id => {{
    const c = DATA[id]; if(!c) return '';
    const img = c.f ? `<img src="/${{c.f}}" alt="">` : `<div class="ini" style="background:${{c.col}}">${{c.i}}</div>`;
    return `<div class="boleta-item">${{img}}<div><a href="/c/${{c.s}}"><b>${{c.n}}</b></a><div style="font-size:12.5px;color:#999">${{c.p}} · ${{c.pr}}</div></div><button class="quitar" onclick="quitar('${{id}}')">Quitar</button></div>`;
  }}).join('');
  tot.textContent = b.length;
}}
function quitar(id){{
  let b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  b = b.filter(x => x !== id);
  localStorage.setItem('mv_boleta', JSON.stringify(b));
  render();
}}
function confirmar(){{
  const b = JSON.parse(localStorage.getItem('mv_boleta') || '[]');
  if(!b.length) return;
  document.getElementById('modal').style.display = 'flex';
  document.getElementById('m-txt').textContent = `Tu boleta tiene ${{b.length}} candidato${{b.length>1?'s':''}}. En una elección real solo podrías elegir uno por categoría.`;
}}
function cerrar(){{ document.getElementById('modal').style.display = 'none'; }}
document.addEventListener('DOMContentLoaded', render);
'''
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi boleta · Mercado Voto</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header()}
<main class="main"><div class="wrap" style="max-width:760px">
  <div class="panel">
    <h2>Mi boleta</h2>
    <div class="sub">Los candidatos que elegiste. Podés sacar y agregar cuando quieras.</div>
    <div id="lista"></div>
    <div class="total"><span>Total</span><span><b id="tot">0</b> <small style="color:#999">votos</small></span></div>
    <button class="btn" onclick="confirmar()">Confirmar boleta</button>
    <div class="aviso">Esto no envía nada. El sitio no guarda datos en ningún servidor: tu boleta vive en este navegador.</div>
  </div>
</div></main>
{footer()}
<div id="modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);align-items:center;justify-content:center;padding:20px;z-index:100">
  <div style="background:#fff;border-radius:8px;padding:26px;max-width:420px;text-align:center">
    <h3 style="font-size:18px;margin-bottom:10px">Boleta confirmada</h3>
    <p id="m-txt" style="color:#666;font-size:14px;margin-bottom:18px"></p>
    <button class="btn" onclick="cerrar()">Listo</button>
  </div>
</div>
<script>{NAV_JS}{js}</script>
</body></html>'''


# ---------------- escribir ----------------
os.makedirs(f"{BASE}/c", exist_ok=True)
open(f"{BASE}/index.html", "w").write(build_index())
for c in CANDS:
    open(f"{BASE}/c/{c['slug']}.html", "w").write(build_ficha(c))
open(f"{BASE}/boleta.html", "w").write(build_boleta())
open(f"{BASE}/c/index.html", "w").write(build_index())
print(f"index + {len(CANDS)} fichas + boleta")
