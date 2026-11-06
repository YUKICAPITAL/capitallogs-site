#!/usr/bin/env python3
"""build.py から seo.py の前に呼ばれる（何度実行しても同じ結果）。
1. 記事ページの画像に width・height を入れる（読み込み中の画面のずれ＝CLS を防ぐ）
2. 記事ページの末尾に「関連する記事」3本（タグの重なり→新しい順）を入れる（<!--related--> 〜 <!--/related--> を毎回置き換え）
3. データのページ（numbers/capital/・numbers/rules/ の3言語）を data/site.json から作り直す
"""
import json, re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
LANGS = {'ja': '', 'en': 'en/', 'zh': 'zh/'}
esc = lambda s: html.escape(str(s if s is not None else ''), quote=True)
def L(o, k, lg): return (o.get(f'{k}_{lg}') or o.get(k)) if lg != 'ja' else o.get(k)

# ---------- 1. 画像の width・height ----------
try:
    from PIL import Image
except ImportError:
    Image = None
SIZE = {}
def dims(p):
    if p not in SIZE:
        try:
            with Image.open(p) as im: SIZE[p] = im.size
        except Exception: SIZE[p] = None
    return SIZE[p]
def add_dims(fp):
    s = fp.read_text(encoding='utf-8'); n = 0
    def f(m):
        nonlocal n
        tag = m.group(0)
        if ' width=' in tag or 'class="avatar"' in tag or Image is None: return tag
        src = re.search(r'src="([^"]+)"', tag)
        if not src or src.group(1).startswith('http'): return tag
        d = dims((fp.parent / src.group(1)).resolve())
        if not d: return tag
        n += 1
        return tag.replace('<img ', f'<img width="{d[0]}" height="{d[1]}" ', 1)
    s2 = re.sub(r'<img [^>]*>', f, s)
    if s2 != s: fp.write_text(s2, encoding='utf-8')
    return n

# ---------- 2. 関連する記事 ----------
REL = {'ja': '関連する記事', 'en': 'Related articles', 'zh': '相关文章'}
ARTS = D['articles']
def related(a, k=3):
    t = set(a.get('tags') or [])
    c = [b for b in ARTS if b['slug'] != a['slug']]
    c.sort(key=lambda b: (len(t & set(b.get('tags') or [])), b['date']), reverse=True)
    return c[:k]
def put_related(fp, a, lg):
    s = fp.read_text(encoding='utf-8')
    s = re.sub(r'<!--related-->.*?<!--/related-->\n?', '', s, flags=re.S)
    items = ''.join(f'<li><a href="../{b["slug"]}/">{esc(L(b, "title", lg))}</a><span class="num">{b["date"]}</span></li>' for b in related(a))
    blk = f'<!--related--><section class="related"><h2>{REL[lg]}</h2><ul>{items}</ul></section><!--/related-->\n'
    s = s.replace('</article>', blk + '</article>', 1)
    fp.write_text(s, encoding='utf-8')

nimg = 0; nrel = 0
for a in ARTS:
    for lg, pre in LANGS.items():
        fp = ROOT / pre / 'articles' / a['slug'] / 'index.html'
        if not fp.exists(): continue
        nimg += add_dims(fp); put_related(fp, a, lg); nrel += 1

# ---------- 3. データのページ ----------
T = {
 'ja': dict(cap_t='総金融資産の推移と配分（毎日更新）', cap_d='個人投資家 YUKI CAPITAL の総金融資産・前日比・含み益・現金・資産の配分を、証券口座の数字のまま毎日更新している。',
            rule_t='保有銘柄と、決めてある売買の条件（毎日更新）', rule_d='YUKI CAPITAL が持っている銘柄と株数、買い増しや売却の条件と現在地を、毎日更新している。',
            upd='最終更新', total='総金融資産', diff='前日比', unreal='含み益', cash='現金', trade='今日の売買', alloc='配分', series='日々の総金融資産',
            date='日付', asset='資産', amount='金額', share='比率', name='銘柄', qty='数量', cond='条件', rule='決めてある条件', now='現在地', status='状況',
            hold='保有銘柄', other='もう1つのデータ', note='投資の助言ではない。僕自身の記録として公開している。', yen=lambda v: f'{v:,}円'),
 'en': dict(cap_t='Net financial assets and allocation (updated daily)', cap_d="YUKI CAPITAL's net financial assets, daily change, unrealized gains, cash and allocation, updated every day straight from the brokerage account.",
            rule_t='Holdings and the buy/sell rules set in advance (updated daily)', rule_d='What YUKI CAPITAL holds, how many shares, and the rules set in advance for adding or selling, with where each stands today.',
            upd='Updated', total='Net financial assets', diff='Daily change', unreal='Unrealized gain', cash='Cash', trade="Today's trades", alloc='Allocation', series='Net financial assets by day',
            date='Date', asset='Asset', amount='Amount', share='Share', name='Holding', qty='Quantity', cond='Rule', rule='Rule set in advance', now='Now', status='Status',
            hold='Holdings', other='The other data page', note='Not investment advice. I publish this as my own record.', yen=None),
 'zh': dict(cap_t='金融资产总额的走势与配置（每日更新）', cap_d='个人投资者 YUKI CAPITAL 的金融资产总额、日变动、浮盈、现金和资产配置，按证券账户的数字每日更新。',
            rule_t='持仓与事先定好的买卖条件（每日更新）', rule_d='YUKI CAPITAL 的持仓与股数，以及事先定好的加仓、卖出条件和当前所处的位置，每日更新。',
            upd='更新', total='金融资产总额', diff='日变动', unreal='浮盈', cash='现金', trade='今日交易', alloc='配置', series='每日的金融资产总额',
            date='日期', asset='资产', amount='金额', share='比例', name='标的', qty='数量', cond='条件', rule='事先定好的条件', now='当前', status='状态',
            hold='持仓', other='另一页数据', note='不构成投资建议。仅作为我本人的记录公开。', yen=None),
}
def money(v, lg):  # トップと同じく3言語とも円で出す（換算しない）
    return {'ja': f'{v:,}円', 'en': f'¥{v:,}', 'zh': f'{v:,}日元'}[lg]

def chart(series):
    xs = [p['total'] for p in series]
    if len(xs) < 2: return ''
    lo, hi = min(xs), max(xs); pad = (hi - lo) * 0.1 or 1; lo -= pad; hi += pad
    W, H, l, r, t, b = 480, 240, 52, 12, 14, 30
    px = lambda i: l + (W - l - r) * i / (len(xs) - 1); py = lambda v: t + (H - t - b) * (1 - (v - lo) / (hi - lo))
    pts = ' '.join(f'{px(i):.1f},{py(v):.1f}' for i, v in enumerate(xs))
    g = ''.join(f'<line x1="{l}" x2="{W-r}" y1="{py(v):.1f}" y2="{py(v):.1f}" class="gl"/><text x="{l-6}" y="{py(v)+4:.1f}" text-anchor="end">{v/1e8:.2f}</text>' for v in (lo + (hi - lo) * k / 3 for k in range(4)))
    lab = ''.join(f'<text x="{px(i):.1f}" y="{H-12}" text-anchor="middle">{series[i]["date"][5:].replace("-", "/")}</text>' for i in sorted({0, len(xs)//2, len(xs)-1}))
    return (f'<figure class="chart"><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="series">{g}{lab}'
            f'<polyline points="{pts}" class="ln"/><circle cx="{px(len(xs)-1):.1f}" cy="{py(xs[-1]):.1f}" r="4" class="dot"/></svg>'
            f'<figcaption>×1億円（100 million yen）</figcaption></figure>')

def table(head, rows):
    return '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{esc(h)}</th>' for h in head) + '</tr></thead><tbody>' + \
           ''.join('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>'

def page(lg, kind):
    t = T[lg]; c = D['capital']; pre = LANGS[lg]
    tpl = (ROOT / pre / 'articles' / ARTS[0]['slug'] / 'index.html').read_text(encoding='utf-8')
    title, desc = (t['cap_t'], t['cap_d']) if kind == 'capital' else (t['rule_t'], t['rule_d'])
    upd = (D.get('updated') or c['date'])[:10]
    if kind == 'capital':
        sign = lambda v: ('+' if v > 0 else '') + money(v, lg)
        body = table(['', c['date']], [[t['total'], money(c['total'], lg)], [t['diff'], f"{sign(c['diff'])}（{c['diff_pct']:+.2f}%）"], [t['unreal'], f"{sign(c['unreal'])}（{c['unreal_pct']:+.2f}%）"], [t['cash'], f"{money(c['cash'], lg)}（{c['cash_pct']:.2f}%）"], [t['trade'], L(c, 'trade', lg)]])
        body += f'<h2>{t["series"]}</h2>' + chart(c['series'])
        ser = c['series']
        body += table([t['date'], t['amount'], t['diff']], [[p['date'], money(p['total'], lg), ('—' if i == 0 else sign(p['total'] - ser[i-1]['total']))] for i, p in reversed(list(enumerate(ser)))])
        body += f'<h2>{t["alloc"]}</h2>' + table([t['asset'], t['share']], [[L(a, 'name', lg), f"{a['pct']:.2f}%"] for a in c['alloc']])
        other = ('rules', t['rule_t'])
    else:
        body = f'<h2>{t["hold"]}</h2>' + table([t['name'], t['qty']], [[L(h, 'name', lg), L(h, 'qty', lg)] for h in D['holdings']])
        body += f'<h2>{t["rule"]}</h2>' + table([t['cond'], t['rule'], t['now'], t['status']], [[L(x, 'title', lg), L(x, 'rule', lg), L(x, 'now', lg), L(x, 'status', lg)] for x in D['conditions']])
        other = ('capital', t['cap_t'])
    art = (f'<article class="art numbers">\n<div class="meta"><span class="num">{t["upd"]} {upd}</span></div>\n<h1>{esc(title)}</h1>\n'
           f'<div class="lead"><p>{esc(desc)}</p></div>\n<div class="card">\n{body}\n<p class="muted" style="font-size:12px;margin-top:16px">{esc(t["note"])}</p>\n'
           f'<p><a href="../{other[0]}/">{esc(t["other"])}：{esc(other[1])}</a></p>\n</div>\n</article>')
    s = re.sub(r'<article class="art">.*?</article>', lambda m: art, tpl, count=1, flags=re.S)
    s = re.sub(r'<!--seo-->.*?<!--/seo-->\n?', '', s, flags=re.S)
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜YUKI CAPITAL</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="https://raw.githubusercontent.com/YUKICAPITAL/capitallogs-site/main/images/og.png">', s, count=1)
    s = re.sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="https://raw.githubusercontent.com/YUKICAPITAL/capitallogs-site/main/images/og.png">', s, count=1)
    s = s.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
    for code in LANGS:  # 言語の切り替え（記事のテンプレートに入っていれば）
        s = s.replace(f'articles/{ARTS[0]["slug"]}/', f'numbers/{kind}/')
    out = ROOT / pre / 'numbers' / kind / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(s, encoding='utf-8')

for lg in LANGS:
    for kind in ('capital', 'rules'): page(lg, kind)
# ---------- 4. プロフィール（英語・中文。日本語は about/index.html を手で持つ） ----------
AB = {
 'en': ('Profile', "YUKI CAPITAL runs restaurants (as owner), real estate and shared offices, and publishes total financial assets and every buy / don't-buy decision each day.",
        [('Profile and businesses', ["YUKI CAPITAL. I run restaurants (as owner), real estate and shared offices, and publish my total financial assets and my decisions to buy or not to buy every day, as they are. I do not try to call the market. I design the allocation and wait quietly.",
                                     "X carries the daily numbers and decisions (Japanese, English, Chinese). note carries first-hand accounts of my experiences and decisions. This site carries articles that test one question against primary sources, and the numbers from each channel."]),
         ('Privacy', ["This site does not collect personal information from visitors. There are no input forms and no cookie tracking. Links to and resources from outside services (X, note, GitHub, Google Fonts) follow each service's terms."]),
         ('Contact', ['By direct message on X (<a href="https://x.com/YUKICAPITALen">@YUKICAPITALen</a>). I do not give investment advice.'])]),
 'zh': ('简介', 'YUKI CAPITAL 经营餐厅（老板）、不动产和共享办公室，每天公开金融资产总额以及买与不买的判断。',
        [('简介与实业', ['YUKI CAPITAL。我经营餐厅（老板）、不动产和共享办公室，每天原样公开金融资产总额，以及买与不买的判断。我不去猜行情，而是设计好配置，安静地等待。',
                         'X 上每天发布数字和判断（日语、英语、中文），note 上写亲身经历与判断经过的实录，本站放置用一手资料检验一个问题的文章，以及各个平台的数字。']),
         ('隐私', ['本站不收集访问者的个人信息。没有输入栏，也不使用 Cookie 跟踪。指向外部服务（X、note、GitHub、Google Fonts）的链接和加载，遵循各服务的条款。']),
         ('联系方式', ['请通过 X（<a href="https://x.com/YUKICAPITALchin">@YUKICAPITALchin</a>）私信联系。本站不提供投资建议。'])]),
}
for lg, (title, desc, cards) in AB.items():
    tpl = (ROOT / LANGS[lg] / 'articles' / ARTS[0]['slug'] / 'index.html').read_text(encoding='utf-8')
    ids = ['', 'privacy', 'contact']
    body = ''.join(f'<div class="card"{(" id=" + chr(34) + ids[i] + chr(34)) if ids[i] else ""} style="margin-bottom:12px"><h2>{esc(h)}</h2>' + ''.join(f'<p>{p}</p>' for p in ps) + '</div>' for i, (h, ps) in enumerate(cards))
    art = f'<article class="art">\n<h1>{esc(title)}</h1>\n{body}\n</article>'
    s2 = re.sub(r'<article class="art">.*?</article>', lambda m: art, tpl, count=1, flags=re.S)
    s2 = re.sub(r'<!--seo-->.*?<!--/seo-->\n?', '', s2, flags=re.S)
    s2 = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}｜YUKI CAPITAL</title>', s2, count=1)
    s2 = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', s2, count=1)
    s2 = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', s2, count=1)
    s2 = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', s2, count=1)
    s2 = s2.replace(f'articles/{ARTS[0]["slug"]}/', 'about/').replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
    out = ROOT / LANGS[lg] / 'about' / 'index.html'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(s2, encoding='utf-8')

print(f'enhance: 画像の寸法 {nimg}枚／関連する記事 {nrel}ページ／データのページ 6ページ')
