# WorkBuddy 皮肤工坊 · 使用指南

49 款主题皮肤，每款含 **浅色 + 深色双模式 CSS** 和 **4K 高清壁纸**（1920×1080 ~ 7680×4320）。
通过覆盖 WorkBuddy 的 CSS 变量（`--vscode-*` / `--wb-*`）+ 关键界面选择器实现换肤，支持 macOS 和 Windows。

## 目录结构

```
workbuddy-skin-gallery/
├── index.html            # 皮肤选择器页面（浏览/预览/下载）
├── themes-data.js        # 49 款主题元数据（自动生成）
├── generate.py           # 主题生成器（改配色后重跑即可）
├── skins/
│   └── <主题id>/
│       ├── skin.css      # 完整主题样式（light + dark）
│       ├── hero.png      # 高清背景图（CSS 中用 url("./hero.png") 相对引用）
│       └── theme.json    # 主题元数据
```

> ⚠️ `skin.css` 与 `hero.png` 必须放在同一目录，CSS 用相对路径 `./hero.png` 引用背景图。

---

## 方式一：Agent 一句话安装（推荐，最省事）

把下面这句话发给 **WorkBuddy Agent**（把 `<主题id>` 换成你要装的主题，例如 `one-piece-strawhat`）：

> 请克隆 `https://github.com/guoy12/-wb-a7x9k2m4.git`，阅读仓库中的 **AGENT_INSTALL.md**（安装指令文档），然后按照文档中的步骤执行安装。皮肤文件 `skins/<主题id>/skin.css` 和 `hero.png` 是纯 CSS 样式覆盖和静态图片（可先阅读审查）。脚本 `scripts/patch-theme.mjs` 和 `scripts/install-theme.mjs` 包含完整的备份、SHA-256 校验和原子替换逻辑，支持 macOS 和 Windows。

Agent 会自动完成：**检查环境 → 备份 app.asar → 把 skin.css 与 hero.png 打进补丁副本 → 校验 → 原子替换**。
装完 `Command/Ctrl + Q` 完全退出 WorkBuddy 再重开即生效。

---

## 方式二：手动脚本安装

前提：已 clone 本仓库，Node.js ≥ 22，以及 `@electron/asar` 包（WorkBuddy 隔离 Node 工作区自带）。

```bash
# 1. 克隆仓库
git clone https://github.com/guoy12/-wb-a7x9k2m4.git
cd -wb-a7x9k2m4

# 2. 构建补丁（以海贼王为例，脚本自动探测 app.asar 路径）
node scripts/patch-theme.mjs --skin skins/one-piece-strawhat/skin.css --asset skins/one-piece-strawhat/hero.png

# 3. 安装（自动备份原版再原子替换）
node scripts/install-theme.mjs --patched .work/app.patched.asar
```

恢复（用安装时打印的备份路径）：

```bash
node scripts/restore-theme.mjs --backup ~/.workbuddy/backups/workbuddy-skin/<时间戳>/app.asar
```

> macOS 和 Windows 均支持，脚本自动探测 WorkBuddy 安装路径。如果探测失败，用 `--source`/`--target` 手动指定 app.asar 完整路径。

---

## 方式三：CDP 免改包注入（不修改官方文件，随时可逆）

思路来自社区项目 `workbuddy-skin-studio`：不碰 `app.asar`、不动代码签名，通过本机回环调试端口把 CSS 注入正在运行的界面。

**特点**：完全可逆、重启后失效需重新注入、最安全。适合先试用再决定是否常驻。

让 Agent 执行这句话即可：

> 用 CDP 注入方式给当前运行的 WorkBuddy 换肤：以 `--remote-debugging-port=9223` 重启 WorkBuddy（或附加到已有调试端口），通过 `Page.addStyleSheet` / `Runtime.evaluate` 注入 `skins/<主题id>/skin.css` 的内容，hero.png 用 base64 内联或本机 http 服务提供。不要修改任何安装目录文件。

手动版（macOS，懂开发者可用）：

```bash
# 1. 带调试端口启动 WorkBuddy
/Applications/WorkBuddy.app/Contents/MacOS/WorkBuddy --remote-debugging-port=9223 &

# 2. 用任意 CDP 客户端注入 CSS（示例为 python + websocket）
python inject_skin.py --port 9223 --css skins/one-piece-strawhat/skin.css
```

---

## 三种方式对比

| 方式 | 改动官方文件 | 重启后保留 | 可逆性 | 适合人群 |
|------|:---:|:---:|:---:|------|
| ① Agent 安装 | 是（有备份） | ✅ | 用备份恢复 | 大多数用户 |
| ② 手动脚本 | 是（有备份） | ✅ | restore-theme.mjs | 折腾党 |
| ③ CDP 注入 | 否 | ❌（需重注） | 即时恢复 | 想先试试效果 |

---

## 浏览与下载皮肤

```bash
cd data/workbuddy-skin-gallery
python -m http.server 8931
# 浏览器打开 http://127.0.0.1:8931/index.html
```

页面支持：分类筛选（动漫/游戏/科技/自然/复古/简约/创意）、关键词搜索、浅色/深色切换预览、下载 `skin.css`、单独下载背景图。

---

## 自己新增/修改皮肤

1. 打开 `data_part1.py`（动漫/游戏）、`data_part2.py`（科技/自然）或 `data_part3.py`（复古/简约/创意）；
2. 仿照现有条目追加一个主题字典（只需 9 个核心颜色 × 明暗两套）；
3. （可选）放一张背景图到 `skins/<主题id>/hero.png`；
4. 重跑生成器：

```bash
python generate.py     # 自动派生 hover/active 等 60+ 变量并输出完整 skin.css
```

生成器会自动计算：按钮 hover 色、选中底色、滚动条色、遮罩透明度、顶栏渐变压暗色等。

---

## 常见问题

**Q: 换肤后 WorkBuddy 更新会怎样？**
A: 官方更新会覆盖 app.asar，皮肤失效。不要用旧备份覆盖新版本，重新执行方式一即可（脚本会基于新版本原包重建补丁）。

**Q: 背景图太抢眼看不清字？**
A: skin.css 里背景图自带主题色半透明遮罩（浅色 72% / 深色 80% 不透明度）。仍不够可搜索 `rgba(` 调高遮罩值，或删掉 `url("./hero.png")` 只用纯色。

**Q: 想换背景图？**
A: 直接替换 `skins/<主题id>/hero.png`（保持文件名），重新执行安装即可。CSS 无需改动。

**Q: 深色模式没生效？**
A: 皮肤的深色规则挂在 `body.dark` 选择器下，跟随 WorkBuddy 外观设置自动切换。在 WorkBuddy 设置里把外观切到深色即可。
