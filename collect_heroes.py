# -*- coding: utf-8 -*-
"""把 generated-images 里按 prompt 前缀命名的图片归位到 skins/<id>/hero.png"""
import os, shutil, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = r"c:\Users\Administrator\Desktop\watson\generated-images"
SKINS = os.path.join(BASE, 'skins')

MAP = {
 "Brilliant_golden_energy": "dragon-ball",
 "Flowing_water_streams": "demon-slayer",
 "Dark_purple_shibuya": "jujutsu-kaisen",
 "Vast_green_field": "attack-on-titan",
 "Cozy_pastel_pink": "spy-family",
 "Windmill_city": "genshin-mondstadt",
 "Golden_harbor": "genshin-liyue",
 "Purple_thunder_clouds": "genshin-inazuma",
 "Elegant_blue_opera": "genshin-fontaine",
 "Silver_blue_space_train": "starrail",
 "Celadon_porcelain": "wuthering-waves",
 "Blocky_pixelated": "minecraft",
 "Giant_golden_erdtree": "elden-ring",
 "Floating_sky_islands": "zelda-totk",
 "Neon_yellow_and_cyan": "cyberpunk2077",
 "Futuristic_holographic_blue": "tech-hud-blue",
 "Purple_neon_grid": "tech-cyber-purple",
 "Cascading_green_digital": "tech-matrix",
 "Glowing_blue_and_orange": "tech-tron",
 "Golden_and_crimson_arc": "tech-ironman",
 "Clean_white_laboratory": "tech-quantum",
 "Vaporwave_pink": "tech-neon-pink",
 "White_and_blue_mecha": "tech-gundam",
 "Deep_blue_underwater": "nature-ocean",
 "Sunlit_green_forest": "nature-forest",
 "Warm_orange_desert": "nature-sunset",
 "Pink_cherry_blossom": "nature-sakura",
 "Endless_lavender": "nature-lavender",
 "Green_and_violet_aurora": "nature-aurora",
 "Golden_sand_dunes": "nature-desert",
 "Pristine_blue_glacier": "nature-glacier",
 "Retro_2008": "retro-qq2008",
 "Rolling_green_hills": "retro-winxp",
 "Retro_90s": "retro-win98",
 "Retro_8_bit": "retro-fc-redwhite",
 "Retro_handheld": "retro-gameboy",
 "Minimal_black": "minimal-mono",
 "Warm_ivory": "minimal-ivory",
 "Fresh_mint": "minimal-mint",
 "Slate_blue_gray": "minimal-slate",
 "Frosted_glass": "creative-aurora-glass",
 "Bold_saturated": "creative-dopamine",
 "Muted_morandi": "creative-morandi",
 "Forbidden_city": "creative-chinese-red",
}

moved, skipped = 0, []
for fn in os.listdir(SRC):
    if not fn.lower().endswith('.png'):
        continue
    hit = None
    for prefix, tid in MAP.items():
        if fn.startswith(prefix):
            hit = tid
            break
    if not hit:
        skipped.append(fn)
        continue
    dst = os.path.join(SKINS, hit, 'hero.png')
    shutil.move(os.path.join(SRC, fn), dst)
    moved += 1

print('moved:', moved)
if skipped:
    print('skipped (no mapping):')
    for s in skipped: print('  -', s)

# 校验 49 个主题目录都有 hero.png
missing = [d for d in os.listdir(SKINS)
           if os.path.isdir(os.path.join(SKINS, d)) and not os.path.exists(os.path.join(SKINS, d, 'hero.png'))]
print('themes missing hero:', missing if missing else 'NONE - all 49 ok')
