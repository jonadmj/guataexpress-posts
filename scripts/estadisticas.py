#!/usr/bin/env python3
"""Estadísticas mensuales de @guataexpress (Instagram) y de la página de Facebook Guataexpress.

  python3 scripts/estadisticas.py 2026-10      # mes concreto
  python3 scripts/estadisticas.py              # mes anterior (hora de Colombia)

Guarda informes/AAAA-MM.json con los datos. Métricas de cuenta: ventana de 30 días que termina el último día del mes
(límite de la API). Posts: los publicados ese mes, con sus métricas acumuladas a la fecha de consulta.
"""
import calendar, datetime as dt, json, sys, urllib.parse, urllib.request, zoneinfo
from pathlib import Path

G = "https://graph.facebook.com/v21.0"; IG = "17841454983723996"; PAGE = "730069583528980"
TZ = zoneinfo.ZoneInfo("America/Bogota")
OUT = Path(__file__).resolve().parent.parent / "informes"

def api(path, tok=None):
    if tok: path += ("&" if "?" in path else "?") + urllib.parse.urlencode({"access_token": tok})
    try:
        with urllib.request.urlopen(f"{G}/{path}", timeout=60) as r: d = json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:300]}
    if tok and isinstance(d, dict): d.pop("paging", None)  # la paginación incluye el token de página: no guardarla
    return d

def facebook(ini, fin, desde):
    """Métricas de la página de Facebook. Nunca devuelve ni imprime el token de página."""
    pt = api(f"{PAGE}?fields=access_token").get("access_token")
    if not pt: return {"_error": "sin acceso a la página"}
    rango = {"since": int(desde.timestamp()), "until": int(fin.timestamp())}
    fb = {}
    for met, campo in [("page_views_total", "visitas_pagina"), ("page_media_view", "visualizaciones"),
                       ("page_post_engagements", "interacciones"), ("page_daily_follows_unique", "nuevos_seguidores")]:
        r = api(f"{PAGE}/insights?" + urllib.parse.urlencode({"metric": met, "period": "day", **rango}), pt)
        if r.get("data"): fb[campo] = sum(v.get("value") or 0 for v in r["data"][0]["values"])
    r = api(f"{PAGE}/insights?" + urllib.parse.urlencode({"metric": "page_total_media_view_unique", "period": "days_28", **rango}), pt)
    if r.get("data"): fb["alcance_28d_aprox"] = r["data"][0]["values"][-1].get("value")
    info = api(f"{PAGE}?fields=followers_count", pt); fb["seguidores_actuales"] = info.get("followers_count")
    posts = []
    r = api(f"{PAGE}/published_posts?fields=id,message,created_time,permalink_url,comments.summary(true).limit(0),reactions.summary(true).limit(0)&limit=50", pt)
    for p in r.get("data", []):
        t = dt.datetime.fromisoformat(p["created_time"].replace("+0000", "+00:00")).astimezone(TZ)
        if not (ini <= t <= fin): continue
        ins = api(f"{p['id']}/insights?metric=post_media_view,post_total_media_view_unique", pt)
        posts.append({"id": p["id"], "fecha": p["created_time"], "enlace": p.get("permalink_url"),
                      "texto": (p.get("message") or "")[:100],
                      "comentarios": p.get("comments", {}).get("summary", {}).get("total_count"),
                      "reacciones": p.get("reactions", {}).get("summary", {}).get("total_count"),
                      "metricas": {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}})
    fb["posts"] = posts
    return fb

def mes_objetivo(arg):
    if arg: y, m = map(int, arg.split("-"))
    else:
        hoy = dt.datetime.now(TZ).date().replace(day=1) - dt.timedelta(days=1); y, m = hoy.year, hoy.month
    return y, m

def main():
    y, m = mes_objetivo(sys.argv[1] if len(sys.argv) > 1 else None)
    ini = dt.datetime(y, m, 1, tzinfo=TZ); fin = dt.datetime(y, m, calendar.monthrange(y, m)[1], 23, 59, tzinfo=TZ)
    desde = max(ini, fin - dt.timedelta(days=30))
    q = urllib.parse.urlencode({"metric": "reach,profile_views,accounts_engaged,total_interactions,likes,comments,saves,shares,website_clicks",
                                "period": "day", "metric_type": "total_value",
                                "since": int(desde.timestamp()), "until": int(fin.timestamp())})
    cuenta = {}
    r = api(f"{IG}/insights?{q}")
    for d in r.get("data", []): cuenta[d["name"]] = d.get("total_value", {}).get("value")
    if "error" in r: cuenta["_error"] = r["error"]
    q2 = urllib.parse.urlencode({"metric": "follower_count", "period": "day", "since": int(desde.timestamp()), "until": int(fin.timestamp())})
    r2 = api(f"{IG}/insights?{q2}")
    if r2.get("data"): cuenta["nuevos_seguidores"] = sum(v["value"] for v in r2["data"][0]["values"])
    info = api(f"{IG}?fields=followers_count,media_count")
    posts = []
    url = f"{IG}/media?fields=id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count&limit=50"
    while url:
        r = api(url); stop = False
        for p in r.get("data", []):
            t = dt.datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00")).astimezone(TZ)
            if t < ini: stop = True; break
            if t > fin: continue
            mets = "reach,saved,shares,total_interactions" + (",views" if p.get("media_product_type") == "REELS" else "")
            ins = api(f"{p['id']}/insights?metric={mets}")
            p["metricas"] = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
            p["caption"] = (p.get("caption") or "")[:100]; posts.append(p)
        nxt = r.get("paging", {}).get("next")
        url = None if stop or not nxt else nxt.split("/v", 1)[1].split("/", 1)[1]
    res = {"mes": f"{y}-{m:02d}", "consultado": dt.datetime.now(TZ).isoformat(timespec="minutes"),
           "ventana_cuenta": [desde.date().isoformat(), fin.date().isoformat()],
           "seguidores_actuales": info.get("followers_count"), "publicaciones_totales": info.get("media_count"),
           "cuenta": cuenta, "posts": posts, "facebook": facebook(ini, fin, desde)}
    OUT.mkdir(exist_ok=True); f = OUT / f"{y}-{m:02d}.json"
    f.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n"); print(json.dumps(res, ensure_ascii=False, indent=2)); print(f"\nGuardado en {f}")

if __name__ == "__main__": main()
