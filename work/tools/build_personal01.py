#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建 personal01.html（自订权重筛选器 · 北区／大埔／沙田）

用法： python3 build_personal01.py
输入： work/tools/personal01.tpl.html + work/tools/personal01_data.json
输出： 仓库根目录 personal01.html

注：本页不列入工具超市（tools.html），只作个人／直接分享用。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

DSTR = {'北区': '北区', '大埔区': '大埔区', '沙田区': '沙田区'}

# 2026-11-14 全站统一简体中文：下面两张映射原为「简→繁」，现保留为恒等映射。
# 目的：build 时不再把校名／站名转回繁体；保留数据结构以免改动生成流程。
# 若日后要恢复繁体输出，改回这两张表即可。
S2T = str.maketrans({
    '侨': '侨', '妇': '妇', '会': '会', '孙': '孙', '凤': '凤', '创': '创', '学': '学',
    '岭': '岭', '节': '节', '属': '属', '锦': '锦', '辉': '辉', '东': '东', '华': '华',
    '马': '马', '灿': '灿', '纪': '纪', '发': '发', '圣': '圣', '荣': '荣', '郑': '郑',
    '梦': '梦', '旧': '旧', '宝': '宝', '达': '达', '黄': '黄', '銮': '銮', '贤': '贤',
    '电': '电', '联': '联', '萧': '萧', '灵': '灵', '风': '风', '润': '润', '树': '树',
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
        o['ns'] = o['n']                      # 简体原名，供搜索比对
        o['n'] = o['n'].translate(S2T)        # 繁体显示，与全站一致
        o['d'] = DSTR.get(o['d'], o['d'])
        o['p'] = fix_phone(o['p'])
        o['k'] = '—' if o['k'] in ('不适用', '不适用', None, '') else o['k']
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
    assert '晨晨' not in html, '私人资讯外泄：晨晨'
    assert '佛教' not in html, '宗教筛选内容残留'
    assert '首选' not in html and '首选' not in html, '私人结论残留'


if __name__ == '__main__':
    main()
