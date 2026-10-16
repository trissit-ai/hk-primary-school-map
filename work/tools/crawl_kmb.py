#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KMB (九巴) 公開數據爬蟲 + 學校就近巴士站配對。
數據源: https://data.etabus.gov.hk/v1/transport/kmb/  (無需 API key)
僅用官方公開數據，不杜撰任何站名／路線。

用法:
  python3 crawl_kmb.py crawl     # 抓取 route-stop，建立 stop->routes (可續跑)
  python3 crawl_kmb.py build     # 用已抓數據 + tool01.html 學校座標，產出 BUS 配對
  python3 crawl_kmb.py all       # crawl 再 build
"""
import json, os, sys, time, math, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL01 = os.path.join(REPO, "tool01.html")
ROUTE_LIST = "/tmp/kmb_routes.json"
STOP_LIST = "/tmp/kmb_stops.json"
STOP_ROUTES = "/tmp/kmb_stop_routes.json"   # 產物: {stop_id: [routes]}
BUS_OUT = "/tmp/kmb_bus.json"               # 產物: {school_name: [{n,d,r}]}
BASE = "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{direction}/{st}"

def fetch(url, tries=6):
    # 關閉環境代理，直連
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with opener.open(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(1.5 + i)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return int(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def crawl():
    routes = json.load(open(ROUTE_LIST, encoding="utf-8"))["data"]
    stop_routes = {}
    if os.path.exists(STOP_ROUTES):
        stop_routes = json.load(open(STOP_ROUTES, encoding="utf-8"))
    done = set(stop_routes.get("__done__", []))
    total = len(routes)
    for i, r in enumerate(routes):
        key = r["route"] + "|" + r["bound"] + "|" + r["service_type"]
        if key in done:
            continue
        direction = "outbound" if r["bound"] == "O" else "inbound"
        url = BASE.format(route=r["route"], direction=direction, st=r["service_type"])
        d = fetch(url)
        if d and "data" in d:
            for it in d["data"]:
                sid = it.get("stop")
                if not sid:
                    continue
                stop_routes.setdefault(sid, [])
                if r["route"] not in stop_routes[sid]:
                    stop_routes[sid].append(r["route"])
        done.add(key)
        if (i+1) % 25 == 0:
            stop_routes["__done__"] = list(done)
            json.dump(stop_routes, open(STOP_ROUTES, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"  [{i+1}/{total}] done, stops mapped={len(stop_routes)-1}", flush=True)
    stop_routes["__done__"] = list(done)
    json.dump(stop_routes, open(STOP_ROUTES, "w", encoding="utf-8"), ensure_ascii=False)
    print("crawl done. stops mapped =", len(stop_routes)-1)

def extract_schools():
    txt = open(TOOL01, encoding="utf-8").read()
    import re
    m = re.search(r"var SCHOOLS\s*=\s*(\[.*?\]);", txt, re.S)
    arr = json.loads(m.group(1))
    out = {}
    for s in arr:
        if s.get("n") and s.get("lat") is not None and s.get("lon") is not None:
            out[s["n"]] = (float(s["lat"]), float(s["lon"]))
    return out

def build():
    import re
    CODE = re.compile(r"\s*\([A-Z0-9]{2,6}\)\s*$")  # 去掉站碼括號，例如 (ED553)
    stop_routes = json.load(open(STOP_ROUTES, encoding="utf-8"))
    stop_routes.pop("__done__", None)
    stops = json.load(open(STOP_LIST, encoding="utf-8"))["data"]
    smap = {s["stop"]: s for s in stops}
    schools = extract_schools()
    bus = {}
    RAD = 600  # 就近半徑(米)
    CAP = 5    # 最多顯示站數
    for name, (slat, slon) in schools.items():
        # 同一站名可能有多個 stop_id（不同方向），按站名去重，保留最近距離並合併路線
        near = {}
        for sid, s in smap.items():
            d = haversine(slat, slon, float(s["lat"]), float(s["long"]))
            if d <= RAD:
                nm = CODE.sub("", s["name_tc"])
                if nm not in near or d < near[nm][0]:
                    near[nm] = (d, sid)
        items = sorted(near.values())[:CAP]
        if not items:
            continue
        entries = []
        for d, sid in items:
            s = smap[sid]
            nm = CODE.sub("", s["name_tc"])
            rs = sorted(set(stop_routes.get(sid, [])), key=lambda x: (len(x), x))
            entries.append({"n": nm, "d": d, "r": rs})
        bus[name] = entries
    json.dump(bus, open(BUS_OUT, "w", encoding="utf-8"), ensure_ascii=False)
    covered = sum(1 for v in bus.values() if v)
    print(f"build done. schools={len(schools)} covered={covered} bus_json={os.path.getsize(BUS_OUT)}B")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "crawl":
        crawl()
    elif cmd == "build":
        build()
    else:
        crawl()
        build()
