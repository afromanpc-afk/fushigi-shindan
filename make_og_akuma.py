# 悪魔診断のシェア画像(1200x630)と、結果ごとのシェア用ページを作る
# 使い方: python3 make_og_akuma.py https://xxxx.netlify.app
# アフロ側の画像や og.png には触らない(それらはビルド時に fetch_assets.py が取り込む)
import sys, os, html, http.server, threading, functools
from playwright.sync_api import sync_playwright

SITE = sys.argv[1].rstrip('/')
ROOT = os.path.dirname(os.path.abspath(__file__))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


H = functools.partial(Quiet, directory=ROOT)
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8767), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

JP = "'Noto Sans CJK JP','Noto Sans CJK SC',sans-serif"
SERIF = "'Noto Serif CJK JP','Noto Serif CJK SC',serif"
GOLD = '#c9a45c'


def demon_tpl(svg, d):
    c = d['color']
    return f'''<html><body style="margin:0"><div style="width:1200px;height:630px;position:relative;overflow:hidden;background:#0f0b15;
    background-image:radial-gradient(ellipse at 22% 40%,{c}33,transparent 55%),radial-gradient(ellipse at 90% 110%,rgba(120,40,90,.28),transparent 60%);
    font-family:{JP};color:#ece3d3;display:flex;align-items:center;gap:60px;padding:0 70px;box-sizing:border-box">
    <div style="flex:none;width:420px;height:504px;border:2px solid {GOLD};box-shadow:0 0 0 8px #0f0b15,0 0 0 9px #2c2236;line-height:0">{svg}</div>
    <div style="display:flex;flex-direction:column;gap:14px;min-width:0">
      <div style="font-size:28px;letter-spacing:.3em;color:#a093ab">私に宿る悪魔は</div>
      <div style="font-size:24px;letter-spacing:.25em;color:{c}">{d['sin']} ・ {d['id'].upper()}</div>
      <div style="font-family:{SERIF};font-weight:900;font-size:{92 if len(d['name'])<=6 else 76}px;line-height:1.1;color:#ece3d3">{d['name']}</div>
      <div style="font-family:{SERIF};font-weight:700;font-size:34px;color:{c}">{d['title']}</div>
      <div style="font-weight:700;font-size:30px;line-height:1.6;color:#ddd3c4;margin-top:6px">{d['lead']}</div>
      <div style="font-weight:700;font-size:24px;letter-spacing:.1em;color:#a093ab;margin-top:8px">#悪魔診断 ・ 全10問</div>
    </div></div></body></html>'''


def intro_tpl(svgs):
    row = ''.join(
        f'<div style="width:{w}px;height:{int(w*1.2)}px;border:2px solid {GOLD};line-height:0;transform:rotate({r}deg);box-shadow:0 0 0 6px #0f0b15;margin-left:{m}px">{s}</div>'
        for s, w, r, m in zip(svgs, (190, 224, 190), (-6, 0, 6), (0, -30, -30)))
    return f'''<html><body style="margin:0"><div style="width:1200px;height:630px;position:relative;overflow:hidden;background:#0f0b15;
    background-image:radial-gradient(ellipse at 70% 40%,rgba(201,164,92,.20),transparent 60%);
    font-family:{JP};color:#ece3d3;display:flex;align-items:center;justify-content:space-between;padding:0 50px 0 64px;box-sizing:border-box">
    <div style="display:flex;flex-direction:column;gap:20px;flex:none;width:520px">
      <div style="font-size:24px;letter-spacing:.3em;color:{GOLD};white-space:nowrap">THE GRIMOIRE TEST</div>
      <div style="font-family:{SERIF};font-weight:900;font-size:80px;line-height:1.25;white-space:nowrap">あなたに宿る<br><span style="color:{GOLD}">悪魔</span>診断</div>
      <div style="font-weight:700;font-size:30px;color:#a093ab;white-space:nowrap">10の質問 ・ 10体の悪魔</div>
    </div>
    <div style="display:flex;align-items:center">{row}</div></div></body></html>'''


def share_page(back, key, title, desc, img, url):
    e = html.escape
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">
<script>location.replace("{back}#{key}")</script></head>
<body style="font-family:sans-serif;padding:24px"><a href="{back}#{key}">結果を見る</a></body></html>'''


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    shot = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.goto('http://127.0.0.1:8767/akuma/')
    pg.wait_for_timeout(400)
    D = pg.evaluate('D')
    order = pg.evaluate('ORDER')
    os.makedirs(f'{ROOT}/akuma/og', exist_ok=True)

    def render(h, out):
        shot.set_content(h)
        shot.wait_for_timeout(200)
        shot.screenshot(path=out)

    for k in order:
        d = D[k]
        render(demon_tpl(pg.evaluate('k=>portrait(k)', k), d), f'{ROOT}/akuma/og/{d["id"]}.png')
        folder = f'{ROOT}/akuma/r/{d["id"]}'
        os.makedirs(folder, exist_ok=True)
        open(f'{folder}/index.html', 'w', encoding='utf-8').write(share_page(
            '../../', d['id'], f'私に宿る悪魔は【{d["name"]}】でした|悪魔診断',
            f'{d["title"]}。{d["lead"]} あなたに宿る悪魔は?',
            f'{SITE}/akuma/og/{d["id"]}.png', f'{SITE}/akuma/r/{d["id"]}/'))
    render(intro_tpl([pg.evaluate('k=>portrait(k)', k) for k in ('S', 'L', 'A')]), f'{ROOT}/akuma/og/intro.png')
    b.close()
srv.shutdown()
print('done')
