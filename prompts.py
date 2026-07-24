# -*- coding: utf-8 -*-
"""49 个主题的背景图生图 prompt
统一风格: 柔和低对比、适合作为工作台 UI 背景、无文字无水印
"""
STYLE = ", soft ambient lighting, muted tones, dreamy atmosphere, suitable as a desktop chat app background, low contrast, no text, no watermark, no characters faces, wide cinematic composition"

PROMPTS = {
# 动漫
"one-piece-strawhat": "Vast blue ocean under bright sky, a small straw hat floating on gentle waves, distant pirate ship silhouette on the horizon, sunny adventurous mood, anime art style" + STYLE,
"one-piece-luffy": "Warm red sunset over the grand line ocean, billowing red sail fabric, energetic crimson and orange sky, dynamic waves" + STYLE,
"one-piece-zoro": "Misty green bamboo forest with three katana swords resting against a rock, moonlight filtering through leaves, serene samurai mood" + STYLE,
"naruto-uzumaki": "Golden autumn leaves swirling over a hidden ninja village rooftop, warm orange sunset, hokage monument mountain silhouette in distance" + STYLE,
"naruto-sasuke": "Dark blue night sky with lightning bolts over a quiet valley, deep indigo clouds, a lone crow flying, cool electric atmosphere" + STYLE,
"dragon-ball": "Brilliant golden energy aura rising over rocky mountain peaks, glowing kamehameha light trail in the sky, epic sunrise" + STYLE,
"demon-slayer": "Flowing water streams with gentle blue-green ripples, japanese wisteria flowers hanging over a calm pond, ukiyo-e wave patterns" + STYLE,
"jujutsu-kaisen": "Dark purple shibuya night street with faint cursed energy swirls, glowing violet talismans floating, mysterious urban atmosphere" + STYLE,
"attack-on-titan": "Vast green field beyond giant stone walls, white wings of freedom flag waving in the wind, dramatic cloudy sky at dawn" + STYLE,
"spy-family": "Cozy pastel pink living room with peanut motifs and plush toys, warm evening lamp light, soft bokeh, kawaii aesthetic" + STYLE,
# 游戏
"genshin-mondstadt": "Windmill city by a cider lake, dandelion seeds floating in gentle breeze, european fantasy architecture, fresh teal sky" + STYLE,
"genshin-liyue": "Golden harbor with ancient chinese architecture, glazed lanterns glowing at dusk, jade green mountains and mist, warm amber tones" + STYLE,
"genshin-inazuma": "Purple thunder clouds over cherry blossom shrine, torii gates and lightning streaks, sakura petals drifting in electric air" + STYLE,
"genshin-fontaine": "Elegant blue opera house with fountains and golden ornaments, art nouveau french architecture, water reflections" + STYLE,
"starrail": "Silver-blue space train traveling through a starfield, nebula and distant galaxies, sleek sci-fi rails of light" + STYLE,
"wuthering-waves": "Celadon porcelain colored waves and mist over a chinese coastal city, jade green glowing resonance patterns in the air" + STYLE,
"minecraft": "Blocky pixelated grass meadow with cubic trees and soft square clouds, voxel landscape at sunrise, gentle green palette" + STYLE,
"elden-ring": "Giant golden erdtree glowing over a misty fantasy landscape, falling golden leaves, epic medieval atmosphere" + STYLE,
"zelda-totk": "Floating sky islands with waterfalls pouring into clouds, lush green shrines and golden zonai ruins, bright adventure sky" + STYLE,
"cyberpunk2077": "Neon yellow and cyan night city street, holographic billboards in the rain, futuristic skyscrapers with glowing signs" + STYLE,
# 科技
"tech-hud-blue": "Futuristic holographic blue interface panels floating in dark space, glowing circuit lines and data streams, clean sci-fi HUD" + STYLE,
"tech-cyber-purple": "Purple neon grid cyberspace, glowing violet laser lines over a digital horizon, synthwave wireframe landscape" + STYLE,
"tech-matrix": "Cascading green digital rain code streams on black background, glowing emerald matrix characters fading into darkness" + STYLE,
"tech-tron": "Glowing blue and orange light trails racing across a dark digital grid, sleek futuristic light cycle tracks" + STYLE,
"tech-ironman": "Golden and crimson arc reactor core glowing in a dark high-tech lab, circular holographic interface elements" + STYLE,
"tech-quantum": "Clean white laboratory with silver quantum computer chandelier, frozen qubit lattice, minimal sci-fi elegance" + STYLE,
"tech-neon-pink": "Vaporwave pink neon sunset over a retro grid beach, palm tree silhouettes and chrome sun, 80s retro-futurism" + STYLE,
"tech-gundam": "White and blue mecha hangar with soft industrial lighting, red and yellow accent details, clean anime sci-fi" + STYLE,
# 自然
"nature-ocean": "Deep blue underwater scene with sun rays piercing through the water, gentle whale silhouette in the distance" + STYLE,
"nature-forest": "Sunlit green forest after rain, light beams through tall trees, fresh moss and ferns, morning mist" + STYLE,
"nature-sunset": "Warm orange desert sunset over sand dunes, golden hour glow, long soft shadows, tranquil sahara evening" + STYLE,
"nature-sakura": "Pink cherry blossom petals drifting over a quiet kyoto river, soft spring sunlight, dreamy bokeh" + STYLE,
"nature-lavender": "Endless lavender field in provence at golden hour, purple rows stretching to a distant farmhouse, gentle haze" + STYLE,
"nature-aurora": "Green and violet aurora borealis dancing over snowy iceland mountains, starry night sky reflected on a frozen lake" + STYLE,
"nature-desert": "Golden sand dunes of dunhuang under a vast sky, crescent moon oasis in distance, silk road caravan silhouette" + STYLE,
"nature-glacier": "Pristine blue glacier ice cave with crystal clear frozen textures, soft arctic light, pure white and ice blue" + STYLE,
# 复古
"retro-qq2008": "Retro 2008 computer desktop aesthetic, glossy aqua blue gel buttons and glass panels, nostalgic chinese internet era vibes, y2k gloss" + STYLE,
"retro-winxp": "Rolling green hills under bright blue sky with fluffy white clouds, bliss wallpaper recreation, nostalgic operating system scenery" + STYLE,
"retro-win98": "Retro 90s operating system aesthetic, pixel art clouds on gray gradient, teal and navy panels, vintage computing nostalgia" + STYLE,
"retro-fc-redwhite": "Retro 8-bit video game scene, red and white console controller on a wooden table, crt tv glow, pixelated clouds" + STYLE,
"retro-gameboy": "Retro handheld game console aesthetic, olive green monochrome pixel landscape with tetris blocks falling, 90s portable gaming" + STYLE,
# 简约
"minimal-mono": "Minimal black white and gray abstract geometry, soft shadows on concrete wall, muji style zen simplicity" + STYLE,
"minimal-ivory": "Warm ivory and oat colored japandi interior, linen textures and soft morning light, wabi-sabi minimalism" + STYLE,
"minimal-mint": "Fresh mint leaves with morning dew drops, pale green pastel gradient, clean and airy minimal composition" + STYLE,
"minimal-slate": "Slate blue-gray architectural minimalism, smooth concrete curves and soft diffused light, calm business aesthetic" + STYLE,
# 创意
"creative-aurora-glass": "Frosted glass panels with aurora gradient light passing through, translucent layers of violet blue and pink, ios style" + STYLE,
"creative-dopamine": "Bold saturated color blocks collage, happy pink orange and turquoise shapes, playful memphis design energy" + STYLE,
"creative-morandi": "Muted morandi color still life, dusty green gray and terracotta ceramic vases, oil painting softness" + STYLE,
"creative-chinese-red": "Forbidden city red wall with golden glazed roof tiles, chinese palace shadows of plum blossom branches, guochao aesthetic" + STYLE,
}
