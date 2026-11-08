#!/usr/bin/env python3
"""Comentarios de Instagram de @guataexpress.

  python3 scripts/comentarios.py pendientes [--posts 15]   # lista comentarios sin respuesta de @guataexpress
  python3 scripts/comentarios.py responder COMMENT_ID "texto"  # responde (SOLO con aprobación del dueño)
"""
import json, sys, urllib.parse, urllib.request

G = "https://graph.facebook.com/v21.0"
IG = "17841454983723996"
YO = "guataexpress"

def api(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{G}/{path}", data=body), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Error API en {path}: {e.read().decode()}")

def pendientes(n=15):
    media = api(f"{IG}/media?fields=id,caption,permalink,comments_count,timestamp&limit={n}")["data"]
    out = []
    for m in media:
        if not m.get("comments_count"): continue
        cs = api(f"{m['id']}/comments?fields=id,text,username,timestamp,replies%7Busername%7D&limit=50")["data"]
        for c in cs:
            if c.get("username") == YO: continue
            if any(r.get("username") == YO for r in c.get("replies", {}).get("data", [])): continue
            out.append({"comment_id": c["id"], "usuario": c.get("username"), "texto": c.get("text"),
                        "fecha": c.get("timestamp"), "post": m.get("permalink"),
                        "post_caption": (m.get("caption") or "")[:80]})
    return out

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pendientes"]:
        n = int(a[a.index("--posts") + 1]) if "--posts" in a else 15
        print(json.dumps(pendientes(n), ensure_ascii=False, indent=2))
    elif a[:1] == ["responder"] and len(a) == 3:
        r = api(f"{a[1]}/replies", {"message": a[2]}); print(f"Respondido: {r}")
    else:
        print(__doc__); sys.exit(1)
