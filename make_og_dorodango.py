# 泥団子ゲームのシェア画像(1200x630)を作る: python3 make_og_dorodango.py
import os, http.server, threading, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
JP = "'Noto Sans CJK JP','Noto Sans CJK SC',sans-serif"
INK = '#2b1d13'

def star(x, y, s, o=1):
    return (f'<div style="position:absolute;left:{x-s}px;top:{y-s}px;width:{s*2}px;height:{s*2}px;background:#fff;opacity:{o};'
            'clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%)"></div>')

HTML = f'''<html><body style="margin:0"><div style="width:1200px;height:630px;position:relative;overflow:hidden;font-family:{JP};color:{INK};
  background:linear-gradient(#bcdde9 0 66%,#e4cc98 66% 83%,#c8a66a 83%)">
  <div style="position:absolute;left:84px;top:96px;display:flex;flex-direction:column;gap:22px">
    <div style="font-weight:900;font-size:32px;letter-spacing:.12em;background:{INK};color:#fffaf0;padding:6px 22px;border-radius:999px;align-self:flex-start">泥団子ゲーム</div>
    <div style="font-weight:900;font-size:108px;line-height:1.12;text-shadow:0 7px 0 #fffaf0">ピカピカ<br>泥団子</div>
    <div style="font-weight:900;font-size:40px;background:#f5c518;border:4px solid {INK};box-shadow:0 6px 0 {INK};padding:10px 28px;border-radius:18px;align-self:flex-start">あなたの泥団子は何点?</div>
  </div>
  <div style="position:absolute;left:703px;top:476px;width:360px;height:54px;border-radius:50%;background:radial-gradient(ellipse,rgba(40,24,10,.55),rgba(40,24,10,0) 70%)"></div>
  <div style="position:absolute;left:670px;top:110px;width:380px;height:380px;border-radius:50%;overflow:hidden;
    background:radial-gradient(circle at 36% 28%,#6a5858,#241a1c 55%,#0b0709)">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(196,230,248,.85) 0,rgba(196,230,248,.35) 36%,rgba(196,230,248,0) 52%)"></div>
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(200,150,95,0) 62%,rgba(200,150,95,.55))"></div>
    <div style="position:absolute;left:62px;top:50px;width:120px;height:70px;border-radius:50%;background:rgba(255,255,255,.95);transform:rotate(-30deg);filter:blur(2px)"></div>
  </div>
  {star(1010,160,34)}{star(640,250,22)}{star(1090,330,16,.9)}{star(700,100,14,.8)}
  <div style="position:absolute;right:48px;bottom:28px;font-weight:900;font-size:28px;letter-spacing:.06em;color:{INK};opacity:.8">#ピカピカ泥団子</div>
</div></body></html>'''

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.set_content(HTML); pg.wait_for_timeout(200)
    os.makedirs(f'{ROOT}/dorodango', exist_ok=True)
    pg.screenshot(path=f'{ROOT}/dorodango/og.png'); b.close()
print('done')
