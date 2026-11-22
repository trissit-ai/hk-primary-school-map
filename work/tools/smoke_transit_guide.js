#!/usr/bin/env node
/* 工具 06 两处「口岸／学校」可搜可滚选下拉的冒烟测试。
 * 用法：NODE_PATH=<global node_modules> node work/tools/smoke_transit_guide.js
 */
const path = require('path');
const fs = require('fs');

let puppeteer;
try { puppeteer = require('puppeteer'); }
catch (e) { puppeteer = require(process.env.PUPPETEER_MODULE); }

const FILE = 'file://' + path.resolve(__dirname, '..', '..', 'transit-guide.html');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const LONG_NAME = 'INTERNATIONAL COLLEGE HONG KONG HONG LOK YUEN (PRIMARY SECTION)';

const errors = [];
const fails = [];
let cases = 0;

function check(ok, label, detail) {
  cases++;
  if (!ok) fails.push({ label, detail });
}

async function type(page, sel, value) {
  await page.$eval(sel, (el, v) => {
    el.value = v;
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
}

async function pick(page, listSel) {
  await page.$eval(listSel + ' .co', el => el.click());
}

(async () => {
  const launch = { headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] };
  if (fs.existsSync(CHROME)) launch.executablePath = CHROME;
  const browser = await puppeteer.launch(launch);
  const page = await browser.newPage();
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(FILE, { waitUntil: 'load' });

  const init = await page.evaluate(() => ({
    ports: window.TG_PORTS.length,
    schools: window.TG_SCHOOLS.length,
    wrapFrom: !!document.getElementById('wrapFrom'),
    wrapTo: !!document.getElementById('wrapTo'),
    maxlength: document.getElementById('inpFrom').getAttribute('maxlength')
  }));
  console.log('初始化:', JSON.stringify(init));
  check(init.ports === 6, '数据·口岸', init.ports);
  check(init.schools === 694, '数据·学校', init.schools);
  check(init.wrapFrom && init.wrapTo, '两处下拉容器', init);
  check(init.maxlength === null, '已移除 maxlength=24（长校名不能被截断）', init.maxlength);

  // 起点：focus 展开全部候选，可往下滚动
  await page.focus('#inpFrom');
  let r = await page.evaluate(() => {
    const b = document.getElementById('listFrom');
    return {
      open: b.classList.contains('open'),
      n: b.querySelectorAll('.co').length,
      portGroup: b.textContent.includes('跨境口岸（6）'),
      schoolGroup: b.textContent.includes('全港学校（694）'),
      hasPort: b.textContent.includes('罗湖'),
      hasSchool: b.textContent.includes('圣公会荣真小学'),
      scrollable: b.scrollHeight > b.clientHeight
    };
  });
  check(r.open && r.n === 700, '展开全部 700 项', r);
  check(r.portGroup && r.schoolGroup, '口岸／学校分组标题', r);
  check(r.hasPort && r.hasSchool, '既有口岸也有学校', r);
  check(r.scrollable, '清单可往下滚动', r);

  // 打字搜：口岸别名
  await type(page, '#inpFrom', '福田');
  r = await page.evaluate(() => {
    const b = document.getElementById('listFrom');
    return { n: b.querySelectorAll('.co').length, text: b.textContent, open: b.classList.contains('open') };
  });
  check(r.open && r.n > 0 && r.text.includes('落马洲支线／福田口岸'), '搜「福田」命中福田口岸', r);
  check(!r.text.includes('罗湖'), '搜「福田」不混入罗湖', r.n);

  // 打字搜：学校名 + 多关键词
  await type(page, '#inpFrom', '荣真');
  r = await page.evaluate(() => document.getElementById('listFrom').textContent);
  check(r.includes('圣公会荣真小学'), '搜「荣真」命中学校', r.slice(0, 120));
  await type(page, '#inpFrom', '北区 圣公会');
  r = await page.evaluate(() => ({
    n: document.getElementById('listFrom').querySelectorAll('.co').length,
    txt: document.getElementById('listFrom').textContent
  }));
  check(r.n > 0 && r.txt.includes('北区'), '多关键词「北区 圣公会」过滤', r.n);
  await type(page, '#inpFrom', 'zzzz不存在的地名');
  r = await page.evaluate(() => document.getElementById('listFrom').textContent);
  check(r.includes('没有匹配'), '无结果有提示', r.slice(0, 120));

  // 选中 → 联动原有 state / 预览
  await type(page, '#inpFrom', '福田');
  await pick(page, '#listFrom');
  r = await page.evaluate(() => ({
    v: document.getElementById('inpFrom').value,
    preview: document.getElementById('routePreview').textContent,
    open: document.getElementById('listFrom').classList.contains('open')
  }));
  check(r.v === '落马洲支线／福田口岸', '点击候选项填入 input', r);
  check(r.preview.includes('落马洲支线／福田口岸'), '选中后联动路线预览', r);
  check(!r.open, '选中后下拉关闭', r);

  // 目的地：键盘上下 + Enter
  await page.focus('#inpTo');
  await type(page, '#inpTo', '文锦渡');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  r = await page.evaluate(() => ({
    v: document.getElementById('inpTo').value,
    preview: document.getElementById('routePreview').textContent
  }));
  check(r.v === '文锦渡', '键盘 ArrowDown+Enter 选中', r);
  check(r.preview.includes('文锦渡'), '目的地联动预览', r);

  // 长英文校名不能被截断
  await page.focus('#inpTo');
  await type(page, '#inpTo', 'INTERNATIONAL COLLEGE');
  await pick(page, '#listTo');
  r = await page.evaluate(() => document.getElementById('inpTo').value);
  check(r === LONG_NAME && r.length > 24, '长校名完整填入', r);

  // 箭头按钮展开 / 收起、Esc 关闭
  await page.click('#tgFrom');
  r = await page.evaluate(() => document.getElementById('listFrom').classList.contains('open'));
  check(r, '右侧箭头展开清单', r);
  await page.click('#tgFrom');
  r = await page.evaluate(() => document.getElementById('listFrom').classList.contains('open'));
  check(!r, '再点箭头收起', r);
  await page.focus('#inpFrom');
  await page.keyboard.press('Escape');
  r = await page.evaluate(() => document.getElementById('listFrom').classList.contains('open'));
  check(!r, 'Esc 关闭', r);

  // 原有按钮与三步流程回归
  await page.click('#btnDemo');
  r = await page.evaluate(() => [document.getElementById('inpFrom').value, document.getElementById('inpTo').value]);
  check(r[0] === '口岸（示意）' && r[1] === '学校（示意）', '填入示意值仍可用', r);
  await page.click('#btnEmpty');
  r = await page.evaluate(() => [document.getElementById('inpFrom').value, document.getElementById('inpTo').value]);
  check(r[0] === '' && r[1] === '', '清空仍可用', r);
  await page.click('#btnNext');
  r = await page.evaluate(() => document.getElementById('step2').classList.contains('active'));
  check(r, '第 1 步下一步仍可用', r);

  // 390px 移动端：下拉展开时无横向溢出
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
  await page.goto(FILE, { waitUntil: 'load' });
  await page.focus('#inpFrom');
  const mob = await page.evaluate(() => {
    const b = document.getElementById('listFrom');
    return {
      sw: document.documentElement.scrollWidth,
      iw: window.innerWidth,
      open: b.classList.contains('open'),
      n: b.querySelectorAll('.co').length,
      listW: Math.round(b.getBoundingClientRect().width)
    };
  });
  console.log('390px 移动端:', JSON.stringify(mob));
  check(mob.sw <= mob.iw + 2, '移动端无横向溢出', mob);
  check(mob.open && mob.n === 700, '移动端下拉可用', mob);

  await browser.close();
  console.log('\n断言数:', cases, '| JS 错误:', errors.length, '| 失败:', fails.length);
  if (errors.length) console.log('JS 错误:\n' + errors.slice(0, 10).join('\n'));
  if (fails.length) {
    fails.slice(0, 12).forEach(f => console.log('FAIL', JSON.stringify(f)));
    process.exit(1);
  }
  console.log('SMOKE_OK');
})().catch(e => { console.error('SMOKE_CRASH', e); process.exit(2); });
