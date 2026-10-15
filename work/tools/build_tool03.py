# -*- coding: utf-8 -*-
"""
生成 工具03 口岸通勤時間試算 (tool03.html)
源數據：hk-school-map/data.json（教育局官方名冊）
用法：cd hk-school-map && python3 work/tools/build_tool03.py
"""
import json, os, io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'data.json')
TPL = os.path.join(ROOT, 'work', 'tools', 'tool03.tpl.html')
OUT = os.path.join(ROOT, 'tool03.html')

# 工具03 只需要：校名/英文/類別/地區/校網/排名/最近港鐵站/步行m/東鐵站數/收表類型
KEEP = ['n', 'e', 't', 'd', 'k', 'r', 's', 'sd', 'h', 'iv']


def main():
    src = json.load(io.open(DATA, encoding='utf-8'))
    schools = src['schools']

    recs = []
    for x in schools:
        r = {k: x.get(k) for k in KEEP}
        recs.append(r)

    dists = sorted({x.get('d') for x in schools if x.get('d')})
    stns = sorted({x.get('s') for x in schools if x.get('s')})
    meta = {'nets': [], 'dists': dists, 'stns': stns}

    tpl = io.open(TPL, encoding='utf-8').read()
    data_js = json.dumps(recs, ensure_ascii=False, separators=(',', ':'))
    meta_js = json.dumps(meta, ensure_ascii=False, separators=(',', ':'))

    assert '/*__DATA__*/' in tpl and '/*__META__*/' in tpl
    html = tpl.replace('/*__DATA__*/', data_js).replace('/*__META__*/', meta_js)

    with io.open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print('schools:', len(recs))
    print('dists:', len(dists), 'stations:', len(stns))
    print('out:', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
