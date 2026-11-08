#!/usr/bin/env python3
"""Estadísticas mensuales de @guataexpress.

  python3 scripts/estadisticas.py 2026-10      # mes concreto
  python3 scripts/estadisticas.py              # mes anterior (hora de Colombia)

Guarda informes/AAAA-MM.json con los datos. Métricas de cuenta: ventana de 30 días que termina el último día del mes
(límite de la API). Posts: los publicados ese mes, con sus métricas acumuladas a la fecha de consulta.
"""
import calendar, datetime as dt, json, sys, urllib.parse, urllib.request, zoneinfo
from pathlib import Path

G = "https://graph.facebook.com/v21.0"; IG = "17841454983723996"
TZ = zoneinfo.ZoneInfo("America/Bogota")
OUT = Path(__file__).resolve().parent.parent / "informes"

def api(path):
    try:
        with urllib.request.urlopen(f"{G}/{path}", timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

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
           "cuenta": cuenta, "posts": posts}
    OUT.mkdir(exist_ok=True); f = OUT / f"{y}-{m:02d}.json"
    f.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n"); print(json.dumps(res, ensure_ascii=False, indent=2)); print(f"\nGuardado en {f}")

if __name__ == "__main__": main()
