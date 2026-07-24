# -*- coding: utf-8 -*-
"""从 Wallhaven 批量下载 4K 超高清壁纸 (3840x2160+, 优先大文件)
策略: 先搜 4K → 降级 2K → 降级 1080P; 同分辨率下选 file_size 最大的
用法: python fetch_wallpapers_hd.py [--force]  (--force 重新下载所有)
"""
import os, sys, time, requests, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SKINS = os.path.join(BASE, 'skins')
MIN_SIZE_KB = 2000  # 目标: 每张至少 2MB (2K/4K 级别)

SEARCH = {
    "one-piece-strawhat": "one piece anime ocean",
    "one-piece-luffy": "one piece luffy",
    "one-piece-zoro": "one piece zoro",
    "naruto-uzumaki": "naruto anime",
    "naruto-sasuke": "sasuke uchiha",
    "dragon-ball": "dragon ball anime goku",
    "demon-slayer": "demon slayer anime",
    "jujutsu-kaisen": "jujutsu kaisen anime",
    "attack-on-titan": "attack on titan anime",
    "spy-family": "spy x family anime",
    "genshin-mondstadt": "genshin impact landscape",
    "genshin-liyue": "genshin impact liyue harbor",
    "genshin-inazuma": "genshin impact inazuma",
    "genshin-fontaine": "genshin impact fontaine",
    "starrail": "honkai star rail",
    "wuthering-waves": "wuthering waves game",
    "minecraft": "minecraft landscape",
    "elden-ring": "elden ring game",
    "zelda-totk": "zelda breath of the wild landscape",
    "cyberpunk2077": "cyberpunk 2077 city",
    "tech-hud-blue": "futuristic interface blue hud",
    "tech-cyber-purple": "cyberpunk purple neon",
    "tech-matrix": "matrix digital rain green code",
    "tech-tron": "tron legacy grid light",
    "tech-ironman": "iron man hud interface",
    "tech-quantum": "futuristic technology abstract",
    "tech-neon-pink": "vaporwave pink neon retro",
    "tech-gundam": "gundam mecha robot",
    "nature-ocean": "deep ocean underwater blue",
    "nature-forest": "green forest landscape",
    "nature-sunset": "desert sunset golden",
    "nature-sakura": "cherry blossom japan spring",
    "nature-lavender": "lavender field provence",
    "nature-aurora": "aurora borealis iceland night",
    "nature-desert": "desert dunes golden sand",
    "nature-glacier": "glacier ice cave blue",
    "retro-qq2008": "retro windows desktop aesthetic",
    "retro-winxp": "windows xp bliss green hills",
    "retro-win98": "windows 98 retro computing",
    "retro-fc-redwhite": "nintendo retro gaming pixel",
    "retro-gameboy": "gameboy retro gaming green",
    "minimal-mono": "minimal black white abstract",
    "minimal-ivory": "minimal japandi interior beige",
    "minimal-mint": "mint green minimal nature",
    "minimal-slate": "slate blue minimal architecture",
    "creative-aurora-glass": "frosted glass gradient abstract",
    "creative-dopamine": "colorful abstract art bright",
    "creative-morandi": "morandi color still life painting",
    "creative-chinese-red": "forbidden city red wall china",
}

RES_TIERS = ["3840x2160", "2560x1440", "1920x1080"]

def search(query, res):
    """搜指定最低分辨率的壁纸, 按收藏数排序"""
    r = requests.get("https://wallhaven.cc/api/v1/search", params={
        "q": query, "categories": "100", "purity": "100",
        "sorting": "favorites", "order": "desc",
        "atleast": res,
    }, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def pick_best(results):
    """从结果中选分辨率最大+文件最大的"""
    if not results: return None
    # 按 file_size 降序, 优先大文件
    results.sort(key=lambda x: x.get("file_size", 0), reverse=True)
    return results[0]

def download(url, dest):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

def run(force=False):
    ok = skip = fail = 0
    for i, (tid, q) in enumerate(SEARCH.items()):
        dest = os.path.join(SKINS, tid, 'hero.png')
        if not force and os.path.exists(dest) and os.path.getsize(dest) >= MIN_SIZE_KB * 1024:
            sz = os.path.getsize(dest) // 1024 // 1024
            print(f"[{i+1}/49] {tid}: already {sz}MB, skip")
            skip += 1; continue

        print(f"[{i+1}/49] {tid}: '{q}' ...", end=' ', flush=True)
        best = None; used_res = ''
        for res in RES_TIERS:
            try:
                results = search(q, res)
                if results:
                    best = pick_best(results)
                    used_res = res
                    break
            except Exception as e:
                print(f"(tier {res} err)", end=' ')
            time.sleep(1)

        if not best:
            print("NO RESULTS"); fail += 1; continue

        try:
            # 直接写入目标文件 (不用 .tmp 避免沙箱拦截删除/移动)
            download(best['path'], dest)
            sz = os.path.getsize(dest)
            print(f"OK {sz//1024//1024}MB {best.get('resolution','?')} (fav={best.get('favorites','?')})")
            ok += 1
        except Exception as e:
            print(f"DL FAIL: {e}"); fail += 1
        time.sleep(2)

    print(f"\n=== done: {ok} upgraded, {skip} already ok, {fail} failed ===")

if __name__ == '__main__':
    run('--force' in sys.argv)
