#!/usr/bin/env python3
"""build_share01.py — 生成 share01.html（小学大事件日期共享 · 非公开页）
表格五维：开放日 / 开始报名 / 截止报名 / 面试日 / 结果公布
种子：data.json 的 iv 栏（各校官网逐校抓取的插班收表状态）→ 开始报名（月份级）；
其余四栏留空待家长共享，核实后填入。
重跑：python3 build_share01.py
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
recs = data if isinstance(data, list) else data.get('schools') or list(data.values())[0]

rows = []
for r in recs:
    iv = (r.get('iv') or '').strip()
    if not iv:
        continue
    rows.append({
        'n': r.get('n', ''), 'e': r.get('e', ''), 'd': r.get('d', ''),
        'k': r.get('k', ''), 't': r.get('t', ''), 'iv': iv,
    })
rows.sort(key=lambda x: (x['iv'], x['d'], x['n']))
payload = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
TODAY = datetime.date.today().strftime('%Y-%m-%d')

HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>小学大事件日期共享 · 非公开页</title>
<style>
:root{--ink:#1c2733;--dim:#5b6b7b;--line:#e3e9ef;--bg:#f4f6f9;--card:#fff;--accent:#2f6fd1;--xhs:#ff2442}
*{box-sizing:border-box;margin:0;padding:0}
body{font:15px/1.65 -apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;background:var(--bg);color:var(--ink)}
.wrap{max-width:1080px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:21px;margin:8px 0 4px}
.sub{color:var(--dim);font-size:13px;margin-bottom:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:16px}
.card h2{font-size:16px;margin-bottom:8px}
.card p{font-size:13.5px;color:var(--dim);margin:4px 0}
.note{background:#fff8e6;border:1px solid #f0dfa8}
.search{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px;margin:6px 0 10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top;white-space:nowrap}
th{color:var(--dim);font-weight:600;background:#f8fafc;position:sticky;top:0}
td.n{font-weight:600;white-space:normal;min-width:180px}
td.dim{color:#b3bfc9}
.count{color:var(--dim);font-size:12px;margin:4px 0 8px}
.xhsb{display:inline-block;background:var(--xhs);color:#fff;font-size:12px;padding:5px 13px;border-radius:999px;text-decoration:none;font-weight:600}
.xhsb:hover{opacity:.9}
footer{border-top:1px solid var(--line);margin-top:10px;padding:14px 4px 0;color:var(--dim);font-size:12px}
footer .row{margin:8px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
@media(max-width:720px){th,td{padding:6px 5px}.hideM{display:none}}
</style>
</head>
<body>
<div class="wrap">
  <h1>小学大事件日期共享</h1>
  <p class="sub">开放日 · 开始报名 · 截止报名 · 面试日 · 结果公布 —— 由家长共建共享的非公开页（请勿外传链接）</p>

  <div class="card note">
    <p><b>为什么这页不公开、不进搜寻引擎？</b>有些日期若被全面公开，只会推高个别学校的报名竞争，对谁都没好处。所以：能公开的放在下面共建表格，其余由家长共享、核实后上架。</p>
  </div>

  <div class="card">
    <h2>① 共建表格（官方已核实 ＋ 家长共享）</h2>
    <p>「开始报名」来自各校官网逐校抓取（插班收表，月份级）＋ 教育局《学校位置及资料》名册（2026-09-30）；其余四栏<b>待家长共享</b>，核实后填入。收表时间学校随时会调整，<b>报名前一律以学校官网当日公布为准</b>。</p>
    <input class="search" id="q" type="search" placeholder="搜寻校名／地区，例如：上水、元朗、圣公会">
    <div class="count" id="cnt"></div>
    <div style="max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:8px">
    <table>
      <thead><tr><th>校名</th><th class="hideM">类别</th><th>地区</th><th class="hideM">校网</th><th>开放日</th><th>开始报名</th><th class="hideM">截止报名</th><th class="hideM">面试日</th><th class="hideM">结果公布</th></tr></thead>
      <tbody id="tb"></tbody>
    </table>
    </div>
  </div>

  <div class="card">
    <h2>② 日期共享（家长共建）</h2>
    <p>开放日、开始报名、截止报名、面试日、结果公布——<b>求各家长共享</b>。请到小红书私信留言<b>学校与日期</b>，我们核对后会加到本共建表格内。</p>
    <p style="margin-top:8px"><a class="xhsb" href="https://www.xiaohongshu.com/search_result?keyword=183236193" target="_blank" rel="noopener">去小红书聊聊</a></p>
  </div>

  <footer>
    <div class="row">
      <a class="xhsb" href="https://www.xiaohongshu.com/search_result?keyword=183236193" target="_blank" rel="noopener">去小红书聊聊</a>
      <span id="busuanzi_container_page_pv" style="display:none">本页访问 <span id="busuanzi_page_pv">–</span> 次</span><span id="busuanzi_container_site_uv" style="display:none">&nbsp;· 访客 <span id="busuanzi_site_uv">–</span> 人</span>
    </div>
    <div>免责声明：本页内容仅供个人参考，不构成任何择校建议；一切以教育局与学校官方公布为准，择校决定与后果由家长自行承担。</div>
    <div>工具免费、无广告、免注册、不收集任何个人资料。最后更新：__TODAY__。</div>
  </footer>
</div>
<script>
var ROWS = __PAYLOAD__;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
var tb=document.getElementById('tb'),cnt=document.getElementById('cnt'),q=document.getElementById('q');
function cell(v){return v?esc(v):'<span class="dim">–</span>';}
function render(){
  var kw=(q.value||'').trim().toLowerCase(), out=[], n=0;
  for(var i=0;i<ROWS.length;i++){
    var r=ROWS[i];
    if(kw&&(r.n+' '+r.e+' '+r.d+' '+r.k).toLowerCase().indexOf(kw)<0)continue;
    n++;
    out.push('<tr><td class="n">'+esc(r.n)+'</td><td class="hideM">'+esc(r.t)+'</td><td>'+esc(r.d)+'</td><td class="hideM">'+esc(r.k)+'</td><td class="dim">–</td><td>'+esc(r.iv)+'</td><td class="hideM dim">–</td><td class="hideM dim">–</td><td class="hideM dim">–</td></tr>');
  }
  tb.innerHTML=out.join('')||'<tr><td colspan="9" style="color:#5b6b7b">没有符合的学校</td></tr>';
  cnt.textContent='共 '+n+' 所有收表资料；空白栏（–）待家长共享';
}
q.addEventListener('input',render);render();
</script>
<script async src="https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
</body>
</html>
"""

HTML = HTML.replace('__PAYLOAD__', payload).replace('__TODAY__', TODAY)
out = os.path.join(ROOT, 'share01.html')
open(out, 'w', encoding='utf-8').write(HTML)
print('written', out, len(HTML), 'bytes;', len(rows), 'rows')
