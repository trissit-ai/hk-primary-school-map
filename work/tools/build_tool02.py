# -*- coding: utf-8 -*-
"""
生成 工具02 校区筛选工具 (tool02.html)
源数据：hk-school-map/data.json（教育局官方名册 + 各校官网调研）
用法：cd hk-school-map && python3 work/tools/build_tool02.py
"""
import json, os, io, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'data.json')
TPL = os.path.join(ROOT, 'work', 'tools', 'tool02.tpl.html')
OUT = os.path.join(ROOT, 'tool02.html')

KEEP = ['n', 'e', 't', 'd', 'a', 'p', 'w', 'k', 'r', 's', 'sd', 'ti', 'h', 'iv', 'cf', 'c27', 'tt']


def pub_state(x):
    """2027/28 学年插班资料状态：D=已公布确切日期 / M=有资料或已公布月份 / U=待核

    坑（2026-10-15 踩到）：不能只看「确切」两字。官网原文常有
    「2027-2028 年度确切笔试日期尚未公布」——含「确切」但其实是没公布。
    判定要点：确切 + 紧跟具体日期（20xx-xx），且整段没有「尚未公布／须向校方」。
    """
    c27 = (x.get('c27') or '')
    if re.search(r'确切(申请期|日期|时间)?\s*[：:]?\s*20\d\d', c27) \
            and not re.search(r'尚未公布|尚未公布|未公布|未公布|须向校方|待公布|待公布', c27):
        return 'D'
    if re.search(r'待核|尚未公布|尚未公布|未公布|未公布|暂未开放|暂未开放|尚未上载|尚未上载', c27):
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
            r.pop('tt', None)   # 只保留真正的一条龙学校，其余不挂此栏
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

    meta = {'nets': nets, 'dists': dists, 'stns': stns, 'tts': ['一条龙', '非一条龙']}

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
