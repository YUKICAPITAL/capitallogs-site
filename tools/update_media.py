"""Update data/site.json media from collected numbers.
Usage: python3 tools/update_media.py /path/to/media_in.json
media_in.json = {
  "x": {"ja": {"followers":N,"daily":{"YYYY-MM-DD":n},"backfill":{"YYYY-MM-DD":n}}, "en": {...}, "zh": {...}},   # output of tools/x_collect.js
  "note": {"d28":N, "daily":{"YYYY-MM-DD":n}},           # note dashboard (過去28日間) table; optional
  "site": {"visits_24h":N,"pv_24h":N,"pv_7d":N,"pv_30d":N} # Cloudflare Web Analytics; optional
}
Missing parts keep the previous values."""
import json,sys,datetime
S='data/site.json'; d=json.load(open(S)); M=d['media']; inp=json.load(open(sys.argv[1]))
JST=datetime.timezone(datetime.timedelta(hours=9)); now=datetime.datetime.now(JST); stamp=now.strftime('%Y-%m-%d %H:%M')
old=M.get('daily') or {'dates':[]}
def prev(key,dt):
    try: return old[key][old['dates'].index(dt)]
    except Exception: return None
X=inp.get('x') or {}
last=max([k for lg in ('ja','en','zh') if isinstance(X.get(lg),dict) for k in list(X[lg]['daily'])+list(X[lg].get('backfill',{}))] or [old['dates'][-1] if old['dates'] else now.strftime('%Y-%m-%d')])
end=datetime.date.fromisoformat(last); dates=[(end-datetime.timedelta(days=i)).isoformat() for i in range(27,-1,-1)]
daily={'dates':dates}
for lg in ('ja','en','zh'):
    src=X.get(lg); key='x_'+lg
    if isinstance(src,dict):
        mrg=dict(src['daily']); mrg.update({k:v for k,v in src.get('backfill',{}).items() if k not in mrg or k==last})
        daily[key]=[mrg.get(dt, prev(key,dt)) for dt in dates]
    else: daily[key]=[prev(key,dt) for dt in dates]
N=inp.get('note') or {}
daily['note']=[(N.get('daily') or {}).get(dt, prev('note',dt)) for dt in dates]
M['daily']=daily
s7=lambda a:sum(v or 0 for v in a[-7:]); s28=lambda a:sum(v or 0 for v in a)
rows={r['name']:r for r in M['impressions']['rows']}
for name,key in [('X 日本語','x_ja'),('X English','x_en'),('X 中文','x_zh')]:
    if name in rows: rows[name]['d7'],rows[name]['d28']=s7(daily[key]),s28(daily[key])
if 'note' in rows and N:
    rows['note']['d7']=s7(daily['note']); rows['note']['d28']=N.get('d28',s28(daily['note']))
SI=inp.get('site') or {}
if 'サイト' in rows and SI.get('pv_7d') is not None:
    rows['サイト']['d7']=SI['pv_7d']; rows['サイト']['d28']=max(SI['pv_7d'],SI.get('pv_30d') or 0)
R=M['impressions']['rows']; M['impressions']['total_d7']=sum(r['d7'] or 0 for r in R); M['impressions']['total_d28']=sum(r['d28'] or 0 for r in R)
if SI.get('visits_24h') is not None: M['site']={'visits_24h':SI['visits_24h'],'pv_24h':SI.get('pv_24h'),'visits_7d':SI.get('visits_7d')}
for f,lg in zip(M['followers'],('ja','en','zh')):
    if isinstance(X.get(lg),dict): f['count']=X[lg]['followers']
i=-1
td={'date':last,'x_ja':daily['x_ja'][i],'x_en':daily['x_en'][i],'x_zh':daily['x_zh'][i],'note':daily['note'][i],
    'site_visits_24h':M['site'].get('visits_24h'),'site_pv_24h':M['site'].get('pv_24h'),'at':stamp}
M['today']=td
intr=[p for p in M.get('intraday',[]) if p['at'][:10]==stamp[:10]]
intr.append({'at':stamp,'x':(td['x_ja'] or 0)+(td['x_en'] or 0)+(td['x_zh'] or 0),'site_pv_24h':td['site_pv_24h'],'site_visits_24h':td['site_visits_24h']})
M['intraday']=intr[-24:]
M['updated']=stamp
json.dump(d,open(S,'w'),ensure_ascii=False,indent=2)
print('media updated',stamp,'today',td,'totals',M['impressions']['total_d7'],M['impressions']['total_d28'])
