#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""構建 personal01.html（自訂權重篩選器 · 北區／大埔／沙田）

用法： python3 build_personal01.py
輸入： work/tools/personal01.tpl.html + work/tools/personal01_data.json
輸出： 倉庫根目錄 personal01.html

註：本頁不列入工具超市（tools.html），只作個人／直接分享用。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

DSTR = {'北区': '北區', '大埔区': '大埔區', '沙田区': '沙田區'}

# 簡→繁（只覆蓋本表 35 所校名出現的字；站名已為繁體）
S2T = str.maketrans({
    '侨': '僑', '妇': '婦', '会': '會', '孙': '孫', '凤': '鳳', '创': '創', '学': '學',
    '岭': '嶺', '节': '節', '属': '屬', '锦': '錦', '辉': '輝', '东': '東', '华': '華',
    '马': '馬', '灿': '燦', '纪': '紀', '发': '發', '圣': '聖', '荣': '榮', '郑': '鄭',
    '梦': '夢', '旧': '舊', '宝': '寶', '达': '達', '黄': '黃', '銮': '鑾', '贤': '賢',
    '电': '電', '联': '聯', '萧': '蕭', '灵': '靈', '风': '風', '润': '潤', '树': '樹',
})


def fix_phone(p):
    p = (p or '').strip()
    if not p:
        return ''
    d = re.sub(r'\D', '', p)
    return (d[:4] + ' ' + d[4:]) if len(d) == 8 else p


def main():
    with open(os.path.join(HERE, 'personal01_data.json'), encoding='utf-8') as f:
        raw = json.load(f)

    keep = ('n', 'a', 'b', 'c', 'aw', 'e', 'f', 'door', 'd', 'k', 'station', 'p', 't')
    data = []
    for r in raw:
        o = {k: r.get(k) for k in keep}
        o['ns'] = o['n']                      # 簡體原名，供搜索比對
        o['n'] = o['n'].translate(S2T)        # 繁體顯示，與全站一致
        o['d'] = DSTR.get(o['d'], o['d'])
        o['p'] = fix_phone(o['p'])
        o['k'] = '—' if o['k'] in ('不适用', '不適用', None, '') else o['k']
        data.append(o)

    with open(os.path.join(HERE, 'personal01.tpl.html'), encoding='utf-8') as f:
        tpl = f.read()

    js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html = tpl.replace('__DATA__', js).replace('__N__', str(len(data)))

    out = os.path.join(ROOT, 'personal01.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print('built %s (%d bytes, %d schools)' % (out, os.path.getsize(out), len(data)))
    assert '__DATA__' not in html and '__N__' not in html
    assert '晨晨' not in html, '私人資訊外洩：晨晨'
    assert '佛教' not in html, '宗教篩選內容殘留'
    assert '首選' not in html and '首选' not in html, '私人結論殘留'


if __name__ == '__main__':
    main()
