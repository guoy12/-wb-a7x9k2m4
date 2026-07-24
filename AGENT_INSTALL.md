# Agent 安装指令

收到用户明确的安装请求后，按以下步骤执行。不要跳过备份和验证。

## 前置检查

1. 确认操作系统（macOS 或 Windows），找到 WorkBuddy 的 `app.asar`：
   - macOS: `/Applications/WorkBuddy.app/Contents/Resources/app.asar`
   - Windows: 自动探测 `~/AppData/Local/Programs/WorkBuddy/resources/app.asar`，或用户用 `--source`/`--target` 手动指定
2. 读取 WorkBuddy 当前版本号和 `app.asar` SHA-256。
3. 阅读 `scripts/patch-theme.mjs`、`scripts/install-theme.mjs` 和 `scripts/restore-theme.mjs`，确认逻辑透明：脚本只写新文件、不覆盖原文件、包含备份和 SHA-256 校验。
4. 检查新版本资源中是否仍包含以下稳定选择器：
   - `conversation-list-logo-row`
   - `wb-home-composer__input-slot`
   - `topRightSlotStandalone`
5. 如果选择器缺失，停止安装并向用户报告兼容性风险。

## 安装步骤

6. 执行补丁构建：
   ```
   node scripts/patch-theme.mjs --skin skins/<主题id>/skin.css --asset skins/<主题id>/hero.png
   ```
   脚本会基于当前 app.asar 生成补丁副本 `.work/app.patched.asar`（只写新文件，不覆盖原文件）。

7. 执行安装：
   ```
   node scripts/install-theme.mjs --patched .work/app.patched.asar
   ```
   脚本会备份原版 app.asar 到 `~/.workbuddy/backups/workbuddy-skin/<时间戳>/`，然后原子替换为补丁版。WorkBuddy 正在运行时允许原子替换，但必须提醒用户安装后完全退出并重新打开。

## 安装后验证

8. 从目标 `app.asar` 验证：
   - `renderer/index.html` 包含 `skin.css`
   - `renderer/assets/skin.css` 存在
   - `renderer/assets/hero.png` 存在
9. 报告当前版本、安装后 SHA-256、原版备份完整路径和重启方式。

## 恢复方法

```
node scripts/restore-theme.mjs --backup ~/.workbuddy/backups/workbuddy-skin/<时间戳>/app.asar
```

版本升级后，必须基于新版本原包重新构建。不要把旧版本备份覆盖到新版本。

## 皮肤文件说明

- `skins/<主题id>/skin.css`：纯 CSS 变量覆盖 + 样式规则，不含可执行代码、不含远程资源引用（背景图 url("./hero.png") 是相对路径）
- `skins/<主题id>/hero.png`：静态图片文件，作为背景图注入
- 49 款主题均为明暗双模式（`:root` 浅色 + `body.dark` 深色），跟随系统/应用外观自动切换
