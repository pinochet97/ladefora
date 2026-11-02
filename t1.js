const AG=[{"when": "2026-11-02T20:00:00-03:00", "kind": "story", "files": ["01_seg-02-11/story_1_comecou.jpg"], "text": ""}, {"when": "2026-11-02T20:30:00-03:00", "kind": "feed", "files": ["01_seg-02-11/feed_abertura.jpg"], "text": "Começou a Black Friday da Lá de Fora.\n\nDe hoje até sábado, 07/11, a gente abre encomenda de iPhone, MacBook, iPad, Apple Watch, AirPods, perfume árabe, JBL, Switch 2 e drone DJI. Tudo chega no Brasil na terça, 10/11.\n\nVocê garante com um sinal e paga o resto quando o produto estiver na sua mão.\n\nA lista de preços está na nossa comunidade do WhatsApp. Link na bio.\n\n#blackfriday #importados #iphone #perfumearabe #ladefora"}];
const WS='2395c3d9-e65c-439e-822c-8c89ab82f075', IG='6ca1b917-83ee-417c-8c96-5f84f76a45ea', FB='b7d39359-5574-4516-aee9-3c61ca471d51';
const SB='https://cwaiyzlyotnmpqsznuda.supabase.co', A='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3YWl5emx5b3RubXBxc3pudWRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc4MTQzNjMsImV4cCI6MjA4MzM5MDM2M30.5jH1x7LreanIYoq4G0x28SonXP1jx0eHUQiN2Mrza3s';
const RAW='https://raw.githubusercontent.com/pinochet97/ladefora/af76731a123184dd8fb1241df5fadd864ab13e3a/artes/';
const tk=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>/auth-token/.test(k))));
const H={apikey:A,Authorization:'Bearer '+tk.access_token};
const uid=tk.user.id; const log=[]; window.__fslog=log;
for (const [n,p] of AG.entries()){
  try{
    const assets=[];
    for (const f of p.files){
      const b=await (await fetch(RAW+f)).blob(); if(b.size<5000) throw new Error('imagem nao baixou '+f);
      const path=WS+'/'+Date.now()+'_'+Math.random().toString(36).slice(2,8)+'.jpg';
      const up=await fetch(SB+'/storage/v1/object/social-media/'+path,{method:'POST',headers:{...H,'Content-Type':'image/jpeg','x-upsert':'false'},body:b});
      if(!up.ok) throw new Error('upload '+up.status+' '+(await up.text()));
      assets.push({id:crypto.randomUUID(),url:SB+'/storage/v1/object/public/social-media/'+path,type:'image',name:f.split('/').pop(),size:b.size,path});
    }
    const post={workspace_id:WS,author_id:uid,content:p.text,content_hash:'ldf-bf-'+n+'-'+Date.now(),hashtags:[],assets,status:'pending_approval',scheduled_at:new Date(p.when).toISOString()};
    const r=await fetch(SB+'/rest/v1/posts',{method:'POST',headers:{...H,'Content-Type':'application/json',Prefer:'return=representation'},body:JSON.stringify(post)});
    const j=await r.json(); if(!r.ok) throw new Error('post '+JSON.stringify(j));
    const pid=j[0].id;
    const ch=p.kind==='story'?[{post_id:pid,social_profile_id:IG,provider:'instagram',status:'scheduled',provider_payload:{post_format:'story'}}]:[{post_id:pid,social_profile_id:IG,provider:'instagram',status:'scheduled',provider_payload:null},{post_id:pid,social_profile_id:FB,provider:'facebook',status:'scheduled',provider_payload:null}];
    const rc=await fetch(SB+'/rest/v1/post_channels',{method:'POST',headers:{...H,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify(ch)});
    if(!rc.ok) throw new Error('canais '+(await rc.text()));
    const ra=await fetch(SB+'/rest/v1/approvals',{method:'POST',headers:{...H,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify({post_id:pid,requested_by:uid,status:'pending'})});
    if(!ra.ok) throw new Error('aprovacao '+(await ra.text()));
    log.push([n,p.when,p.kind,'ok',pid]);
  }catch(e){ log.push([n,p.when,p.kind,'ERRO',String(e)]); }
}
window.__fsdone=true; log.length