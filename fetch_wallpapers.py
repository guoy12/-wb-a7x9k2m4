# -*- coding: utf-8 -*-
"""从 Wallhaven 批量下载 1920x1080+ 高清壁纸替换 skins/<id>/hero.png
用法: python fetch_wallpapers.py
无 API key，速率约 45 req/min，加 2 秒延时。
"""
import os, sys, time, requests, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SKINS = os.path.join(BASE, 'skins')
TMP = os.path.join(BASE, '_wallhaven_cache')
os.makedirs(TMP, exist_ok=True)

SEARCH = {
    "one-piece-strawhat": "one piece anime ocean",
    "one-piece-luffy": "one piece luffy",
    "one-piece-zoro": "one piece zoro swordsman",
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

def search_wallhaven(query, page=1):
    url = "https://wallhaven.cc/api/v1/search"
    params = {
        "q": query, "categories": "100", "purity": "100",
        "sorting": "relevance", "atleast": "1920x1080",
        "page": str(page)
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])

def download(url, dest):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

def run():
    ok = fail = skip = 0
    for i, (tid, q) in enumerate(SEARCH.items()):
        dest = os.path.join(SKINS, tid, 'hero.png')
        print(f"[{i+1}/49] {tid}: '{q}' ...", end=' ', flush=True)
        try:
            results = search_wallhaven(q)
            if not results:
                print("NO RESULTS (keep old)"); skip += 1; continue
            # 取第一张图（relevance 排序）
            img_url = results[0]['path']
            ext = img_url.rsplit('.', 1)[-1].lower()
            tmp_file = os.path.join(TMP, f"{tid}.{ext}")
            download(img_url, tmp_file)
            sz = os.path.getsize(tmp_file)
            if sz < 30000:
                print(f"TOO SMALL {sz//1024}KB (keep old)"); skip += 1; continue
            # 转为 png（如果不是 png，用 requests 下载原始格式，再重命名）
            shutil.move(tmp_file, dest) if ext == 'png' else shutil.move(tmp_file, dest)
            print(f"OK {sz//1024}KB {results[0].get('resolution','?')}")
            ok += 1
        except Exception as e:
            print(f"FAIL: {e}")
            fail += 1
        time.sleep(2)  # 速率控制
    print(f"\n=== done: {ok} downloaded, {skip} skipped, {fail} failed ===")

if __name__ == '__main__':
    run()
