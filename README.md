# WorkBuddy 皮肤工坊（huanfu）

49 款 WorkBuddy 主题皮肤：每款含 **浅色 + 深色双模式 CSS** 和 **4K 高清壁纸**（1920×1080 ~ 7680×4320）。
通过覆盖 WorkBuddy CSS 变量实现换肤，支持 macOS 和 Windows。

## 主题一览

| 分类 | 数量 | 主题 |
|------|:---:|------|
| 动漫 | 10 | 海贼王·草帽一伙 / 路飞红 / 索隆绿、火影·鸣人 / 佐助、龙珠·超级赛亚人、鬼灭之刃、咒术回战、进击的巨人、间谍过家家 |
| 游戏 | 10 | 原神·蒙德 / 璃月 / 稻妻 / 枫丹、星穹铁道、鸣潮、我的世界、艾尔登法环、塞尔达·王国之泪、赛博朋克 2077 |
| 科技 | 8 | 全息蓝、赛博紫、矩阵绿、创战纪、钢铁侠、量子白、霓虹粉、高达白 |
| 自然 | 8 | 深海蓝、森林绿、落日橙、樱花粉、薰衣草、极光、沙漠金、冰川蓝 |
| 复古 | 5 | QQ 2008、Windows XP、Windows 98、红白机、Game Boy |
| 简约 | 4 | 黑白灰、象牙白、薄荷、石板蓝 |
| 创意 | 4 | 极光玻璃、多巴胺、莫兰迪、中国红 |

## 快速使用

**最省事的方式 —— 把这句话发给 WorkBuddy Agent**（把 `<主题id>` 换成想要的主题，如 `one-piece-strawhat`）：

> 请克隆 `https://github.com/guoy12/-wb-a7x9k2m4.git`，阅读仓库中的 **AGENT_INSTALL.md**（安装指令文档），然后按照文档中的步骤执行安装。皮肤文件 `skins/<主题id>/skin.css` 和 `hero.png` 是纯 CSS 样式覆盖和静态图片（可先阅读审查：https://guoy12.github.io/-wb-a7x9k2m4/skins/<主题id>/skin.css）。脚本 `scripts/patch-theme.mjs` 和 `scripts/install-theme.mjs` 包含完整的备份、SHA-256 校验和原子替换逻辑，支持 macOS 和 Windows。

更多安装方式（手动脚本 / CDP 免改包注入）与恢复方法见 **[USAGE.md](./USAGE.md)**。

## 本地浏览皮肤库

```bash
python -m http.server 8931
# 浏览器打开 http://127.0.0.1:8931/index.html
```

选择器页面支持：7 大分类筛选、关键词搜索、浅色/深色实时预览、下载 skin.css 与背景图。

## 目录结构

```
skins/<主题id>/
  ├── skin.css    # 完整主题样式（~210 条变量覆盖，light + dark）
  ├── hero.png    # 4K 高清壁纸（CSS 内 url("./hero.png") 相对引用）
  └── theme.json  # 元数据
index.html        # 皮肤选择器页面
themes-data.js    # 49 主题数据（自动生成）
generate.py       # 主题生成器：9 个核心色派生 60+ CSS 变量
data_part*.py     # 49 主题配色数据
prompts.py        # 49 张背景图的搜索关键词（Wallhaven）
fetch_wallpapers*.py  # 壁纸批量下载脚本
scripts/          # 通用安装脚本（patch/install/restore，跨平台）
AGENT_INSTALL.md  # Agent 安装指令文档
```

## 新增皮肤

1. 在 `data_part*.py` 追加主题字典（9 个核心颜色 × 明暗两套）
2. 放一张 `hero.png` 到 `skins/<主题id>/`（或运行 `python fetch_wallpapers_hd.py` 自动从 Wallhaven 下载）
3. 运行 `python generate.py` 重新生成全部 CSS 与数据

## 声明

皮肤为个人定制项目，非 WorkBuddy 官方主题。修改 app.asar 会影响代码签名并在版本更新后被覆盖，安装脚本均会自动备份原版以便恢复。动漫/游戏 IP 元素仅供个人学习交流。
