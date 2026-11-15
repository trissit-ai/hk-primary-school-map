#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 工具04 · 口岸通勤时间试算 v2（tool04.html）

数据：work/tools/tool04_schools.json（694 校，含最近港铁站 s / 步行米 sd）
      work/tools/port_commute_data.json（口岸接驳 / 港铁网络 / 峰值 / 来源）
模板：work/tools/tool04_commute.tpl.html
输出：仓库根 tool04.html

用法：python3 work/tools/build_tool04_commute.py
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def validate(data, schools):
    """生成前核对数据自洽，避免把错数据推上线。"""
    assert len(schools) > 600, '学校数据异常：%d 所' % len(schools)
    assert 'ft' not in data['ports'], '落马洲支线与福田口岸是同一个口岸，不应再拆成两项'
    assert data['peaks'][0]['id'] == 'p0500', '深夜时段必须是 peaks 第一项（peakAt 依赖）'
    stops = set()
    for line in data['lines']:
        stops.update(line['stops'])
    stops.add('落马洲')
    sids = {s['id'] for s in data['sources']}
    for key, port in data['ports'].items():
        assert 'open' in port and 'close' in port, '%s 缺开放时间数值' % key
        for sid in (port.get('clearSrc') or '').split('/'):
            assert not sid or sid in sids, '%s 引用了不存在的来源 %s' % (key, sid)
        for board in port.get('boards', []):
            assert board.get('ride', 0) > 0, '%s / %s 缺车程' % (key, board.get('route'))
            if board.get('hub'):
                assert board['hub'] in stops, '%s / %s 的接续站 %s 不在港铁网络' % (
                    key, board.get('route'), board['hub'])
            for sid in (board.get('src') or '').split('/'):
                assert not sid or sid in sids, '%s / %s 引用了不存在的来源 %s' % (
                    key, board.get('route'), sid)
    missing = {s['s'] for s in schools if s.get('s')} - stops
    assert not missing, '学校最近港铁站不在网络：%s' % ', '.join(sorted(missing)[:8])


def main():
    schools = json.load(io.open(os.path.join(HERE, 'tool04_schools.json'), encoding='utf-8'))
    data = json.load(io.open(os.path.join(HERE, 'port_commute_data.json'), encoding='utf-8'))
    tpl = io.open(os.path.join(HERE, 'tool04_commute.tpl.html'), encoding='utf-8').read()
    validate(data, schools)

    # 内联数据（静态站无后端，必须内联）
    schools_js = json.dumps(schools, ensure_ascii=False, separators=(',', ':'))
    data_js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

    html = tpl.replace('/*__SCHOOLS__*/', schools_js) \
              .replace('/*__DATA__*/', data_js) \
              .replace('__N__', str(len(schools)))

    assert '/*__SCHOOLS__*/' not in html and '/*__DATA__*/' not in html
    assert '__N__' not in html
    assert 'keyword=183236193' in html, '页脚小红书 CTA 缺失'
    for bad in ('需实走', '暂无港铁接驳数据', '下一版要补', '全部为推算值，实走会不同'):
        assert bad not in html, '残留劝退话术: ' + bad

    out = os.path.join(ROOT, 'tool04.html')
    io.open(out, 'w', encoding='utf-8').write(html)
    print('built %s | %d schools | %d bytes' % (out, len(schools), len(html.encode('utf-8'))))


if __name__ == '__main__':
    main()
