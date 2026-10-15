# -*- coding: utf-8 -*-
"""
生成 工具02 校區篩選工具 (tool02.html)
源數據：hk-school-map/data.json（教育局官方名冊 + 各校官網調研）
用法：cd hk-school-map && python3 work/tools/build_tool02.py
"""
import json, os, io, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'data.json')
TPL = os.path.join(ROOT, 'work', 'tools', 'tool02.tpl.html')
OUT = os.path.join(ROOT, 'tool02.html')

KEEP = ['n', 'e', 't', 'd', 'a', 'p', 'w', 'k', 'r', 's', 'sd', 'ti', 'h', 'iv', 'cf', 'c27', 'tt']


def pub_state(x):
    """2027/28 學年插班資料狀態：D=已公布確切日期 / M=有資料或已公布月份 / U=待核

    坑（2026-10-15 踩到）：不能只看「確切」兩字。官網原文常有
    「2027-2028 年度確切筆試日期尚未公布」——含「確切」但其實是沒公布。
    判定要點：確切 + 緊跟具體日期（20xx-xx），且整段沒有「尚未公布／須向校方」。
    """
    c27 = (x.get('c27') or '')
    if re.search(r'確切(申請期|日期|時間)?\s*[：:]?\s*20\d\d', c27) \
            and not re.search(r'尚未公布|尚未公佈|未公布|未公佈|須向校方|待公布|待公佈', c27):
        return 'D'
    if re.search(r'待核|尚未公布|尚未公佈|未公布|未公佈|暂未开放|暫未開放|尚未上載|尚未上载', c27):
        return 'U'
    if c27:
        return 'M'
    return 'U'


def main():
    src = json.load(io.open(DATA, encoding='utf-8'))
    schools = src['schools']

    recs = []
    for x in schools:
        r = {k: x.get(k) for k in KEEP}
        if r.get('tt') is None:
            r.pop('tt', None)   # 只保留真正的一條龍學校，其餘不掛此欄
        c27 = (x.get('c27') or '').strip()
        if len(c27) > 220:
            c27 = c27[:220] + '…'
        r['c27'] = c27
        r['y'] = 1 if x.get('iv') == '全年收表' else 0
        r['pu'] = pub_state(x)
        recs.append(r)

    nets = sorted({str(x.get('k')) for x in schools
                   if x.get('k') and x.get('k') not in ('不适用', '未列名册')},
                  key=lambda v: int(v) if v.isdigit() else 9999)
    dists = sorted({x.get('d') for x in schools if x.get('d')})
    stns = sorted({x.get('s') for x in schools if x.get('s')})

    meta = {'nets': nets, 'dists': dists, 'stns': stns, 'tts': ['一條龍', '非一條龍']}

    tpl = io.open(TPL, encoding='utf-8').read()
    data_js = json.dumps(recs, ensure_ascii=False, separators=(',', ':'))
    meta_js = json.dumps(meta, ensure_ascii=False, separators=(',', ':'))

    assert '/*__DATA__*/' in tpl and '/*__META__*/' in tpl
    html = tpl.replace('/*__DATA__*/', data_js).replace('/*__META__*/', meta_js)

    with io.open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print('schools:', len(recs))
    print('nets:', len(nets), 'dists:', len(dists), 'stations:', len(stns))
    print('out:', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
