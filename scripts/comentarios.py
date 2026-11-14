#!/usr/bin/env python3
"""Comentarios de Instagram (@guataexpress) y de la página de Facebook (Guataexpress).

  python3 scripts/comentarios.py pendientes [--posts 15]       # comentarios sin respuesta nuestra (IG + FB)
  python3 scripts/comentarios.py responder COMMENT_ID "texto"  # responde (SOLO con aprobación del dueño)

Los comentarios de Facebook tienen IDs con "_" (p. ej. 123_456); los de Instagram, solo dígitos.
Nunca imprimir tokens: las respuestas se limpian de "paging" y el token de página solo se usa en memoria.
"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path

G = "https://graph.facebook.com/v21.0"
IG = "17841454983723996"
PAGE = "730069583528980"
YO = "guataexpress"
IGNORADOS = Path(__file__).resolve().parent.parent / "comentarios_ignorados.json"

def api(path, data=None, tok=None):
    if tok:
        if data is not None: data = {**data, "access_token": tok}
        else: path += ("&" if "?" in path else "?") + urllib.parse.urlencode({"access_token": tok})
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{G}/{path}", data=body), timeout=60) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Error API en {path.split('?')[0]}: {e.read().decode()[:300]}")
    if isinstance(d, dict): d.pop("paging", None)  # la paginación puede incluir el token de página
    return d

def token_pagina():
    return api(f"{PAGE}?fields=access_token")["access_token"]  # solo en memoria

def pendientes_instagram(n, ign):
    out = []
    for m in api(f"{IG}/media?fields=id,caption,permalink,comments_count&limit={n}")["data"]:
        if not m.get("comments_count"): continue
        for c in api(f"{m['id']}/comments?fields=id,text,username,timestamp,replies%7Busername%7D&limit=50")["data"]:
            if c.get("username") == YO or c["id"] in ign: continue
            if any(r.get("username") == YO for r in c.get("replies", {}).get("data", [])): continue
            out.append({"red": "instagram", "comment_id": c["id"], "usuario": c.get("username"), "texto": c.get("text"),
                        "fecha": c.get("timestamp"), "post": m.get("permalink"), "post_caption": (m.get("caption") or "")[:80]})
    return out

def pendientes_facebook(n, ign, pt):
    out = []
    posts = api(f"{PAGE}/published_posts?fields=id,message,permalink_url,comments.summary(true).limit(0)&limit={n}", tok=pt)["data"]
    for p in posts:
        if not p.get("comments", {}).get("summary", {}).get("total_count"): continue
        cs = api(f"{p['id']}/comments?fields=id,message,from%7Bid,name%7D,created_time,comments%7Bfrom%7Bid%7D%7D&limit=50", tok=pt)["data"]
        for c in cs:
            if c.get("from", {}).get("id") == PAGE or c["id"] in ign: continue
            if any(r.get("from", {}).get("id") == PAGE for r in c.get("comments", {}).get("data", [])): continue
            out.append({"red": "facebook", "comment_id": c["id"], "usuario": c.get("from", {}).get("name", "(usuario de Facebook)"),
                        "texto": c.get("message"), "fecha": c.get("created_time"), "post": p.get("permalink_url"),
                        "post_caption": (p.get("message") or "")[:80]})
    return out

def pendientes(n=15):
    ign = set(json.loads(IGNORADOS.read_text())["ids"]) if IGNORADOS.exists() else set()
    out = pendientes_instagram(n, ign)
    try:
        out += pendientes_facebook(n, ign, token_pagina())
    except SystemExit as e:
        out.append({"red": "facebook", "error": str(e)[:300]})
    return out

def responder(cid, texto):
    if "_" in cid:  # Facebook: se responde como la página
        return api(f"{cid}/comments", {"message": texto}, tok=token_pagina())
    return api(f"{cid}/replies", {"message": texto})

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pendientes"]:
        n = int(a[a.index("--posts") + 1]) if "--posts" in a else 15
        print(json.dumps(pendientes(n), ensure_ascii=False, indent=2))
    elif a[:1] == ["responder"] and len(a) == 3:
        print(f"Respondido: {responder(a[1], a[2])}")
    else:
        print(__doc__); sys.exit(1)
