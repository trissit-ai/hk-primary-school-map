#!/usr/bin/env node
/* 工具 04 冒烟测试：无头 Chrome 逐口岸 × 学校 × 时段试算，检查渲染与 JS 错误。
 * 用法：NODE_PATH=<global node_modules> node work/tools/smoke_tool04.js
 */
const path = require('path');
const fs = require('fs');

let puppeteer;
try { puppeteer = require('puppeteer'); }
catch (e) { puppeteer = require(process.env.PUPPETEER_MODULE); }

const FILE = 'file://' + path.resolve(__dirname, '..', '..', 'tool04.html');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const SCHOOLS = {
  sheungshui: '圣公会荣真小学',
  fanling: '圣公会嘉福荣真小学',
  shatin: '圣公会主风小学',
  tuenmun: '保良局梁周顺琴小学',
  chaiwan: '港大同学会小学',
  wuksisha: '树宏学校',
  mongkok: '优才(杨殷有娣)书院'
};

const errors = [];
const fails = [];
let cases = 0;

async function run(page, port, school, time, day, label) {
  await page.select('#fPort', port);
  await page.$eval('#fSchool', (el, v) => { el.value = v; }, school);
  await page.$eval('#fClear', (el, v) => { el.value = v; }, time);
  await page.select('#fDay', day);
  await page.click('#btnCalc');
  const r = await page.evaluate(() => {
    const out = document.getElementById('out');
    return {
      text: out.innerText,
      steps: out.querySelectorAll('.route li').length,
      rows: out.querySelectorAll('table.tbl tbody tr').length,
      tables: out.querySelectorAll('table.tbl').length,
      bds: out.querySelectorAll('.bd').length
    };
  });
  cases++;
  const bad = [];
  if (/NaN|undefined|Infinity/.test(r.text)) bad.push('出现 NaN/undefined/Infinity');
  if (r.text.includes('找不到这所学校')) bad.push('学校匹配失败');
  if (r.text.includes('暂未能排出线路')) bad.push('港铁排线失败');
  if (r.text.includes('请先选一个具体口岸')) bad.push('不限口岸仍是死路');
  if (port === 'any') {
    if (r.rows !== 6) bad.push('横向对比应 6 行，实际 ' + r.rows);
  } else {
    if (r.steps < 3) bad.push('逐段路线不足 3 段，实际 ' + r.steps);
    if (!r.text.includes('完关 → 到校合计')) bad.push('缺合计行');
    if (!r.text.includes('预计到校')) bad.push('缺到校时间');
    if (!r.tables) bad.push('缺峰值对照表');
  }
  if (bad.length) fails.push({ label, port, school, time, day, bad, text: r.text.slice(0, 260) });
  return r;
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
    ports: document.getElementById('fPort').options.length,
    days: document.getElementById('fDay').options.length,
    schools: document.getElementById('schList').options.length,
    sources: document.querySelectorAll('#srcList a').length,
    cta: !!document.querySelector('footer a.xhs')
  }));
  console.log('初始化:', JSON.stringify(init));
  if (init.ports !== 7) fails.push({ label: '初始化', bad: ['口岸下拉应 7 项'] });
  if (init.schools !== 694) fails.push({ label: '初始化', bad: ['学校联想应 694 项'] });
  if (!init.cta) fails.push({ label: '初始化', bad: ['页脚缺小红书 CTA'] });

  // 铁路口岸 × 学校 × 时段
  for (const port of ['lo', 'lok']) {
    for (const key of ['sheungshui', 'shatin', 'mongkok']) {
      await run(page, port, SCHOOLS[key], '07:00', 'wd', '平日早高峰');
      await run(page, port, SCHOOLS[key], '09:30', 'wd', '平峰基线');
    }
  }
  // 公路口岸
  for (const port of ['lt', 'sw', 'hg', 'mk']) {
    for (const key of ['sheungshui', 'tuenmun', 'chaiwan']) {
      await run(page, port, SCHOOLS[key], '07:00', 'wd', '公路口岸');
    }
  }
  // 文锦渡：73K 已标「不驶入管制站」，主方案必须是校巴而不是 73K
  await run(page, 'mk', SCHOOLS.sheungshui, '07:00', 'wd', '文锦渡主方案');
  const mkSteps = await page.evaluate(() =>
    Array.from(document.querySelectorAll('#out .route li .what')).map(e => e.textContent));
  if (!mkSteps.some(s => s.includes('跨境校巴'))) fails.push({ label: '文锦渡主方案', bad: ['主方案未选校巴直达'] });
  if (mkSteps.some(s => s.includes('73K'))) fails.push({ label: '文锦渡主方案', bad: ['仍把 73K 当主方案'] });

  // 日期类型 / 深夜 / 口岸关闭 / 不限口岸
  await run(page, 'hg', SCHOOLS.wuksisha, '07:00', 'we', '周末（B15 应出现）');
  await run(page, 'hg', SCHOOLS.shatin, '05:00', 'wd', '深夜（NB73）');
  await run(page, 'lok', SCHOOLS.sheungshui, '23:00', 'wd', '口岸已关闭告警');
  await run(page, 'any', SCHOOLS.shatin, '07:00', 'mon', '不限口岸横向对比');
  await run(page, 'any', SCHOOLS.tuenmun, '09:30', 'wd', '不限口岸平峰');

  // 深夜只留通宵线：抓一次结果文案
  const night = await page.evaluate(() => {
    document.getElementById('fPort').value = 'hg';
    document.getElementById('fSchool').value = '圣公会主风小学';
    document.getElementById('fClear').value = '05:00';
    document.getElementById('btnCalc').click();
    return document.getElementById('out').innerText;
  });
  if (!night.includes('NB73')) fails.push({ label: '深夜过滤', bad: ['深夜未显示通宵线 NB73'] });
  if (night.includes('B12') && night.includes('屿巴 B12')) fails.push({ label: '深夜过滤', bad: ['深夜仍显示日间 B12'] });

  // 390px 移动端横向溢出
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
  await page.goto(FILE, { waitUntil: 'load' });
  await page.select('#fPort', 'lt');
  await page.$eval('#fSchool', (el, v) => { el.value = v; }, SCHOOLS.shatin);
  await page.click('#btnCalc');
  const mob = await page.evaluate(() => ({
    sw: document.documentElement.scrollWidth,
    iw: window.innerWidth,
    steps: document.querySelectorAll('#out .route li').length
  }));
  console.log('390px 移动端:', JSON.stringify(mob));
  if (mob.sw > mob.iw + 2) fails.push({ label: '移动端', bad: ['横向溢出 scrollWidth=' + mob.sw + ' innerWidth=' + mob.iw] });
  if (mob.steps < 3) fails.push({ label: '移动端', bad: ['移动端结果未渲染'] });

  await browser.close();
  console.log('\n试算用例:', cases, '| JS 错误:', errors.length, '| 断言失败:', fails.length);
  if (errors.length) console.log('JS 错误:\n' + errors.slice(0, 10).join('\n'));
  if (fails.length) {
    fails.slice(0, 10).forEach(f => console.log('FAIL', JSON.stringify(f)));
    process.exit(1);
  }
  console.log('SMOKE_OK');
})().catch(e => { console.error('SMOKE_CRASH', e); process.exit(2); });
