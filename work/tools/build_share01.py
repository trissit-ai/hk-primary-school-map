#!/usr/bin/env python3
"""build_share01.py — 生成 share01.html（小學大事件日期共享 · 非公開頁）
表格五維：開放日 / 開始報名 / 截止報名 / 面試日 / 結果公佈
種子：data.json 的 iv 欄（各校官網逐校抓取的插班收表狀態）→ 開始報名（月份級）；
其餘四欄留空待家長共享，核實後填入。
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
<title>小學大事件日期共享 · 非公開頁</title>
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
  <h1>小學大事件日期共享</h1>
  <p class="sub">開放日 · 開始報名 · 截止報名 · 面試日 · 結果公佈 —— 由家長共建共享的非公開頁（請勿外傳链接）</p>

  <div class="card note">
    <p><b>為什麼這頁不公開、不進搜尋引擎？</b>有些日期若被全面公開，只會推高個別學校的報名競爭，對誰都沒好處。所以：能公開的放在下面共建表格，其餘由家長共享、核實後上架。</p>
  </div>

  <div class="card">
    <h2>① 共建表格（官方已核實 ＋ 家長共享）</h2>
    <p>「開始報名」來自各校官網逐校抓取（插班收表，月份級）＋ 教育局《學校位置及資料》名冊（2026-09-30）；其餘四欄<b>待家長共享</b>，核實後填入。收表時間學校隨時會調整，<b>報名前一律以學校官網當日公布為準</b>。</p>
    <input class="search" id="q" type="search" placeholder="搜尋校名／地區，例如：上水、元朗、聖公會">
    <div class="count" id="cnt"></div>
    <div style="max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:8px">
    <table>
      <thead><tr><th>校名</th><th class="hideM">類別</th><th>地區</th><th class="hideM">校網</th><th>開放日</th><th>開始報名</th><th class="hideM">截止報名</th><th class="hideM">面試日</th><th class="hideM">結果公佈</th></tr></thead>
      <tbody id="tb"></tbody>
    </table>
    </div>
  </div>

  <div class="card">
    <h2>② 日期共享（家長共建）</h2>
    <p>開放日、開始報名、截止報名、面試日、結果公佈——<b>求各家長共享</b>。請到小紅書私信留言<b>學校與日期</b>，我們核對後會加到本共建表格內。</p>
    <p style="margin-top:8px"><a class="xhsb" href="https://www.xiaohongshu.com/search_result?keyword=183236193" target="_blank" rel="noopener">去小紅書聊聊</a></p>
  </div>

  <footer>
    <div class="row">
      <a class="xhsb" href="https://www.xiaohongshu.com/search_result?keyword=183236193" target="_blank" rel="noopener">去小紅書聊聊</a>
      <span id="busuanzi_container_page_pv" style="display:none">本頁訪問 <span id="busuanzi_value_page_pv">–</span> 次</span><span id="busuanzi_container_site_uv" style="display:none">&nbsp;· 訪客 <span id="busuanzi_value_site_uv">–</span> 人</span>
    </div>
    <div>免責聲明：本頁內容僅供個人參考，不構成任何擇校建議；一切以教育局與學校官方公布為準，擇校決定與後果由家長自行承擔。</div>
    <div>工具免費、無廣告、免註冊、不收集任何個人資料。最後更新：__TODAY__。</div>
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
  tb.innerHTML=out.join('')||'<tr><td colspan="9" style="color:#5b6b7b">沒有符合的學校</td></tr>';
  cnt.textContent='共 '+n+' 所有收表資料；空白欄（–）待家長共享';
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
