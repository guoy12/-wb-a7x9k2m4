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
    "creative-aurora-glass":"🔮","creative-dopamine":"🎨","creative-morandi":"🏺","creative-chinese-red":"🏯",
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
   由 workbuddy-skin-gallery 生成, 结构参考 workbuddy-qq2008-theme */
%(rootsel)s {
  --vscode-foreground: %(text)s !important;
  --vscode-editor-foreground: %(text)s !important;
  --vscode-descriptionForeground: %(muted)s !important;
  --vscode-disabledForeground: %(muted)s !important;
  --vscode-editor-background: %(bg)s !important;
  --vscode-sideBar-background: %(sidebar)s !important;
  --vscode-panel-background: %(bg)s !important;
  --vscode-input-background: %(input)s !important;
  --vscode-dropdown-background: %(input)s !important;
  --vscode-menu-background: %(card)s !important;
  --vscode-editorWidget-background: %(card)s !important;
  --vscode-textCodeBlock-background: %(hover)s !important;
  --vscode-input-border: %(border)s !important;
  --vscode-focusBorder: %(accent)s !important;
  --vscode-icon-foreground: %(muted)s !important;
  --vscode-textLink-foreground: %(accent)s !important;
  --vscode-textLink-activeForeground: %(accent_hover)s !important;
  --vscode-button-background: %(accent)s !important;
  --vscode-button-foreground: %(onaccent)s !important;
  --vscode-button-hoverBackground: %(accent_hover)s !important;
  --vscode-progressBar-background: %(accent)s !important;
  --vscode-badge-background: %(accent)s !important;
  --vscode-badge-foreground: %(onaccent)s !important;
  --vscode-list-hoverBackground: %(hover)s !important;
  --vscode-list-activeSelectionBackground: %(active)s !important;
  --vscode-list-activeSelectionForeground: %(text)s !important;
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

%(bodysel)s .wb-home-composer__input-slot,
%(bodysel)s .claw-agent-chat-pane .colleague-chat-cb-chat [class*="input-area-container"],
%(bodysel)s .project-detail-view__chat-input,
%(bodysel)s .atm-modal-chat-input {
  border: 1px solid %(border)s !important;
  background: %(input)s !important;
  box-shadow: 0 1px 4px %(shadow)s !important;
}

%(bodysel)s .wb-home-composer__input-slot [class*="editable"][contenteditable="true"],
%(bodysel)s .claw-agent-chat-pane [contenteditable="true"] {
  color: %(text)s !important;
}

%(bodysel)s [role="dialog"],
%(bodysel)s .workspace-more-popover,
%(bodysel)s .user-menu-popover {
  border: 1px solid %(border)s !important;
  background: %(card)s !important;
  box-shadow: 0 6px 18px %(shadow)s !important;
}

%(bodysel)s ::-webkit-scrollbar-thumb {
  border: 2px solid transparent;
  border-radius: 8px;
  background: %(border)s;
  background-clip: padding-box;
}

%(bodysel)s ::selection {
  color: %(onaccent)s !important;
  background: %(accent)s !important;
}

/* ---- 主题图标个性化: logo 替换为主题 emoji ---- */
%(bodysel)s .conversation-list-logo .logo-workbuddy-icon {
  display: none !important;
}
%(bodysel)s .conversation-list-logo-row::before {
  content: "%(emoji)s";
  font-size: 24px;
  line-height: 36px;
  width: 36px;
  height: 36px;
  text-align: center;
  flex: 0 0 36px;
}

/* 聊天框右上角主题图标 (参考 qq2008 企鹅图) */
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
            v1, v2, v3 = rgba(d['bg'], 0.15), rgba(d['bg'], 0.45), rgba(d['bg'], 0.82)
        else:
            v1, v2, v3 = rgba(d['bg'], 0.12), rgba(d['bg'], 0.42), rgba(d['bg'], 0.78)
        hero = 'linear-gradient(180deg, %s 0%%, %s 45%%, %s 100%%), url("./%s"), ' % (v1, v2, v3, hero_file)
    else:
        hero = ''
    v.update(
        id=theme['id'], name=theme['name'], mode=mode,
        rootsel='body.dark' if dark else ':root, body, body.light',
        bodysel='body.dark' if dark else 'body',
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
