// Run on https://x.com/i/account_analytics (logged in with the 3 accounts). Returns JSON for JA/EN/ZH.
window.__hdrs=window.__hdrs||{};
if(!window.__hk){window.__hk=1;const sh=XMLHttpRequest.prototype.setRequestHeader;XMLHttpRequest.prototype.setRequestHeader=function(k,v){if(!/cookie/i.test(k))window.__hdrs[k]=v;return sh.apply(this,arguments)};}
for(const t of ['2W','7D']){ if(window.__hdrs.authorization) break; const b=[...document.querySelectorAll('main *')].find(e=>e.children.length==0&&e.textContent.trim()===t); b&&b.click(); await new Promise(r=>setTimeout(r,2500)); }
const day=86400000, to=Math.floor(Date.now()/day)*day+day, from=to-29*day;
const v={current_from:from,current_from_iso:new Date(from).toISOString(),current_to:to,current_to_iso:new Date(to).toISOString(),prev_from:from-29*day,prev_from_iso:new Date(from-29*day).toISOString(),prev_to:from,prev_to_iso:new Date(from).toISOString(),backfill_from:to-2*day,backfill_to:to,show_realtime_active_followers:true,show_verified_followers:true};
const base={...window.__hdrs}; ['x-client-transaction-id','Content-Type','x-web-auth-multi-user-id'].forEach(k=>delete base[k]);
const IDS={ja:'2029099094157959168',en:'2076820289531641856',zh:'2077559421815906304'};
const out={at:new Date().toISOString()};
for(const [lg,id] of Object.entries(IDS)){
 const U='/i/api/graphql/2hqAR3h2xhN1cUrUBZypyg/accountOverviewDailyQuery?variables='+encodeURIComponent(JSON.stringify(v));
 let r=await fetch(U,{headers:{...base,'x-web-auth-multi-user-id':id},credentials:'include',cache:'no-store'});
 if(r.status!==200) r=await fetch(U,{headers:base,credentials:'include',cache:'no-store'});
 const res=JSON.parse(await r.text()).data.viewer_v2.user_results.result;
 if(atob(res.id)!=='User:'+id){out[lg]='mismatch';continue;}
 const d={}; res.current_time_series.filter(x=>x.engagement_type==='Displayed').forEach(x=>{const k=new Date(x.timestamp).toISOString().slice(0,10); d[k]=(d[k]||0)+x.count});
 const hb={}; (res.hourly_backfill||[]).filter(x=>x.engagement_type==='Displayed').forEach(x=>{const k=new Date(x.timestamp).toISOString().slice(0,10); hb[k]=(hb[k]||0)+x.count});
 out[lg]={followers:res.relationship_counts.followers,daily:d,backfill:hb};
}
JSON.stringify(out)
