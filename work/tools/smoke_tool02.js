// 烟测：直接加载生成的 tool02.html 脚本（剥离自动 init），注入 DOM stub，
// 调用真实的 reject()/defaults()，验证「一條龍」与地区/校网筛选逻辑。
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', '..', 'tool02.html'), 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('no <script> found'); process.exit(2); }
let script = m[1];
// 去掉启动 IIFE，避免触碰 DOM
script = script.replace(/\(function init\(\)\{[\s\S]*?\}\)\(\);/, '');

function fakeEl() {
  return new Proxy(function(){}, {
    get(t, p) {
      if (p === 'children') return [];
      if (p === 'querySelectorAll') return () => [];
      if (p === 'style') return {};
      if (p === 'getAttribute') return () => '';
      if (p === 'closest') return () => null;
      return fakeEl();
    },
    set() { return true; },
    apply() { return fakeEl(); }
  });
}
const sandbox = {
  document: { getElementById: () => fakeEl(), createElement: () => fakeEl(), body: { appendChild(){}, removeChild(){} } },
  window: { innerWidth: 1200 },
  localStorage: { getItem: () => null, setItem(){} },
  Blob: function(){}, URL: { createObjectURL: () => '', revokeObjectURL(){} },
  alert: () => {},
  console
};
vm.createContext(sandbox);
vm.runInContext(script, sandbox);

const { SCHOOLS, META, reject, defaults } = sandbox;

function permissive() {
  return { path:'p3', addr:'other', netOne:'', types:{官立:1,資助:1,直資:1,私立:1,國際:1,英基:1,特殊:1},
           port:'any', hops:0, walk:0, dists:{}, nets:{}, tt:{}, stn:'',
           oNow:false, oPub:false, oNoU:false, oTop:false, oNoSp:false, sort:'mix', top:0, chk:{} };
}
function count(f) { let n=0; for (const s of SCHOOLS) if (!reject(s, f)) n++; return n; }

const res = {};
res.allOpen = count(permissive());
const f1 = permissive(); f1.tt = {'一條龍':1}; res.onlyTT = count(f1);
const f2 = permissive(); f2.tt = {'非一條龍':1}; res.onlyNonTT = count(f2);
const f3 = permissive(); f3.tt = {'一條龍':1,'非一條龍':1}; res.bothTT = count(f3);
res.ttDataCount = SCHOOLS.filter(s => 'tt' in s).length;
res.defaultAsShipped = count(defaults());

// 地区筛选（用 META.dists 里真实的串，避免区/區字形差异）
const northKey = META.dists.find(x => x.indexOf('北') === 0);
const yuenKey = META.dists.find(x => x.indexOf('元朗') === 0);
const fp = permissive(); fp.dists = {}; fp.dists[northKey] = 1; res.distNorth = count(fp);
const fy = permissive(); fy.dists = {}; fy.dists[yuenKey] = 1; res.distYuen = count(fy);
const ft = permissive(); ft.dists = {}; ft.dists[northKey] = 1; ft.tt = {'一條龍':1}; res.northAndTT = count(ft);

// 校网 p1 + net 41
const f5 = permissive(); f5.path = 'p1'; f5.nets = {'41':1}; res.p1net41 = count(f5);

console.log(JSON.stringify(res, null, 2));
const ok = res.allOpen === 694 && res.onlyTT === 17 && res.onlyNonTT === 677 &&
           res.bothTT === 694 && res.ttDataCount === 17 && res.distNorth === 34 &&
           res.distYuen === 57 && res.northAndTT === 0 && res.p1net41 > 0;
console.log(ok ? 'ALL_PASS' : 'FAIL: ' + JSON.stringify(res));
process.exit(ok ? 0 : 1);
