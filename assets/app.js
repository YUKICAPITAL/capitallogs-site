(function(){
  var $=function(id){return document.getElementById(id)};
  var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
  var yen=function(n){return n==null?'—':n.toLocaleString('ja-JP')};
  var man=function(n){ // 389388548 -> 3億8,938万
    if(n==null) return '—';
    var oku=Math.floor(n/1e8), m=Math.round((n%1e8)/1e4);
    return (oku?oku+'億':'')+m.toLocaleString('ja-JP')+'万';
  };
  var pct=function(p,sign){ if(p==null) return '—'; var s=(p>0?'+':p<0?'−':'')+Math.abs(p).toFixed(2)+'%'; return s;};
  var cls=function(p){return p<0?'neg':p>0?'pos':''};
  var mono=function(t,c){return '<span class="num '+(c||'')+'">'+esc(t)+'</span>'};
  var nullv=function(v,ph){return v==null?'<span class="num ph">'+esc(ph||'[n]')+'</span>':mono(typeof v==='number'?v.toLocaleString('ja-JP'):v)};

  fetch('data/site.json',{cache:'no-store'}).then(function(r){return r.json()}).then(render).catch(function(e){console.error(e)});

  function render(d){
    // links
    document.querySelectorAll('[data-link]').forEach(function(a){var k=a.getAttribute('data-link'); if(d.links[k]) a.href=d.links[k];});
    $('p-name').textContent=d.profile.name; $('p-tag').textContent=d.profile.tagline;
    var fx=d.media.followers[0], fn=d.media.followers[3];
    if(fx&&fx.count!=null) $('f-x').textContent=fx.count.toLocaleString('ja-JP');
    if(fn&&fn.count!=null) $('f-note').textContent=fn.count.toLocaleString('ja-JP');

    // capital
    var c=d.capital;
    $('c-label').textContent=c.label;
    $('c-diff').textContent='前日比 '+pct(c.diff_pct);
    var narrow=window.innerWidth<720;
    $('c-total').innerHTML=narrow?esc(man(c.total))+'<small>円</small>':esc(yen(c.total))+'<small>円</small>';
    $('c-unreal').textContent=pct(c.unreal_pct);
    $('c-cash').textContent=narrow?man(c.cash):yen(c.cash);
    $('c-trade').textContent=c.trade;
    // chart
    var s=c.series, vals=s.map(function(p){return p.total}), mn=Math.min.apply(null,vals), mx=Math.max.apply(null,vals), rg=(mx-mn)||1;
    var pts=s.map(function(p,i){var x=s.length>1?i/(s.length-1)*100:50; var y=2+(1-(p.total-mn)/rg)*36; return x.toFixed(1)+','+y.toFixed(1)});
    var last=pts[pts.length-1].split(',');
    $('c-chart').innerHTML='<polyline points="'+pts.join(' ')+'" fill="none" stroke="#7FA6C9" stroke-width="2" vector-effect="non-scaling-stroke"/><circle cx="'+last[0]+'" cy="'+last[1]+'" r="1.2" fill="#fff"/>';
    var f=s[0], l=s[s.length-1], dd=l.total-f.total;
    $('c-axis').innerHTML='<span>'+esc(f.date.slice(5).replace('-','.'))+' ｜ '+esc(narrow?man(f.total):yen(f.total))+'</span><span>'+(dd<0?'−':'+')+esc(narrow?man(Math.abs(dd))+'円':yen(Math.abs(dd))+'円')+'</span><span>'+esc(l.date.slice(5).replace('-','.'))+'</span>';
    var cols=['#7FA6C9','#4F7CA3','#A8C0D6','#E6E8EB'];
    $('c-bar').innerHTML=c.alloc.map(function(a,i){return '<div style="width:'+a.pct+'%;background:'+cols[i%cols.length]+'"></div>'}).join('');
    $('c-legend').innerHTML=c.alloc.map(function(a){return '<span>'+esc(a.name)+' '+a.pct.toFixed(1)+'%</span>'}).join('');
    if(d.articles&&d.articles.length){ $('c-newest').hidden=false; $('c-newest-title').textContent=d.articles[0].title; $('c-newest').href='articles/'+d.articles[0].slug+'/'; }

    // conditions
    $('cond-list').innerHTML=d.conditions.map(function(x){return '<div class="row"><div class="t"><b>'+esc(x.title)+'</b><span>'+esc(x.rule)+'</span></div><div class="r">'+(x.now?'<span class="num v">'+esc(x.now)+'</span>':'')+'<span class="chip">'+esc(x.status)+'</span></div></div>'}).join('');
    // holdings
    $('hold-n').textContent=d.holdings.length+'銘柄';
    $('hold-list').innerHTML=d.holdings.map(function(h){return '<div class="row"><span>'+esc(h.name)+'</span>'+mono(h.qty)+'</div>'}).join('');

    // articles
    var A=d.articles||[];
    if(!A.length){
      $('art-grid').innerHTML='<a class="card feature" href="articles/"><div class="img"><span class="chip dark">準備中</span></div><div class="body"><span class="chip" style="align-self:flex-start">記事</span><span class="title">最初の記事を準備している</span><p>インタビュー・実業・資本の設計。ここでしか読めない記事を、これから置いていく。</p></div></a>';
    } else {
      var a0=A[0];
      var feat='<a class="card feature" href="articles/'+esc(a0.slug)+'/"><div class="img" style="'+(a0.image?'background-image:url('+esc(a0.image)+')':'')+'"><span class="chip dark">最新</span></div><div class="body"><span class="chip" style="align-self:flex-start">'+esc(a0.category)+'</span><span class="title">'+esc(a0.title)+'</span><p>'+esc(a0.lead||'')+'</p><span class="muted num" style="font-size:11px">'+esc(a0.date)+'</span><span class="btn-dark" style="margin-top:4px">記事を読む</span></div></a>';
      var rest=A.slice(1,4).map(function(a){return '<a class="card mini" href="articles/'+esc(a.slug)+'/"><div class="img" style="'+(a.image?'background-image:url('+esc(a.image)+')':'')+'"></div><div class="body"><span class="chip" style="align-self:flex-start">'+esc(a.category)+'</span><span class="title">'+esc(a.title)+'</span><span class="muted num" style="font-size:11px">'+esc(a.date)+'</span></div></a>'}).join('');
      $('art-grid').innerHTML=feat+'<div class="minis">'+rest+'</div>';
    }
    var cats=['すべて','インタビュー','実業','資本の設計','対談','家族'];
    $('cats').innerHTML=cats.map(function(x,i){return '<span class="chip '+(i?'ghost':'dark')+'">'+esc(x)+'</span>'}).join('');

    // posts
    var P=d.posts;
    $('posts-sub').textContent=P.count+'本 ｜ '+P.date.slice(5).replace('-','.');
    $('posts-cta').textContent='今日の'+P.count+'本を X で読む ↗';
    $('stories').innerHTML=P.items.map(function(p,i){
      var imp=p.impressions==null?'[インプ]':p.impressions.toLocaleString('ja-JP')+' インプ';
      if(p.image) return '<a class="story img" href="'+esc(p.url)+'"><img class="pic" src="'+esc(p.image)+'" alt=""><div class="body"><span class="chip" style="align-self:flex-start">'+esc(p.kind)+'</span><span class="title" style="font-size:14px">'+esc(p.title)+'</span></div></a>';
      return '<a class="story'+(i===0?' blue':'')+'" href="'+esc(p.url)+'"><span class="chip" style="align-self:flex-start">'+esc(p.kind)+'</span><span class="title">'+esc(p.title)+'</span><span class="meta num">'+esc(imp)+' ・ X で読む ↗</span></a>';
    }).join('');
    $('posts-list').innerHTML=P.items.map(function(p){
      var imp=p.impressions==null?'<span class="num ph" style="font-size:13px">[インプ]</span>':mono(p.impressions.toLocaleString('ja-JP'));
      return '<a class="row" href="'+esc(p.url)+'"><div class="t">'+(p.image?'<img class="thumb" src="'+esc(p.image)+'" alt="">':'')+'<div><div class="meta num">'+esc(p.time)+' ｜ '+esc(p.kind)+'</div><div class="title">'+esc(p.title)+'</div></div></div><div class="r">'+imp+'<span class="chip dark">X で読む ↗</span></div></a>';
    }).join('');

    // note
    $('note-list').innerHTML=d.note.map(function(n){return '<a class="card notecard" href="'+esc(n.url)+'">'+(n.image?'<img class="thumb" src="'+esc(n.image)+'" alt="">':'<div class="thumb"></div>')+'<div class="t"><span class="muted num" style="font-size:11px">'+esc(n.date.replace(/-/g,'.'))+'</span><span class="title">'+esc(n.title)+'</span><span class="read">note で続きを読む ↗</span></div></a>'}).join('');

    // diary
    var D=d.diary; var dc=$('diary-card'); dc.href=D.url||d.links.x_ja;
    dc.innerHTML=(D.image?'<img class="pic" src="'+esc(D.image)+'" alt="">':'')+'<div class="body"><div class="head"><span class="muted num" style="font-size:11px">'+esc(D.date)+'</span>'+(D.place?'<span class="chip">'+esc(D.place)+'</span>':'')+'</div><span class="title">'+esc(D.title)+'</span><p>'+esc(D.text)+'</p></div>';

    // archive
    $('arch-list').innerHTML=d.archive.slice(0,6).map(function(r){
      return '<a class="row" href="archive/#'+esc(r.date)+'"><span class="num d">'+esc(r.label)+'</span><span class="num v">'+(r.total==null?'<span class="muted">休場</span>':esc(yen(r.total)))+'</span><span class="num p '+cls(r.diff_pct)+'">'+(r.diff_pct==null?'':esc(pct(r.diff_pct)))+'</span><span class="m">'+esc(r.memo||'')+'</span></a>';
    }).join('');

    // media
    var M=d.media;
    $('media-upd').textContent=M.updated?'最終更新 '+M.updated:'最終更新 [連携後]';
    $('imp-total').textContent=M.impressions_month==null?'[合計]':M.impressions_month.toLocaleString('ja-JP');
    var bars=M.impressions_daily&&M.impressions_daily.length?M.impressions_daily:[30,55,40,70,50,62,45,80];
    var bmx=Math.max.apply(null,bars)||1;
    $('imp-bars').innerHTML=bars.map(function(v,i){return '<div class="'+(i===bars.length-1?'last':'')+'" style="height:'+(v/bmx*100)+'%"></div>'}).join('');
    $('imp-note').textContent=M.impressions_daily&&M.impressions_daily.length?'日別':'日別。X・note のデータ連携後に実数を表示（形は見本）';
    $('fol-list').innerHTML=M.followers.map(function(f){return '<a class="row" href="'+esc(f.url)+'"><span style="font-size:14px;font-weight:500">'+esc(f.name)+' <span class="muted" style="font-size:12px">'+esc(f.handle)+'</span></span><span class="r">'+nullv(f.count)+'<span class="chip">フォロー</span></span></a>'}).join('');
  }
})();
