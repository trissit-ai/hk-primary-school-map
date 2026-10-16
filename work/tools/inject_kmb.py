#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 KMB 就近巴士站配對注入 tool01.html 的學校氣泡。
冪等：重複執行不會重複插入。需先跑 crawl_kmb.py build 產出 /tmp/kmb_bus.json。
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
             '  h += \'<div class="pop-sec"><b>就近巴士站（九巴・官方站點距離推算）</b>\';\n'
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

    # 1) 移除舊的 BUS 定義（冪等）
    t = re.sub(r"\nvar BUS = \{.*?\};\n", "\n", t, flags=re.S)
    # 2) 插入 BUS 定義到 popupSchool 之前
    t = t.replace("function popupSchool(s){",
                  "var BUS = " + json.dumps(bus, ensure_ascii=False) + ";\n\nfunction popupSchool(s){", 1)

    # 3) 插入巴士區塊到 popupSchool（在插班段之前；冪等防重複）
    if "就近巴士站（九巴" not in t:
        t = t.replace('  var iv = s.c27 || s.c26;', BUS_BLOCK + '\n  var iv = s.c27 || s.c26;', 1)

    # 4) CSS（冪等）
    if ".pop-bus{" not in t:
        t = t.replace(".pop-sec{margin-top:8px;", CSS + ".pop-sec{margin-top:8px;", 1)

    # 5) 更新免責聲明（冪等）
    old = "站點距離與口岸站數為推算值。"
    new = ("站點距離與口岸站數為推算值；就近巴士站為九巴官方站點座標按距離推算，"
           "城巴／專線小巴請另查官方 App（本工具暫未接入）。")
    if old in t and "城巴／專線小巴" not in t:
        t = t.replace(old, new, 1)

    open(TOOL01, "w", encoding="utf-8").write(t)
    print("injected. schools in BUS =", len(bus), "tool01 size =", os.path.getsize(TOOL01))

if __name__ == "__main__":
    main()
