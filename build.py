#!/usr/bin/env python3
"""Genera Mercado Voto desde data/candidatos.json."""
import json, os, html, re, math

BASE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(f"{BASE}/data/candidatos.json"))
CANDS = {c["id"]: c for c in D["candidatos"]}
CAND = sorted(D["candidatos"], key=lambda c: c["nombre"])
CANDIDATURAS = D["candidaturas"]
PROP = json.load(open(f"{BASE}/data/propuestas.json", encoding="utf-8"))
EJE_NAME = {e["id"]: e["nombre"] for e in PROP["ejes"]}
ESPACIOS = {e["id"]: e for e in PROP["espacios"]}
TIPO_N = {"propuesta": "Propuesta", "vision": "Visión de país", "futuro": "Futuro posible"}
SITE = "https://mercado-voto.vercel.app"
V = "27"  # versión de assets, para romper caché

CARGOS = [("presidencial", "Presidente"), ("gobernador", "Gobernador"), ("intendente", "Intendente"), ("legislador", "Legisladores")]
CARGO_SING = {"presidencial": "Presidente", "gobernador": "Gobernador", "intendente": "Intendente", "legislador": "Legislador"}
POLOS = [("Economía", "Estado", "Mercado"), ("Sociedad", "Conservador", "Progresista"),
         ("Poder", "Institucional", "Personalista"), ("Federalismo", "Centralista", "Federal"),
         ("Cambio", "Continuidad", "Ruptura"), ("Exterior", "Autonomía", "Occidente")]
FUERZA_ESTRELLAS = {"letal": 1, "fuerte": 2, "media-fuerte": 2, "media": 3}


def esc(s):
    return html.escape(s or "", quote=True)


def limpia(s):
    s = (s or "").replace("—", ",").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip()


def ini(nombre):
    p = [x for x in re.split(r"\s+", nombre) if x]
    return (p[0][0] + (p[-1][0] if len(p) > 1 else "")).upper()


def parrafos(texto):
    ps = [limpia(p) for p in re.split(r"\n\s*\n", texto or "") if p.strip()]
    if not ps:
        return ""
    html_ = f"<p>{esc(ps[0])}</p>"
    if len(ps) > 1:
        resto = "".join(f"<p>{esc(p)}</p>" for p in ps[1:])
        html_ += f'<details class="mas"><summary>Leer la crítica completa</summary>{resto}</details>'
    return html_


def letales(c):
    return sum(1 for cr in c["criticas"] if cr.get("fuerza") == "letal")


def estrellas(c, corto=False):
    tot = c["cumplidas"] + c["incumplidas"]
    if not tot:
        return '<span class="estrellas vacia">Sin promesas medidas</span>'
    pct = c["cumplidas"] / tot
    n = max(1, min(5, int(pct * 5 + 0.5)))
    txt = f'({c["cumplidas"]}/{tot})' if corto else f'{c["cumplidas"]} de {tot} promesas cumplidas'
    return (f'<span class="estrellas" title="{c["cumplidas"]} de {tot} promesas cumplidas">'
            f'<i>{"★" * n}{"☆" * (5 - n)}</i><span>{txt}</span></span>')


def foto(c, clase="foto", eager=False):
    if c["foto"]:
        lazy = "" if eager else ' loading="lazy"'
        return f'<img class="{clase}" src="/{c["foto"]}" alt="{esc(c["nombre"])}"{lazy}>'
    return f'<div class="{clase} ini" style="--c:{c["color"]}">{ini(c["nombre"])}</div>'


def rasgos(ejes, n=2):
    """Los polos más marcados de un perfil, para describirlo en dos palabras."""
    marcados = sorted(((abs(v - 50), i, v) for i, v in enumerate(ejes) if abs(v - 50) >= 15), reverse=True)[:n]
    return [POLOS[i][2] if v > 50 else POLOS[i][1] for _, i, v in marcados]


def radar(c):
    cx, cy, rmax = 120, 112, 78
    pts, labels = [], []
    for i, v in enumerate(c["ejes"]):
        ang = math.radians(-90 + i * 60)
        r = 10 + (v / 100) * (rmax - 10)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        lx, ly = cx + (rmax + 14) * math.cos(ang), cy + (rmax + 14) * math.sin(ang)
        anchor = "middle" if abs(math.cos(ang)) < 0.3 else ("end" if math.cos(ang) < 0 else "start")
        pol = POLOS[i][2] if v >= 50 else POLOS[i][1]
        dy = -4 if ang < -1 else (12 if math.sin(ang) > 0.9 else 3)
        labels.append(f'<text x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}" class="rl">{esc(pol)}</text>')
    anillos = ""
    for frac in (0.33, 0.66, 1.0):
        p = " ".join(f"{cx + rmax*frac*math.cos(math.radians(-90+i*60)):.1f},{cy + rmax*frac*math.sin(math.radians(-90+i*60)):.1f}" for i in range(6))
        anillos += f'<polygon points="{p}" class="ra"/>'
    radios = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+rmax*math.cos(math.radians(-90+i*60)):.1f}" '
                     f'y2="{cy+rmax*math.sin(math.radians(-90+i*60)):.1f}" class="ra"/>' for i in range(6))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    puntos = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{c["color"]}"/>' for x, y in pts)
    return (f'<svg class="radar" viewBox="-38 0 316 225" role="img" aria-label="Perfil ideológico estimado de {esc(c["nombre"])}">'
            f'{anillos}{radios}<polygon points="{poly}" fill="{c["color"]}" fill-opacity="0.2" stroke="{c["color"]}" stroke-width="2"/>'
            f'{puntos}{"".join(labels)}</svg>')


def barras(c):
    filas = ""
    for (eje, izq, der), v in zip(POLOS, c["ejes"]):
        filas += (f'<div class="eje"><div class="eje-n"><span>{izq}</span><b>{eje}</b><span>{der}</span></div>'
                  f'<div class="eje-b"><i style="left:{v}%;background:{c["color"]}"></i></div></div>')
    return f'<div class="ejes">{filas}</div>'


MARK = '''<svg class="mark" viewBox="0 0 34 34" aria-hidden="true">
<rect width="34" height="34" rx="8" fill="#2d2d2d"/>
<path d="M18.2 8.6h3.1L19.7 27H11.1L9.5 12.4h12.2" fill="#ffe600"/>
<path d="M12.4 12.4a4.6 4.6 0 0 1 9.2 0" fill="none" stroke="#2d2d2d" stroke-width="2.1" stroke-linecap="round"/>
<path d="M13.9 19.2l2.1 2.1 4.3-4.5" fill="none" stroke="#2d2d2d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

ICON = {
    "wa": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.8 3h3.1l-6.8 7.7 8 10.3h-6.2l-4.9-6.3L5.4 21H2.3l7.2-8.3L1.8 3h6.4l4.4 5.8L17.8 3Zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5Z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></svg>',
    "share": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg>',
    "img": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 4v11m-4-4 4 4 4-4M4 19h16"/></svg>',
    "tg": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.9 4.6 18.8 19c-.2 1-.8 1.3-1.7.8l-4.6-3.4-2.2 2.1c-.3.3-.5.5-1 .5l.3-4.7 8.6-7.8c.4-.3-.1-.5-.6-.2L6.9 13 2.3 11.6c-1-.3-1-1 .2-1.5l18-6.9c.8-.3 1.6.2 1.4 1.4Z"/></svg>',
    "cart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M5 4h14l-1.5 15.5a1.5 1.5 0 0 1-1.5 1.5H8a1.5 1.5 0 0 1-1.5-1.5L5 4Zm4 0a3 3 0 0 1 6 0M9.5 12l2 2 3.5-4"/></svg>',
    "filtro": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 6h16M7 12h10M10 18h4"/></svg>',
}


ICONO = """<ellipse cx="66" cy="60" rx="58" ry="46" stroke="#00368C" stroke-width="4" fill="none"/>
<g stroke="#00368C" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
<path d="M56 62h44v28H56z" fill="#fff"/>
<g transform="rotate(-15 64 44)"><rect x="52" y="24" width="23" height="36" rx="2" fill="#fff"/><path d="M57 40l4 4 8.5-9" fill="none" stroke-width="4"/></g>
<path d="M56 62l8-8h44l-8 8z" fill="#fff"/>
<path d="M70 58h24" stroke-width="5.5"/>
<g fill="#fff"><rect x="14" y="28" width="26" height="30" rx="11"/><rect x="30" y="27" width="20" height="9" rx="4.5"/><rect x="30" y="37" width="20" height="9" rx="4.5"/><rect x="30" y="47" width="18" height="9" rx="4.5"/><rect x="24" y="55" width="20" height="9" rx="4.5" transform="rotate(18 34 59)"/></g>
</g>"""


def logo():
    return ('<a class="logo" href="/" aria-label="Mercado Voto, inicio">'
            '<img src="/assets/logo.webp?v=23" alt="Mercado Voto" width="534" height="162" loading="eager"></a>')


def etiqueta(cargo, jur):
    if cargo == "presidencial":
        return "Presidente"
    if cargo == "legislador":
        return "Legislador · " + jur if jur and jur != "Nacional" else "Legislador nacional"
    return ("Gobernador · " if cargo == "gobernador" else "Intendente · ") + jur


def head(titulo, desc, og_img, url, extra=""):
    return f'''<!DOCTYPE html><html lang="es-AR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#ffe600">
<link rel="icon" href="/favicon.png" type="image/png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mercado Voto">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={V}">{extra}
</head><body>'''


def header():
    nav = "".join(f'<a href="/?cargo={k}#catalogo">{v}</a>' for k, v in CARGOS)
    nav += '<a class="nav-prop" href="/propuestas">Propuestas</a>'
    nav += ('<a href="/?badge=NUEVO#catalogo">Outsiders</a><a href="/?orden=letales#catalogo">Más criticados</a>'
            '<a href="/?orden=cumplimiento#catalogo">Mejor reputación</a><a href="/?orden=ruptura#catalogo">Más disruptivos</a>')
    return f'''<header class="top"><div class="wrap">
  {logo()}
  <form class="buscador" action="/" role="search"><input id="q" name="q" type="search" placeholder="Buscá candidatos, partidos o ciudades…" autocomplete="off" aria-label="Buscar"><button aria-label="Buscar"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></form>
  <a class="mi-boleta" href="/boleta" aria-label="Mi boleta">{ICON["cart"]}<span class="n">0</span><span class="t">Mi boleta</span></a>
</div>
<nav class="nav"><div class="wrap">{nav}</div></nav></header>'''


def minibar():
    return '''<a class="minibar" id="minibar" href="/boleta" hidden>
  <span class="mb-slots" id="mb-slots"></span>
  <span class="mb-txt"><b id="mb-n">0 de 8</b><small id="mb-hint">Seguí sumando</small></span>
  <span class="mb-cta">Ver boleta →</span>
</a>'''


def footer():
    return f'''<footer><div class="wrap">
  <div class="f-logo">{logo()}<p>Un simulador para elegir candidatos como si fueran productos, leer lo que se dice a favor y en contra, y compartir tu boleta.</p></div>
  <div><b>Cómo leer las fichas</b><p>Las críticas, los argumentos a favor y el radar ideológico son una síntesis editorial, no una medición. Las estrellas salen de las promesas cumplidas registradas.</p></div>
  <div><b>Privacidad</b><p>No se compra ni se vota nada. Tu boleta vive en tu navegador y sólo se comparte si vos mandás el link.</p></div>
</div><div class="wrap legal">Mercado Voto es un proyecto independiente y satírico, sin relación con ningún marketplace ni partido. Fotos: Wikimedia Commons.</div></footer>
<div id="toast" class="toast" role="status" aria-live="polite"></div>'''


def scripts(*extra):
    base = ["/assets/data.js", "/assets/app.js"] + list(extra)
    return "".join(f'<script src="{s}?v={V}"></script>' for s in base)



# ---------------------------------------------------------------- propuestas

def prop_card(p):
    e = ESPACIOS[p["espacio"]]
    eje = EJE_NAME[p["eje"]]
    pedido = json.dumps({"id": p["id"], "titulo": p["titulo"], "esp": e["nombre"],
                         "eje": eje, "tipo": TIPO_N[p["tipo"]]}, ensure_ascii=False)
    return f'''<article class="prop" data-esp="{p["espacio"]}" data-eje="{p["eje"]}" data-tipo="{p["tipo"]}"
  data-busca="{esc((p["titulo"] + " " + p["bajada"] + " " + e["nombre"] + " " + eje).lower())}">
  <div class="p-top"><span class="p-eje">{esc(eje)}</span><span class="p-esp" style="--c:{e["color"]}">{esc(e["nombre"])}</span></div>
  <span class="p-tipo t-{p["tipo"]}">{TIPO_N[p["tipo"]]}</span>
  <h3>{esc(p["titulo"])}</h3>
  <p>{esc(p["bajada"])}</p>
  <div class="p-foot">
    <button class="btn add-p" data-id="{p["id"]}" data-prop='{esc(pedido)}'>Agregar</button>
    <button class="link-btn ver-p" data-id="{p["id"]}">Ver detalle</button>
  </div>
</article>'''


def build_propuestas():
    props = PROP["propuestas"]
    fichas = "\n".join(prop_card(p) for p in props)
    chips_esp = '<button class="chip on" data-f="esp" data-v="">Todos</button>' + "".join(
        f'<button class="chip" data-f="esp" data-v="{e["id"]}"><i style="--c:{e["color"]}"></i>{esc(e["nombre"])}</button>'
        for e in PROP["espacios"])
    chips_eje = '<button class="chip on" data-f="eje" data-v="">Todos</button>' + "".join(
        f'<button class="chip" data-f="eje" data-v="{e["id"]}">{esc(e["nombre"])}</button>' for e in PROP["ejes"])
    chips_tipo = "".join(
        f'<button class="chip{" on" if k == "propuesta" else ""}" data-f="tipo" data-v="{k}">{v}</button>'
        for k, v in TIPO_N.items())
    n_prop = sum(1 for p in props if p["tipo"] == "propuesta")
    n_vis = sum(1 for p in props if p["tipo"] == "vision")
    n_fut = sum(1 for p in props if p["tipo"] == "futuro")
    datos = json.dumps({p["id"]: {"titulo": p["titulo"], "cuerpo": p["cuerpo"], "detalle": p["detalle"],
                                  "esp": ESPACIOS[p["espacio"]]["nombre"], "color": ESPACIOS[p["espacio"]]["color"],
                                  "eje": EJE_NAME[p["eje"]], "tipo": TIPO_N[p["tipo"]], "fuente": p["fuente"],
                                  "costo": p["costo"], "alcance": p["alcance"],
                                  "candidatos": [{"n": CANDS[c]["nombre"], "s": CANDS[c]["slug"]} for c in p["candidatos"] if c in CANDS]}
                      for p in props}, ensure_ascii=False)
    desc = (f"Comprá propuestas, no solo candidatos. {len(props)} ideas de {len(PROP['espacios'])} espacios políticos, "
            "ordenadas en doce ejes temáticos, con visión de país y futuro posible.")
    return f'''{head("Propuestas, visión de país y futuro posible · Mercado Voto", desc, "/api/og", "/propuestas")}
{header()}
<main class="main"><div class="wrap">
<section class="ph">
  <small>EL OTRO CARRITO</small>
  <h1>Comprá propuestas,<br>no solo candidatos</h1>
  <p>Además de elegir a quién votás, podés elegir qué te compran. Cada espacio vende sus ideas: {n_prop} propuestas concretas, {n_vis} visiones de país y {n_fut} futuros posibles, ordenados en doce ejes.</p>
  <div class="ph-stats"><span><b>{n_prop}</b> propuestas</span><span><b>{len(PROP["espacios"])}</b> espacios</span><span><b>12</b> ejes</span></div>
</section>
<section class="pcats">
  <button class="pcat on" data-tipo="propuesta"><span>🧾</span><b>Propuestas</b><small>{n_prop} ideas concretas</small></button>
  <button class="pcat" data-tipo="vision"><span>🌎</span><b>Visión de país</b><small>{n_vis} modelos en disputa</small></button>
  <button class="pcat" data-tipo="futuro"><span>🚀</span><b>Futuro posible</b><small>{n_fut} proyecciones</small></button>
</section>
<section class="pfiltros">
  <div class="pbuscar"><input id="pq" type="search" placeholder="Buscar una propuesta, un tema, una promesa…" aria-label="Buscar propuestas"></div>
  <div class="pchips"><b>Espacio</b>{chips_esp}</div>
  <div class="pchips"><b>Eje</b>{chips_eje}</div>
  <div class="pchips"><b>Tipo</b>{chips_tipo}</div>
</section>
<div class="presumen"><h2 id="p-titulo">Todas las propuestas</h2><span id="p-cuenta">{len(props)} resultados</span></div>
<div class="pgrid" id="pgrid">{fichas}</div>
<div class="sin-res" id="pvacio" hidden><b>No encontramos propuestas con esos filtros.</b><p>Probá con otro eje o limpiá la búsqueda.</p></div>
</div></main>
<div class="pbar" id="pbar" hidden><span><b id="pbar-n">0</b> propuestas en tu carrito</span><a class="btn" href="/boleta">Ver mi boleta →</a></div>
<div class="modal" id="pm" hidden role="dialog" aria-modal="true">
  <div class="modal-c pm-c">
    <button class="cerrar" id="pm-cerrar" aria-label="Cerrar">✕</button>
    <div id="pm-body"></div>
  </div>
</div>
{footer()}
{scripts("/assets/propuestas.js")}
<script>window.MVP = {datos};</script>
</body></html>'''


# ---------------------------------------------------------------- catálogo

def card(cid, cargo, jur):
    c = CANDS[cid]
    badge = f'<span class="badge b-{c["badge"].lower()}">{c["badge"]}</span>' if c.get("badge") else ""
    n_let = letales(c)
    alerta = f'<div class="alerta">⚠ {n_let} crítica{"s" if n_let > 1 else ""} letal{"es" if n_let > 1 else ""}</div>' if n_let else ""
    tot = c["cumplidas"] + c["incumplidas"]
    cum = round(100 * c["cumplidas"] / tot) if tot else -1
    return f'''<article class="card" data-cargo="{cargo}" data-jur="{esc(jur)}" data-partido="{esc(c["partido"])}" data-badge="{c.get("badge","")}"
  data-nombre="{esc(c["nombre"].lower())}" data-eco="{c["ejes"][0]}" data-cum="{cum}" data-rupt="{c["ejes"][4]}" data-let="{n_let}">
  <a class="card-foto" href="/c/{c["slug"]}" tabindex="-1" aria-hidden="true">{foto(c)}{badge}</a>
  <div class="cuerpo">
    <span class="race">{esc(etiqueta(cargo, jur))}</span>
    <a class="nom" href="/c/{c["slug"]}">{esc(c["nombre"])}</a>
    <div class="gancho">{esc(c.get("gancho",""))}</div>
    {estrellas(c, corto=True)}
    <div class="precio">1 voto</div>
    <div class="envio">Envío gratis a tu urna</div>
    <div class="vend">{esc(c["partido"])}</div>
    {alerta}
    <button class="btn add" data-cid="{cid}" data-cargo="{cargo}" data-jur="{esc(jur)}">Agregar a la boleta</button>
  </div>
</article>'''


def build_index():
    cards = "\n".join(card(x["cid"], x["cargo"], x["jur"]) for x in CANDIDATURAS)
    partidos = sorted({c["partido"] for c in CAND})
    opt_pa = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in partidos)
    cuenta = {k: sum(1 for x in CANDIDATURAS if x["cargo"] == k) for k, _ in CARGOS}
    icon_cat = {"presidencial": "🏛️", "gobernador": "🗺️", "intendente": "🏙️", "legislador": "📜"}
    cats = "".join(f'<a class="cat" href="/?cargo={k}#catalogo" data-cargo="{k}"><span class="ci">{icon_cat[k]}</span><b>{v}</b><small>{cuenta[k]} opciones</small></a>' for k, v in CARGOS)
    cats += '<a class="cat" href="/?badge=NUEVO#catalogo"><span class="ci">✨</span><b>Outsiders</b><small>Recién llegados</small></a>'
    cats += '<button class="cat" type="button" id="sorpresa"><span class="ci">🎲</span><b>Sorprendeme</b><small>Boleta al azar</small></button>'
    filtros = f'''<aside class="filtros" id="filtros" aria-label="Filtros">
  <div class="filtros-top"><b>Filtrar</b><button type="button" class="cerrar" id="cerrar-filtros" aria-label="Cerrar filtros">✕</button></div>
  <h3>Elección</h3>
  <label><input type="radio" name="cargo" value="" checked> Todas</label>
  {"".join(f'<label><input type="radio" name="cargo" value="{k}"> {v} <small>{cuenta[k]}</small></label>' for k, v in CARGOS)}
  <h3>Jurisdicción</h3>
  <select id="f-jur" aria-label="Jurisdicción"><option value="">Todas</option></select>
  <h3>Espacio político</h3>
  <select id="f-partido" aria-label="Espacio político"><option value="">Todos</option>{opt_pa}</select>
  <h3>Condición</h3>
  <label><input type="radio" name="badge" value="" checked> Todos</label>
  <label><input type="radio" name="badge" value="NUEVO"> Nuevo (outsider)</label>
  <label><input type="radio" name="badge" value="CLÁSICO"> Clásico</label>
  <label><input type="radio" name="badge" value="REACONDICIONADO"> Reacondicionado</label>
  <h3>Economía</h3>
  <input type="range" id="f-eco" min="0" max="100" value="0" step="10" aria-label="Eje económico">
  <div class="rango"><span>Más Estado</span><span>Más mercado</span></div>
  <div class="rango-v" id="f-eco-v">Sin filtro</div>
  <button type="button" class="btn sec" id="limpiar">Limpiar filtros</button>
</aside>'''
    hero = '''<section class="hero" aria-roledescription="carrusel" aria-label="Destacados">
  <div class="slides" id="slides">
    <div class="slide s1"><div class="s-txt"><small>ELECCIONES 2027</small><h1>Armá tu boleta<br>como si fuera un carrito</h1><p>Un presidente, un gobernador, un intendente y cinco legisladores. Leé lo bueno y lo malo de cada uno antes de comprar.</p><a class="btn hero-btn" href="/?cargo=presidencial#catalogo">Empezar por Presidente</a></div><div class="s-art" aria-hidden="true">🗳️</div></div>
    <div class="slide s2"><div class="s-txt"><small>HOT SALE DE PROMESAS</small><h2>Hasta 100% incumplidas</h2><p>Ordená por reputación y mirá quién cumplió lo que prometió.</p><a class="btn hero-btn" href="/?orden=cumplimiento#catalogo">Ver mejor reputación</a></div><div class="s-art" aria-hidden="true">🏷️</div></div>
    <div class="slide s3"><div class="s-txt"><small>NUEVO</small><h2>¿Tu boleta es pura sangre<br>o Frankenstein?</h2><p>Al finalizar la compra te decimos qué tan coherente es. Después, a mandarla al grupo.</p><a class="btn hero-btn" href="/boleta">Ir a mi boleta</a></div><div class="s-art" aria-hidden="true">🧟</div></div>
  </div>
  <div class="dots" id="dots"></div>
</section>'''
    desc = "Elegí presidente, gobernador, intendente y legisladores como si fueran productos. Fichas con lo bueno, lo malo y las críticas de cada candidato. Armá tu boleta y compartila."
    return f'''{head("Mercado Voto · armá tu boleta", desc, "/api/og", "/")}
{header()}
<main class="main"><div class="wrap">
{hero}
<section class="propband">
  <div class="pb-txt"><small>NUEVO</small><h2>Ahora también se compran propuestas</h2><p>Cada espacio vende sus ideas: economía, trabajo, educación, seguridad y ocho ejes más. Sumá visión de país y futuro posible a tu carrito.</p><a class="btn" href="/propuestas">Ver las {len(PROP["propuestas"])} propuestas</a></div>
  <div class="pb-art" aria-hidden="true">💡</div>
</section>
<section class="cats" aria-label="Categorías">{cats}</section>
<div class="cols" id="catalogo">
  {filtros}
  <div>
    <div class="resumen">
      <div><h2 class="titulo-cat" id="titulo-cat">Todos los candidatos</h2><div class="cuenta" id="cuenta">{len(CANDIDATURAS)} resultados</div></div>
      <div class="resumen-acc">
        <button type="button" class="btn-filtros" id="abrir-filtros">{ICON["filtro"]} Filtrar</button>
        <label class="orden">Ordenar por <select id="orden">
          <option value="">Más relevantes</option>
          <option value="cumplimiento">Mejor reputación</option>
          <option value="letales">Más criticados</option>
          <option value="ruptura">Más disruptivos</option>
          <option value="nombre">Nombre, A a Z</option>
        </select></label>
      </div>
    </div>
    <div class="chips-activos" id="chips"></div>
    <div class="grid" id="grid">
{cards}
    </div>
    <div class="sin-res" id="vacio" hidden><b>No encontramos candidatos con esos filtros.</b><p>Probá con otra búsqueda o limpiá los filtros.</p></div>
  </div>
</div>
</div></main>
{minibar()}
{footer()}
{scripts("/assets/catalogo.js")}
</body></html>'''


# ---------------------------------------------------------------- ficha

def distancia(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a["ejes"], b["ejes"])))


def mini_card(c):
    return (f'<a class="mini" href="/c/{c["slug"]}">{foto(c, "mini-f")}<b>{esc(c["nombre"])}</b>'
            f'<span>{esc(c["partido"])}</span><span class="mini-p">1 voto</span></a>')


def build_ficha(c):
    cargos = [x for x in CANDIDATURAS if x["cid"] == c["id"]]
    tot = c["cumplidas"] + c["incumplidas"]
    n_let = letales(c)
    sub = " · ".join(filter(None, [c.get("badge", "").capitalize() or "Usado", etiqueta(cargos[0]["cargo"], cargos[0]["jur"]) if cargos else "", f'{len(c["criticas"])} críticas']))
    badge = f'<span class="badge b-{c["badge"].lower()}">{c["badge"]}</span>' if c.get("badge") else ""

    # opiniones (críticas como reseñas)
    dist = {k: 0 for k in (5, 4, 3, 2, 1)}
    ops = ""
    for k, cr in enumerate(c["criticas"]):
        f = (cr.get("fuerza") or "media").replace(" ", "-")
        n = FUERZA_ESTRELLAS.get(f, 3)
        dist[n] += 1
        ops += f'''<article class="op" id="critica-{k+1}">
  <div class="op-cab"><span class="estrellas"><i>{"★" * n}{"☆" * (5 - n)}</i></span><span class="fuerza {f}">Crítica {esc(cr.get("fuerza",""))}</span></div>
  <div class="op-area">{esc(limpia(cr.get("area","")))} · {esc(limpia(cr.get("tipo","")))}</div>
  <h3 class="op-tesis">{esc(limpia(cr.get("tesis","")))}</h3>
  {parrafos(cr.get("cuerpo",""))}
  <details><summary>Ver la evidencia</summary><div class="evid">{esc(limpia(cr.get("evidencia","")))}</div></details>
</article>'''
    prom = sum(k * v for k, v in dist.items()) / max(1, len(c["criticas"]))
    dist_html = "".join(f'<div class="dist"><span>{k} ★</span><div><i style="width:{100*v/max(1,len(c["criticas"])):.0f}%"></i></div><span>{v}</span></div>' for k, v in dist.items())

    qa = "".join(f'''<div class="qa"><div class="qa-p"><b>P:</b> {esc(limpia(cr.get("tesis","")))}</div>
<div class="qa-r"><b>R (lo que respondería):</b> {esc(limpia(cr.get("respuesta_esperada","")))}</div>
<div class="qa-r contra"><b>Repregunta:</b> {esc(limpia(cr.get("refutacion","")))}</div></div>''' for cr in c["criticas"] if cr.get("respuesta_esperada"))

    a_favor = "".join(f"<li>{esc(limpia(p))}</li>" for p in c.get("a_favor", [])) or '<li style="color:#999">Todavía no tiene argumentos cargados.</li>'
    en_contra = "".join(f'<li><a href="#critica-{k+1}">{esc(limpia(cr["tesis"]))}</a></li>' for k, cr in enumerate(c["criticas"][:4])) or '<li style="color:#999">Perfil en construcción. Todavía no tiene críticas cargadas.</li>'
    cum = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_cumplidas"])
    inc = "".join(f"<li>{esc(limpia(p))}</li>" for p in c["promesas_incumplidas"])
    promesas = (f'''<section class="panel"><h2>Promesas</h2><div class="sub">{c["cumplidas"]} cumplidas y {c["incumplidas"]} incumplidas según el registro.</div>
      <div class="barra-prom"><i style="width:{100*c["cumplidas"]/tot:.0f}%"></i></div>
      <h3 class="ok">Cumplidas</h3><ul class="limpia si">{cum}</ul>
      <h3 class="nok">Incumplidas</h3><ul class="limpia no">{inc}</ul></section>''' if tot else "")
    tray = "".join(f'<li><span class="f">{esc(t.get("fecha",""))}</span><span>{esc(limpia(t.get("evento","")))}</span></li>' for t in c["trayectoria"])
    tray_html = f"<h3>Trayectoria</h3><ul class='timeline'>{tray}</ul>" if tray else ""
    vuln = "".join(f"<li>{esc(limpia(v))}</li>" for v in c["vulnerabilidades"])
    r = rasgos(c["ejes"])
    caract = [("Espacio", c["partido"]), ("Cargo actual", limpia(c["rol"])), ("Se postula a", ", ".join(etiqueta(x["cargo"], x["jur"]) for x in cargos)),
              ("Etiquetas", c["tag"]), ("Perfil", " y ".join(r) if r else "Centro en casi todo"),
              ("Promesas cumplidas", f'{c["cumplidas"]} de {tot}' if tot else "Sin registro"),
              ("Críticas letales", str(n_let)), ("Garantía", "No tiene. Sin devolución por 4 años.")]
    caract_html = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in caract)

    otros = sorted((x for x in CAND if x["id"] != c["id"]), key=lambda x: distancia(c, x))
    parecidos = "".join(mini_card(x) for x in otros[:6])
    opuestos = "".join(mini_card(x) for x in otros[::-1][:6])

    if len(cargos) > 1:
        sel = "".join(f'<option value="{i}">{esc(etiqueta(x["cargo"], x["jur"]))}</option>' for i, x in enumerate(cargos))
        selector = f'<label class="sel-cargo">Comprar como<select id="sel-cargo">{sel}</select></label>'
    else:
        selector = f'<div class="sel-cargo uno">Para: <b>{esc(etiqueta(cargos[0]["cargo"], cargos[0]["jur"]))}</b></div>' if cargos else ""
    ficha_js = json.dumps({"id": c["id"], "nombre": c["nombre"], "slug": c["slug"], "gancho": c.get("gancho", ""),
                           "cargos": [[x["cargo"], x["jur"]] for x in cargos]}, ensure_ascii=False)
    desc = f'{c.get("gancho","")} Lo bueno, lo malo y las críticas de {c["nombre"]} en Mercado Voto.'
    share = f'''<div class="share-row" aria-label="Compartir">
        <span>Compartir</span>
        <button class="sh wa" data-share="wa" aria-label="Compartir por WhatsApp">{ICON["wa"]}</button>
        <button class="sh x" data-share="x" aria-label="Compartir en X">{ICON["x"]}</button>
        <button class="sh tg" data-share="tg" aria-label="Compartir por Telegram">{ICON["tg"]}</button>
        <button class="sh ln" data-share="link" aria-label="Copiar link">{ICON["link"]}</button>
      </div>'''
    return f'''{head(f'{c["nombre"]} · 1 voto · Mercado Voto', desc, f'/api/og?c={c["id"]}', f'/c/{c["slug"]}')}
{header()}
<main class="main"><div class="wrap">
  <div class="miga"><a href="/">Inicio</a> › {"<a href='/?cargo=" + cargos[0]["cargo"] + "#catalogo'>" + CARGO_SING[cargos[0]["cargo"]] + "</a> › " if cargos else ""}<span>{esc(c["nombre"])}</span></div>
  <div class="pdp">
    <div class="pdp-galeria">
      <div class="pdp-foto">{foto(c, "foto", eager=True)}{badge}</div>
    </div>
    <div class="pdp-info">
      <div class="pdp-sub">{esc(sub)}</div>
      <h1>{esc(c["nombre"])}</h1>
      <p class="pdp-gancho">{esc(c.get("gancho",""))}</p>
      <a href="#opiniones" class="pdp-est">{estrellas(c)}</a>
      <div class="precio-grande">1 voto</div>
      <div class="cuotas">en 4 cuotas anuales sin interés</div>
      <h3 class="saber">Lo que tenés que saber</h3>
      <ul class="saber-l">
        <li>Espacio: <b>{esc(c["partido"])}</b></li>
        <li>{esc(limpia(c["rol"]))}</li>
        <li>Perfil: {esc(" y ".join(r) if r else "centro en casi todo")}</li>
        {f'<li class="rojo">Tiene {n_let} crítica{"s" if n_let>1 else ""} letal{"es" if n_let>1 else ""}</li>' if n_let else ""}
      </ul>
      <a class="ver-car" href="#caracteristicas">Ver características</a>
    </div>
    <aside class="pdp-compra">
      <div class="envio-g"><b>Envío gratis</b> a tu urna</div>
      <div class="llega">Llega el día de la elección</div>
      <div class="stock">Stock disponible <small>(1 ejemplar, no se repone)</small></div>
      {selector}
      <button class="btn grande" id="comprar">Comprar ahora</button>
      <button class="btn sec grande add-ficha" id="agregar">Agregar a la boleta</button>
      <div class="vendedor">Vendido por <b>{esc(c["partido"])}</b><br><small>VotoLíder · {len(c["criticas"])} reclamos abiertos</small></div>
      <ul class="garantias">
        <li><b>Devolución:</b> no admite devolución por 4 años.</li>
        <li><b>Garantía de fábrica:</b> ninguna.</li>
        <li><b>Compra protegida:</b> tu voto es secreto.</li>
      </ul>
      {share}
    </aside>
  </div>

  <section class="panel pros-cons">
    <div class="pc pro"><h2><span>👍</span> Lo bueno</h2><div class="sub">Lo que dicen quienes lo apoyan.</div><ul>{a_favor}</ul></div>
    <div class="pc con"><h2><span>👎</span> Lo malo</h2><div class="sub">Las críticas más fuertes. Tocá una para leerla.</div><ul>{en_contra}</ul></div>
  </section>

  <div class="bloques">
    <div>
      <section class="panel" id="caracteristicas"><h2>Características</h2><table class="caract">{caract_html}</table></section>
      <section class="panel"><h2>Descripción</h2><p>{esc(limpia(c["bio"]))}</p>{tray_html}</section>
      <section class="panel" id="opiniones"><h2>Opiniones sobre el candidato</h2>
        <div class="op-res"><div class="op-prom"><b>{prom:.1f}</b><span class="estrellas"><i>{"★" * round(prom)}{"☆" * (5 - round(prom))}</i></span><small>{len(c["criticas"])} críticas</small></div><div class="op-dist">{dist_html}</div></div>
        <div class="sub">Cada crítica es una reseña: una estrella si es letal, tres si es media.</div>
        {ops}
      </section>
      {f'<section class="panel"><h2>Preguntas al candidato</h2><div class="sub">Qué le preguntarías, qué respondería y por qué no alcanza.</div>{qa}</section>' if qa else ""}
    </div>
    <div>
      <section class="panel"><h2>Composición ideológica</h2><div class="sub">Estimación editorial sobre seis ejes. No es una medición.</div>{radar(c)}{barras(c)}</section>
      {promesas}
      {f'<section class="panel"><h2>Puntos débiles</h2><ul class="limpia">{vuln}</ul></section>' if vuln else ""}
    </div>
  </div>
  <section class="panel carrusel"><h2>Quienes eligieron a {esc(c["nombre"].split()[0])} también eligieron</h2><div class="sub">Los perfiles ideológicos más parecidos.</div><div class="minis">{parecidos}</div></section>
  <section class="panel carrusel"><h2>Polos opuestos</h2><div class="sub">Si querés comparar con lo más distinto.</div><div class="minis">{opuestos}</div></section>
</div></main>
{minibar()}
{footer()}
<script>window.FICHA = {ficha_js};</script>
{scripts("/assets/ficha.js")}
</body></html>'''


# ---------------------------------------------------------------- boleta

def build_boleta():
    desc = "Armé mi boleta en Mercado Voto. Mirá a quién elegí y armá la tuya."
    share = f'''<div class="share-grid">
        <button class="sh-b wa" data-share="wa">{ICON["wa"]}<span>WhatsApp</span></button>
        <button class="sh-b x" data-share="x">{ICON["x"]}<span>X</span></button>
        <button class="sh-b tg" data-share="tg">{ICON["tg"]}<span>Telegram</span></button>
        <button class="sh-b ln" data-share="link">{ICON["link"]}<span>Copiar link</span></button>
        <button class="sh-b im" data-share="post">{ICON["img"]}<span>Imagen post</span></button>
        <button class="sh-b im" data-share="story">{ICON["img"]}<span>Imagen historia</span></button>
      </div>
      <button class="btn sec nativo" data-share="native" hidden>{ICON["share"]} Más opciones…</button>'''
    return f'''{head("Mi boleta · Mercado Voto", desc, "/api/og", "/boleta")}
{header()}
<main class="main"><div class="wrap">
  <div class="compartida" id="compartida" hidden>
    <div><b>👀 Te compartieron esta boleta</b><p>Mirá qué eligió, leé las fichas y armá la tuya.</p></div>
    <div class="comp-acc"><button class="btn" id="copiar-boleta">Usarla como base</button><a class="btn sec" href="/?cargo=presidencial#catalogo">Armar la mía de cero</a></div>
  </div>
  <ol class="pasos" id="pasos"><li class="on">Elegí</li><li>Revisá</li><li>Compartí</li></ol>
  <div class="checkout">
    <section class="panel">
      <div class="boleta-cab"><h1 id="b-titulo">Tu boleta</h1><button class="link-btn" id="vaciar">Vaciar</button></div>
      <div class="sub" id="b-sub">Un presidente, un gobernador, un intendente y hasta cinco legisladores.</div>
      <div id="slots"></div>
    </section>
    <section class="panel">
      <div class="boleta-cab"><h2>Propuestas en tu carrito</h2><a class="link-btn" href="/propuestas">Sumar más</a></div>
      <div class="sub">Las ideas que elegiste comprar, además de los candidatos.</div>
      <div id="b-props"></div>
    </section>
    <aside class="resumen-compra">
      <section class="panel">
        <h2>Resumen de compra</h2>
        <div class="rc-fila"><span>Candidatos (<b id="rc-n">0</b>)</span><span id="rc-votos">0 votos</span></div>
        <div class="rc-fila"><span>Propuestas</span><span id="rc-props">0</span></div>
        <div class="rc-fila"><span>Envío</span><span class="verde">Gratis</span></div>
        <div class="rc-fila"><span>Promesas cumplidas</span><span id="rc-prom">-</span></div>
        <div class="rc-fila"><span>Críticas letales en el carrito</span><span id="rc-let">0</span></div>
        <div class="rc-total"><span>Total</span><b id="rc-total">0 votos</b></div>
        <button class="btn grande" id="finalizar">Finalizar compra</button>
        <button class="btn sec" id="sorpresa">🎲 Completar al azar</button>
      </section>
      <section class="panel perfil" id="perfil" hidden>
        <h2 id="perfil-h">Perfil de tu boleta</h2>
        <div class="perfil-tipo" id="perfil-tipo"></div>
        <div id="perfil-radar"></div>
        <p class="perfil-desc" id="perfil-desc"></p>
      </section>
    </aside>
  </div>
</div></main>
<div class="modal" id="modal" hidden role="dialog" aria-modal="true" aria-labelledby="m-tit">
  <div class="modal-c">
    <button class="cerrar" id="m-cerrar" aria-label="Cerrar">✕</button>
    <div class="ok-ico">✓</div>
    <h2 id="m-tit">¡Listo! Compraste tu boleta</h2>
    <p id="m-sub">Ahora mandala al grupo de la familia y que empiece el debate.</p>
    <div class="m-prev"><img id="m-img" alt="Vista previa de tu boleta"></div>
    {share}
  </div>
</div>
{footer()}
<canvas id="confeti" aria-hidden="true"></canvas>
{scripts("/assets/share.js", "/assets/boleta.js")}
</body></html>'''


# ---------------------------------------------------------------- datos para el cliente y la API

def datos_cliente():
    cands = {}
    for c in CAND:
        tot = c["cumplidas"] + c["incumplidas"]
        cands[c["id"]] = {"n": c["nombre"], "s": c["slug"], "p": c["partido"], "f": c["foto"], "i": ini(c["nombre"]),
                          "col": c["color"], "e": c["ejes"], "cu": c["cumplidas"], "to": tot, "le": letales(c),
                          "g": c.get("gancho", "")}
    return {"c": cands, "k": [[x["cid"], x["cargo"], x["jur"]] for x in CANDIDATURAS],
            "polos": [list(p) for p in POLOS]}




os.makedirs(f"{BASE}/c", exist_ok=True)
os.makedirs(f"{BASE}/api", exist_ok=True)
open(f"{BASE}/index.html", "w").write(build_index())
for c in CAND:
    open(f"{BASE}/c/{c['slug']}.html", "w").write(build_ficha(c))
open(f"{BASE}/boleta.html", "w").write(build_boleta())

datos = json.dumps(datos_cliente(), ensure_ascii=False, separators=(",", ":"))
open(f"{BASE}/assets/data.js", "w").write(f"window.MV={datos};\n")
open(f"{BASE}/api/_data.js", "w").write(f"// Generado por build.py\nexport default {datos};\n")
print(f"index con {len(CANDIDATURAS)} candidaturas · {len(CAND)} fichas · boleta")
open(f"{BASE}/propuestas.html", "w", encoding="utf-8").write(build_propuestas())
print("propuestas:", len(PROP["propuestas"]))
