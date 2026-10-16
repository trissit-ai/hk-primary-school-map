#!/usr/bin/env python3
"""build_dates.py — 生成隱藏頁 dates.html（家長共享情報站：面試日／開放日／報名日）
數據來源：data.json 的 iv 欄（各校官網逐校抓取的插班收表狀態，148 所有值）。
開放日／面試日由家長經小紅書私信投稿（本頁不預填、不編造）。
重跑：python3 build_dates.py（在 work/tools/ 目錄下執行）
"""
import json, os, re, datetime

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
<title>家長共享情報站 · 面試日／開放日／報名日（非公開頁）</title>
<style>
:root{--ink:#1c2733;--dim:#5b6b7b;--line:#e3e9ef;--bg:#f4f6f9;--card:#fff;--accent:#2f6fd1;--xhs:#ff2442}
*{box-sizing:border-box;margin:0;padding:0}
body{font:15px/1.65 -apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;background:var(--bg);color:var(--ink)}
.wrap{max-width:960px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:21px;margin:8px 0 4px}
.sub{color:var(--dim);font-size:13px;margin-bottom:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:16px}
.card h2{font-size:16px;margin-bottom:8px}
.card p{font-size:13.5px;color:var(--dim);margin:4px 0}
.note{background:#fff8e6;border:1px solid #f0dfa8}
.search{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px;margin:6px 0 10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
th{color:var(--dim);font-weight:600;background:#f8fafc;position:sticky;top:0}
td.n{font-weight:600}
.count{color:var(--dim);font-size:12px;margin:4px 0 8px}
.xhsb{display:inline-block;background:var(--xhs);color:#fff;font-size:12px;padding:5px 13px;border-radius:999px;text-decoration:none;font-weight:600}
.xhsb:hover{opacity:.9}
.steps{font-size:13.5px;color:var(--ink);padding-left:20px}
.steps li{margin:4px 0}
footer{border-top:1px solid var(--line);margin-top:10px;padding:14px 4px 0;color:var(--dim);font-size:12px}
footer .row{margin:8px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
@media(max-width:640px){th,td{padding:6px 5px}.hideM{display:none}}
</style>
</head>
<body>
<div class="wrap">
  <h1>家長共享情報站</h1>
  <p class="sub">面試日 · 開放日 · 報名日 —— 由家長共建共享的非公開頁（請勿外傳链接）</p>

  <div class="card note">
    <p><b>為什麼這頁不公開、不進搜尋引擎？</b>有些日期若被全面公開，只會推高個別學校的報名競爭，對誰都沒好處。所以：能公開的放在下面表格；<b>完整版與敏感情報，只在小紅書私信發給真正在辦升學的家長</b>（會簡單核實，請見諒）。</p>
  </div>

  <div class="card">
    <h2>① 報名／收表日（官方與已核實資料）</h2>
    <p>來源：各校官網逐校抓取（插班收表狀態）＋ 教育局《學校位置及資料》名冊（2026-09-30）。收表時間學校隨時會調整，<b>報名前一律以學校官網當日公布為準</b>。</p>
    <input class="search" id="q" type="search" placeholder="搜尋校名／地區，例如：上水、元朗、聖公會">
    <div class="count" id="cnt"></div>
    <div style="max-height:480px;overflow:auto;border:1px solid var(--line);border-radius:8px">
    <table>
      <thead><tr><th>校名</th><th class="hideM">類別</th><th>地區</th><th class="hideM">校網</th><th>收表／報名</th></tr></thead>
      <tbody id="tb"></tbody>
    </table>
    </div>
  </div>

  <div class="card">
    <h2>② 開放日（家長共享）</h2>
    <p>暫未有人投稿。開放日資訊由家長報料、我們核實後上架，這裡會持續更新。</p>
  </div>

  <div class="card">
    <h2>③ 面試日全集 ＋ 敏感情報（不公開展示）</h2>
    <p>面試日期、收表尾聲提醒等敏感情報<b>不在本頁展示</b>，統一走小紅書私信發放，避免推高競爭。</p>
    <p class="row"><a class="xhsb" href="https://www.xiaohongshu.com/search_result?keyword=183236193" target="_blank" rel="noopener">去小紅書私信領取</a></p>
  </div>

  <div class="card">
    <h2>如何投稿／報料</h2>
    <ol class="steps">
      <li>小紅書私信 <b>183236193（愛欣）</b>；</li>
      <li>附上：校名、日期／時間、資訊來源（官網截圖或通告照片最快捷）；</li>
      <li>我們核實後 48 小時內上架到本頁，來源會標註「家長報料」。</li>
    </ol>
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
function render(){
  var kw=(q.value||'').trim().toLowerCase(), out=[], n=0;
  for(var i=0;i<ROWS.length;i++){
    var r=ROWS[i];
    if(kw&&(r.n+' '+r.e+' '+r.d+' '+r.k).toLowerCase().indexOf(kw)<0)continue;
    n++;
    out.push('<tr><td class="n">'+esc(r.n)+'</td><td class="hideM">'+esc(r.t)+'</td><td>'+esc(r.d)+'</td><td class="hideM">'+esc(r.k)+'</td><td>'+esc(r.iv)+'</td></tr>');
  }
  tb.innerHTML=out.join('')||'<tr><td colspan="5" style="color:#5b6b7b">沒有符合的學校</td></tr>';
  cnt.textContent='共 '+n+' 所有收表資料';
}
q.addEventListener('input',render);render();
</script>
<script async src="https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
</body>
</html>
"""

HTML = HTML.replace('__PAYLOAD__', payload).replace('__TODAY__', TODAY)
out = os.path.join(ROOT, 'dates.html')
open(out, 'w', encoding='utf-8').write(HTML)
print('written', out, len(HTML), 'bytes;', len(rows), 'rows')
