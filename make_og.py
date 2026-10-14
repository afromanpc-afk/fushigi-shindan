# 使い方: python3 make_og.py https://xxxx.netlify.app
import sys,os,json,html,http.server,threading,functools,re
from playwright.sync_api import sync_playwright
SITE=sys.argv[1].rstrip('/')
ROOT=os.path.dirname(os.path.abspath(__file__))
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT)
class Q(H.func):
    def log_message(self,*a):pass
H=functools.partial(Q,directory=ROOT)
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8766),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
JP="'Noto Sans CJK JP','Noto Sans CJK SC',sans-serif"
SERIF="'Noto Serif CJK JP','Noto Serif CJK SC',serif"

def afro_tpl(svg,t,intro=False):
    sec=t.get('secret')
    bg='#2b1a12' if sec else '#f6c945'; ink='#fff4d6' if sec else '#2b1a12'
    head='あなたはどのタイプのアフロ?' if not intro else '10の質問でわかる'
    name=t['name'] if not intro else 'あなたは<br>どのタイプの<br>アフロ?'
    nick='' if intro else f'<div class="nick" style="background:{t["color"]}">{t["nick"]}</div>'
    catch='性格は髪に出る。8タイプ+激レア隠しタイプ' if intro else t['catch']
    badge='<div class="sec">SECRET TYPE</div>' if sec else ''
    return f'''<html><body style="margin:0"><div style="width:1200px;height:630px;background:{bg};position:relative;overflow:hidden;font-family:{JP};color:{ink};display:flex;align-items:center;gap:56px;padding:0 64px;box-sizing:border-box;
    background-image:repeating-radial-gradient(circle at 20% 120%,transparent 0 40px,rgba(255,91,46,.10) 40px 80px)">
    <div style="flex:none;width:400px;border:6px solid #2b1a12;border-radius:28px;overflow:hidden;box-shadow:12px 12px 0 #2b1a12;line-height:0">{svg}</div>
    <div style="display:flex;flex-direction:column;gap:18px;min-width:0">
      {badge}<div style="font-weight:900;font-size:30px;opacity:.75">{head}</div>
      <div style="font-weight:900;font-size:{78 if intro else 72}px;line-height:1.15;text-shadow:5px 5px 0 #ff5b2e">{name}</div>
      {nick}<div style="font-weight:700;font-size:32px;line-height:1.5">{catch}</div>
      <div style="font-weight:900;font-size:24px;opacity:.7">#アフロ診断 ・ 全10問</div></div>
    <style>.nick{{align-self:flex-start;color:#fff;font-weight:900;font-size:30px;padding:6px 26px;border-radius:999px;border:4px solid #2b1a12}}
    .sec{{align-self:flex-start;background:#ffd447;color:#2b1a12;font-weight:900;font-size:24px;letter-spacing:.3em;padding:4px 16px;border-radius:6px}}</style>
    </div></body></html>'''

def top_tpl():
    return f'''<html><body style="margin:0"><div style="width:1200px;height:630px;background:#f3eee6;font-family:{JP};color:#1f1a24;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box;gap:24px">
    <div style="font-weight:900;font-size:120px;line-height:1.1">ふしぎ診断所</div><div style="font-weight:700;font-size:40px;color:#6d6575">10問で答えがわかる、ちょっと変わった性格診断。</div>
    <div style="display:flex;gap:16px"><span style="background:#f6c945;border:4px solid #1f1a24;border-radius:999px;padding:6px 26px;font-weight:900;font-size:30px">アフロ診断</span></div></div></body></html>'''

def share_page(path_back,key,title,desc,img,url):
    e=html.escape
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">
<script>location.replace("{path_back}#{key}")</script></head>
<body style="font-family:sans-serif;padding:24px"><a href="{path_back}#{key}">結果を見る</a></body></html>'''

def set_head_meta(file,img,url):
    s=open(file).read()
    s=re.sub(r'\n?<meta (property="og:(image|url)[^"]*"|name="twitter:(card|image)")[^>]*>','',s)
    add=f'\n<meta property="og:url" content="{url}">\n<meta property="og:image" content="{img}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{img}">'
    s=s.replace('<meta property="og:type" content="website">','<meta property="og:type" content="website">'+add,1)
    open(file,'w').write(s)

with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); shot=b.new_page(viewport={'width':1200,'height':630})
    def render(h,out):
        shot.set_content(h); shot.wait_for_timeout(150); shot.screenshot(path=out)
    # アフロ
    pg.goto('http://127.0.0.1:8766/afro/'); pg.wait_for_timeout(300)
    T=pg.evaluate('T'); os.makedirs(f'{ROOT}/afro/og',exist_ok=True)
    for k,t in T.items():
        svg=pg.evaluate('k=>afro(k)',k)
        render(afro_tpl(svg,t),f'{ROOT}/afro/og/{k}.png')
        d=f'{ROOT}/afro/r/{k}'; os.makedirs(d,exist_ok=True)
        title=(f'激レア!隠しタイプ【{t["name"]}】' if t.get('secret') else f'私は【{t["name"]}】でした')+'|アフロ診断'
        open(f'{d}/index.html','w').write(share_page('../../',k,title,t['catch']+' あなたはどのタイプのアフロ?',f'{SITE}/afro/og/{k}.png',f'{SITE}/afro/r/{k}/'))
    render(afro_tpl(pg.evaluate('afro("maru")'),T['maru'],True),f'{ROOT}/afro/og/intro.png')
    set_head_meta(f'{ROOT}/afro/index.html',f'{SITE}/afro/og/intro.png',f'{SITE}/afro/')
    render(top_tpl(),f'{ROOT}/og.png')
    set_head_meta(f'{ROOT}/index.html',f'{SITE}/og.png',f'{SITE}/')
    b.close()
srv.shutdown(); print('done')
