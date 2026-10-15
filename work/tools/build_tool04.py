#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""構建 tool04.html（工具 04 · 自訂權重篩選器，全港版）

輸入： work/tools/psp2026_all.json（教育局《小學概覽 2026》全港逐校抓取，S 級）
       ../../data.json（學校名冊 + 港鐵站座標）
輸出： 倉庫根目錄 tool04.html

用法： python3 build_tool04.py
"""
import io
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# 東鐵線站序（羅湖／落馬洲起算，兩者皆為 0）——用 dict，不要用 list.index
HOPS = {'羅湖': 0, '落馬洲': 0, '上水': 1, '粉嶺': 2, '太和': 3, '大埔墟': 4, '沙田': 5,
        '火炭': 6, '大圍': 7, '九龍塘': 8, '旺角東': 9, '紅磡': 10, '會展': 11, '金鐘': 12}
HOPS.update({'罗湖': 0, '落马洲': 0, '上水': 1, '粉岭': 2, '太和': 3, '大埔墟': 4, '沙田': 5,
             '火炭': 6, '大围': 7, '九龙塘': 8, '旺角东': 9, '红磡': 10, '会展': 11, '金钟': 12})

PER_HOP = 3.0        # 每站（分，含停站）
TRAIN_WAIT = 3.0     # 等車
WALK_SPEED = 80.0    # 米／分
BASE = 35.0          # 出門→口岸 10 ＋ 過關 20 ＋ 到港鐵站 5
DETOUR = 1.9         # 非東鐵：直線距離→車程（分／公里）
TRANSFER = 8.0       # 非東鐵：換乘與步行罰時
MAX_WALK = 2000      # 落站步行上限（米），超過即不給推算值

LANG = {
    '英文': 15,
    '中文（包括:普通話）及英文': 12, '中文（包括：普通話）及英文': 12,
    '中文及英文': 9,
    '中文（包括:普通話）': 6, '中文（包括：普通話）': 6,
    '中文': 2,
}
BUS = {'校車; 保姆車': 10, '校車': 8, '保姆車': 6, '-': 0, '': 0}


def hav(a, b, c, d):
    R = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


def norm_name(s):
    return re.sub(r'[\s（）()\-·．.、]', '', s or '')


def main():
    psp = json.load(io.open(os.path.join(HERE, 'psp2026_all.json'), encoding='utf-8'))
    D = json.load(io.open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
    schools = D['schools']
    stn = {s['n']: s for s in D['stations']}

    # 1) 先按電話對齊；2) 用對齊成功的配對學習 繁→簡 字表；3) 再補姓名比對
    by_phone = {re.sub(r'\D', '', x.get('p') or ''): x for x in schools if x.get('p')}
    by_name = {norm_name(x['n']): x for x in schools}

    joined = {}
    pairs = []
    for r in psp:
        t = re.sub(r'\D', '', r.get('tel') or '')
        if t and t in by_phone:
            joined[r['id']] = by_phone[t]
            pairs.append((r['n'], by_phone[t]['n']))

    t2s = {}
    for a, b in pairs:                       # a=繁（概覽） b=簡（名冊）
        na, nb = norm_name(a), norm_name(b)
        if len(na) == len(nb):
            for x, y in zip(na, nb):
                if x != y:
                    t2s.setdefault(x, y)

    def simp(s):
        return ''.join(t2s.get(c, c) for c in norm_name(s))

    by_simp = {}
    for x in schools:
        by_simp.setdefault(simp(x['n']), x)

    for r in psp:
        if r['id'] in joined:
            continue
        x = by_simp.get(simp(r['n'])) or by_name.get(norm_name(r['n']))
        if x:
            joined[r['id']] = x

    # 起點站座標（落馬洲／羅湖）
    start = stn.get('落馬洲') or stn.get('罗湖')
    if start is None:
        for k, v in stn.items():
            if k in ('落馬洲', '罗湖', '羅湖'):
                start = v
                break

    recs = []
    for r in psp:
        dragon = (r.get('一條龍中學') or '-').strip()
        direct = (r.get('直屬中學') or '-').strip()
        linked = (r.get('聯繫中學') or '-').strip()
        a = 15 if dragon and dragon != '-' else 12 if direct and direct != '-' \
            else 10 if linked and linked != '-' else 0

        lang = (r.get('教學語言') or '').strip()
        c = LANG.get(lang, 0)

        p3 = r.get('p3') or 0
        p3v = min(100.0, p3 / 8.0 * 100.0)

        fee_raw = (r.get('學費') or '-').strip()
        m = re.search(r'(\d[\d,]*)', fee_raw)
        fee = int(m.group(1).replace(',', '')) if m else 0
        feev = 100.0 if fee == 0 else max(0.0, 100.0 - fee / 700.0)

        bus = (r.get('校車服務') or '-').strip()
        busv = BUS.get(bus, 0) / 10.0 * 100.0

        x = joined.get(r['id'])
        door = None
        est = 0          # 1=東鐵站序推算 2=直線距離推算（誤差較大）
        station = ''
        walk = None
        if x:
            station = x.get('s') or ''
            walk = x.get('sd')
            # 最近站超過 2 公里＝該站不具參考性（離島、無鐵路地區），不給推算值
            if station and walk is not None and walk <= MAX_WALK:
                if station in HOPS:
                    rail = HOPS[station] * PER_HOP + TRAIN_WAIT
                    est = 1
                elif start:
                    km = hav(start['lat'], start['lon'], x['lat'], x['lon'])
                    rail = km * DETOUR + TRANSFER
                    est = 2
                else:
                    rail = None
                if rail is not None:
                    door = int(round(BASE + rail + (walk or 0) / WALK_SPEED))

        cmv = None if door is None else max(0.0, min(100.0, (100 - door) / 56.0 * 100.0))

        recs.append({
            'n': r['n'], 'ns': r['n'],
            'd': r.get('d', ''), 'k': r.get('k', ''),
            't': (r.get('學校類別') or '').strip(),
            'p': r.get('tel', ''),
            'a': a, 'c': c, 'p3': p3, 'fee': fee, 'bus': BUS.get(bus, 0),
            'p3v': round(p3v, 1), 'feev': round(feev, 1), 'busv': round(busv, 1),
            'st': station, 'wd': walk, 'door': door, 'est': est,
            'cm': None if cmv is None else round(cmv, 1),
            'start': r.get('start', ''),
            'lang': lang, 'rel': dragon if dragon != '-' else (direct if direct != '-' else (linked if linked != '-' else '')),
        })

    with_door = sum(1 for x in recs if x['door'] is not None)
    print('schools %d | joined %d | has door %d' % (len(recs), len(joined), with_door))

    tpl = io.open(os.path.join(HERE, 'tool04.tpl.html'), encoding='utf-8').read()
    html = tpl.replace('__DATA__', json.dumps(recs, ensure_ascii=False, separators=(',', ':'))) \
              .replace('__N__', str(len(recs))) \
              .replace('__DOOR__', str(with_door))
    out = os.path.join(ROOT, 'tool04.html')
    io.open(out, 'w', encoding='utf-8').write(html)
    print('built', out, os.path.getsize(out), 'bytes')

    assert '__DATA__' not in html
    # 全港公開版：只禁私人資訊與私人結論，不禁校名（含宗教背景學校，公開名冊本就收錄）
    for w in ('晨晨', '首選', '首选'):
        assert w not in html, w
    json.dump(recs, io.open(os.path.join(HERE, 'tool04_data.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)


if __name__ == '__main__':
    main()
