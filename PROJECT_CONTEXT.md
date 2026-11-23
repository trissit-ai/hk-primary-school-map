# 香港择校工具超市 · 项目上下文（截至 2026-10-16）

> 用途：给助手和下次会话留底，避免丢上下文。项目本身是一个**免费、不商业化、不评价学校**的跨境（北上）学童择校工具超市，核心目的是把家长引流到爱欣的小红书（小红书号 **183236193**）沉淀关系。

---

## 一、项目定位与部署
- **目标**：给跨境学童家庭做择校工具；免费、不商业化、不评价学校好坏；最终把家长导到爱欣的小红书做社群沉淀。
- **引流路径（已定 B 纯社群）**：不在页面加收款码/打赏；footer 红色「去小红书聊聊」按钮 + 具体诱因文案「想拿面试日全集、开放日情报？私信领取」→ 小红书（爱欣 183236193）。
- **仓库 / 部署**：`github.com/trissit-ai/hk-primary-school-map`（GitHub Pages）
- **本地路径**：`~/WorkBuddy/2026-10-13-23-44-01/hk-school-map`
- **反馈邮箱**：`aixinxin@agent.qq.com`

## 二、页面清单（当前线上）
| 页面 | 内容 |
|---|---|
| `index.html` | 超市主页 |
| `tool01.html` | 地图（学校气泡，含九巴就近巴士站） |
| `tool02/03/04.html` | 校区筛选 / 口岸通勤 / 自订权重·全港 |
| `personal01.html` | 自订权重·北区大埔沙田 |
| `share01.html` | 小学大事件日期共享（隐藏页，家长共建；敏感情报只走小红书私信） |

- **每页 footer 统一**：红色「去小红书聊聊」按钮 + 免责声明行 + 不蒜子访问统计（page_pv + site_uv）。
- **硬规则**：每个工具的「去小红书聊聊」按钮要**各自独立的对应小红书地址**（不是共用搜索链接）。目前只有 tool01 给了（爱欣笔记直链，带 xsec_token，有时效）；其余页暂用搜索 `183236193`，待 Tris 逐页补。

## 三、这几天定下的关键决策（时间线）
1. 全站 footer 统一：小红书号改为红色按钮跳转（不再显示明文号码）；每页必带免责声明 + 访问统计。
2. **取消打赏/收款码**，改走 B 纯社群：footer CTA 文案改为「想拿面试日全集、开放日情报？私信领取」。
3. `index` 文案「查得到出处」→「查得到『公开』出处」。
4. 隐藏页 `dates.html` → 改名 `share01.html`（小学大事件日期共享），加 5 维栏（开放日 / 开始报名 / 截止报名 / 面试日 / 结果公布），投稿卡片合一。
5. `tool01` 去掉隐藏 feedback 面板改标准 footer；删掉与 Home 重复的红色按钮；去小红书链接改为爱欣笔记直链。
6. `tool01` 学校气泡加**九巴（KMB）就近巴士站**：站名 + 距离 + 路线号。KMB 用官方 API 免 key 抓取；城巴/小巴因官方 API 需 key 暂未做，UI 注明未接入。
7. （待办）data.json 含 c27 面试栏 249 条，与「敏感情报只私信」策略冲突，待拍板是否剔除。

## 四、已完成 / 上线状态
- `tool01` 九巴数据 commit **7bc2a5d** 已上线，线上验证通过（三处标记命中）。
- 全站 footer / 免责 / 统计 / CTA 已上线。
- `share01` 已上线。

## 五、待办与风险（未决）
- **PAT 未撤销**（安全红线，见第七节）。
- 其余工具（index/tool02/03/04/personal01）的小红书地址逐页待给。
- data.json c27 面试栏 249 条与私信策略冲突，待拍板剔除。
- 城巴/小巴覆盖待补（需 API key 或替代源）。
- tool01 爱欣笔记直链 xsec_token 有时效，失效需换新链接。

## 六、技术备忘（下次别重踩）
- **网络 / 推送**：`github.com:443` 直连时通时断。推送用直连 retry 循环：
  `git -c http.version=HTTP/1.1 -c http.proxy= -c https.proxy= -c http.timeout=22 push origin main`（6–8 次，sleep 3）。环境变量代理 51913 对 git 会 502。
- **KMB API**：`data.etabus.gov.hk/v1` 免 key。`route-stop` 是**路径式** `route-stop/{route}/{direction}/{service_type}`，direction = `outbound`/`inbound`（不是 O/I）；`stop/` 一次给全站 6774 站坐标+名。Citybus / GMB 需 API key（403/404），红色小巴无官方 API。
- **重生成脚本**：`work/tools/crawl_kmb.py`（crawl 抓路线→建 stop→routes；build 学校就近 600m 配對，站名去重合併路線）+ `work/tools/inject_kmb.py`（冪等注入 tool01）。流程：跑 `python3 crawl_kmb.py all && python3 inject_kmb.py` → commit → push。
- `tool01.html` 是**手维护文件**（无 build 脚本/模板），直接改 + commit 即可；其余 tool 有 tpl + build 脚本。
- BSD `grep` 对中文多字节不可靠，一律用 `rg`（ripgrep）。

## 七、安全红线：GitHub PAT
- **是什么**：一条有 repo 写权限的 GitHub Personal Access Token，曾被用于推送，现存在本机 memory 与 WorkBuddy 本地 trace 日志（明文），以及 macOS keychain（git 凭据）。
- **暴露面核查（本次）**：不在公开仓库工作树，也不在 git 历史（pickaxe 查无）；remote URL 不含 token；`~/.git-credentials` 不存在。即**没有外泄到 GitHub 公开历史**。
- **为什么还要撤（目的）**：
  1. 它是一条**活的有写权限的 token**，明文躺在本地日志里；这些日志可能被备份/同步（如 iCloud、WorkBuddy 云端），一旦外泄别人可借此 push 你的仓库或在 GitHub 上以你身份操作。
  2. 轮转长期明文 token 是基本安全卫生——一条在日志里躺了好几天的 token 就该杀。
- **怎么整（步骤）**：
  1. 打开 `https://github.com/settings/tokens`（头像 → Settings → Developer settings → Personal access tokens）。
  2. 找到以 `ghp_okRNE…` 开头的那条 → 点开 → **Revoke / Delete** → 确认。
  3. 撤后**下一次 `git push` 会 401**，需重认证，二选一：
     - **推荐切 SSH（一劳永逸）**：`git remote set-url origin git@github.com:trissit-ai/hk-primary-school-map.git`，并把你的 SSH 公钥加进 GitHub（Settings → SSH and GPG keys）。之后不再依赖 token。
     - 或新建一个**只给 `repo` 范围**的新 PAT，push 时用户名填 GitHub 用户名、密码填新 token，keychain 会自动更新。
- **注意**：撤之前先确认你另有一种认证手段（已有 SSH key，或能登录 GitHub 建新 token），否则会卡住推送。
- 已动作：助手已把该 token 从我本机 memory 文件里涂掉，避免后续会话再带出。

---

## 八、语言规范：全站统一简体中文（Tris 2026-11-14 拍板「都统一用简中」）

**结论**：此前 `index.html` 等页面虽写 `lang="zh-Hans"`，正文却大量是繁体；工具 06 是唯一全简中页，首页还专门标注「簡中頁面」。Tris 17:2x 明确要求全部统一简中，已执行。

| 项 | 处理 |
| --- | --- |
| 线上页面 | 根目录 12 个 `.html` 全部繁→简，`<html lang="zh-CN">` 统一 |
| 模板源 | `work/tools/*.tpl.html` 5 个同步转简中，避免 rebuild 回退 |
| 打包页 | `work/minitool-dist/index.html` + `main.js` 同步转简中 |
| 构建脚本 | `build_*.py` 5 个 + `inject_kmb.py` 的界面文案转简中；**数据字段键用占位符保护**，仍可读取原 JSON。`build_personal01.py` 的「简→繁」两张映射改为恒等，不再把校名转回繁体 |
| 公开说明 | `README.md` 转简中 |
| 首页标注 | `index.html` 的「簡中頁面 · 示意數據」改为「示意数据」；第 6 条 note 的「工具 06 是简中页面」整句删除 —— 全站都简中后该标注无意义 |

**刻意保留繁体（不是漏改）**：`data.json`、`work/tools/*_data.json`、`psp2026_all.json`、`tt_tc.csv`、`tt_mapping.txt` 保留教育局等**官方源数据的原字形与字段键**；`crawl_*.py` 里对接官方繁体网页的匹配字串（如 `學校資料`、`FIELDS` 里的繁体字段名）也不动，否则爬虫会匹配失效。这些都不属于用户可见文案。页面显示用的是内嵌副本，已全部简中。

**未来 rebuild 的已知边界**：模板与脚本已是简中，但数据值仍是官方繁体；重新 build 生成的页面，数据区会带回繁体值。若要求连生成页也 100% 简中，需把数据 JSON 的**值**按 t2s 转一遍（键保留），或由 Tris 明确授权连源数据一起转。本轮未动源数据。

**备份**：转简前 20 个页面/脚本副本在 `/tmp/hk-map-backup-20261114/`，可逐文件比对回滚。

**验证**：无头 Chrome 逐页打开 13 个页面 —— `lang` 全 `zh-CN`、繁体专用字残留 0、JS 错误 0；关键锚点（小红书号 183236193、不蒜子 4 个 id、bsz.js、Home 链接、script/div 标签数）转换前后逐一比对无差异；工具 06 三步主流程（填示意值→认车→模拟→作答）回归通过；390px 移动端横向溢出 0。

**注意今晚笔记10**：工具 04 页面已改简中，而今晚 19:59 笔记10 的讲解视频画面截的是改前的繁中界面。视频本身不含错误数据、可照常发布；若要画面与线上完全一致，需重录该片。

---

## 九、工具 09「课文唱唱」上线（2026-11-23）

- **位置**：`tool09/index.html`（工具首页）+ `tool09/01_日月潭/index.html`（第一课，子目录）+ `tool09/01_日月潭/assets/photos/01–09.jpg` 与 `CREDITS.json`；`index.html` 首页「已经上线」区新增工具 09 卡片，并在 note 增加第 7 条说明。
- **编号说明**：Tris 明确指定「工具 09」。线上工具 07「校网查询」、08「插班时间线」仍是「待上线」占位，因此编号是跳的；若日后要连号，需 Tris 单独拍板重排。
- **视觉**：按 Zestwell / Citrus Season 的**视觉语言**转译（暖奶油 #FFF9EC、黄油、腮红、梅墨 #3A3550；Newsreader / Oswald / DM Mono；mask 逐行升起入场、focus glide、GALLERY / LIST 切换、右侧抽屉、九宫格 LIST、reduced motion、390px 响应式），**没有**照搬画店的商品详情 / 购物袋 / WebGL 3D 环形走廊。3×3 九宫格母题用九张真实日月潭照片对应。
- **没有生成新 AI 素材**：沿用已署名的 Wikimedia Commons 实拍照片（课堂识读更真实、也不新增授权风险）；提交时 ComfyUI 8188 队列 `running=1 pending=5`，按「队列太多就走可灵」的规则本可改走可灵，但本轮判断不需要新素材，故未排队、未消耗额度。
- **音频**：`日月潭_听妈妈的话_s20261223.flac`（110.920 秒）→ AAC 128k → Base64 内嵌为内存 Blob URL，单文件约 2.49 MB，seek 不依赖服务端 Range。
- **字幕时间轴**：本机离线 faster-whisper small + medium 词级识别 + 课文正文字符序列对齐，medium 匹配率 0.718 / small 0.531；VAD 复核 0–13.62 秒与 78 秒之后无人声。**该曲只唱课文正文 5 行**（13.62–80.34 秒），没有课号「9 日月潭①」、页下注释和页码「45」；其后约 30.6 秒纯器乐尾奏。
- **授权**：照片逐张署名、BY-SA 提示、YuE2 CC BY-NC 4.0 非商用声明、课文版权提示均写在页面抽屉与工具首页；全站 footer 规范（小红书 CTA / 免责 / 不蒜子）已保留。
- **验证**：本地 HTTP 下 `duration=110.92 / readyState=4`；seek 0 / 20 / 45 / 60 / 90 秒的字幕、照片、章节高亮、时钟、尾奏提示全部同步；5 段跳转、9 张 LIST 卡片、9 条署名抽屉均通过；1440px 与真实 390px 视口截图无重叠与横向溢出。
- **行内锚点修正（2026-11-23 下午，commit `b43625d`）**：Tris 指出第 4 行「要是下起…上轻纱」字幕慢。根因不是行边界错，而是 KTV 把 71 字符均分 21.60 秒：线性预测「要是下起」61.80s，本机 Whisper 实测 medium 58.20s / small 57.92s，慢 3.6–3.9s。修法是在第 4 行加 `anchors`（i=字符索引、d=相对行起点秒数，随 SPEED 缩放、随校准平移）：33→58.10s、42→60.35s、52→64.50s（轻纱扫完）、64.50–67.24s 保留拖腔停顿、53→67.24s、62→70.30s。其他 4 行仍走均分逻辑、段落导航不变。数值回归：58.5s 由 22 字提升到 34 字，64.5s 扫完 52 字，其他行逐点一致；滑块 0.90/1.10 与校准整体后移 2s 均验证锚点跟随正确。源数据同步写在 `riyuetan_timeline_tingmama.json` 与 `make_ktv_tingmama.py`。

- **页头页尾规范补齐（2026-11-23 16:4x，commit `fc30d21`）**：Tris 指出工具09 两页页头缺 HOME 键。已按全站规范在 `tool09/index.html` 与 `tool09/01_日月潭/index.html` 页头最左加 34px 圆形 HOME（inline SVG 房子，因 Tris 禁 emoji，不用旧页的 🏠）+ 面包屑；页尾三要素（红色「去小红书聊聊」按钮 / 免责声明 / 不蒜子双 id + bsz.js）在入口页 footer 与课文页「说明」抽屉 `.foot` 内齐全。课文页不蒜子 span 移入抽屉内，避免被 `#app` flex 布局挤到播放条下方。1440px 与真实 390px 截图无重叠，线上 SHA256 与本地一致（入口 `921aacd0…`、课文 `81d02455…`）。全站既有页 `tool03.html` / `personal02.html` / `share01.html` 仍无 HOME 键，未动，待 Tris 决定是否统一补。
### 九.1 工具09 扩为课文目录 + 广东话硬规则（2026-11-23 晚）

- **Tris 新指令**：把工具09 做成课文目录；按香港三年级上册常见课文清单（参考）每一篇建一个子目录，「多少课文就多少子目录多少首歌」；**所有歌一律用广东话 / 粤语演唱**（本条 Tris 两次强调，已写进 SOP 与项目 MEMORY，列为硬规则）。
- **清单理解**：香港无全港统一教材，各校按《适用书目表》自选；这份是《现代小学语文》+《启思小学中国语文》高频选文参考，非官方精确清单。按书名号内明确列出的课文计 **20 篇**：现代文 12（我的家 / 想念你 / 我生病了 / 看时间 / 快乐的一天 / 做个好学生 / 买东西 / 我坐校车上学 / 美丽的彩虹 / 春天来了 / 可爱的动物 / 台风来了）、古诗 6（山行 / 赠刘景文 / 夜书所见 / 望天门山 / 饮湖上初晴后雨 / 望洞庭）、文言文 2（守株待兔 / 刻舟求剑）。连同已上线《日月潭》共 21 首。
- **应用文不计入**：留言条 / 书信 / 通知 / 启事属写作文体训练、无书名号、不是课文，默认不建子目录不配歌（列为 SOP 待拍板 D）。
- **已落地**：`tool09/index.html` 入口页改为完整目录（已上线 01 + 四组清单 + 应用文说明区 + 广东话说明）；新建 `02_…` 至 `21_…` 共 20 个子目录，各放统一占位页（`gen_lesson_placeholders.py` 生成，脚本在文旅2 目录），标明「待权威课文全文」并列出六步流程（含粤语约束）。占位页不是空壳：HOME 键 / 面包屑 / 页尾三要素齐全。
- **未启动生成（守住不替 Tris 拍板）**：用户只给课文名、没给全文；项目硬规则是歌词以权威原文为准一字不漏，错一字整首白做。且粤语演唱 YuE2 未实测，不能承诺纯正发音。按 SOP 待拍板 A/D/E，先等 Tris 定：①全文来源（默认 Tris 给权威源逐字核对 / 备选助手网搜标源交叉验证）②应用文是否算 ③逐课曲风三选一。确认后才进 ComfyUI。
- **自检**：目录页 21 链接 = 21 子目录、断链 0；每页 HOME / aria-label / 面包屑 / 免责 / 不蒜子双 id / bsz.js 齐全；占位符残留 0。

### 九.2 工具09 目录页改 dark cosmic 风格 + 三项拍板落地（2026-11-23 晚二）

**Tris 三项拍板**：①全文＝助手网搜标源 + 交叉验证，逐篇给 Tris 确认；②应用文（留言条/书信/通知/启事）不做，目录页连说明区都删掉；③曲风分组——古诗《青花瓷》、文言文《菊花台》、现代文「陈奕迅《英雄联盟》」（查证：陈奕迅无同名曲，实为《英雄联盟：双城之战》主题曲《孤勇者》，待 Tris 确认），全部叠加粤语演唱硬规则。

**视觉大改（目录页 `tool09/index.html` 重写）**：按 motionsites.ai「cosmic portfolio」prompt 把视觉语言转译成静态单页（GitHub Pages 无 React/Vite 构建链，不引 React）：
- 强制深色：--bg 0 0% 4% / surface 8% / text 96% / muted 53% / stroke 12%；accent 渐变 #89AACC→#4E85BF。
- 字体 Inter（正文）+ Instrument Serif（italic 大标题）。
- Loading screen：rAF 计数 000→100（2700ms）+ 旋转词 + 底部进度条，可点击跳过，reduced-motion 直接隐藏。
- Hero：hls.js 接 mux 演示流做背景视频（失败静默降级到渐变）、暗遮罩 + 底部渐隐、eyebrow「COLLECTION '26」、role 轮转「把 {课文/古诗/小故事/童年} 唱给你听」、两个 CTA、SCROLL 指示。
- 导航：浮动 pill（圆形 HOME 键 + Home/Work/About + Say hi），滚动加阴影；**保留 HOME 键 + 面包屑规范**。
- 目录：21 张卡片（日月潭真实图 thumbnail + 20 张程序生成缩略图），**按 Tris 要求去掉描述段落和三个 bullet**（红框内容），卡片只留缩略图 + 编号行（含曲风标签）+ 标题 + 打开按钮；hover 渐变描边 + halftone + View 标签。
- Selected Work / Featured lessons 标题、Stats（21 首 / 20 篇 / 3 组曲风）、marquee、联系区（翻转视频 + CTA）。
- 页尾三要素（红色小红书按钮 / 免责声明 / 不蒜子双 id + bsz.js）保留，深色下对比度可读。
- GSAP 入场 + scroll 渐显用 CDN 渐进增强，CDN 失败不影响内容。

**20 个占位页也转 dark**（`gen_lesson_placeholders.py` 模板重写重跑）：与目录页风格连贯，曲风写进页面（步骤 02 显示分组曲风），全文来源步骤改为网搜交叉验证逐篇确认。第一课 `01_日月潭` 是成品播放器、暖色沉浸式页，**未动**（改动风险高且用户只说目录页整体风格）。

**自检**：目录页 `node --check` 通过；DOM 渲染出 21 张卡片、编号 01–21 连续、链接 21、断链 0、应用文残留 0；1440px 与 520px 视口截图无重叠无横向溢出；21 页 HOME/面包屑/免责/不蒜子/bsz.js 齐全（第一课非深色是预期）；曲风分组断言通过。

**上线校验（commit `2636073`）**：本地 = GitHub raw = Pages 三方 SHA 一致（目录 `31b0a5d3…`、占位14 `e5c50fec…`）。本次 Pages 构建延迟较久：commit 09:36:48Z 后，Pages 的 `last-modified` 到 09:39:06Z 才刷新（约 2.5 分钟），期间多次拉取都是旧版（content-length 16560 / SHA 69f9a821…）。教训：以响应头 `last-modified` 是否晚于 commit 时间判断构建是否完成，比轮询特征串更快定位；不要误判推送失败。
