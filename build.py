#!/usr/bin/env python3
"""Genera Mercado Voto desde data/candidatos.json."""
import json, os, html, re, math

BASE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(f"{BASE}/data/candidatos.json"))
CANDS = {c["id"]: c for c in D["candidatos"]}
CAND = sorted(D["candidatos"], key=lambda c: c["nombre"])
CANDIDATURAS = D["candidaturas"]

CARGOS = [("presidencial", "Presidente"), ("gobernador", "Gobernador"), ("intendente", "Intendente"), ("legislador", "Legisladores")]
POLOS = [("Economía", "Estado", "Mercado"), ("Sociedad", "Conservador", "Progresista"),
         ("Poder", "Institucional", "Personalista"), ("Federalismo", "Centralista", "Federal"),
         ("Cambio", "Continuidad", "Ruptura"), ("Exterior", "Autonomía", "Occidente")]


def esc(s):
    return html.escape(s or "", quote=True)


def limpia(s):
    s = (s or "").replace("—", ",").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip()


def ini(nombre):
    p = [x for x in re.split(r"\s+", nombre) if x]
    return (p[0][0] + (p[-1][0] if len(p) > 1 else "")).upper()


def estrellas(c):
    tot = c["cumplidas"] + c["incumplidas"]
    if not tot:
        return '<span class="estrellas vacia">sin promesas registradas</span>'
    pct = c["cumplidas"] / tot
    n = max(1, min(5, int(pct * 5 + 0.5)))
    return f'<span class="estrellas">{"★" * n}{"☆" * (5 - n)}<span>{c["cumplidas"]} de {tot} promesas</span></span>'


def foto(c, clase="foto"):
    if c["foto"]:
        return f'<div class="{clase}"><img src="/{c["foto"]}" alt="{esc(c["nombre"])}" loading="lazy"></div>'
    return f'<div class="{clase}"><div class="ini" style="background:{c["color"]}">{ini(c["nombre"])}</div></div>'


def radar(c):
    cx, cy, rmax = 110, 110, 78
    pts, labels = [], []
    for i, v in enumerate(c["ejes"]):
        ang = math.radians(-90 + i * 60)
        r = 16 + (v / 100) * (rmax - 16)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        lx, ly = cx + (rmax + 21) * math.cos(ang), cy + (rmax + 21) * math.sin(ang)
        anchor = "middle" if abs(math.cos(ang)) < 0.3 else ("end" if math.cos(ang) < 0 else "start")
        labels.append(f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="{anchor}" font-size="9.5" '
                      f'fill="#888" font-weight="600">{esc(POLOS[i][0])}</text>')
    anillos = ""
    for frac in (0.25, 0.5, 0.75, 1.0):
        p = " ".join(f"{cx + rmax*frac*math.cos(math.radians(-90+i*60)):.1f},{cy + rmax*frac*math.sin(math.radians(-90+i*60)):.1f}" for i in range(6))
        anillos += f'<polygon points="{p}" fill="none" stroke="#e8e8e8"/>'
    radios = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+rmax*math.cos(math.radians(-90+i*60)):.1f}" '
                     f'y2="{cy+rmax*math.sin(math.radians(-90+i*60)):.1f}" stroke="#eee"/>' for i in range(6))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    puntos = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{c["color"]}"/>' for x, y in pts)
    return (f'<svg class="radar" viewBox="0 0 220 220" role="img" aria-label="Perfil ideológico estimado de {esc(c["nombre"])}">'
            f'{anillos}{radios}<polygon points="{poly}" fill="{c["color"]}" fill-opacity="0.18" stroke="{c["color"]}" stroke-width="2"/>'
            f'{puntos}{"".join(labels)}</svg>')


MARK = '''<svg class="mark" viewBox="0 0 34 34" aria-hidden="true">
<rect width="34" height="34" rx="8" fill="#2d2d2d"/>
<path d="M18.2 8.6h3.1L19.7 27H11.1L9.5 12.4h12.2" fill="#ffe600"/>
<path d="M12.4 12.4a4.6 4.6 0 0 1 9.2 0" fill="none" stroke="#2d2d2d" stroke-width="2.1" stroke-linecap="round"/>
<path d="M13.9 19.2l2.1 2.1 4.3-4.5" fill="none" stroke="#2d2d2d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


def logo():
    return f'<a class="logo" href="/">{MARK}<span>mercado <b>voto</b></span></a>'


def etiqueta(cargo, jur):
    if cargo == "presidencial":
        return "Presidente"
    if cargo == "legislador":
        return "Legislador · " + jur if jur else "Legislador"
    return ("Gobernador · " if cargo == "gobernador" else "Intendente · ") + jur


def header(activo=""):
    nav = "".join(f'<a href="/?cargo={k}">{v}</a>' for k, v in CARGOS)
    nav += '<a href="/?orden=ruptura">Más disruptivos</a><a href="/?orden=cumplimiento">Mejor reputación</a>'
    return f'''<header class="top"><div class="wrap">
  {logo()}
  <div class="buscador"><input id="q" type="text" placeholder="Buscá un candidato, un partido o una ciudad" autocomplete="off"><button aria-label="Buscar">⌕</button></div>
  <a class="mi-boleta" href="/boleta">Mi boleta <span class="n">0</span></a>
</div></header>
<nav class="nav"><div class="wrap">{nav}</div></nav>'''


def footer():
    return '''<footer><div class="wrap">
  <div>Mercado Voto · simulador. No se compra nada, no se vota nada.</div>
  <div>Perfiles y críticas: proyecto A Quién Criticás. Fotos: Wikimedia Commons.</div>
</div></footer>'''


def card(cid, cargo, jur):
    c = CANDS[cid]
    return f'''<div class="card" data-cargo="{cargo}" data-jur="{esc(jur)}" data-partido="{esc(c["partido"])}"
  data-nombre="{esc(c["nombre"].lower())}" data-eco="{c["ejes"][0]}" data-cum="{c["cumplidas"]}" data-rupt="{c["ejes"][4]}">
  {foto(c)}
  <span class="race">{esc(etiqueta(cargo, jur))}</span>
  <div class="cuerpo">
    <a class="nom" href="/c/{c["slug"]}">{esc(c["nombre"])}</a>
    <div class="meta">{esc(c["partido"])}</div>
    <div class="precio">1 voto <small>por período</small></div>
    <div class="envio">Asume en diciembre</div>
    {estrellas(c)}
    <button class="btn" onclick="agregar('{c["id"]}', '{cargo}', '{esc(jur)}', true)">Comprar</button>
  </div>
</div>'''


def build_index():
    cards = "\n".join(card(x["cid"], x["cargo"], x["jur"]) for x in CANDIDATURAS)
    partidos = sorted({c["partido"] for c in CAND})
    opt_pa = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in partidos)
    filtros = f'''<aside class="filtros">
  <h3>Elección</h3>
  <label><input type="radio" name="cargo" value="" checked> Todas</label>
  {"".join(f'<label><input type="radio" name="cargo" value="{k}"> {v}</label>' for k, v in CARGOS)}
  <h3>Jurisdicción</h3>
  <select id="f-jur"><option value="">Todas</option></select>
  <h3>Espacio político</h3>
  <select id="f-partido"><option value="">Todos</option>{opt_pa}</select>
  <h3>Eje económico</h3>
  <input type="range" id="f-eco" min="0" max="100" value="0" step="10">
  <div class="rango"><span>Estado</span><span>Mercado</span></div>
</aside>'''
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mercado Voto · elegí antes de votar</title>
<meta name="description" content="Los candidatos de las elecciones argentinas, con su perfil, su radar ideológico y las críticas que no responden.">
<meta name="theme-color" content="#ffe600">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header()}
<main class="main"><div class="wrap"><div class="cols">
  {filtros}
  <div>
    <div class="resumen">
      <div class="cuenta" id="cuenta">{len(CANDIDATURAS)} resultados</div>
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
</div></div></main>
{footer()}
<script src="/assets/carrito.js?v=5"></script>
<script src="/assets/catalogo.js?v=5"></script>
</body></html>'''


def build_ficha(c):
    cargos = [x for x in CANDIDATURAS if x["cid"] == c["id"]]
    chips = "".join(f'<span class="chip cargo">{esc(etiqueta(x["cargo"], x["jur"]))}</span>' for x in cargos)
    crit = ""
    for cr in c["criticas"]:
        f = (cr.get("fuerza") or "").replace(" ", "-")
        crit += f'''<div class="critica">
  <div class="cab"><span class="area">{esc(limpia(cr.get("area","")))} · {esc(limpia(cr.get("tipo","")))}</span>
  <span class="fuerza {f}">{esc(cr.get("fuerza",""))}</span></div>
  <div class="tesis">{esc(limpia(cr.get("tesis","")))}</div>
  <div class="cuerpo">{esc(limpia(cr.get("cuerpo","")))}</div>
  <details><summary>Ver la evidencia</summary><div class="evid">{esc(limpia(cr.get("evidencia","")))}</div></details>
</div>'''
    if not crit:
        crit = '<p style="color:#888">Perfil preliminar. Todavía no tiene críticas cargadas.</p>'
    qa = "".join(f'''<div class="qa"><div class="p">{esc(limpia(cr.get("tesis","")))}</div>
<div class="r"><b>Lo que respondería:</b> {esc(limpia(cr.get("respuesta_esperada","")))}</div>
<div class="r" style="margin-top:8px"><b>Por qué no alcanza:</b> {esc(limpia(cr.get("refutacion","")))}</div></div>''' for cr in c["criticas"][:3])
    if not qa:
        qa = '<p style="color:#888">Sin preguntas cargadas.</p>'
    cum = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_cumplidas"]) or "<li>Sin promesas registradas</li>"
    inc = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_incumplidas"]) or "<li>Sin promesas registradas</li>"
    tray = "".join(f'<li><span class="f">{esc(t.get("fecha",""))}</span><span>{esc(limpia(t.get("evento","")))}</span></li>' for t in c["trayectoria"])
    tray_html = f"<h3>Trayectoria</h3><ul class='timeline'>{tray}</ul>" if tray else ""
    vuln = "".join(f"<li>{esc(limpia(v))}</li>" for v in c["vulnerabilidades"]) or "<li>Sin datos cargados</li>"
    polos = "".join(f'<div><b>{a}</b><br>{b} ↔ {d}</div>' for a, b, d in POLOS)
    rel = [x for x in CAND if x["id"] != c["id"] and x["partido"] == c["partido"]][:4]
    rel_html = "".join(f'<a href="/c/{x["slug"]}" class="rel"><b>{esc(x["nombre"])}</b><span>{esc(x["partido"])}</span></a>' for x in rel) or "<p style='color:#888'>No hay otros del mismo espacio.</p>"
    botones = "".join(
        '<button class="btn" onclick="agregar('
        + "'" + c["id"] + "', '" + x["cargo"] + "', '" + esc(x["jur"]) + "', true"
        + ')">Comprar como ' + esc(etiqueta(x["cargo"], x["jur"])) + "</button>"
        for x in cargos)
    share_data = json.dumps({"nombre": c["nombre"], "slug": c["slug"], "partido": c["partido"],
                             "cargo": cargos[0]["cargo"] if cargos else "presidencial",
                             "jur": cargos[0]["jur"] if cargos else "Nacional",
                             "foto": c["foto"], "color": c["color"], "iniciales": ini(c["nombre"])},
                            ensure_ascii=False)
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(c["nombre"])} · Mercado Voto</title>
<meta name="description" content="{esc(limpia(c["bio"]))[:150]}">
<meta property="og:title" content="{esc(c["nombre"])} · Mercado Voto">
<meta property="og:description" content="{esc(limpia(c["bio"]))[:140]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header()}
<main class="main"><div class="wrap">
  <div class="miga"><a href="/">Inicio</a> › <a href="/c/{c["slug"]}">{esc(c["nombre"])}</a></div>
  <div class="ficha">
    {foto(c)}
    <div>
      <h1>{esc(c["nombre"])}</h1>
      <div class="rol">{esc(limpia(c["rol"])) or esc(c["partido"])}</div>
      <div class="tagline">{chips}</div>
      <div class="precio-grande">1 voto <small>por período de 4 años</small></div>
      <div class="cuotas">12 cuotas de 0 votos · envío gratis a todo el país</div>
      <div class="caja-partido">
        <div>Espacio: <b>{esc(c["partido"])}</b></div>
        <div style="margin-top:8px">{estrellas(c)}</div>
      </div>
      {botones}
      <button class="btn share" onclick="descargarVoto()">Descargar mi voto</button>
      <div class="aviso">Simulador. No se registra ningún voto ni se envía nada a ningún lado.</div>
    </div>
  </div>
  <div class="bloques">
    <div>
      <div class="panel"><h2>Quién es</h2><p>{esc(limpia(c["bio"]))}</p>{tray_html}</div>
      <div class="panel"><h2>A quién criticás</h2>
        <div class="sub">Las críticas más fuertes contra este candidato, con la evidencia y lo que respondería.</div>{crit}</div>
      <div class="panel"><h2>Preguntas y respuestas</h2>
        <div class="sub">Cada crítica puesta en formato de pregunta, con la respuesta esperada y por qué no cierra.</div>{qa}</div>
    </div>
    <div>
      <div class="panel"><h2>Composición ideológica</h2>
        <div class="sub">Estimación editorial sobre seis ejes. No es una medición.</div>{radar(c)}
        <div class="leyenda">{polos}</div></div>
      <div class="panel"><h2>Promesas</h2>
        <h3 style="color:var(--ml-green)">Cumplidas</h3><ul class="limpia si">{cum}</ul>
        <h3 style="color:#c33">Incumplidas</h3><ul class="limpia no">{inc}</ul></div>
      <div class="panel"><h2>Puntos débiles</h2><ul class="limpia">{vuln}</ul></div>
      <div class="panel"><h2>Quizás te interese</h2>{rel_html}</div>
    </div>
  </div>
</div></main>
{footer()}
<script src="/assets/carrito.js?v=5"></script>
<script>window.CAND = {share_data};</script>
<script src="/assets/share.js?v=5"></script>
</body></html>'''


def build_boleta():
    data = json.dumps({c["id"]: {"n": c["nombre"], "p": c["partido"], "f": c["foto"],
                                 "i": ini(c["nombre"]), "col": c["color"]} for c in CAND}, ensure_ascii=False)
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi boleta · Mercado Voto</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head><body>
{header()}
<main class="main"><div class="wrap" style="max-width:720px">
  <div class="panel">
    <h2>Armá tu boleta</h2>
    <div class="sub">Un presidente, un gobernador, un intendente y hasta cinco legisladores.</div>
    <div class="slot" id="s-presidencial"></div>
    <div class="slot" id="s-gobernador"></div>
    <div class="slot" id="s-intendente"></div>
    <h3 style="margin:22px 0 10px;font-size:14px;color:#444">Legisladores <span id="leg-cuenta" style="color:#999;font-weight:400"></span></h3>
    <div id="s-legislador"></div>
    <button class="btn" id="btn-armar" onclick="armar()">Armá mi boleta</button>
    <div class="aviso">Se genera una imagen para compartir. No se envía nada a ningún servidor.</div>
  </div>
</div></main>
{footer()}
<script src="/assets/carrito.js?v=5"></script>
<script src="/assets/share.js?v=5"></script>
<script>
const DATA = {data};
const CARGOS = [['presidencial','Presidente'],['gobernador','Gobernador'],['intendente','Intendente']];
function fichaHTML(it, idx){{
  const c = DATA[it.i]; if(!c) return '';
  const img = c.f ? '<img src="/' + c.f + '" alt="">' : '<div class="ini" style="background:' + c.col + '">' + c.i + '</div>';
  return '<div class="slot-item">' + img + '<div class="slot-txt"><b>' + c.n + '</b><span>' + c.p +
    (it.j && it.j !== 'Nacional' ? ' · ' + it.j : '') + '</span></div>' +
    '<button class="quitar" onclick="quitar(' + idx + ')">Quitar</button></div>';
}}
function vacioHTML(cargo, etiqueta){{
  return '<div class="slot-vacio"><span>' + etiqueta + '</span><a href="/?cargo=' + cargo + '">+ Elegir</a></div>';
}}
function renderBoleta(){{
  const b = leer();
  CARGOS.forEach(([cargo, etq]) => {{
    const idx = b.findIndex(x => x.c === cargo);
    document.getElementById('s-' + cargo).innerHTML =
      '<div class="slot-label">' + etq + '</div>' +
      (idx >= 0 ? fichaHTML(b[idx], idx) : vacioHTML(cargo, 'Sin elegir todavía'));
  }});
  const legs = b.map((x, i) => ({{x, i}})).filter(o => o.x.c === 'legislador');
  document.getElementById('leg-cuenta').textContent = '(' + legs.length + ' de 5)';
  let html = legs.map(o => fichaHTML(o.x, o.i)).join('');
  for (let k = legs.length; k < 5; k++) html += vacioHTML('legislador', 'Lugar ' + (k + 1) + ' libre');
  document.getElementById('s-legislador').innerHTML = html;
  document.getElementById('btn-armar').disabled = b.length === 0;
  document.getElementById('btn-armar').style.opacity = b.length ? 1 : .45;
}}
function armar(){{
  const b = leer();
  if(!b.length) return;
  const items = b.map(x => {{
    const c = DATA[x.i];
    return {{ c: x.c, j: x.j, n: c.n, p: c.p, color: c.col }};
  }});
  descargarBoleta(items);
}}
document.addEventListener('DOMContentLoaded', renderBoleta);
</script>
</body></html>'''


os.makedirs(f"{BASE}/c", exist_ok=True)
open(f"{BASE}/index.html", "w").write(build_index())
for c in CAND:
    open(f"{BASE}/c/{c['slug']}.html", "w").write(build_ficha(c))
open(f"{BASE}/boleta.html", "w").write(build_boleta())
print(f"index con {len(CANDIDATURAS)} candidaturas · {len(CAND)} fichas · boleta")
