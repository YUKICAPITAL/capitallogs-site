#!/usr/bin/env python3
"""SEO の土台を data/site.json から機械で作り直す（build.py の最後に自動で呼ばれる。何度実行しても同じ結果）。
- 全ページの head に canonical・hreflang（ja/en/zh/x-default）・og:url・og:locale を入れる（<!--seo--> 〜 <!--/seo--> の間を毎回置き換え）
- 記事ページに構造化データ（JSON-LD の Article）、トップに WebSite と Person
- 記事一覧（3言語）に、記事へのリンクをあらかじめ HTML で書き込む（JavaScript を読まない検索エンジンにも見える）
- sitemap.xml（言語の別ページを xhtml:link で対応づけ）と robots.txt
https を強制したら BASE を https:// に変えるだけでよい。"""
import json, re, html, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://yuki-capital.com'
D = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
LANGS = [('ja', '', 'ja_JP'), ('en', 'en/', 'en_US'), ('zh', 'zh/', 'zh_CN')]
HL = {'ja': 'ja', 'en': 'en', 'zh': 'zh-Hans'}
TODAY = (D.get('updated') or datetime.date.today().isoformat())[:10]
esc = lambda s: html.escape(s or '', quote=True)

def head_block(path_by_lang, lg, extra=''):
    """path_by_lang: {'ja':'articles/x/', ...}。存在する言語だけ渡す"""
    loc = dict((l, o) for l, _, o in LANGS)[lg]
    out = [f'<link rel="canonical" href="{BASE}/{path_by_lang[lg]}">']
    if len(path_by_lang) > 1:
        for l, p in path_by_lang.items():
            out.append(f'<link rel="alternate" hreflang="{HL[l]}" href="{BASE}/{p}">')
        out.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/{path_by_lang.get("ja", path_by_lang[lg])}">')
    out.append(f'<meta property="og:locale" content="{loc}">')
    out.append(f'<meta property="og:site_name" content="YUKI CAPITAL">')
    if extra: out.append(extra)
    return '<!--seo-->\n' + '\n'.join(out) + '\n<!--/seo-->\n'

def patch(fp, block, desc=None, ogurl=None):
    s = fp.read_text(encoding='utf-8')
    s = re.sub(r'<!--seo-->.*?<!--/seo-->\n?', '', s, flags=re.S)
    # 古い hreflang・canonical を外す（重複させない）
    s = re.sub(r'<link rel="(alternate" hreflang="[^"]*"|canonical") href="[^"]*">\n?', '', s)
    if ogurl:
        if '<meta property="og:url"' in s: s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{ogurl}">', s)
        else: block = block.replace('<!--/seo-->', f'<meta property="og:url" content="{ogurl}">\n<!--/seo-->')
    if desc and '<meta name="description"' not in s:
        block = block.replace('<!--seo-->\n', f'<!--seo-->\n<meta name="description" content="{esc(desc)}">\n')
    s = s.replace('</head>', block + '</head>', 1)
    fp.write_text(s, encoding='utf-8')

def L(o, k, lg): return o.get(f'{k}_{lg}') or o.get(k) if lg != 'ja' else o.get(k)

# --- トップ（3言語）
tops = {l: p for l, p, _ in LANGS}
person = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebSite", "name": "YUKI CAPITAL", "url": BASE + '/', "inLanguage": ["ja", "en", "zh-Hans"]},
    {"@type": "Person", "name": "YUKI CAPITAL", "url": BASE + '/', "sameAs": ["https://x.com/capitallogs", "https://x.com/YUKICAPITALen", "https://x.com/YUKICAPITALchin", "https://note.com/capitallogs"]}]}
for lg, p, _ in LANGS:
    fp = ROOT / p / 'index.html'
    s = fp.read_text(encoding='utf-8')
    s = s.replace('http://yuki-capital.com', BASE)   # og:image など（https へ統一）
    fp.write_text(s, encoding='utf-8')
    patch(fp, head_block(tops, lg, '<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False) + '</script>'), ogurl=f'{BASE}/{p}')

# --- 記事一覧（3言語）：説明・リンクの事前書き込み
LIST_DESC = {'ja': '問いを1つ立て、一次資料で検証する記事の一覧。AI・宇宙・量子・金融・実業を、総金融資産を公開している経営者の目線で読む。',
             'en': 'Articles that pose one question and test it against primary sources: AI, space, quantum, finance and business, from a business owner in Japan who publishes his total assets.',
             'zh': '每篇文章提出一个问题，并用一手资料检验。AI、航天、量子、金融与实业，来自在日本公开总资产的经营者。'}
lists = {l: p + 'articles/' for l, p, _ in LANGS}
for lg, p, _ in LANGS:
    fp = ROOT / p / 'articles/index.html'
    up = '../' if lg == 'ja' else '../../'
    cards = ''.join(f'<a class="card notecard" href="{a["slug"]}/">' + (f'<img class="thumb" src="{up}{a["image"]}" alt="" loading="lazy">' if a.get('image') else '<div class="thumb"></div>')
                    + f'<div class="t"><span class="title">{esc(L(a, "title", lg))}</span><span class="muted num" style="font-size:11px">{a["date"]}</span></div></a>' for a in D['articles'])
    s = fp.read_text(encoding='utf-8')
    s = re.sub(r'<div id="list" class="grid">.*?</div></section>', f'<div id="list" class="grid">{cards}</div></section>', s, flags=re.S)
    fp.write_text(s, encoding='utf-8')
    patch(fp, head_block(lists, lg), desc=LIST_DESC[lg], ogurl=f'{BASE}/{lists[lg]}')

# --- 毎日の記録・について（日本語のみ）
for p, desc in [('archive/', '総金融資産と、その日の投稿・売買・記事の1行の記録。毎日更新。'), ('about/', 'YUKI CAPITAL について。飲食店・不動産・シェアオフィスの経営者が、資本の動きと判断を毎日公開している理由。')]:
    patch(ROOT / p / 'index.html', head_block({'ja': p}, 'ja'), desc=desc, ogurl=f'{BASE}/{p}')

# --- 記事ページ（3言語）
urls = []
for a in D['articles']:
    paths = {l: f'{p}articles/{a["slug"]}/' for l, p, _ in LANGS if (ROOT / p / 'articles' / a['slug'] / 'index.html').exists()}
    for lg, path in paths.items():
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": L(a, 'title', lg)[:110],
              "description": (L(a, 'lead', lg) or '')[:200], "datePublished": a['date'], "dateModified": a['date'],
              "inLanguage": HL[lg], "image": [f'https://raw.githubusercontent.com/YUKICAPITAL/capitallogs-site/main/{a["image"]}'] if a.get('image') else [],
              "author": {"@type": "Person", "name": "YUKI CAPITAL", "url": BASE + '/'},
              "publisher": {"@type": "Organization", "name": "YUKI CAPITAL", "logo": {"@type": "ImageObject", "url": BASE + '/images/icon.png'}},
              "mainEntityOfPage": f'{BASE}/{path}', "keywords": [D['tags'][t].get('name' if lg == 'ja' else f'name_{lg}', t) for t in a.get('tags', []) if t in D.get('tags', {})]}
        fp = ROOT / path / 'index.html'
        s = fp.read_text(encoding='utf-8')
        # 説明文は検索結果に収まる長さに（全角120字・英語160字）
        lim = 160 if lg == 'en' else 120
        m = re.search(r'<meta name="description" content="([^"]*)">', s)
        if m and len(html.unescape(m.group(1))) > lim:
            short = html.unescape(m.group(1))[:lim].rstrip() + '…'
            s = s.replace(m.group(0), f'<meta name="description" content="{esc(short)}">')
        fp.write_text(s, encoding='utf-8')
        patch(fp, head_block(paths, lg, '<meta property="article:published_time" content="' + a['date'] + '">\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'), ogurl=f'{BASE}/{path}')
    urls.append((paths, a['date'], '0.8'))

# --- データのページ（tools/enhance.py が作る・毎日更新）
for kind in ('capital', 'rules'):
    paths = {lg: f'{p}numbers/{kind}/' for lg, p, _ in LANGS}
    for lg, p, _ in LANGS:
        fp = ROOT / p / 'numbers' / kind / 'index.html'
        if fp.exists(): patch(fp, head_block(paths, lg), ogurl=f'{BASE}/{paths[lg]}')
    urls.append((paths, TODAY, '0.7'))

# --- sitemap.xml と robots.txt
urls = [(tops, TODAY, '1.0'), (lists, D['articles'][0]['date'], '0.9'), ({'ja': 'archive/'}, TODAY, '0.6'), ({'ja': 'about/'}, '2026-10-20', '0.4')] + urls
x = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for paths, mod, pri in urls:
    for lg, path in paths.items():
        x.append(f'<url><loc>{BASE}/{path}</loc><lastmod>{mod}</lastmod><priority>{pri}</priority>')
        if len(paths) > 1:
            for l2, p2 in paths.items(): x.append(f'  <xhtml:link rel="alternate" hreflang="{HL[l2]}" href="{BASE}/{p2}"/>')
            x.append(f'  <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/{paths.get("ja")}"/>')
        x.append('</url>')
x.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(x) + '\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n', encoding='utf-8')
print('seo: pages', sum(len(p) for p, _, _ in urls), '/ sitemap urls', sum(1 for l in x if l.startswith('<url>')))
