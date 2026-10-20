(function(){
  var LANG=document.documentElement.getAttribute('data-lang')||'ja';
  var T=window.I18N[LANG]||window.I18N.ja;
  var ROOT=document.documentElement.getAttribute('data-root')||'';
  var $=function(id){return document.getElementById(id)};
  var AP=ROOT+(LANG==='ja'?'':LANG+'/')+'articles/';
  var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
  var L=function(o,k){return (LANG!=='ja'&&o[k+'_'+LANG]!=null)?o[k+'_'+LANG]:o[k]};
  var fmt=function(n){return n==null?'—':n.toLocaleString(LANG==='ja'?'ja-JP':'en-US')};
  var man=function(n){ if(n==null) return '—'; var oku=Math.floor(n/1e8), m=Math.round((n%1e8)/1e4); return (oku?oku+'億':'')+m.toLocaleString('ja-JP')+'万';};
  var pct=function(p){ if(p==null) return '—'; return (p>0?'+':p<0?'−':'')+Math.abs(p).toFixed(2)+'%';};
  var cls=function(p){return p<0?'neg':p>0?'pos':''};
  var mono=function(t,c){return '<span class="num '+(c||'')+'">'+esc(t)+'</span>'};
  var nullv=function(v){return v==null?'<span class="num ph">[n]</span>':mono(fmt(v))};
  var narrow=window.innerWidth<720;
  var yenShort=function(n){return LANG==='ja'&&narrow?man(n):fmt(n)};

  // language auto-redirect on the root page (first visit only)
  try{
    if(document.documentElement.getAttribute('data-root-page')==='1'){
      var saved=localStorage.getItem('lang');
      if(!saved){
        var nl=(navigator.language||'').toLowerCase();
        if(nl.indexOf('en')===0){location.replace('en/');return;}
        if(nl.indexOf('zh')===0){location.replace('zh/');return;}
      } else if(saved!=='ja'){ location.replace(saved+'/'); return; }
    }
  }catch(e){}
  document.querySelectorAll('[data-setlang]').forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem('lang',a.getAttribute('data-setlang'))}catch(e){}})});

  // static strings
  document.querySelectorAll('[data-i18n]').forEach(function(el){var k=el.getAttribute('data-i18n'); if(T[k]!=null) el.textContent=T[k];});

  fetch(ROOT+'data/site.json',{cache:'no-store'}).then(function(r){return r.json()}).then(render).catch(function(e){console.error(e)});

  function render(d){
    var xkey=LANG==='en'?'x_en':LANG==='zh'?'x_zh':'x_ja';
    document.querySelectorAll('[data-link]').forEach(function(a){var k=a.getAttribute('data-link'); if(k==='x_main') k=xkey; if(d.links[k]) a.href=d.links[k];});
    var icon=ROOT+(L(d.profile,'icon')||d.profile.icon);
    document.querySelectorAll('img.avatar').forEach(function(i){i.src=icon});
    $('p-name').textContent=d.profile.name; $('p-tag').textContent=L(d.profile,'tagline');
    var fi=LANG==='en'?1:LANG==='zh'?2:0; var fx=d.media.followers[fi], fn=d.media.followers[3];
    if(fx&&fx.count!=null) $('f-x').textContent=fmt(fx.count);
    if(fn&&fn.count!=null) $('f-note').textContent=fmt(fn.count);

    var c=d.capital;
    $('c-label').textContent=L(c,'label');
    $('c-diff').textContent=T.cap_diff+pct(c.diff_pct);
    $('c-total').innerHTML=esc(yenShort(c.total))+'<small>'+esc(T.yen)+'</small>';
    $('c-unreal').textContent=pct(c.unreal_pct);
    $('c-cash').textContent=yenShort(c.cash);
    $('c-trade').textContent=L(c,'trade');
    var s=c.series, vals=s.map(function(p){return p.total}), mn=Math.min.apply(null,vals), mx=Math.max.apply(null,vals), rg=(mx-mn)||1;
    var pts=s.map(function(p,i){var x=s.length>1?i/(s.length-1)*100:50; var y=2+(1-(p.total-mn)/rg)*36; return x.toFixed(1)+','+y.toFixed(1)});
    var last=pts[pts.length-1].split(',');
    $('c-chart').innerHTML='<polyline points="'+pts.join(' ')+'" fill="none" stroke="#7FA6C9" stroke-width="2" vector-effect="non-scaling-stroke"/><circle cx="'+last[0]+'" cy="'+last[1]+'" r="1.2" fill="#fff"/>';
    var f=s[0], l=s[s.length-1], dd=l.total-f.total;
    $('c-axis').innerHTML='<span>'+esc(f.date.slice(5).replace('-','.'))+' ｜ '+esc(yenShort(f.total))+'</span><span>'+(dd<0?'−':'+')+esc(yenShort(Math.abs(dd)))+esc(T.yen)+'</span><span>'+esc(l.date.slice(5).replace('-','.'))+'</span>';
    var cols=['#7FA6C9','#4F7CA3','#A8C0D6','#E6E8EB'];
    $('c-bar').innerHTML=c.alloc.map(function(a,i){return '<div style="width:'+a.pct+'%;background:'+cols[i%cols.length]+'"></div>'}).join('');
    $('c-legend').innerHTML=c.alloc.map(function(a){return '<span>'+esc(L(a,'name'))+' '+a.pct.toFixed(1)+'%</span>'}).join('');
    if(d.articles&&d.articles.length){ var a0=d.articles[0]; $('c-newest').hidden=false; $('c-newest-title').textContent=L(a0,'title'); $('c-newest').href=AP+a0.slug+'/'; }

    $('cond-list').innerHTML=d.conditions.map(function(x){return '<div class="row"><div class="t"><b>'+esc(L(x,'title'))+'</b><span>'+esc(L(x,'rule'))+'</span></div><div class="r">'+(x.now?'<span class="num v">'+esc(L(x,'now'))+'</span>':'')+'<span class="chip">'+esc(L(x,'status'))+'</span></div></div>'}).join('');
    $('hold-n').textContent=d.holdings.length+T.hold_n;
    $('hold-list').innerHTML=d.holdings.map(function(h){return '<div class="row"><span>'+esc(L(h,'name'))+'</span>'+mono(L(h,'qty'))+'</div>'}).join('');

    var A=d.articles||[];
    if(!A.length){
      $('art-grid').innerHTML='<a class="card feature" href="'+ROOT+'articles/"><div class="img"><span class="chip dark">'+esc(T.art_soon)+'</span></div><div class="body"><span class="chip" style="align-self:flex-start">'+esc(T.art_h)+'</span><span class="title">'+esc(T.art_soon_title)+'</span><p>'+esc(T.art_soon_text)+'</p></div></a>';
    } else {
      var a0=A[0];
      var feat='<a class="card feature" href="'+AP+esc(a0.slug)+'/"><div class="img" style="'+(a0.image?'background-image:url('+esc(ROOT+a0.image)+')':'')+'"><span class="chip dark">'+esc(T.art_latest)+'</span></div><div class="body"><span class="chip" style="align-self:flex-start">'+esc(L(a0,'category'))+'</span><span class="title">'+esc(L(a0,'title'))+'</span><p>'+esc(L(a0,'lead')||'')+'</p><span class="muted num" style="font-size:11px">'+esc(a0.date)+'</span><span class="btn-dark" style="margin-top:4px">'+esc(T.art_read)+'</span></div></a>';
      var rest=A.slice(1,4).map(function(a){return '<a class="card mini" href="'+AP+esc(a.slug)+'/"><div class="img" style="'+(a.image?'background-image:url('+esc(ROOT+a.image)+')':'')+'"></div><div class="body"><span class="chip" style="align-self:flex-start">'+esc(L(a,'category'))+'</span><span class="title">'+esc(L(a,'title'))+'</span><span class="muted num" style="font-size:11px">'+esc(a.date)+'</span></div></a>'}).join('');
      $('art-grid').innerHTML=feat+'<div class="minis">'+rest+'</div>';
    }
    $('cats').innerHTML=T.cats.map(function(x,i){return '<span class="chip '+(i?'ghost':'dark')+'">'+esc(x)+'</span>'}).join('');

    var P=d.posts;
    $('posts-sub').textContent=P.count+T.posts_sub+P.date.slice(5).replace('-','.');
    $('posts-cta').textContent=T.posts_cta.replace('{n}',P.count);
    $('stories').innerHTML=P.items.map(function(p,i){
      var url=L(p,'url'); var imp=p.impressions==null?T.posts_imp:fmt(p.impressions);
      if(p.image) return '<a class="story img" href="'+esc(url)+'"><img class="pic" src="'+esc(p.image)+'" alt=""><div class="body"><span class="chip" style="align-self:flex-start">'+esc(L(p,'kind'))+'</span><span class="title" style="font-size:14px">'+esc(L(p,'title'))+'</span></div></a>';
      return '<a class="story'+(i===0?' blue':'')+'" href="'+esc(url)+'"><span class="chip" style="align-self:flex-start">'+esc(L(p,'kind'))+'</span><span class="title">'+esc(L(p,'title'))+'</span><span class="meta num">'+esc(imp)+' ・ '+esc(T.posts_read)+'</span></a>';
    }).join('');
    $('posts-list').innerHTML=P.items.map(function(p){
      var imp=p.impressions==null?'<span class="num ph" style="font-size:13px">'+esc(T.posts_imp)+'</span>':mono(fmt(p.impressions));
      return '<a class="row" href="'+esc(L(p,'url'))+'"><div class="t">'+(p.image?'<img class="thumb" src="'+esc(p.image)+'" alt="">':'')+'<div><div class="meta num">'+esc(p.time)+' ｜ '+esc(L(p,'kind'))+'</div><div class="title">'+esc(L(p,'title'))+'</div></div></div><div class="r">'+imp+'<span class="chip dark">'+esc(T.posts_read)+'</span></div></a>';
    }).join('');

    $('note-list').innerHTML=d.note.map(function(n){return '<a class="card notecard" href="'+esc(n.url)+'">'+(n.image?'<img class="thumb" src="'+esc(n.image)+'" alt="">':'<div class="thumb"></div>')+'<div class="t"><span class="muted num" style="font-size:11px">'+esc(n.date.replace(/-/g,'.'))+(T.note_lang?' ｜ '+esc(T.note_lang):'')+'</span><span class="title">'+esc(n.title)+'</span><span class="read">'+esc(T.note_read)+'</span></div></a>'}).join('');

    var D=d.diary; var dc=$('diary-card'); dc.href=L(D,'url')||d.links[xkey];
    dc.innerHTML=(D.image?'<img class="pic" src="'+esc(D.image)+'" alt="">':'')+'<div class="body"><div class="head"><span class="muted num" style="font-size:11px">'+esc(L(D,'date'))+'</span>'+(D.place?'<span class="chip">'+esc(L(D,'place'))+'</span>':'')+'</div><span class="title">'+esc(L(D,'title'))+'</span><p>'+esc(L(D,'text'))+'</p></div>';

    $('arch-list').innerHTML=d.archive.slice(0,6).map(function(r){
      return '<a class="row" href="'+ROOT+'archive/#'+esc(r.date)+'"><span class="num d">'+esc(L(r,'label'))+'</span><span class="num v">'+(r.total==null?'<span class="muted">'+esc(T.arch_closed)+'</span>':esc(fmt(r.total)))+'</span><span class="num p '+cls(r.diff_pct)+'">'+(r.diff_pct==null?'':esc(pct(r.diff_pct)))+'</span><span class="m">'+esc(L(r,'memo')||'')+'</span></a>';
    }).join('');

    var M=d.media;
    $('media-upd').textContent=M.updated?T.media_upd+M.updated:T.media_upd_na;
    $('imp-total').textContent=M.impressions_month==null?'[—]':fmt(M.impressions_month);
    var bars=M.impressions_daily&&M.impressions_daily.length?M.impressions_daily:[30,55,40,70,50,62,45,80];
    var bmx=Math.max.apply(null,bars)||1;
    $('imp-bars').innerHTML=bars.map(function(v,i){return '<div class="'+(i===bars.length-1?'last':'')+'" style="height:'+(v/bmx*100)+'%"></div>'}).join('');
    $('imp-note').textContent=M.impressions_daily&&M.impressions_daily.length?T.media_imp_daily:T.media_imp_note;
    $('fol-list').innerHTML=M.followers.map(function(f){return '<a class="row" href="'+esc(f.url)+'"><span style="font-size:14px;font-weight:500">'+esc(L(f,'name'))+' <span class="muted" style="font-size:12px">'+esc(f.handle)+'</span></span><span class="r">'+nullv(f.count)+'<span class="chip">'+esc(T.media_follow)+'</span></span></a>'}).join('');
  }
})();
