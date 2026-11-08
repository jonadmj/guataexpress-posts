#!/usr/bin/env python3
"""Publica en Instagram los posts aprobados de cola.json cuya fecha es hoy (hora de Colombia).

Uso:  python3 scripts/publicar.py [--dry-run] [--fecha AAAA-MM-DD] [--id ID]
El token lo inyecta el proxy de Claude para graph.facebook.com (no hace falta variable).
"""
import argparse, datetime, json, sys, time, urllib.parse, urllib.request, zoneinfo
from pathlib import Path

G = "https://graph.facebook.com/v21.0"
IG = "17841454983723996"
RAW = "https://raw.githubusercontent.com/jonadmj/guataexpress-posts/main/"
COLA = Path(__file__).resolve().parent.parent / "cola.json"

def api(path, data=None):
    url = f"{G}/{path}"
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Error API en {path}: {e.read().decode()}")

def esperar(cid):
    for _ in range(30):
        s = api(f"{cid}?fields=status_code,status")
        if s.get("status_code") == "FINISHED": return
        if s.get("status_code") == "ERROR": raise SystemExit(f"Contenedor {cid} con error: {s}")
        time.sleep(4)
    raise SystemExit(f"Contenedor {cid} no terminó a tiempo")

def check_urls(imgs):
    for p in imgs:
        u = RAW + p
        with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30) as r:
            ct = r.headers.get("Content-Type", "")
            if r.status != 200 or "jpeg" not in ct: raise SystemExit(f"Imagen no válida: {u} ({r.status} {ct})")

def publicar(post, dry):
    imgs = post["imagenes"]; caption = post["caption"]; loc = post.get("ubicacion_id")
    check_urls(imgs)
    print(f"[{post['id']}] {len(imgs)} imagen(es), ubicación={loc or '-'}")
    if dry: print("  dry-run: imágenes accesibles, no se crea nada"); return None
    base = {"caption": caption}
    if loc: base["location_id"] = loc
    if len(imgs) == 1:
        cid = api(f"{IG}/media", {"image_url": RAW + imgs[0], **base})["id"]
    else:
        kids = [api(f"{IG}/media", {"image_url": RAW + p, "is_carousel_item": "true"})["id"] for p in imgs]
        for k in kids: esperar(k)
        cid = api(f"{IG}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), **base})["id"]
    esperar(cid)
    mid = api(f"{IG}/media_publish", {"creation_id": cid})["id"]
    link = api(f"{mid}?fields=permalink")["permalink"]
    if post.get("primer_comentario"):
        api(f"{mid}/comments", {"message": post["primer_comentario"]})
    return mid, link

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fecha"); ap.add_argument("--id"); a = ap.parse_args()
    hoy = a.fecha or datetime.datetime.now(zoneinfo.ZoneInfo("America/Bogota")).date().isoformat()
    cola = json.loads(COLA.read_text())
    sel = [p for p in cola["posts"] if (p["id"] == a.id if a.id else p["fecha"] == hoy)]
    if not sel: print(f"No hay posts para {a.id or hoy}"); return
    for p in sel:
        if p["estado"] != "aprobado":
            print(f"[{p['id']}] estado={p['estado']} → NO se publica"); continue
        r = publicar(p, a.dry_run)
        if r:
            p["estado"] = "publicado"; p["media_id"], p["enlace"] = r
            p["publicado_en"] = datetime.datetime.now(zoneinfo.ZoneInfo("America/Bogota")).isoformat(timespec="minutes")
            COLA.write_text(json.dumps(cola, ensure_ascii=False, indent=2) + "\n")
            print(f"[{p['id']}] PUBLICADO {p['enlace']}")

if __name__ == "__main__": main()
