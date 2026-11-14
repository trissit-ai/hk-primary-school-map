#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 KMB 就近巴士站配对注入 tool01.html 的学校气泡。
幂等：重复执行不会重复插入。需先跑 crawl_kmb.py build 产出 /tmp/kmb_bus.json。
"""
import json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL01 = os.path.join(REPO, "tool01.html")
BUS_IN = "/tmp/kmb_bus.json"

CSS = ("\n.pop-bus{margin:3px 0;font-size:12px;color:#3a4655;display:flex;flex-wrap:wrap;"
       "align-items:baseline;gap:5px}\n.pop-bus .bsn{font-weight:600;color:#2f3a48}"
       ".pop-bus .bmd{color:#8b95a3;font-size:11px}.pop-bus .brs{color:#2f7fd1;font-weight:600}\n")

BUS_BLOCK = ('if (typeof BUS !== "undefined" && BUS[s.n]) {\n'
             '  var bx = BUS[s.n];\n'
             '  h += \'<div class="pop-sec"><b>就近巴士站（九巴・官方站点距离推算）</b>\';\n'
             '  for (var bi=0; bi<bx.length; bi++){\n'
             '    var b = bx[bi];\n'
             '    h += \'<div class="pop-bus"><span class="bsn">\'+esc(b.n)+\'</span>\'\n'
             '       + \'<span class="bmd">\'+b.d+\'m</span>\'\n'
             '       + \'<span class="brs">\'+esc(b.r.join("、"))+\'</span></div>\';\n'
             '  }\n'
             '  h += \'</div>\';\n'
             '}\n')

def main():
    bus = json.load(open(BUS_IN, encoding="utf-8"))
    t = open(TOOL01, encoding="utf-8").read()

    # 1) 移除旧的 BUS 定义（幂等）
    t = re.sub(r"\nvar BUS = \{.*?\};\n", "\n", t, flags=re.S)
    # 2) 插入 BUS 定义到 popupSchool 之前
    t = t.replace("function popupSchool(s){",
                  "var BUS = " + json.dumps(bus, ensure_ascii=False) + ";\n\nfunction popupSchool(s){", 1)

    # 3) 插入巴士区块到 popupSchool（在插班段之前；幂等防重复）
    if "就近巴士站（九巴" not in t:
        t = t.replace('  var iv = s.c27 || s.c26;', BUS_BLOCK + '\n  var iv = s.c27 || s.c26;', 1)

    # 4) CSS（幂等）
    if ".pop-bus{" not in t:
        t = t.replace(".pop-sec{margin-top:8px;", CSS + ".pop-sec{margin-top:8px;", 1)

    # 5) 更新免责声明（幂等）
    old = "站点距离与口岸站数为推算值。"
    new = ("站点距离与口岸站数为推算值；就近巴士站为九巴官方站点座标按距离推算，"
           "城巴／专线小巴请另查官方 App（本工具暂未接入）。")
    if old in t and "城巴／专线小巴" not in t:
        t = t.replace(old, new, 1)

    open(TOOL01, "w", encoding="utf-8").write(t)
    print("injected. schools in BUS =", len(bus), "tool01 size =", os.path.getsize(TOOL01))

if __name__ == "__main__":
    main()
