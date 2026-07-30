# -*- coding: utf-8 -*-
"""WorkBuddy 皮肤生成器: 读取三部分主题数据, 批量生成 skin.css + theme.json + themes-data.js
用法: python generate.py
输出:
  skins/<id>/skin.css      完整主题样式(参考 qq2008-skin.css 结构)
  skins/<id>/theme.json    主题元数据
  themes-data.js           window.THEMES 供选择器页面使用
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_part1 import THEMES_PART1
from data_part2 import THEMES_PART2
from data_part3 import THEMES_PART3

BASE = os.path.dirname(os.path.abspath(__file__))
ALL = THEMES_PART1 + THEMES_PART2 + THEMES_PART3
CAT_NAMES = {"anime":"动漫","game":"游戏","tech":"科技","nature":"自然","retro":"复古","minimal":"简约","creative":"创意"}

# ---------- 颜色工具 ----------
def hx(c):
    c = c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def rgb(t):
    return '#%02x%02x%02x' % tuple(max(0,min(255,int(round(v)))) for v in t)
def mix(c1,c2,f):
    a,b = hx(c1),hx(c2); return rgb(tuple(a[i]+(b[i]-a[i])*f for i in range(3)))
def lighten(c,f=0.2): return mix(c,'#ffffff',f)
def darken(c,f=0.2): return mix(c,'#000000',f)
def luminance(c):
    r,g,b = hx(c); return 0.299*r+0.587*g+0.114*b
def rgba(c,a):
    r,g,b = hx(c); return f'rgba({r},{g},{b},{a})'

# ---------- HSL 工具 ----------
def hex2hsl(c):
    r,g,b = [int(c[i:i+2],16)/255 for i in (1,3,5)]
    mx,mn = max(r,g,b),min(r,g,b)
    l = (mx+mn)/2
    if mx==mn: return 0,0,l
    d = mx-mn
    s = d/(2-mx-mn) if l>0.5 else d/(mx+mn)
    if mx==r: h = ((g-b)/d + (6 if g<b else 0))/6
    elif mx==g: h = ((b-r)/d + 2)/6
    else: h = ((r-g)/d + 4)/6
    return h*360, s, l

def hsl2hex(h,s,l):
    h = h % 360
    c = (1-abs(2*l-1))*s
    x = c*(1-abs((h/60)%2-1))
    m = l - c/2
    if h<60: r,g,b = c,x,0
    elif h<120: r,g,b = x,c,0
    elif h<180: r,g,b = 0,c,x
    elif h<240: r,g,b = 0,x,c
    elif h<300: r,g,b = x,0,c
    else: r,g,b = c,0,x
    return '#%02x%02x%02x' % tuple(round((v+m)*255) for v in (r,g,b))

def fix_dark_bg(c):
    """深色背景校正: 提取色相, 降饱和到 0.18, 亮度统一到 0.095 — 避免'脏暗彩色'"""
    h,s,l = hex2hsl(c)
    return hsl2hex(h, 0.18, 0.095)

def fix_dark_sidebar(c):
    """深色侧栏校正: 比 bg 稍亮, 饱和度类似"""
    h,s,l = hex2hsl(c)
    return hsl2hex(h, 0.20, 0.135)

def fix_dark_topbar(c):
    """深色顶栏校正: 保留色相, 降饱和到 0.55, 亮度到 0.32 — 不太暗也不太艳"""
    h,s,l = hex2hsl(c)
    return hsl2hex(h, min(s, 0.55), 0.32)

def fix_dark_border(c):
    """深色边框校正: 亮度提升, 在深色背景上可见"""
    h,s,l = hex2hsl(c)
    return hsl2hex(h, min(s, 0.50), max(l, 0.30))

# ---------- 主题 emoji ----------
THEME_EMOJI = {
    "one-piece-strawhat":"⚓","one-piece-luffy":"🏴‍☠️","one-piece-zoro":"⚔️",
    "naruto-uzumaki":"🍥","naruto-sasuke":"⚡","dragon-ball":"🐉",
    "demon-slayer":"🌊","jujutsu-kaisen":"👁️","attack-on-titan":"🕊️","spy-family":"🥜",
    "genshin-mondstadt":"🍃","genshin-liyue":"🏮","genshin-inazuma":"⚡","genshin-fontaine":"🎭",
    "starrail":"🚂","wuthering-waves":"🌊","minecraft":"⛏️","elden-ring":"👑",
    "zelda-totk":"🗡️","cyberpunk2077":"🌃",
    "tech-hud-blue":"💠","tech-cyber-purple":"🔮","tech-matrix":"💊","tech-tron":"🏍️",
    "tech-ironman":"🤖","tech-quantum":"⚛️","tech-neon-pink":"🌆","tech-gundam":"🦾",
    "nature-ocean":"🐋","nature-forest":"🌲","nature-sunset":"🌅","nature-sakura":"🌸",
    "nature-lavender":"💜","nature-aurora":"🌌","nature-desert":"🏜️","nature-glacier":"🧊",
    "retro-qq2008":"🐧","retro-winxp":"🖥️","retro-win98":"💾","retro-fc-redwhite":"🎮","retro-gameboy":"👾",
    "minimal-mono":"⬛","minimal-ivory":"🕯️","minimal-mint":"🌿","minimal-slate":"🏢",
    "creative-aurora-glass":"🔮","creative-dopamine":"🎨","creative-morandi":"🏺","creative-chinese-red":"🏯","pink-crystal":"🌸",
}

def derive(p, dark=False):
    """从核心配色派生完整变量集"""
    d = {}
    d['accent'] = p['accent']
    d['accent_hover'] = darken(p['accent'],0.12) if not dark else lighten(p['accent'],0.12)
    d['secondary'] = p['secondary']
    d['bg'] = p['bg']
    d['sidebar'] = p['sidebar']
    d['topbar1'], d['topbar2'] = p['topbar1'], p['topbar2']
    d['text'] = p['text']; d['muted'] = p['muted']
    d['border'] = p['border']
    if not dark:
        d['card'] = '#ffffff'
        d['input'] = '#ffffff'
        d['hover'] = mix(p['sidebar'],'#ffffff',0.4)
        d['active'] = mix(p['accent'],'#ffffff',0.78)
        d['chip_bg'] = rgba(p['accent'],0.10)
        d['sel_bg'] = mix(p['accent'],'#ffffff',0.82)
        d['shadow'] = rgba(darken(p['accent'],0.3),0.14)
    else:
        # 深色模式: 先校正背景/侧栏/顶栏/边框 — 低饱和深灰, 避免"脏暗彩色"
        bg_fixed = fix_dark_bg(p['bg'])
        sidebar_fixed = fix_dark_sidebar(p['sidebar'])
        d['bg'] = bg_fixed
        d['sidebar'] = sidebar_fixed
        d['topbar1'] = fix_dark_topbar(p['topbar1'])
        d['topbar2'] = fix_dark_topbar(p['topbar2'])
        d['border'] = fix_dark_border(p['border'])
        d['card'] = lighten(bg_fixed,0.08)
        d['input'] = lighten(bg_fixed,0.05)
        d['hover'] = lighten(sidebar_fixed,0.10)
        d['active'] = mix(p['accent'],bg_fixed,0.45)
        d['chip_bg'] = rgba(p['accent'],0.18)
        d['sel_bg'] = mix(p['accent'],bg_fixed,0.50)
        d['shadow'] = 'rgba(0,0,0,0.5)'
    return d

# ---------- CSS 模板 ----------
CSS_TMPL = '''@charset "UTF-8";
/* WorkBuddy Skin: %(name)s (%(id)s) - %(mode)s
   由 workbuddy-skin-gallery 生成 */
%(rootsel)s {
  /* -- 基础色 -- */
  --vscode-foreground: %(text)s !important;
  --vscode-editor-foreground: %(text)s !important;
  --vscode-descriptionForeground: %(muted)s !important;
  --vscode-disabledForeground: %(muted)s !important;
  --vscode-editor-background: %(bg)s !important;
  --vscode-sideBar-background: %(sidebar)s !important;
  --vscode-panel-background: %(bg)s !important;
  /* -- 输入/下拉/菜单 -- */
  --vscode-input-background: %(input)s !important;
  --vscode-dropdown-background: %(input)s !important;
  --vscode-menu-background: %(card)s !important;
  --vscode-editorWidget-background: %(card)s !important;
  --vscode-textCodeBlock-background: %(hover)s !important;
  --vscode-input-border: %(border)s !important;
  --vscode-focusBorder: %(accent)s !important;
  /* -- 图标/链接 -- */
  --vscode-icon-foreground: %(muted)s !important;
  --vscode-textLink-foreground: %(accent)s !important;
  --vscode-textLink-activeForeground: %(accent_hover)s !important;
  /* -- 按钮 -- */
  --vscode-button-background: %(accent)s !important;
  --vscode-button-foreground: %(onaccent)s !important;
  --vscode-button-hoverBackground: %(accent_hover)s !important;
  --vscode-progressBar-background: %(accent)s !important;
  --vscode-badge-background: %(accent)s !important;
  --vscode-badge-foreground: %(onaccent)s !important;
  /* -- 列表 -- */
  --vscode-list-hoverBackground: %(hover)s !important;
  --vscode-list-activeSelectionBackground: %(active)s !important;
  --vscode-list-activeSelectionForeground: %(text)s !important;
  --vscode-list-inactiveSelectionBackground: %(hover)s !important;
  --vscode-list-focusBackground: %(active)s !important;
  /* -- 行号/缩进/括号 -- */
  --vscode-editorLineNumber-foreground: %(muted)s !important;
  --vscode-editorLineNumber-activeForeground: %(text)s !important;
  --vscode-editorIndentGuide-background1: %(border)s !important;
  --vscode-editorBracketHighlight-foreground1: %(accent)s !important;
  --vscode-editorBracketHighlight-foreground2: %(secondary)s !important;
  /* -- 滚动条 -- */
  --vscode-scrollbarSlider-background: %(border)s !important;
  --vscode-scrollbarSlider-hoverBackground: %(accent)s !important;
  --vscode-scrollbarSlider-activeBackground: %(accent_hover)s !important;
  /* -- Tab -- */
  --vscode-tab-activeBackground: %(card)s !important;
  --vscode-tab-inactiveBackground: %(bg)s !important;
  --vscode-tab-border: %(border)s !important;
  --vscode-tab-activeForeground: %(text)s !important;
  --vscode-tab-inactiveForeground: %(muted)s !important;
  /* -- Activity Bar / Status Bar / Title Bar -- */
  --vscode-activityBar-background: %(sidebar)s !important;
  --vscode-activityBar-foreground: %(accent)s !important;
  --vscode-activityBar-inactiveForeground: %(muted)s !important;
  --vscode-statusBar-background: %(topbar2)s !important;
  --vscode-statusBar-foreground: %(ontopbar)s !important;
  --vscode-titleBar-activeBackground: %(topbar1)s !important;
  --vscode-titleBar-activeForeground: %(ontopbar)s !important;
  /* -- 通知 -- */
  --vscode-notifications-background: %(card)s !important;
  --vscode-notifications-foreground: %(text)s !important;
  --vscode-notificationLink-foreground: %(accent)s !important;
  /* -- WorkBuddy 专有 -- */
  --wb-home-bg-primary: %(sidebar)s !important;
  --wb-home-bg-secondary: %(bg)s !important;
  --wb-bg-primary: %(card)s !important;
  --wb-bg-secondary: %(bg)s !important;
  --wb-bg-tertiary: %(hover)s !important;
  --wb-bg-hover: %(hover)s !important;
  --wb-bg-active: %(active)s !important;
  --wb-sidebar-bg: %(sidebar)s !important;
  --wb-text-primary: %(text)s !important;
  --wb-text-strong: %(text)s !important;
  --wb-text-medium: %(text)s !important;
  --wb-text-secondary: %(muted)s !important;
  --wb-text-tertiary: %(muted)s !important;
  --wb-color-text-primary: %(text)s !important;
  --wb-color-text-secondary: %(muted)s !important;
  --wb-color-text-tertiary: %(muted)s !important;
  --wb-icon-primary: %(text)s !important;
  --wb-icon-secondary: %(muted)s !important;
  --wb-icon-muted: %(muted)s !important;
  --wb-border-default: %(border)s !important;
  --wb-border-subtle: %(hover)s !important;
  --wb-border-focus: %(accent)s !important;
  --wb-bg-card-strong: %(card)s !important;
  --wb-bg-pill-hover: %(hover)s !important;
  --wb-bg-pill-active: %(accent)s !important;
  --wb-bg-pill-active-hover: %(accent_hover)s !important;
  --wb-control-selected-bg: %(accent)s !important;
  --wb-control-selected-bg-hover: %(accent_hover)s !important;
  --wb-button-primary-bg: %(accent)s !important;
  --wb-button-primary-bg-hover: %(accent_hover)s !important;
  --wb-button-primary-bg-active: %(accent_hover)s !important;
  --wb-quick-action-arrow-bg: %(hover)s !important;
  --wb-quick-action-selected-bg: %(accent)s !important;
  --wb-quick-action-selected-fg: %(onaccent)s !important;
  --wb-quick-action-item-bg-hover: %(hover)s !important;
  --wb-quick-action-item-border-hover: %(border)s !important;
  --wb-quick-action-sub-item-bg: %(bg)s !important;
  --wb-quick-action-sub-item-hover-bg: %(hover)s !important;
  --wb-home-composer-card-bg: %(card)s !important;
  --wb-home-composer-sub-card-bg: %(bg)s !important;
  --wb-home-composer-chip-bg-hover: %(hover)s !important;
  --wb-home-composer-arrow-fg: %(muted)s !important;
  --wb-quick-actions-fade-bg: %(bg)s !important;
  --cb-dropdown-bg-color: %(card)s !important;
  --cb-dropdown-item-hover-bg-color: %(hover)s !important;
  --cb-hover-card-bg-color: %(hover)s !important;
  /* ⭐ 输入框双遮蔽源覆盖（白条根因） */
  --atm-surface: %(input)s !important;
  --atm-chat-content-bg: %(input)s !important;
  --cb-input-background: %(input)s !important;
  --cb-main-area-background: %(bg)s !important;
  --cb-content-background: %(bg)s !important;
  --cb-bg-surface: %(card)s !important;
  --cb-vscode-editor-background: %(bg)s !important;
  --cb-vscode-sideBar-background: %(sidebar)s !important;
  --cb-vscode-foreground: %(text)s !important;
  --cb-vscode-editor-foreground: %(text)s !important;
  --cb-text-primary: %(text)s !important;
  --cb-text-secondary: %(muted)s !important;
  --cb-vscode-titleBar-activeBackground: %(topbar1)s !important;
  --cb-vscode-titleBar-activeForeground: %(ontopbar)s !important;
  --cb-vscode-input-background: %(input)s !important;
  --cb-vscode-dropdown-background: %(card)s !important;
  --cb-vscode-button-background: %(accent)s !important;
  --cb-vscode-button-foreground: %(onaccent)s !important;
  --cb-vscode-button-hoverBackground: %(accent_hover)s !important;
  --cb-vscode-list-hoverBackground: %(hover)s !important;
  --cb-vscode-scrollbarSlider-background: %(border)s !important;
  --cb-vscode-scrollbarSlider-hoverBackground: %(accent)s !important;
}

/* ---- 全局过渡动画（主题切换平滑） ---- */
%(bodysel)s,
%(bodysel)s #root,
%(bodysel)s .teams-container,
%(bodysel)s .conversation-sidebar,
%(bodysel)s .main-content,
%(bodysel)s .claw-agent-chat-pane,
%(bodysel)s .conversation-list,
%(bodysel)s .conversation-list-topbar,
%(bodysel)s .workbuddy-topbar {
  transition: background-color .15s ease, color .15s ease !important;
}

%(bodysel)s,
%(bodysel)s #root {
  color: %(text)s !important;
  background: %(bg)s !important;
}

%(bodysel)s .teams-container {
  background: %(sidebar)s !important;
}

%(bodysel)s .teams-container [data-view-id="sidebar"],
%(bodysel)s .conversation-sidebar,
%(bodysel)s .conversation-list {
  background: linear-gradient(180deg, %(sidebar_hi)s 0%%, %(sidebar)s 48%%, %(sidebar_lo)s 100%%) !important;
  border-right: 1px solid %(border)s !important;
}

%(bodysel)s .conversation-list-topbar,
%(bodysel)s .claw-agent-chat-topbar,
%(bodysel)s .workbuddy-topbar,
%(bodysel)s .teams-top-bar {
  background: linear-gradient(180deg, %(topbar1)s 0%%, %(topbar2)s 100%%) !important;
  border-bottom: 1px solid %(topbar_lo)s !important;
  color: %(ontopbar)s !important;
}

%(bodysel)s .conversation-list-topbar :where(button, svg),
%(bodysel)s .claw-agent-chat-topbar :where(button, svg),
%(bodysel)s .workbuddy-topbar :where(button, svg),
%(bodysel)s .teams-top-bar :where(button, svg) {
  color: %(ontopbar)s !important;
}

/* ---- 主内容区 + hero 背景图 ---- */
%(bodysel)s .teams-container [data-view-id]:not([data-view-id="sidebar"]),
%(bodysel)s .teams-main-content,
%(bodysel)s .main-content,
%(bodysel)s .main-content--welcome,
%(bodysel)s .welcome,
%(bodysel)s .welcome-container,
%(bodysel)s .claw-agent-chat-pane {
  background-color: %(bg)s !important;
  background-image:%(hero_layer)s linear-gradient(135deg, %(bg_hi)s 0%%, %(bg)s 46%%, %(bg_lo)s 100%%) !important;
  background-size: cover !important;
  background-position: center !important;
}

/* ---- Tab 选中态 ---- */
%(bodysel)s .conversation-list-tab-row.active,
%(bodysel)s .conversation-list-tab-button-box.active {
  border-color: %(accent)s !important;
  background: %(sel_bg)s !important;
}

%(bodysel)s .conversation-agent-card:hover {
  background: %(hover)s !important;
}

%(bodysel)s .conversation-agent-card[class*="selected"] {
  border-color: %(accent)s !important;
  background: %(sel_bg)s !important;
}

%(bodysel)s .wb-scene-tabs__pill--active,
%(bodysel)s .wb-scene-tabs__pill--active:hover {
  border-color: %(accent)s !important;
  background: linear-gradient(180deg, %(accent)s 0%%, %(accent_hover)s 100%%) !important;
  color: %(onaccent)s !important;
}

/* ---- 快捷操作 chips ---- */
%(bodysel)s .wb-home-composer__chips .quick-actions__item,
%(bodysel)s .wb-home-composer__chips .quick-actions-sub__item,
%(bodysel)s .wb-home-composer__chip,
%(bodysel)s .claw-agent-chat-pane .colleague-chat-suggestions__item {
  border: 1px solid %(border)s !important;
  background: %(chip_bg)s !important;
  color: %(text)s !important;
}

%(bodysel)s .wb-home-composer__chips .quick-actions__item:hover,
%(bodysel)s .wb-home-composer__chips .quick-actions-sub__item:hover,
%(bodysel)s .wb-home-composer__chip:hover,
%(bodysel)s .claw-agent-chat-pane .colleague-chat-suggestions__item:hover {
  border-color: %(accent)s !important;
  background: %(hover)s !important;
}

/* ---- 输入框 ---- */
%(bodysel)s .wb-home-composer__input-slot,
%(bodysel)s .claw-agent-chat-pane .colleague-chat-cb-chat [class*="input-area-container"],
%(bodysel)s .project-detail-view__chat-input,
%(bodysel)s .atm-modal-chat-input {
  border: 1px solid %(border)s !important;
  background: %(input)s !important;
  box-shadow: 0 1px 4px %(shadow)s !important;
  border-radius: 12px !important;
  transition: border-color .2s ease, box-shadow .2s ease !important;
}

%(bodysel)s .wb-home-composer__input-slot:focus-within,
%(bodysel)s .claw-agent-chat-pane [class*="input-area-container"]:focus-within {
  border-color: %(accent)s !important;
  box-shadow: 0 0 0 3px %(chip_bg)s, 0 1px 8px %(shadow)s !important;
}

%(bodysel)s .wb-home-composer__input-slot [class*="editable"][contenteditable="true"],
%(bodysel)s .claw-agent-chat-pane [contenteditable="true"] {
  color: %(text)s !important;
}

/* ⭐ atm-modal-chat-input 直接覆盖（白条根因：双遮蔽源） */
%(bodysel)s .atm-modal-chat-input,
%(bodysel)s .atm-modal-chat-input * {
  --atm-surface: %(input)s !important;
  --atm-chat-content-bg: %(input)s !important;
}
%(bodysel)s .atm-modal-chat-input [class*="_mainArea_"],
%(bodysel)s .atm-modal-chat-input [class*="_content_"],
%(bodysel)s .atm-modal-chat-input textarea,
%(bodysel)s .atm-modal-chat-input [contenteditable] {
  background: %(input)s !important;
  border: 1px solid %(border)s !important;
  border-radius: 12px !important;
}

/* ---- 弹窗/浮层 ---- */
%(bodysel)s [role="dialog"],
%(bodysel)s .workspace-more-popover,
%(bodysel)s .user-menu-popover,
%(bodysel)s [class*="tooltip"],
%(bodysel)s [class*="popover"],
%(bodysel)s [class*="dropdown-menu"] {
  border: 1px solid %(border)s !important;
  background: %(card)s !important;
  color: %(text)s !important;
  box-shadow: 0 6px 18px %(shadow)s !important;
}

/* ---- 滚动条 (只改颜色不改尺寸) ---- */
%(bodysel)s ::-webkit-scrollbar-track {
  background: transparent !important;
}
%(bodysel)s ::-webkit-scrollbar-thumb {
  border: 2px solid transparent;
  border-radius: 8px;
  background: %(border)s;
  background-clip: padding-box;
}
%(bodysel)s ::-webkit-scrollbar-thumb:hover {
  background: %(accent)s;
}

/* ---- 选中文字 ---- */
%(bodysel)s ::selection {
  color: %(onaccent)s !important;
  background: %(accent)s !important;
}

/* ---- 代码块 ---- */
%(bodysel)s code,
%(bodysel)s pre,
%(bodysel)s .code-block,
%(bodysel)s [class*="code-block"],
%(bodysel)s [class*="codeBlock"] {
  background: %(hover)s !important;
  color: %(text)s !important;
  border: 1px solid %(border)s !important;
  border-radius: 8px !important;
}
%(bodysel)s pre code {
  background: transparent !important;
  border: none !important;
}

/* ---- Markdown 内容 ---- */
%(bodysel)s h1, %(bodysel)s h2, %(bodysel)s h3,
%(bodysel)s h4, %(bodysel)s h5, %(bodysel)s h6 {
  color: %(text)s !important;
}
%(bodysel)s blockquote {
  border-left: 3px solid %(accent)s !important;
  background: %(chip_bg)s !important;
  color: %(text)s !important;
  border-radius: 0 8px 8px 0 !important;
}
%(bodysel)s table {
  border-collapse: collapse !important;
}
%(bodysel)s th, %(bodysel)s td {
  border: 1px solid %(border)s !important;
  color: %(text)s !important;
}
%(bodysel)s th {
  background: %(hover)s !important;
}
%(bodysel)s hr {
  border-color: %(border)s !important;
}
%(bodysel)s a {
  color: %(accent)s !important;
}
%(bodysel)s a:hover {
  color: %(accent_hover)s !important;
}

/* ---- 主题图标个性化: logo 替换为主题 emoji ---- */
%(bodysel)s .conversation-list-logo .logo-workbuddy-icon {
  display: none !important;
}
%(bodysel)s .conversation-list-logo-row::before {
  content: "%(emoji)s";
  font-size: 24px;
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
}

/* 聊天框右上角主题图标 */
%(bodysel)s .wb-home-composer__input-slot [class*="topRightSlotStandalone"] img {
  display: none !important;
}
%(bodysel)s .wb-home-composer__input-slot [class*="topRightSlotStandalone"]::after {
  content: "%(emoji)s";
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 36px;
  opacity: 0.85;
  pointer-events: none;
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
}

/* ---- 加载动画/skeleton ---- */
%(bodysel)s [class*="skeleton"],
%(bodysel)s [class*="loading"],
%(bodysel)s [class*="spinner"],
%(bodysel)s [class*="placeholder"],
%(bodysel)s [class*="shimmer"] {
  background: %(hover)s !important;
  color: %(muted)s !important;
}
%(bodysel)s [class*="spinner"] {
  border-color: %(border)s !important;
  border-top-color: %(accent)s !important;
}

/* ---- 开关/复选框/单选 ---- */
%(bodysel)s input[type="checkbox"]:checked,
%(bodysel)s input[type="radio"]:checked,
%(bodysel)s [class*="switch"][class*="checked"],
%(bodysel)s [class*="toggle"][class*="on"] {
  background: %(accent)s !important;
  border-color: %(accent)s !important;
}
%(bodysel)s [class*="switch"],
%(bodysel)s [class*="toggle"] {
  border-color: %(border)s !important;
}

/* ---- 右键菜单/上下文菜单 ---- */
%(bodysel)s [class*="context-menu"],
%(bodysel)s [class*="contextMenu"],
%(bodysel)s [class*="menu-item"],
%(bodysel)s [class*="menuItem"],
%(bodysel)s [class*="menu-list"],
%(bodysel)s [class*="menuList"] {
  background: %(card)s !important;
  color: %(text)s !important;
  border-color: %(border)s !important;
}
%(bodysel)s [class*="menu-item"]:hover,
%(bodysel)s [class*="menuItem"]:hover {
  background: %(hover)s !important;
  color: %(text)s !important;
}

/* ---- 设置页面 ---- */
%(bodysel)s [class*="settings"],
%(bodysel)s [class*="preferences"],
%(bodysel)s [class*="config-page"],
%(bodysel)s [class*="SettingItem"],
%(bodysel)s [class*="setting-item"] {
  background: %(card)s !important;
  color: %(text)s !important;
  border-color: %(border)s !important;
}
%(bodysel)s [class*="setting-item"]:hover {
  background: %(hover)s !important;
}

/* ---- 空状态 ---- */
%(bodysel)s [class*="empty-state"],
%(bodysel)s [class*="emptyState"],
%(bodysel)s [class*="no-data"],
%(bodysel)s [class*="noData"],
%(bodysel)s [class*="illustration"] {
  color: %(muted)s !important;
}

/* ---- 链接预览卡片 ---- */
%(bodysel)s [class*="link-card"],
%(bodysel)s [class*="linkCard"],
%(bodysel)s [class*="preview-card"],
%(bodysel)s [class*="previewCard"] {
  background: %(card)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
  border-radius: 8px !important;
}
%(bodysel)s [class*="link-card"]:hover,
%(bodysel)s [class*="linkCard"]:hover,
%(bodysel)s [class*="preview-card"]:hover {
  border-color: %(accent)s !important;
}

/* ---- 代码复制按钮 ---- */
%(bodysel)s [class*="copy-button"],
%(bodysel)s [class*="copyButton"],
%(bodysel)s [class*="code-copy"],
%(bodysel)s [class*="codeCopy"] {
  background: %(hover)s !important;
  color: %(muted)s !important;
  border-color: %(border)s !important;
  border-radius: 6px !important;
}
%(bodysel)s [class*="copy-button"]:hover,
%(bodysel)s [class*="copyButton"]:hover,
%(bodysel)s [class*="code-copy"]:hover {
  background: %(accent)s !important;
  color: %(onaccent)s !important;
}

/* ---- 搜索高亮 ---- */
%(bodysel)s mark,
%(bodysel)s [class*="highlight"],
%(bodysel)s [class*="search-match"] {
  background: %(chip_bg)s !important;
  color: %(accent)s !important;
  border-radius: 3px !important;
}

/* ---- 拖拽区域 ---- */
%(bodysel)s [class*="dropzone"]:not([class*="dragging"]),
%(bodysel)s [class*="dropZone"]:not([class*="dragging"]) {
  border-color: %(border)s !important;
  background: %(hover)s !important;
}
%(bodysel)s [class*="dropzone"][class*="dragging"],
%(bodysel)s [class*="dropZone"][class*="active"],
%(bodysel)s [class*="drop-zone"][class*="drag"] {
  border-color: %(accent)s !important;
  background: %(chip_bg)s !important;
}

/* ---- 消息时间戳/元信息 ---- */
%(bodysel)s [class*="timestamp"],
%(bodysel)s [class*="message-time"],
%(bodysel)s [class*="messageTime"],
%(bodysel)s [class*="meta-text"],
%(bodysel)s [class*="metaText"] {
  color: %(muted)s !important;
}

/* ---- 专家页面 / 技能卡片 ---- */
%(bodysel)s [class*="expert-card"],
%(bodysel)s [class*="expertCard"],
%(bodysel)s [class*="skill-card"],
%(bodysel)s [class*="skillCard"] {
  background: %(card)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
  border-radius: 8px !important;
}
%(bodysel)s [class*="expert-card"]:hover,
%(bodysel)s [class*="expertCard"]:hover,
%(bodysel)s [class*="skill-card"]:hover,
%(bodysel)s [class*="skillCard"]:hover {
  border-color: %(accent)s !important;
  background: %(hover)s !important;
}

/* ---- 命令面板 ---- */
%(bodysel)s [class*="command-palette"],
%(bodysel)s [class*="commandPalette"],
%(bodysel)s [class*="quick-input"],
%(bodysel)s [class*="quickInput"],
%(bodysel)s [class*="command-input"],
%(bodysel)s [class*="commandInput"] {
  background: %(card)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
}

/* ---- @提及 / 附件 ---- */
%(bodysel)s [class*="mention"],
%(bodysel)s [class*="Mention"] {
  background: %(chip_bg)s !important;
  color: %(accent)s !important;
  border-radius: 4px !important;
}
%(bodysel)s [class*="attachment"],
%(bodysel)s [class*="Attachment"],
%(bodysel)s [class*="file-card"],
%(bodysel)s [class*="fileCard"] {
  background: %(hover)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
  border-radius: 8px !important;
}

/* ---- Markdown 容器 / diff / 终端 ---- */
%(bodysel)s [class*="markdown-body"],
%(bodysel)s [class*="markdownBody"],
%(bodysel)s [class*="prose"] {
  color: %(text)s !important;
}
%(bodysel)s [class*="diff-view"],
%(bodysel)s [class*="diffView"],
%(bodysel)s [class*="code-diff"],
%(bodysel)s [class*="codeDiff"] {
  background: %(hover)s !important;
  border-color: %(border)s !important;
  border-radius: 8px !important;
}
%(bodysel)s [class*="diff-view"] [class*="add"],
%(bodysel)s [class*="diffView"] [class*="add"],
%(bodysel)s [class*="line-add"] {
  background: %(chip_bg)s !important;
}
%(bodysel)s [class*="diff-view"] [class*="del"],
%(bodysel)s [class*="diffView"] [class*="del"],
%(bodysel)s [class*="line-del"] {
  background: rgba(255,0,0,0.08) !important;
}
%(bodysel)s [class*="terminal"],
%(bodysel)s [class*="Terminal"],
%(bodysel)s [class*="xterm"] {
  background: %(bg)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
  border-radius: 8px !important;
}

/* ---- 头像 / 树 / 分页 / 面包屑 ---- */
%(bodysel)s [class*="avatar"],
%(bodysel)s [class*="Avatar"] {
  border-color: %(border)s !important;
}
%(bodysel)s [class*="tree-node"],
%(bodysel)s [class*="treeNode"],
%(bodysel)s [class*="tree-item"],
%(bodysel)s [class*="treeItem"] {
  color: %(text)s !important;
}
%(bodysel)s [class*="tree-node"]:hover,
%(bodysel)s [class*="treeNode"]:hover,
%(bodysel)s [class*="tree-item"]:hover {
  background: %(hover)s !important;
}
%(bodysel)s [class*="tree-node"][class*="active"],
%(bodysel)s [class*="treeNode"][class*="selected"],
%(bodysel)s [class*="tree-item"][class*="active"] {
  background: %(active)s !important;
  color: %(text)s !important;
}
%(bodysel)s [class*="pagination"],
%(bodysel)s [class*="Pagination"] {
  color: %(text)s !important;
}
%(bodysel)s [class*="pagination"] [class*="active"],
%(bodysel)s [class*="Pagination"] [class*="active"] {
  background: %(accent)s !important;
  color: %(onaccent)s !important;
  border-color: %(accent)s !important;
}
%(bodysel)s [class*="breadcrumb"],
%(bodysel)s [class*="Breadcrumb"] {
  color: %(muted)s !important;
}
%(bodysel)s [class*="breadcrumb"] a,
%(bodysel)s [class*="Breadcrumb"] a {
  color: %(accent)s !important;
}

/* ---- 优化: caret-color / 等宽字体 / Firefox 兼容 / 链接 ---- */
%(bodysel)s [contenteditable="true"],
%(bodysel)s input[type="text"],
%(bodysel)s input[type="search"],
%(bodysel)s textarea {
  caret-color: %(accent)s !important;
}
%(bodysel)s code,
%(bodysel)s pre,
%(bodysel)s [class*="code-block"],
%(bodysel)s [class*="codeBlock"] {
  font-family: "SF Mono", "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas", monospace !important;
}
%(bodysel)s ::-moz-selection {
  color: %(onaccent)s !important;
  background: %(accent)s !important;
}
%(bodysel)s {
  scrollbar-color: %(border)s transparent;
  scrollbar-width: thin;
}
%(bodysel)s a {
  text-decoration: none !important;
}
%(bodysel)s a:hover {
  text-decoration: underline !important;
}

/* ---- 欢迎页搜索框 / 空状态搜索 ---- */
%(bodysel)s [class*="welcome-search"],
%(bodysel)s [class*="welcomeSearch"],
%(bodysel)s [class*="home-search"],
%(bodysel)s [class*="homeSearch"],
%(bodysel)s [class*="hero-search"],
%(bodysel)s [class*="heroSearch"],
%(bodysel)s [class*="empty-search"],
%(bodysel)s [class*="emptySearch"],
%(bodysel)s [class*="quick-search-input"],
%(bodysel)s [class*="quickSearchInput"] {
  background: %(hover)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
  border-radius: 12px !important;
}
%(bodysel)s [class*="welcome-search"] input,
%(bodysel)s [class*="welcomeSearch"] input,
%(bodysel)s [class*="home-search"] input,
%(bodysel)s [class*="hero-search"] input,
%(bodysel)s [class*="empty-search"] input,
%(bodysel)s [class*="quick-search-input"] input,
%(bodysel)s [class*="welcome-search"] textarea,
%(bodysel)s [class*="hero-search"] textarea,
%(bodysel)s [class*="empty-search"] textarea {
  background: transparent !important;
  color: %(text)s !important;
}
%(bodysel)s [class*="welcome-search"] input::placeholder,
%(bodysel)s [class*="welcome-search"] textarea::placeholder,
%(bodysel)s [class*="hero-search"] input::placeholder,
%(bodysel)s [class*="empty-search"] input::placeholder,
%(bodysel)s [class*="home-search"] input::placeholder {
  color: %(muted)s !important;
}

/* ---- 透明容器/卡片背景（防止白色矩形） ---- */
%(bodysel)s [class*="welcome-card"],
%(bodysel)s [class*="welcomeCard"],
%(bodysel)s [class*="welcome-container"]:not([class*="modal"]),
%(bodysel)s [class*="welcome-container"]:not([class*="dialog"]) {
  background: transparent !important;
}

/* ---- 欢迎页头像/装饰容器（防止白色圆形） ---- */
%(bodysel)s [class*="welcome-avatar"],
%(bodysel)s [class*="welcomeAvatar"],
%(bodysel)s [class*="robot-avatar"],
%(bodysel)s [class*="robotAvatar"],
%(bodysel)s [class*="assistant-avatar"],
%(bodysel)s [class*="assistantAvatar"],
%(bodysel)s [class*="welcome-icon"],
%(bodysel)s [class*="welcomeIcon"],
%(bodysel)s [class*="welcome-logo"],
%(bodysel)s [class*="welcomeLogo"] {
  background: %(chip_bg)s !important;
  border-color: %(border)s !important;
}

/* ---- 通用兜底：欢迎页所有非输入容器强制透明背景 ---- */
%(bodysel)s [class*="welcome"] [class*="container"]:not([class*="modal"]):not([class*="dialog"]),
%(bodysel)s [class*="welcome"] [class*="box"]:not([class*="modal"]):not([class*="dialog"]),
%(bodysel)s [class*="welcome"] [class*="wrapper"]:not([class*="modal"]):not([class*="dialog"]) {
  background: transparent !important;
}

/* ---- 任务/状态通知条（防止白框） ---- */
%(bodysel)s [class*="task-notify"],
%(bodysel)s [class*="taskNotify"],
%(bodysel)s [class*="running-task"],
%(bodysel)s [class*="runningTask"],
%(bodysel)s [class*="progress-toast"],
%(bodysel)s [class*="progressToast"],
%(bodysel)s [class*="read-tip"],
%(bodysel)s [class*="readTip"],
%(bodysel)s [class*="file-loaded"],
%(bodysel)s [class*="fileLoaded"],
%(bodysel)s [class*="status-message"],
%(bodysel)s [class*="statusMessage"],
%(bodysel)s [class*="info-tip"],
%(bodysel)s [class*="infoTip"],
%(bodysel)s [class*="tip-bar"],
%(bodysel)s [class*="tipBar"],
%(bodysel)s [class*="notification-bar"],
%(bodysel)s [class*="notificationBar"] {
  background: %(hover)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
}

/* ---- 按 placeholder 文本选择（覆盖"思考中"输入框） ---- */
%(bodysel)s input[placeholder*="思考"],
%(bodysel)s input[placeholder*="input"],
%(bodysel)s input[placeholder*="消息"],
%(bodysel)s input[placeholder*="请输入"],
%(bodysel)s textarea[placeholder*="思考"],
%(bodysel)s textarea[placeholder*="消息"],
%(bodysel)s div[placeholder*="思考"],
%(bodysel)s div[contenteditable="true"][data-placeholder*="思考"],
%(bodysel)s div[contenteditable="true"][aria-placeholder*="思考"] {
  background: %(hover)s !important;
  border-color: %(border)s !important;
  color: %(text)s !important;
}

/* ---- 兜底：所有 body 下的浅色容器都强制覆盖 ---- */
%(bodysel)s div[style*="background-color: rgb(255, 255, 255)"],
%(bodysel)s div[style*="background: rgb(255, 255, 255)"],
%(bodysel)s div[style*="background-color:#fff"],
%(bodysel)s div[style*="background-color: #fff"],
%(bodysel)s div[style*="background:#fff"],
%(bodysel)s div[style*="background: #fff"] {
  background: %(hover)s !important;
  background-color: %(hover)s !important;
}

/* ---- reduced motion ---- */
@media (prefers-reduced-motion: reduce) {
  %(bodysel)s,
  %(bodysel)s #root,
  %(bodysel)s .teams-container,
  %(bodysel)s .conversation-sidebar,
  %(bodysel)s .main-content,
  %(bodysel)s .claw-agent-chat-pane {
    transition: none !important;
  }
}
'''

def render_css(theme, palette, mode, dark, hero_file=None):
    d = derive(palette, dark)
    on_accent = '#ffffff' if luminance(d['accent']) < 150 else '#1a1a1a'
    on_topbar = '#ffffff' if luminance(d['topbar2']) < 150 else '#1a1a1a'
    v = dict(d)
    # hero 背景图: 纵向三段渐变遮罩 — 更透更清晰, 底部仍保文字可读
    if hero_file:
        if not dark:
            v1, v2, v3 = rgba(d['bg'], 0.30), rgba(d['bg'], 0.55), rgba(d['bg'], 0.75)
        else:
            v1, v2, v3 = rgba(d['bg'], 0.25), rgba(d['bg'], 0.50), rgba(d['bg'], 0.70)
        hero = 'linear-gradient(180deg, %s 0%%, %s 45%%, %s 100%%), url("./%s"), ' % (v1, v2, v3, hero_file)
    else:
        hero = ''
    v.update(
        id=theme['id'], name=theme['name'], mode=mode,
        rootsel='body.dark, body.dark-theme, body[data-theme="dark"], html.dark body' if dark else ':root, body, body.light',
        bodysel='body.dark, body.dark-theme, body[data-theme="dark"], html.dark body' if dark else 'body',
        onaccent=on_accent, ontopbar=on_topbar,
        hero_layer=hero,
        emoji=THEME_EMOJI.get(theme['id'], '🎨'),
        sidebar_hi=lighten(d['sidebar'],0.10) if not dark else lighten(d['sidebar'],0.06),
        sidebar_lo=darken(d['sidebar'],0.08) if not dark else darken(d['sidebar'],0.15),
        topbar_lo=darken(d['topbar2'],0.18),
        bg_hi=lighten(d['bg'],0.35) if not dark else lighten(d['bg'],0.05),
        bg_lo=darken(d['bg'],0.04) if not dark else darken(d['bg'],0.20),
    )
    return CSS_TMPL % v

def main():
    out = os.path.join(BASE, 'skins')
    os.makedirs(out, exist_ok=True)
    js_themes = []
    hero_exts = ('hero.jpg','hero.jpeg','hero.png','hero.webp')
    for t in ALL:
        tdir = os.path.join(out, t['id'])
        os.makedirs(tdir, exist_ok=True)
        hero_file = next((e for e in hero_exts if os.path.exists(os.path.join(tdir, e))), None)
        css = render_css(t, t['light'], 'light', False, hero_file) + '\n' + render_css(t, t['dark'], 'dark', True, hero_file)
        with open(os.path.join(tdir,'skin.css'),'w',encoding='utf-8') as f:
            f.write(css)
        meta = dict(schemaVersion=1, id=t['id'], name=t['name'], category=t['cat'],
                    categoryName=CAT_NAMES[t['cat']], desc=t['desc'], tags=t['tags'])
        if hero_file:
            meta['hero'] = hero_file
        with open(os.path.join(tdir,'theme.json'),'w',encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        jt = dict(meta)
        jt['badge'] = t.get('badge')
        jt['hasHero'] = bool(hero_file)
        jt['emoji'] = THEME_EMOJI.get(t['id'], '🎨')
        jt['light'] = t['light']
        # dark 配色: 用 derive 校正后的值, 与 skin.css 保持一致
        d_dk = derive(t['dark'], dark=True)
        jt['dark'] = dict(t['dark'])
        for k in ('bg','sidebar','topbar1','topbar2','border'):
            jt['dark'][k] = d_dk[k]
        js_themes.append(jt)
    n_hero = sum(1 for x in js_themes if x['hasHero'])
    with open(os.path.join(BASE,'themes-data.js'),'w',encoding='utf-8') as f:
        f.write('// 由 generate.py 自动生成, 请勿手改\n')
        f.write('window.THEMES = ')
        json.dump(js_themes, f, ensure_ascii=False, indent=1)
        f.write(';\n')
    print('[OK] generated %d themes (%d with hero) -> %s' % (len(ALL), n_hero, out))
    for t in ALL[:3]:
        print('  -', t['id'], t['name'])
    print('  ...')

if __name__ == '__main__':
    main()
