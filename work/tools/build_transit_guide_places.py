#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重生成 transit-guide.html（工具 06）内嵌的口岸／学校候选清单。

数据取自工具 04 的权威 JSON，避免手工维护 694 项：
  work/tools/port_commute_data.json -> 6 个具体口岸（排除「不限／还没定」）
  work/tools/tool04_schools.json    -> 694 所学校（校名 + 地区）

页面里用 <!-- TG_PLACES_START --> ... <!-- TG_PLACES_END --> 标记数据块，
本脚本幂等替换标记之间的内容，不改页面其余部分。

用法：python3 work/tools/build_transit_guide_places.py
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAGE = os.path.join(ROOT, 'transit-guide.html')
START = '<!-- TG_PLACES_START -->'
END = '<!-- TG_PLACES_END -->'

# 同一口岸的常见叫法，只用于搜索匹配，不显示在界面上
PORT_ALIAS = {
    'lo': '罗湖口岸 罗湖站',
    'lok': '落马洲 落马洲支线 福田口岸 福田 落马洲站',
    'lt': '莲塘 香园围 莲塘口岸 香园围口岸',
    'sw': '深圳湾 深圳湾口岸',
    'hg': '新皇岗 皇岗 皇岗口岸 新皇岗口岸',
    'mk': '文锦渡 文锦渡口岸',
}
# 显示名覆盖：政府路线表里带启用日期，作为地点名太长
PORT_DISPLAY = {'hg': '新皇岗'}


def main():
    data = json.load(io.open(os.path.join(HERE, 'port_commute_data.json'), encoding='utf-8'))
    schools = json.load(io.open(os.path.join(HERE, 'tool04_schools.json'), encoding='utf-8'))

    ports = []
    for key, port in data['ports'].items():
        if key == 'any':
            continue
        label = PORT_DISPLAY.get(key, port['label'])
        ports.append([label, PORT_ALIAS.get(key, label)])
    ports.sort(key=lambda x: x[0])

    sch = [[s['n'], s.get('d') or ''] for s in schools if s.get('n')]
    sch.sort(key=lambda x: x[0])
    assert len(sch) > 600, '学校数据异常：%d 所' % len(sch)
    assert len(ports) == 6, '口岸应 6 个，实际 %d' % len(ports)

    block = (START + '\n<script>\n'
             + '/* 由 build_transit_guide_places.py 从工具 04 数据生成，勿手改 */\n'
             + 'var TG_PORTS = ' + json.dumps(ports, ensure_ascii=False, separators=(',', ':')) + ';\n'
             + 'var TG_SCHOOLS = ' + json.dumps(sch, ensure_ascii=False, separators=(',', ':')) + ';\n'
             + '</script>\n' + END)

    html = io.open(PAGE, encoding='utf-8').read()
    pat = re.escape(START) + r'.*?' + re.escape(END)
    assert re.search(pat, html, re.S), '页面里找不到 TG_PLACES 标记块'
    html = re.sub(pat, lambda m: block, html, count=1, flags=re.S)

    io.open(PAGE, 'w', encoding='utf-8').write(html)
    print('built %s | %d ports + %d schools | %d bytes'
          % (PAGE, len(ports), len(sch), len(html.encode('utf-8'))))


if __name__ == '__main__':
    main()
