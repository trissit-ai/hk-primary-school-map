#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取教育局《小學概覽 2026》全港學校詳情頁（S 級官方）

用法： python3 crawl_psp2026.py [max_id]
輸出： work/tools/psp2026_all.json
"""
import concurrent.futures as cf
import html
import json
import os
import re
import ssl
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'psp2026_all.json')
BASE = 'https://www.chsc.hk/psp2026/sch_detail.php?lang_id=3&sch_id='

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

FIELDS = ['學校類別', '學生性別', '辦學團體', '宗教', '一條龍中學', '直屬中學', '聯繫中學',
          '教學語言', '校車服務', '學費', '堂費', '家長教師會會費', '其他收費']


def fetch(sid, tries=3):
    for _ in range(tries):
        try:
            req = urllib.request.Request(BASE + str(sid),
                                         headers={'User-Agent': 'Mozilla/5.0 (Macintosh)'})
            return urllib.request.urlopen(req, timeout=30, context=CTX).read().decode('utf-8', 'ignore')
        except Exception:
            continue
    return None


def to_text(h):
    t = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    lines = [x.strip() for x in t.split('\n') if x.strip()]
    return lines


def parse(sid, h):
    if not h or 'sch_detail' not in h and len(h) < 5000:
        return None
    m = re.search(r'PSP2026\s+(.+?)學校資料', h)
    if not m:
        return None
    name = m.group(1).strip()
    lines = to_text(h)

    rec = {'id': sid, 'n': name}
    for i, ln in enumerate(lines):
        for f in FIELDS:
            if ln == f and i + 1 < len(lines):
                rec.setdefault(f, lines[i + 1] if lines[i + 1] != ':' else
                               (lines[i + 2] if i + 2 < len(lines) else ''))

    # 地區 / 校網（行內可能是「大埔區   校網編號 : 84」）
    for ln in lines:
        m2 = re.match(r'^(中西區|香港東區|離島區|香港南區|灣仔區|九龍城區|觀塘區|西貢區|深水埗區|'
                      r'黃大仙區|油尖旺區|北區|沙田區|大埔區|葵青區|荃灣區|屯門區|元朗區)\s*校網編號\s*:\s*(\S+)$', ln)
        if m2:
            rec['d'], rec['k'] = m2.group(1), m2.group(2)
            break

    # 班級結構：取最後一次出現的「小三 班數」＝ 2026/27 學年
    idxs = [i for i, ln in enumerate(lines) if ln.replace(' ', '').startswith('小三') and '班數' in ln]
    if idxs:
        for j in range(idxs[-1] + 1, min(idxs[-1] + 6, len(lines))):
            if lines[j].isdigit():
                rec['p3'] = int(lines[j])
                break

    # 上學時間 / 電話
    for i, ln in enumerate(lines):
        if ln.startswith('一般上學時間') and 'start' not in rec:
            m4 = re.search(r'上午\s*(\d+:\d+)', ' '.join(lines[i:i + 4]))
            if m4:
                rec['start'] = '上午' + m4.group(1)
        if ln.startswith('電話') and 'tel' not in rec:
            m5 = re.search(r'(\d{8})', ''.join(lines[i:i + 3]))
            if m5:
                rec['tel'] = m5.group(1)
    return rec


def main():
    mx = int(sys.argv[1]) if len(sys.argv) > 1 else 660
    out = []
    miss = []
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch, i): i for i in range(1, mx + 1)}
        for fu in cf.as_completed(futs):
            i = futs[fu]
            h = fu.result()
            r = parse(i, h)
            if r:
                out.append(r)
            else:
                miss.append(i)
    out.sort(key=lambda x: x['id'])
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print('parsed %d / %d, empty ids: %d' % (len(out), mx, len(miss)))
    print('sample:', json.dumps(out[0], ensure_ascii=False)[:300] if out else 'NONE')


if __name__ == '__main__':
    main()
