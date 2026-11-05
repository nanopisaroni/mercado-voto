#!/usr/bin/env python3
"""Chequea que respondan los links de referencia de las propuestas.

Uso: python3 scripts/check_refs.py
argentina.gob.ar devuelve errores 500 intermitentes; el script reintenta antes de marcar un link como caído.
"""
import json, os, subprocess, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(f"{BASE}/data/propuestas.json"))
urls = sorted({r["u"] for p in P["propuestas"] for r in p["refs"]})
caidos = []
for u in urls:
    for intento in range(3):
        c = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-m", "30", "-A", "Mozilla/5.0", "-w", "%{http_code}", u],
                           capture_output=True, text=True).stdout
        if c == "200":
            break
        time.sleep(4)
    if c != "200":
        caidos.append((c, u))
    time.sleep(1)
print(f"{len(urls)} links, {len(caidos)} sin respuesta 200")
for c, u in caidos:
    print(c, u)
