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
VIDEOS = json.load(open(f"{BASE}/data/videos.json", encoding="utf-8"))
CAMPANAS = json.load(open(f"{BASE}/data/campanas.json", encoding="utf-8"))
try:
    COMENT = json.load(open(f"{BASE}/data/comentarios.json", encoding="utf-8"))
except Exception:
    COMENT = {}
TIPO_N = {"propuesta": "Propuesta", "vision": "Visión de país", "futuro": "Futuro posible"}
SITE = "https://mercado-voto.vercel.app"
V = "39"  # versión de assets, para romper caché

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
            f'<img src="/assets/logo.webp?v={V}" alt="Mercado Voto" width="534" height="162" loading="eager"></a>')


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
<script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
<script defer src="/_vercel/insights/script.js"></script>
</head><body>'''


def header():
    nav = "".join(f'<a href="/?cargo={k}#catalogo">{v}</a>' for k, v in CARGOS)
    nav += '<a class="nav-prop" href="/propuestas">Propuestas</a>'
    nav += '<a class="nav-camp" href="/campanas">Campaña digital</a>'
    nav += ('<a href="/?badge=NUEVO#catalogo">Outsiders</a><a href="/?orden=letales#catalogo">Más criticados</a>'
            '<a href="/?orden=cumplimiento#catalogo">Mejor reputación</a><a href="/?orden=ruptura#catalogo">Más disruptivos</a>')
    nav = '<button type="button" class="lugar-btn" data-lugar>📍 <span class="lugar-txt">¿Dónde votás?</span></button>' + nav
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
  <div><b>Privacidad</b><p>Las boletas no se compran ni se votan. Las campañas digitales son un servicio aparte. Tu boleta vive en tu navegador. Cuando la finalizás, la sumamos al ranking de los más elegidos de forma anónima: sin nombre, mail ni datos personales.</p></div>
</div><div class="wrap legal">Mercado Voto es un proyecto independiente y satírico, sin relación con ningún marketplace ni partido. Fotos: Wikimedia Commons.</div></footer>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<div class="modal" id="m-lugar" hidden role="dialog" aria-modal="true" aria-labelledby="ml-tit">
  <div class="modal-c lugar-c">
    <button class="cerrar" data-cerrar-lugar aria-label="Cerrar">✕</button>
    <div class="ml-ico">📍</div>
    <h2 id="ml-tit">¿Dónde votás?</h2>
    <p>Así te mostramos sólo los candidatos a gobernador e intendente que te tocan.</p>
    <label class="ml-campo">Provincia<select id="ml-prov"></select></label>
    <div class="ml-campo" id="ml-ciudad-w" hidden><span>Ciudad</span><div class="ml-ciudades" id="ml-ciudades"></div></div>
    <div class="ml-aviso" id="ml-aviso" hidden></div>
    <button class="btn grande" id="ml-ok" disabled>Listo</button>
    <button class="link-btn" data-cerrar-lugar>Ahora no, ver todo</button>
  </div>
</div>'''


def scripts(*extra):
    base = ["/assets/data.js", "/assets/app.js"] + list(extra)
    return "".join(f'<script src="{s}?v={V}"></script>' for s in base)



# ---------------------------------------------------------------- propuestas

ICONO_EJE = {"economia": "💵", "trabajo": "👷", "produccion": "🌾", "educacion": "🎓", "salud": "🏥",
             "seguridad": "🚓", "energia": "⚡", "infraestructura": "🛣️", "social": "🤝",
             "instituciones": "🏛️", "federalismo": "🗺️", "exterior": "🌎"}


def prop_card(p):
    e = ESPACIOS[p["espacio"]]
    eje = EJE_NAME[p["eje"]]
    ico = ICONO_EJE.get(p["eje"], "•")
    pedido = json.dumps({"id": p["id"], "titulo": p["titulo"], "esp": e["nombre"],
                         "eje": eje, "tipo": TIPO_N[p["tipo"]]}, ensure_ascii=False)
    pill = ""
    if p["tipo"] != "propuesta":
        pill = f'<span class="p-pill">{TIPO_N[p["tipo"]].upper()}</span>'
    costo = f'<span class="p-costo c-{p["costo"] or "na"}">Costo {p["costo"]}</span>' if p["costo"] else ""
    est = estado_badge(p, corto=True)
    return f'''<article class="prop" data-esp="{p["espacio"]}" data-eje="{p["eje"]}" data-tipo="{p["tipo"]}" data-estado="{p["estado"]["cod"]}"
  data-busca="{esc((p["titulo"] + " " + p["bajada"] + " " + e["nombre"] + " " + eje).lower())}">
  <a class="p-visual" href="/p/{p["slug"]}" style="--c:{e["color"]}" tabindex="-1" aria-hidden="true">
    <span class="p-ico" aria-hidden="true">{ico}</span>
    <span class="p-marca">{esc(e["nombre"])}</span>
    {pill}
  </a>
  <div class="p-info">
    {est}
    <h3><a href="/p/{p["slug"]}">{esc(p["titulo"])}</a></h3>
    <p class="p-baja">{esc(p["bajada"])}</p>
    <div class="p-chips"><span class="p-eje">{esc(eje)}</span>{costo}</div>
    <div class="p-precio">1 propuesta</div>
    <div class="p-envio">Envío gratis a tu urna</div>
    <div class="p-foot">
      <button class="btn add-p" data-id="{p["id"]}" data-prop='{esc(pedido)}'>Agregar</button>
      <a class="link-btn" href="/p/{p["slug"]}">Ver ficha completa</a>
    </div>
  </div>
</article>'''


ESTADO_N = {"aprobada": ("✓", "Aprobada"), "parcial": ("◐", "Parcialmente concretada"), "en-curso": ("➜", "En curso"),
            "promesa": ("○", "Promesa"), "rechazada": ("✕", "Rechazada o vetada"), "provincial": ("◆", "Política provincial"),
            "vision": ("☆", "")}
TIPO_REF = {"plataforma": "Plataforma oficial", "norma": "Norma oficial", "oficial": "Sitio oficial",
            "prensa": "Prensa", "perfil": "Perfil periodístico"}
FUENTE_PRIMARIA = {"plataforma": ("alta", "Plataforma presentada ante la Justicia Electoral"),
                   "oficial": ("alta", "Anuncio oficial del gobierno"),
                   "prensa": ("media", "Nota periodística sobre el programa"),
                   "perfil": ("baja", "Perfil periodístico del espacio, no un documento del partido")}


def estado_badge(p, corto=False):
    cod = p["estado"]["cod"]
    if cod == "vision":
        return f'<span class="estado e-vision">{TIPO_N[p["tipo"]]}</span>'
    ico, txt = ESTADO_N[cod]
    return f'<span class="estado e-{cod}">{ico} {txt}</span>'


def texto_estado(p):
    t = p["estado"]["txt"]
    if t.strip().rstrip(".") in ("Promesa", "Promesa de campaña", "Propuesta de método"):
        return "Todavía no tiene proyecto aprobado ni medidas tomadas. Es lo que el espacio ofrece si gobierna o suma votos."
    return t


def fecha_larga(iso):
    a, m, d = iso.split("-")
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{int(d)} de {meses[int(m) - 1]} de {a}"


def prop_mini(p):
    e = ESPACIOS[p["espacio"]]
    return (f'<a class="pmini" href="/p/{p["slug"]}"><span class="pmini-c" style="--c:{e["color"]}">{ICONO_EJE.get(p["eje"], "•")}</span>'
            f'<span class="pmini-t"><small>{esc(e["nombre"])}</small><b>{esc(p["titulo"])}</b>{estado_badge(p, True)}</span></a>')


def build_propuesta(p):
    e = ESPACIOS[p["espacio"]]
    eje = EJE_NAME[p["eje"]]
    vision = p["estado"]["cod"] == "vision"
    ico = ICONO_EJE.get(p["eje"], "•")
    pedido = json.dumps({"id": p["id"], "titulo": p["titulo"], "esp": e["nombre"], "eje": eje, "tipo": TIPO_N[p["tipo"]]}, ensure_ascii=False)
    cands = [CANDS[c] for c in p["candidatos"] if c in CANDS]
    cands_html = "".join(f'<a class="pcand" href="/c/{c["slug"]}">{foto(c, "pcand-f")}<span>{esc(c["nombre"])}</span></a>' for c in cands)
    refs = p["refs"]
    n_norma = sum(1 for r in refs if r["tipo"] == "norma")
    prim = refs[0]
    nivel, prim_txt = FUENTE_PRIMARIA[prim["tipo"]]
    verif = f"""<div class="verif">
        <b>Verificación</b>
        <ul>
          <li class="v-{nivel}"><span>{'✓' if nivel != 'baja' else '!'}</span>Fuente primaria: {esc(prim_txt)}</li>
          <li class="v-alta"><span>✓</span>{len(refs)} referencias, {n_norma} de ellas normas oficiales</li>
          <li class="v-alta"><span>✓</span>Estado chequeado al {fecha_larga(PROP["verificado"])}</li>
        </ul>
        <a href="#referencias">Ver todas las fuentes</a>
      </div>"""
    refs_html = "".join(
        f'<li id="ref-{i + 1}"><span class="rtipo r-{r["tipo"]}">{TIPO_REF[r["tipo"]]}</span>'
        f'<a href="{esc(r["u"])}" target="_blank" rel="noopener">{esc(r["t"])}</a>{" <em>· fuente primaria</em>" if r.get("primaria") else ""}</li>'
        for i, r in enumerate(refs))
    li = lambda xs: "".join(f"<li>{esc(x)}</li>" for x in xs)
    como = "".join(f'<li><span class="paso-n">{i + 1}</span><span>{esc(x)}</span></li>' for i, x in enumerate(p["como"]))
    mismos = [x for x in PROP["propuestas"] if x["eje"] == p["eje"] and x["id"] != p["id"] and x["espacio"] != p["espacio"] and x["tipo"] == p["tipo"]]
    del_esp = [x for x in PROP["propuestas"] if x["espacio"] == p["espacio"] and x["id"] != p["id"]]
    share = f'''<div class="share-row" aria-label="Compartir">
        <span>Compartir</span>
        <button class="sh wa" data-share="wa" aria-label="Compartir por WhatsApp">{ICON["wa"]}</button>
        <button class="sh x" data-share="x" aria-label="Compartir en X">{ICON["x"]}</button>
        <button class="sh tg" data-share="tg" aria-label="Compartir por Telegram">{ICON["tg"]}</button>
        <button class="sh ln" data-share="link" aria-label="Copiar link">{ICON["link"]}</button>
      </div>'''
    if vision:
        cuerpo = f'''
  <section class="panel"><h2>La idea</h2><p class="lead">{esc(p["problema"])}</p><p>{esc(p["cuerpo"])}</p></section>
  <section class="panel"><h2>En qué se nota</h2><ol class="pasos-p">{como}</ol></section>'''
    else:
        cuerpo = f'''
  <section class="panel"><h2>El problema que ataca</h2><p class="lead">{esc(p["problema"])}</p><p>{esc(p["cuerpo"])}</p></section>
  <section class="panel"><h2>Cómo funcionaría</h2><ol class="pasos-p">{como}</ol></section>
  <section class="panel"><h2>Qué hace falta para que pase</h2>
    <div class="req">
      <div><small>Instrumento</small><b>{esc(p["via"]["instrumento"])}</b></div>
      <div><small>Votos necesarios</small><b>{esc(p["via"]["mayoria"])}</b></div>
      <div><small>Plazo</small><b>{esc(p["via"]["plazo"])}</b></div>
    </div>
  </section>
  <section class="panel"><h2>Quién gana y quién paga</h2>
    <div class="gp2"><div class="gana"><small>Ganan</small><p>{esc(p["ganan"])}</p></div><div class="paga"><small>Pagan</small><p>{esc(p["pagan"])}</p></div></div>
    <div class="costo-box"><b>Costo fiscal{": " + esc(p["costo"]) if p["costo"] else ""}</b><span>{esc(p["costo_txt"])}</span></div>
  </section>'''
    pros_contras = f'''<section class="panel pros-cons">
    <div class="pc pro"><h2><span>👍</span> A favor</h2><div class="sub">Los mejores argumentos para comprarla.</div><ul>{li(p["pros"])}</ul></div>
    <div class="pc con"><h2><span>👎</span> En contra</h2><div class="sub">Los mejores argumentos para no comprarla.</div><ul>{li(p["contras"])}</ul></div>
  </section>'''
    lateral = ""
    if not vision:
        lateral += f'''<section class="panel"><h2>Cómo saber si se cumplió</h2><div class="medir"><span>📏</span><p>{esc(p["medir"])}</p></div></section>
    <section class="panel"><h2>Antecedentes</h2><ul class="timeline">{"".join(f'<li><span class="f">{esc(a["a"])}</span><span>{esc(a["t"])}</span></li>' for a in p["antecedentes"])}</ul></section>'''
    lateral += f'''<section class="panel"><h2>Lo que todavía no responde</h2><ul class="limpia preguntas">{li(p["preguntas"])}</ul></section>'''
    comparar = (f'''<section class="panel carrusel"><h2>Qué proponen otros sobre {esc(eje)}</h2><div class="sub">Compará antes de comprar.</div><div class="pminis">{"".join(prop_mini(x) for x in mismos[:8])}</div></section>''' if mismos else "")
    mas = (f'''<section class="panel carrusel"><h2>Más de {esc(e["nombre"])}</h2><div class="pminis">{"".join(prop_mini(x) for x in del_esp[:8])}</div></section>''' if del_esp else "")
    ficha_js = json.dumps({"slug": p["slug"], "titulo": p["titulo"], "esp": e["nombre"]}, ensure_ascii=False)
    desc = f'{p["bajada"]} {e["nombre"]}: cómo funcionaría, qué hace falta, quién paga y las fuentes.'
    detalle = li(p["detalle"])
    return f'''{head(f'{p["titulo"]} · {e["nombre"]} · Mercado Voto', desc, f'/api/og?pr={p["id"]}', f'/p/{p["slug"]}')}
{header()}
<main class="main"><div class="wrap">
  <div class="miga"><a href="/">Inicio</a> › <a href="/propuestas">Propuestas</a> › <a href="/propuestas?eje={p["eje"]}">{esc(eje)}</a> › <span>{esc(p["titulo"])}</span></div>
  <div class="pdp ppdp">
    <div class="pdp-galeria">
      <div class="pp-visual" style="--c:{e["color"]}">
        <span class="pp-ico" aria-hidden="true">{ico}</span>
        <span class="pp-eje">{esc(eje)}</span>
        <span class="pp-marca">{esc(e["nombre"])}</span>
        <span class="pp-tipo">{TIPO_N[p["tipo"]].upper()}</span>
      </div>
    </div>
    <div class="pdp-info">
      <div class="pdp-sub">{TIPO_N[p["tipo"]]} · {esc(eje)} · Alcance {esc(p["alcance"].lower())}</div>
      <h1>{esc(p["titulo"])}</h1>
      <p class="pdp-gancho">{esc(p["bajada"])}</p>
      <div class="estado-box e-{p["estado"]["cod"]}">{estado_badge(p)}<p>{esc(texto_estado(p))}</p></div>
      <div class="precio-grande">1 propuesta</div>
      <div class="cuotas">{"Costo fiscal " + esc(p["costo"]) if p["costo"] else "Sin costo fiscal directo"}</div>
      <h3 class="saber">Lo que incluye</h3>
      <ul class="saber-l">{detalle}</ul>
      {f'<h3 class="saber">La impulsan</h3><div class="pcands">{cands_html}</div>' if cands_html else ""}
    </div>
    <aside class="pdp-compra">
      <div class="envio-g"><b>Envío gratis</b> a tu urna</div>
      <div class="vendedor">Vendida por <b>{esc(e["nombre"])}</b><br><small>{esc(e["familia"])}</small></div>
      <button class="btn grande add-p" data-id="{p["id"]}" data-prop=\'{esc(pedido)}\'>Agregar al carrito</button>
      <a class="btn sec grande" href="#comparar">Comparar con otros espacios</a>
      {verif}
      {share}
    </aside>
  </div>
  <div class="bloques">
    <div>{cuerpo}
      {pros_contras}
      <section class="panel" id="referencias"><h2>Referencias</h2><div class="sub">Fuentes de esta ficha. Las normas enlazan al texto oficial en argentina.gob.ar.</div><ol class="refs">{refs_html}</ol></section>
    </div>
    <div>{lateral}</div>
  </div>
  <div id="comparar">{comparar}</div>
  {mas}
  <p class="nota-ed">Ficha editorial de Mercado Voto. Resume la propuesta del espacio y los argumentos a favor y en contra; no es una opinión del sitio. ¿Encontraste un error? Escribinos y lo corregimos.</p>
</div></main>
{footer()}
<script>window.PROP = {ficha_js};</script>
{scripts("/assets/propuesta.js")}
</body></html>'''


def build_propuestas():
    props = PROP["propuestas"]
    fichas = "\n".join(prop_card(p) for p in props)
    n_prop = sum(1 for p in props if p["tipo"] == "propuesta")
    n_vis = sum(1 for p in props if p["tipo"] == "vision")
    n_fut = sum(1 for p in props if p["tipo"] == "futuro")

    def cuenta_eje(eid):
        return sum(1 for p in props if p["eje"] == eid and p["tipo"] == "propuesta")

    cats = "".join(
        f'<li><button class="cat-item" data-f="eje" data-v="{e["id"]}">{esc(e["nombre"])}<b>{cuenta_eje(e["id"])}</b></button></li>'
        for e in PROP["ejes"])
    chips_esp = "".join(
        f'<button class="chip" data-f="esp" data-v="{e["id"]}"><i style="--c:{e["color"]}"></i>{esc(e["nombre"])}</button>'
        for e in PROP["espacios"])
    tipos = "".join(
        f'<button class="chip{" on" if k == "propuesta" else ""}" data-f="tipo" data-v="{k}">{v}</button>'
        for k, v in TIPO_N.items())
    estados = '<button class="chip on" data-f="est" data-v="">Todos</button>' + "".join(
        f'<button class="chip" data-f="est" data-v="{k}">{ESTADO_N[k][1]} <small>{sum(1 for p in props if p["estado"]["cod"] == k)}</small></button>'
        for k in ["aprobada", "parcial", "en-curso", "promesa", "rechazada", "provincial"])
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
<div class="pcols">
  <aside class="pfiltros" id="pfiltros">
    <div class="pbuscar"><input id="pq" type="search" placeholder="Buscar propuestas…" aria-label="Buscar propuestas"></div>
    <h3>Categorías</h3>
    <ul class="pcats-list">
      <li><button class="cat-item on" data-f="eje" data-v="">Todas<b>{n_prop}</b></button></li>
      {cats}
    </ul>
    <h3>Espacio</h3>
    <div class="pchips-esp">{chips_esp}</div>
    <h3>Tipo</h3>
    <div class="pchips-tipo">{tipos}</div>
    <h3>Estado</h3>
    <div class="pchips-tipo">{estados}</div>
  </aside>
  <div class="pmain">
    <div class="presumen"><h2 id="p-titulo">Todas las propuestas</h2><span id="p-cuenta">{len(props)} resultados</span></div>
    <div class="pgrid" id="pgrid">{fichas}</div>
    <div class="sin-res" id="pvacio" hidden><b>No encontramos propuestas con esos filtros.</b><p>Probá con otro eje o limpiá la búsqueda.</p></div>
  </div>
</div>
</div></main>
<div class="pbar" id="pbar" hidden><span><b id="pbar-n">0</b> propuestas en tu carrito</span><a class="btn" href="/boleta">Ver mi boleta →</a></div>
{footer()}
{scripts("/assets/propuestas.js")}
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
    <div class="slide s1"><div class="s-txt"><small>ELECCIONES 2027</small><h1>Armá tu boleta<br>como si fuera un carrito</h1><p>Un presidente, un gobernador, un intendente y cinco legisladores. Leé lo bueno y lo malo de cada uno antes de comprar.</p><a class="btn hero-btn" href="/?guia=1#catalogo" data-guia>Armar mi boleta paso a paso</a><span class="hero-cont" id="hero-cont"></span></div><div class="s-art" aria-hidden="true">🗳️</div></div>
    <div class="slide s2"><div class="s-txt"><small>HOT SALE DE PROMESAS</small><h2>Hasta 100% incumplidas</h2><p>Ordená por reputación y mirá quién cumplió lo que prometió.</p><a class="btn hero-btn" href="/?orden=cumplimiento#catalogo">Ver mejor reputación</a></div><div class="s-art" aria-hidden="true">🏷️</div></div>
    <div class="slide s3"><div class="s-txt"><small>NUEVO</small><h2>¿Tu boleta es pura sangre<br>o Frankenstein?</h2><p>Al finalizar la compra te decimos qué tan coherente es. Después, a mandarla al grupo.</p><a class="btn hero-btn" href="/boleta">Ir a mi boleta</a></div><div class="s-art" aria-hidden="true">🧟</div></div>
    <div class="slide s4"><div class="s-txt"><small>PROPUESTAS EN VENTA</small><h2>Ahora también se compran propuestas</h2><p>Cada espacio vende sus ideas: economía, trabajo, educación, seguridad y ocho ejes más. Sumá visión de país y futuro posible a tu carrito.</p><a class="btn hero-btn" href="/propuestas">Ver las __NPROP__ propuestas</a></div><div class="s-art" aria-hidden="true">💡</div></div>
  </div>
  <div class="dots" id="dots"></div>
</section>'''.replace("__NPROP__", str(len(PROP["propuestas"])))
    desc = "Elegí presidente, gobernador, intendente y legisladores como si fueran productos. Fichas con lo bueno, lo malo y las críticas de cada candidato. Armá tu boleta y compartila."
    return f'''{head("Mercado Voto · armá tu boleta", desc, "/api/og", "/")}
{header()}
<main class="main"><div class="wrap">
{hero}

<section class="cats" aria-label="Categorías">{cats}</section>
<section class="panel semana" id="semana" hidden aria-labelledby="sem-tit">
  <div class="sem-cab"><div><h2 id="sem-tit">🔥 Lo más vendido de la semana</h2><div class="sub" id="sem-sub"></div></div>
  <a class="sem-ver" href="/boleta">Ver cómo se arma</a></div>
  <div id="sem-bloque" hidden><ol class="sem-lista" id="sem-lista"></ol></div>
  <div class="tend" id="tend" hidden><b>En tendencia</b><div class="tend-chips" id="tend-chips"></div></div>
  <p class="rk-nota">Cuenta las boletas armadas en los últimos siete días y las visitas de las últimas 48 horas. No es una encuesta.</p>
</section>
<section class="panel top-ranking" id="ranking" hidden aria-labelledby="rk-tit">
  <div class="rk-cab"><div><h2 id="rk-tit">🔥 Los más comprados</h2><div class="sub" id="rk-sub"></div></div>
  <div class="rk-tabs" id="rk-tabs" role="tablist"></div></div>
  <ol class="rk-lista" id="rk-lista"></ol>
  <p class="rk-nota">Cuenta las boletas finalizadas en este sitio. No es una encuesta ni una muestra representativa.</p>
</section>
<div class="cols" id="catalogo">
  {filtros}
  <div>
    <div class="resumen">
      <div><h2 class="titulo-cat" id="titulo-cat">Todos los candidatos</h2><div class="cuenta" id="cuenta">{len(CANDIDATURAS)} resultados</div></div>
      <div class="resumen-acc">
        <button type="button" class="btn-filtros" id="abrir-filtros">{ICON["filtro"]} Filtrar</button>
        <label class="orden">Ordenar por <select id="orden">
          <option value="">Más relevantes</option>
          <option value="elegidos" data-rk hidden>Más elegidos</option>
          <option value="cumplimiento">Mejor reputación</option>
          <option value="letales">Más criticados</option>
          <option value="ruptura">Más disruptivos</option>
          <option value="nombre">Nombre, A a Z</option>
        </select></label>
      </div>
    </div>
    <div class="guia" id="guia" hidden>
      <div class="guia-pasos" id="guia-pasos"></div>
      <div class="guia-txt"><b id="guia-tit"></b><small id="guia-sub"></small></div>
      <div class="guia-acc"><button type="button" class="link-btn" id="guia-saltar">Saltar</button><button type="button" class="btn" id="guia-sig" hidden></button><button type="button" class="cerrar" id="guia-salir" aria-label="Salir del armado guiado">✕</button></div>
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
{scripts("/assets/catalogo.js", "/assets/semana.js")}
</body></html>'''



# ---------------------------------------------------------------- bloques de ficha

ESP_MAP = [("LA LIBERTAD AVANZA", "lla"), ("PRO", "pro"), ("UNIÓN CÍVICA RADICAL", "ucr"), ("UCR", "ucr"),
           ("HACEMOS", "hacemos"), ("PROVINCIAS UNIDAS", "pu"), ("FRENTE DE IZQUIERDA", "fit"),
           ("PARTIDO OBRERO", "fit"), ("COALICIÓN CÍVICA", "cc"), ("ENCUENTRO", "erf"),
           ("UNIÓN POR LA PATRIA", "fp"), ("JUSTICIALISTA", "fp"), ("PERONISTA", "fp")]


def espacio_de(c):
    up = (c.get("partido") or "").upper()
    for k, v in ESP_MAP:
        if k in up:
            return v
    return None


def bloque_videos(c):
    vids = VIDEOS.get(c["id"], [])
    busq = "https://www.youtube.com/results?search_query=" + \
        __import__("urllib.parse", fromlist=["quote"]).quote(c["nombre"] + " entrevista")
    if not vids:
        return f'''<section class="panel" id="videos"><h2>Escuchalo antes de comprar</h2>
  <div class="sub">No encontramos videos verificados de {esc(c["nombre"])}. Podés buscarlo vos.</div>
  <a class="btn sec" href="{busq}" target="_blank" rel="noopener">Buscar videos en YouTube</a></section>'''
    items = ""
    for i, v in enumerate(vids):
        items += f'''<button class="vid" data-vid="{v["id"]}" aria-label="Reproducir {esc(v["titulo"])}">
  <img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy">
  <span class="play" aria-hidden="true">▶</span>
  <span class="vid-t">{esc(v["titulo"])}</span>
  <span class="vid-c">{esc((v.get("canal") or "YouTube")[:28])}</span>
</button>'''
    return f'''<section class="panel" id="videos">
  <div class="vids-cab"><div><h2>Escuchalo antes de comprar</h2>
  <div class="sub">Para oírle la voz y ver qué responde cuando le preguntan, no solo lo que dice el afiche.</div></div>
  <a class="link-btn" href="{busq}" target="_blank" rel="noopener">Ver más en YouTube ↗</a></div>
  <div class="vids-grid">{items}</div>
</section>'''


def bloque_propuestas(c):
    props = [p for p in PROP["propuestas"] if c["id"] in p["candidatos"]]
    if not props:
        return ""
    return f'''<section class="panel carrusel"><h2>Propuestas que impulsa</h2><div class="sub">Cada una tiene su ficha con fuentes, costo y qué hace falta para que pase.</div><div class="pminis">{"".join(prop_mini(p) for p in props)}</div></section>'''


def bloque_veredicto(c):
    favor = (c.get("a_favor") or [""])[0]
    contra = (c.get("vulnerabilidades") or [""])[0]
    if not favor and not contra:
        return ""
    e = espacio_de(c)
    extra = ""
    if e:
        esp = ESPACIOS.get(e)
        n = sum(1 for x in PROP["propuestas"] if x["espacio"] == e)
        if esp:
            extra = f'''<div class="ver-extra"><a href="/propuestas?esp={e}">Ver las {n} propuestas de {esc(esp["nombre"])} →</a></div>'''
    return f'''<section class="panel veredicto">
  <h2>El veredicto</h2>
  <div class="vcols">
    <div class="vsi"><b>Compralo si te convence esto</b><p>{esc(limpia(favor))}</p></div>
    <div class="vno"><b>No lo compres si te pesa esto</b><p>{esc(limpia(contra))}</p></div>
  </div>
  {extra}
</section>'''


# ---------------------------------------------------------------- ficha

def distancia(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a["ejes"], b["ejes"])))


def mini_card(c):
    return (f'<a class="mini" href="/c/{c["slug"]}">{foto(c, "mini-f")}<b>{esc(c["nombre"])}</b>'
            f'<span>{esc(c["partido"])}</span><span class="mini-p">1 voto</span></a>')


def bloque_comentarios(c):
    items = COMENT.get(c["id"]) or []
    if not items:
        return ""

    def uno(x):
        red = (x.get("red") or "x").lower()
        ico = "X" if red == "x" else "IG"
        cap = f'<img src="{esc(x["captura"])}" alt="Captura del comentario" loading="lazy">' if x.get("captura") else ""
        link = f'<a href="{esc(x["url"])}" target="_blank" rel="noopener">Ver el posteo</a>' if x.get("url") else ""
        pie = f'<div class="com-pie">{link}</div>' if link else ""
        return f'''<article class="com">
  <div class="com-cab"><span class="com-red {red}">{ico}</span><b>{esc(x.get("autor", ""))}</b><span class="com-f">{esc(x.get("fecha", ""))}</span></div>
  <p>{esc(x.get("texto", ""))}</p>{cap}{pie}
</article>'''

    hay_x = any((x.get("red") or "x").lower() == "x" for x in items)
    titulo = "Lo que dicen en X" if hay_x else "Lo que dicen en redes"
    return f'''<section class="panel coms"><h2>{titulo}</h2>
  <div class="sub">Selección del equipo. No es una muestra ni un ranking: son las piezas que nos parecieron más útiles para leer al candidato.</div>
  <div class="com-grid">{"".join(uno(x) for x in items)}</div></section>'''


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
        {f'<li>En X: <a href="https://x.com/{esc(c["x"])}" target="_blank" rel="noopener">@{esc(c["x"])}</a></li>' if c.get("x") else ""}
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

  {bloque_videos(c)}

  {bloque_veredicto(c)}
  {bloque_propuestas(c)}
  {bloque_comentarios(c)}

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
    <p class="m-rk" id="m-rk" hidden></p>
    <div class="m-prev"><img id="m-img" alt="Vista previa de tu boleta"></div>
    {share}
  </div>
</div>
{footer()}
<canvas id="confeti" aria-hidden="true"></canvas>
{scripts("/assets/share.js", "/assets/boleta.js")}
</body></html>'''


# ---------------------------------------------------------------- datos para el cliente y la API

PROVINCIAS = ["Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa",
              "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis",
              "Santa Cruz", "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"]
# Ciudades con candidatos a intendente cargados y su provincia. En CABA el "intendente" es el jefe de Gobierno.
CIUDAD_PROV = {"CABA": "CABA", "Córdoba": "Córdoba", "Rosario": "Santa Fe", "Mendoza": "Mendoza"}


def lugares():
    ciudades = {x["jur"] for x in CANDIDATURAS if x["cargo"] == "intendente"}
    faltan = ciudades - set(CIUDAD_PROV)
    assert not faltan, f"Falta mapear a provincia: {faltan}"
    return {"provs": PROVINCIAS, "ciudades": {c: CIUDAD_PROV[c] for c in sorted(ciudades)}}


def datos_cliente():
    cands = {}
    for c in CAND:
        tot = c["cumplidas"] + c["incumplidas"]
        cands[c["id"]] = {"n": c["nombre"], "s": c["slug"], "p": c["partido"], "f": c["foto"], "i": ini(c["nombre"]),
                          "col": c["color"], "e": c["ejes"], "cu": c["cumplidas"], "to": tot, "le": letales(c),
                          "g": c.get("gancho", "")}
    return {"c": cands, "k": [[x["cid"], x["cargo"], x["jur"]] for x in CANDIDATURAS], "lugar": lugares(),
            "polos": [list(p) for p in POLOS]}




# ---------------------------------------------------------------- campañas

ICONO_PLAN = {"arranque": "🚀", "treinta": "📅", "integral": "🏆"}


def plata(n):
    return "$" + f"{n:,}".replace(",", ".")


def camp_card(p):
    incluye = "".join(f"<li>{esc(x)}</li>" for x in p["incluye"])
    return f'''<article class="ccard" data-plan="{p["id"]}" data-nombre="{esc(p["nombre"])}" data-precio="{p["precio"]}">
  <div class="ccard-img" aria-hidden="true"><span>{ICONO_PLAN.get(p["id"], "✨")}</span><small>MERCADO VOTO · SERVICIOS</small></div>
  <div class="ccard-cuerpo">
    <span class="ccard-tag">Campaña digital · {esc(p["dias"])}</span>
    <h3>{esc(p["nombre"])}</h3>
    <p class="ccard-res">{esc(p["resumen"])}</p>
    <div class="ccard-precio">{plata(p["precio"])}<small>pago único · precio de lanzamiento</small></div>
    <details class="ccard-inc"><summary>Qué incluye</summary><ul>{incluye}</ul><p class="ccard-ideal">{esc(p["ideal"])}</p></details>
    <button class="btn add-camp" data-plan="{p["id"]}">Contratar</button>
  </div>
</article>'''


def addon_card(a):
    return f'''<div class="addon" data-addon="{a["id"]}" data-nombre="{esc(a["nombre"])}" data-precio="{a["precio"]}">
  <div class="addon-txt"><b>{esc(a["nombre"])}</b><p>{esc(a["detalle"])}</p></div>
  <div class="addon-acc"><span>{plata(a["precio"])}</span><button type="button" class="link-btn addon-add">Sumar</button></div>
</div>'''


def build_campanas():
    planes = "".join(camp_card(p) for p in CAMPANAS["planes"])
    addons = "".join(addon_card(a) for a in CAMPANAS["addons"])
    desc = "Campaña digital para candidaturas: sliders, posteos, videos verticales y PDF de lineamientos. Elegí un plan y coordinamos."
    return f'''{head("Campaña digital · Mercado Voto", desc, "/api/og", "/campanas")}
{header()}
<main class="main"><div class="wrap">
<div class="miga"><a href="/">Inicio</a> › <span>Campaña digital</span></div>
<section class="camp-hero">
  <div class="ch-txt"><small>SE COMPRA ACÁ</small><h1>Campaña digital para tu candidatura</h1>
  <p>Sliders, posteos, videos verticales y el PDF de lineamientos. Elegí un plan, sumá lo que falte y lo coordinamos por WhatsApp.</p></div>
  <div class="ch-art" aria-hidden="true">📣</div>
</section>
<div class="camp-grid">{planes}</div>
<h2 class="camp-sub">Sumale algo suelto</h2>
<div class="addons">{addons}</div>
<section class="panel camp-como">
  <h2>Cómo sigue</h2>
  <ol class="pasos">
    <li><b>1. Elegís el plan</b><span>Contratar y sumar los extras que necesites.</span></li>
    <li><b>2. Dejás el contacto</b><span>Nombre, mail o WhatsApp y el espacio.</span></li>
    <li><b>3. Coordinamos</b><span>Te escribimos para el pago por transferencia y arrancamos en 48 horas.</span></li>
  </ol>
  <p class="rk-nota">Los precios son de lanzamiento y se pueden cambiar. El sitio no cobra nada: registra el pedido y lo coordina una persona.</p>
</section>
</div></main>
<div class="camp-bar" id="camp-bar" hidden>
  <div class="cb-txt" id="cb-txt"></div>
  <div class="cb-total" id="cb-total"></div>
  <button class="btn" type="button" id="cb-seguir">Continuar</button>
</div>
<div class="modal" id="m-pedido" hidden role="dialog" aria-modal="true" aria-labelledby="mp-tit">
  <div class="modal-c ped-c">
    <button class="cerrar" type="button" data-cerrar-pedido aria-label="Cerrar">✕</button>
    <h2 id="mp-tit">Confirmá el pedido</h2>
    <div id="ped-resumen"></div>
    <form id="ped-form">
      <label class="ml-campo">Tu nombre<input id="p-nombre" required maxlength="80" autocomplete="name"></label>
      <label class="ml-campo">Mail o WhatsApp<input id="p-contacto" required maxlength="120" autocomplete="email" placeholder="Para escribirte"></label>
      <label class="ml-campo">Espacio o candidatura<input id="p-espacio" maxlength="80" placeholder="Ej: UCR Córdoba"></label>
      <label class="ml-campo">Algo que tengamos que saber<textarea id="p-notas" rows="3" maxlength="500"></textarea></label>
      <div class="p-error" id="p-error" hidden></div>
      <button class="btn grande" type="submit" id="p-enviar">Confirmar pedido</button>
      <p class="ped-nota">No se cobra nada ahora. Te escribimos para coordinar el pago.</p>
    </form>
    <div id="ped-ok" hidden></div>
  </div>
</div>
{footer()}
{scripts("/assets/campanas.js")}
</body></html>'''


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
prop_og = {p["id"]: {"t": p["titulo"], "b": p["bajada"], "esp": ESPACIOS[p["espacio"]]["nombre"],
                    "col": ESPACIOS[p["espacio"]]["color"], "eje": EJE_NAME[p["eje"]], "tipo": TIPO_N[p["tipo"]],
                    "est": "" if p["estado"]["cod"] == "vision" else ESTADO_N[p["estado"]["cod"]][1],
                    "refs": len(p["refs"])} for p in PROP["propuestas"]}
open(f"{BASE}/api/_prop.js", "w").write("// Generado por build.py\nexport default " + json.dumps(prop_og, ensure_ascii=False, separators=(",", ":")) + ";\n")
os.makedirs(f"{BASE}/p", exist_ok=True)
for p in PROP["propuestas"]:
    open(f"{BASE}/p/{p['slug']}.html", "w", encoding="utf-8").write(build_propuesta(p))
print("propuestas:", len(PROP["propuestas"]))
open(f"{BASE}/campanas.html", "w", encoding="utf-8").write(build_campanas())
print("campañas:", len(CAMPANAS["planes"]), "planes y", len(CAMPANAS["addons"]), "extras")
