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
