#!/usr/bin/env python3
"""index.html（日本語・正本）から en/index.html と zh/index.html を作る。
使い方: python3 build.py  （push の前に毎回実行する）"""
import re, os, pathlib
ROOT = pathlib.Path(__file__).parent
src = (ROOT / 'index.html').read_text(encoding='utf-8')
assert not any(m in src for m in ('<<<<<<<','>>>>>>>')), 'index.html に衝突の印が残っている'
import json, datetime as _dt
_notes = json.loads((ROOT / 'data' / 'site.json').read_text(encoding='utf-8'))['note']
assert all(n.get('image') for n in _notes), 'note の画像が空の行がある：' + ','.join(n['date'] for n in _notes if not n.get('image')) + '（note の API の eyecatch を入れてから build する｜対策252）'
_m = json.loads((ROOT / 'data' / 'site.json').read_text(encoding='utf-8'))['media']
_now = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))
_upd = _dt.datetime.strptime(_m['updated'], '%Y-%m-%d %H:%M').replace(tzinfo=_now.tzinfo)
assert (_now - _upd) <= _dt.timedelta(hours=12), f"media の数字が古い（最終更新 {_m['updated']}）。tools/x_collect.js と update_media.py で取り直してから build する（対策249）"
import time
ver = time.strftime('%Y%m%d%H%M')
src = re.sub(r'\?v=(VER|\d+)', '?v=' + ver, src)
(ROOT / 'index.html').write_text(src, encoding='utf-8')
META = {
    'en': dict(lang='en', title='YUKI CAPITAL｜Capital Logs',
               desc='A Tokyo business owner publishes his total financial assets and every buy/no-buy decision, daily, as they are. X, note and the articles on this site, all from here.',
               og_title='YUKI CAPITAL｜Capital Logs', og_desc='Total financial assets and every decision, published daily.'),
    'zh': dict(lang='zh-Hans', title='YUKI CAPITAL｜资本记录',
               desc='在东京经营实业的投资者，每天原原本本公开总金融资产与买或不买的判断。X、note 与本站文章，从这里出发。',
               og_title='YUKI CAPITAL｜资本记录', og_desc='总金融资产与每一次判断，每天公开。'),
}
for code, m in META.items():
    t = src
    t = t.replace('<html lang="ja" data-lang="ja" data-root="" data-root-page="1">',
                  f'<html lang="{m["lang"]}" data-lang="{code}" data-root="../">')
    t = re.sub(r'<title>.*?</title>', f'<title>{m["title"]}</title>', t, count=1)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{m["desc"]}">', t, count=1)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{m["og_title"]}">', t, count=1)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{m["og_desc"]}">', t, count=1)
    t = t.replace('<meta property="og:url" content="https://yuki-capital.com/">', f'<meta property="og:url" content="https://yuki-capital.com/{code}/">')
    # relative paths one level up
    t = re.sub(r'(href|src)="(assets|images|data|articles|archive)/', r'\1="../\2/', t)
    t = t.replace('href="favicon.ico"', 'href="../favicon.ico"')
    # language switch
    t = t.replace('<a href="./" data-setlang="ja" class="on">日本語</a><a href="en/" data-setlang="en">EN</a><a href="zh/" data-setlang="zh">中文</a>',
                  '<a href="../" data-setlang="ja"%s>日本語</a><a href="../en/" data-setlang="en"%s>EN</a><a href="../zh/" data-setlang="zh"%s>中文</a>' % (
                      '', ' class="on"' if code == 'en' else '', ' class="on"' if code == 'zh' else ''))
    out = ROOT / code / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(t, encoding='utf-8')
    print('wrote', out)
# SEO（canonical・hreflang・構造化データ・記事一覧の事前書き込み・sitemap.xml・robots.txt）
import subprocess, sys
subprocess.run([sys.executable, str(ROOT / 'tools' / 'enhance.py')], check=True)  # 画像の寸法・関連する記事・データのページ
subprocess.run([sys.executable, str(ROOT / 'tools' / 'seo.py')], check=True)
