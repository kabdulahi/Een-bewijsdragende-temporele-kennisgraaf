"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const data = JSON.parse($("lesgegevens").textContent);
  const segmenten = data.segmenten, model = data.model;
  let tijd = data.begintijd || 0, speelt = false, actief = -1, vorigFrame = null, frame = null;
  let weergave = "golf", yaw = -.35, pitch = .35, pointer = null;
  let woorden = [], gemarkeerd = -1;
  const klok = t => Math.floor(t/60).toString().padStart(2,"0") + ":" + Math.floor(t%60).toString().padStart(2,"0");
  const fmt = (n, d=4) => Math.abs(n) < 1e-10 ? (0).toFixed(d) : n.toFixed(d);
  const set = (id, s) => { $(id).textContent = s; };
  const indexBij = t => { const i = segmenten.findIndex(s => t < s.einde); return i < 0 ? segmenten.length-1 : i; };
  set("titel", data.velden.Titel); document.title = data.velden.Titel + " · Ophangen";
  set("tempo-uitleg", data.tempo + " woorden/minuut · " + data.woorden + " woorden · " + klok(data.pauzetijd) + " expliciete stilte. Woordmarkering volgt het berekende spreektempo; dit venster speelt geen audio af.");
  set("modeltijd-uitleg", "Modeltijd τ = " + model.modeltempo + " × collegetijd in seconden. τ is dimensieloos. De afspeelsnelheid versnelt beide klokken; de modelkoppeling blijft gelijk.");
  $("tijd").max = data.duur;
  segmenten.forEach((s,i) => { const o = document.createElement("option"); o.value=i; o.textContent=String(i+1).padStart(2,"0")+" · "+s.titel; $("fragment").append(o); });
  const symboolsleutels = Array.from(new Set([...Object.keys(data.symbolisch),...Object.keys(data.symbolen)])).sort();
  symboolsleutels.forEach(s => { const o=document.createElement("option"); o.value=s; o.textContent=s; $("symbool").append(o); });
  $("symbool").value="psi";
  set("ket", data.symbolisch.psi);
  set("psi", data.symbolisch.golffunctie);
  set("operatoren", data.symbolisch.H+"\n"+data.symbolisch.commutator+"\n"+data.symbolisch.U+"\n"+data.symbolisch.rho);

  function toestand() {
    const tau = tijd * model.modeltempo;
    const q = model.q0*Math.cos(tau)+model.p0*Math.sin(tau), p=model.p0*Math.cos(tau)-model.q0*Math.sin(tau);
    return {tau,q,p,energie:(model.q0**2+model.p0**2+1)/2};
  }
  function psi(x,s) {
    const a=Math.PI**(-.25)*Math.exp(-((x-s.q)**2)/2), fase=s.p*(x-s.q/2)-s.tau/2;
    return [a*Math.cos(fase),a*Math.sin(fase)];
  }
  function symbool(s) {
    const sleutel=$("symbool").value;
    set("symboolbetekenis", data.symbolen[sleutel] || "Analytische formule van de coherente oscillator.");
    set("symboolformule", data.symbolisch[sleutel] || "Dit symbool is gedefinieerd in het woordenboek. Het heeft hier geen afzonderlijk berekende toestandswaarde.");
    const v=psi(0,s);
    const waarden={q:"⟨q̂⟩ = "+fmt(s.q),p:"⟨p̂⟩ = "+fmt(s.p),tau:"τ = "+fmt(s.tau),
      alpha:"α = "+fmt(s.q/Math.sqrt(2))+" + i("+fmt(s.p/Math.sqrt(2))+")",
      psi:"ψ(0,τ) = "+fmt(v[0])+" + i("+fmt(v[1])+")",
      golffunctie:"ψ(0,τ) = "+fmt(v[0])+" + i("+fmt(v[1])+")",
      H:"⟨Ĥ⟩ = "+fmt(s.energie),E:"⟨Ĥ⟩ = "+fmt(s.energie),
      rho:"Tr ρ = 1; Tr ρ² = 1 (zuivere toestand)",hbar:"ℏ = 1",m:"m = 1",omega:"ω = 1",
      Deltaq:"Δq = 1/√2",Deltap:"Δp = 1/√2",commutator:"[q̂,p̂] = i I"};
    set("symboolwaarde", waarden[sleutel] || "");
  }
  function inhoud(i) {
    const s=segmenten[i]; actief=i; $("fragment").value=i;
    set("fragmenttitel",s.titel); set("fragmenttijd",klok(s.start)+" – "+klok(s.einde)+" / FRAGMENT "+(i+1));
    woorden=[]; gemarkeerd=-1;
    $("transcripttekst").replaceChildren(...s.alinea.map(alinea => {
      const p=document.createElement("p");
      alinea.split(/\s+/).filter(Boolean).forEach(w => {
        const span=document.createElement("span"); span.textContent=w; woorden.push(span); p.append(span,document.createTextNode(" "));
      });
      return p;
    }));
    $("transcriptvenster").querySelector(".paneelinhoud").scrollTop=0;
    $("fragmentformules").replaceChildren(...s.formules.map(f=>{const pre=document.createElement("pre");pre.className="formule";pre.textContent=f;return pre;}));
    $("fragmentbegrippen").replaceChildren(...s.symbolen.flatMap(sleutel=>{
      const dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=sleutel;dd.textContent=data.symbolen[sleutel]||"";
      return [dt,dd];
    }));
  }
  function ververs() {
    const i=indexBij(tijd); if(i!==actief) inhoud(i);
    const s=segmenten[i], t=toestand();
    set("klok",klok(tijd)+" / "+klok(data.duur)); set("tau","Modeltijd τ = "+fmt(t.tau,3));
    $("tijd").value=tijd; $("tijd").setAttribute("aria-valuetext",klok(tijd)+", "+s.titel);
    $("vorige").disabled=tijd<=0; $("volgende").disabled=tijd>=data.duur;
    const woordindex=tijd<s.spreekeinde ? Math.min(woorden.length-1,Math.floor((tijd-s.start)*data.tempo/60)) : -1;
    if(woordindex!==gemarkeerd){
      if(woorden[gemarkeerd]) woorden[gemarkeerd].classList.remove("nu");
      if(woorden[woordindex]){
        woorden[woordindex].classList.add("nu");
        if(speelt && $("volgtekst").checked && $("transcriptvenster").open){
          const paneel=$("transcriptvenster").querySelector(".paneelinhoud");
          const vak=paneel.getBoundingClientRect(), woord=woorden[woordindex].getBoundingClientRect();
          if(woord.bottom>vak.bottom-40 || woord.top<vak.top+20)
            paneel.scrollTop += woord.top-vak.top-vak.height*.35;
        }
      }
      gemarkeerd=woordindex;
    }
    set("leesstatus",tijd>=data.duur?"Einde van het hoorcollege":tijd>=s.spreekeinde?"Stilte voor de afleiding · nog "+Math.ceil(s.einde-tijd)+" s":"Spreekgedeelte · woord "+(woordindex+1)+" van "+s.woorden);
    set("status",tijd>=data.duur?"College afgerond":speelt?"Afspelen":"Gepauzeerd");
    const entries=[["⟨q̂⟩ / klassieke q",fmt(t.q)],["⟨p̂⟩ / klassieke p",fmt(t.p)],["⟨Ĥ⟩",fmt(t.energie)],["Δq² = Δp²","0,5"],["Δq · Δp","0,5"],["∫ |ψ|² dx","1 (analytisch)"]];
    $("meetwaarden").replaceChildren(...entries.flatMap(([k,v])=>{const dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=k;dd.textContent=v;return[dt,dd];}));
    symbool(t); tekenModel(t); tekenStructuur();
  }
  function speel(waarde) {
    speelt=waarde;vorigFrame=null;set("afspelen",speelt?"Pauzeren":"Afspelen");
    set("status",tijd>=data.duur?"College afgerond":speelt?"Afspelen":"Gepauzeerd");
    if(speelt&&frame===null)frame=requestAnimationFrame(tik);
  }
  function ga(t) {speel(false);tijd=Math.max(0,Math.min(data.duur,t));ververs();}
  function tik(nu) {
    frame=null;if(!speelt)return;
    if(vorigFrame!==null)tijd=Math.min(data.duur,tijd+(nu-vorigFrame)/1000*Number($("snelheid").value));
    vorigFrame=nu;if(tijd>=data.duur)speel(false);
    ververs();if(speelt)frame=requestAnimationFrame(tik);
  }
  function context(id) {
    const canvas=$(id), r=canvas.getBoundingClientRect(), ctx=canvas.getContext("2d");
    if(!r.width||!r.height||!ctx)return null;
    const dpr=Math.min(devicePixelRatio||1,2),w=Math.round(r.width*dpr),h=Math.round(r.height*dpr);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,r.width,r.height);
    return {ctx,w:r.width,h:r.height};
  }
  function project(p,w,h,klein=false) {
    const y=klein?-.25:yaw, a=klein?.4:pitch;
    const x=Math.cos(y)*p[0]+Math.sin(y)*p[1],d=-Math.sin(y)*p[0]+Math.cos(y)*p[1];
    const z=Math.cos(a)*p[2]-Math.sin(a)*d, depth=Math.sin(a)*p[2]+Math.cos(a)*d;
    const scale=Math.min(w/7,h/4.7)*6/(6+depth);
    return [w/2+x*scale,h/2-z*scale];
  }
  function lijn(ctx,punten,kleur,dikte=1) {
    ctx.beginPath();punten.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=kleur;ctx.lineWidth=dikte;ctx.stroke();
  }
  function punt(ctx,p,kleur,r=4,label="") {
    ctx.beginPath();ctx.arc(...p,r,0,2*Math.PI);ctx.fillStyle=kleur;ctx.fill();
    if(label){ctx.font="11px system-ui";ctx.fillText(label,p[0]+7,p[1]-8);}
  }
  function tekenStructuur() {
    const c=context("structuurbeeld");if(!c)return;
    const {ctx,w,h}=c;
    const punten=segmenten.map((s,i)=>project([-2.7+5.4*(s.start+s.einde)/2/data.duur,.5*Math.sin(i),.5*Math.cos(i)],w,h,true));
    lijn(ctx,punten,"#507380",1.5);
    punten.forEach((p,i)=>punt(ctx,p,i===actief?"#b5dec2":"#728d9a",i===actief?6:3,String(i+1)));
    const a=project([-2.7,0,-1.1],w,h,true),b=project([2.7,0,-1.1],w,h,true);
    lijn(ctx,[a,b],"#385563");punt(ctx,[a[0]+(b[0]-a[0])*tijd/data.duur,a[1]+(b[1]-a[1])*tijd/data.duur],"#ebc797",4);
  }
  function tekenModel(s) {
    const c=context("modelbeeld");if(!c)return;
    const {ctx,w,h}=c;const ink="#9aafbc",accent="#b5dec2",gold="#ebc797";
    ctx.font="11px system-ui";
    if(weergave==="golf") {
      [[[ -3,0,0],[3,0,0],"x"],[[0,-1.8,0],[0,1.8,0],"Re ψ"],[[0,0,-1.8],[0,0,1.8],"Im ψ"]].forEach(([a,b,label])=>{
        const end=project(b,w,h);lijn(ctx,[project(a,w,h),end],"#44616e");ctx.fillStyle=ink;ctx.fillText(label,end[0]+5,end[1]-5);
      });
      const punten=Array.from({length:361},(_,i)=>{const x=-9+i*.05,v=psi(x,s);return project([x/3,2*v[0],2*v[1]],w,h);});
      lijn(ctx,punten,accent,2);
      const v=psi(s.q,s);punt(ctx,project([s.q/3,2*v[0],2*v[1]],w,h),gold,5);
      set("modeluitleg","3D-golf: x van −9 tot 9; de andere assen tonen Re ψ en Im ψ. De gouden stip ligt bij het centrum ⟨q̂⟩. De globale fase draait de complexe golf, terwijl |ψ|² daarvan onafhankelijk is.");
    } else if(weergave==="dichtheid") {
      const xy=(x,y)=>[28+(x+9)/18*(w-48),h-28-y*(h-70)/.65];
      lijn(ctx,[xy(-9,0),xy(9,0)],ink);
      const punten=Array.from({length:361},(_,i)=>{const x=-9+i*.05;return xy(x,Math.exp(-((x-s.q)**2))/Math.sqrt(Math.PI));});
      lijn(ctx,punten,accent,2);lijn(ctx,[xy(s.q,0),xy(s.q,.6)],gold);
      ctx.fillStyle=ink;ctx.fillText("|ψ|²",10,18);ctx.fillText("x = −9",26,h-8);ctx.fillText("9",w-23,h-8);
      set("modeluitleg","Kansdichtheid |ψ(x,τ)|² = exp(−(x−q(τ))²)/√π. De verticale lijn volgt het klassieke centrum. De breedte blijft Δq = 1/√2; de totale kans over de volledige reële as is 1.");
    } else {
      const scale=Math.min((w-70)/14,(h-60)/14), xy=(q,p)=>[w/2+q*scale,h/2-p*scale];
      lijn(ctx,[xy(-7,0),xy(7,0)],ink);lijn(ctx,[xy(0,-7),xy(0,7)],ink);
      const radius=Math.hypot(model.q0,model.p0);
      lijn(ctx,Array.from({length:121},(_,i)=>xy(radius*Math.cos(i*Math.PI/60),radius*Math.sin(i*Math.PI/60))),"#6c8490",1);
      [2,1.5,1,.5].forEach((r,i)=>lijn(ctx,Array.from({length:121},(_,j)=>xy(s.q+r*Math.cos(j*Math.PI/60),s.p+r*Math.sin(j*Math.PI/60))),["#365653","#4e7968","#82ae93",accent][i],1.4));
      punt(ctx,xy(s.q,s.p),gold,5);
      ctx.fillStyle=ink;ctx.fillText("q",w-20,h/2-8);ctx.fillText("p",w/2+7,18);
      set("modeluitleg","De gouden stip volgt de klassieke baan (q,p). Groene cirkels zijn contouren van W(x,k;τ)=exp(−(x−q)²−(k−p)²)/π. Alleen voor deze coherente toestand is W overal positief; dit geldt niet voor elke quantumtoestand.");
    }
    $("modelbeeld").setAttribute("aria-label",$("modeluitleg").textContent);
  }
  $("fragment").addEventListener("change",e=>ga(segmenten[Number(e.target.value)].start));
  $("symbool").addEventListener("change",()=>symbool(toestand()));
  $("tijd").addEventListener("input",e=>ga(Number(e.target.value)));
  $("begin").addEventListener("click",()=>ga(0));
  $("vorige").addEventListener("click",()=>ga(segmenten[Math.max(0,actief-1)].start));
  $("volgende").addEventListener("click",()=>ga(actief<segmenten.length-1?segmenten[actief+1].start:data.duur));
  $("afspelen").addEventListener("click",()=>{if(tijd>=data.duur)ga(0);speel(!speelt);});
  $("snelheid").addEventListener("change",()=>{vorigFrame=null;});
  for(const naam of ["golf","dichtheid","faseruimte"])$(naam).addEventListener("click",()=>{
    weergave=naam;for(const n of ["golf","dichtheid","faseruimte"])$(n).setAttribute("aria-pressed",String(n===naam));tekenModel(toestand());
  });
  $("camera").addEventListener("click",()=>{yaw=-.35;pitch=.35;tekenModel(toestand());});
  $("modelbeeld").addEventListener("pointerdown",e=>{pointer=[e.clientX,e.clientY];$("modelbeeld").setPointerCapture(e.pointerId);});
  $("modelbeeld").addEventListener("pointermove",e=>{if(!pointer)return;yaw+=(e.clientX-pointer[0])*.01;pitch=Math.max(-1.1,Math.min(1.1,pitch+(e.clientY-pointer[1])*.01));pointer=[e.clientX,e.clientY];tekenModel(toestand());});
  for(const event of ["pointerup","pointercancel"])$("modelbeeld").addEventListener(event,()=>{pointer=null;});
  for(const knop of document.querySelectorAll("[data-sluit]"))knop.addEventListener("click",()=>{
    $(knop.dataset.sluit).close();speel(false);$("alles-open").focus();
  });
  $("alles-open").addEventListener("click",()=>{
    for(const d of document.querySelectorAll("dialog"))if(!d.open)d.show();
    ververs();$("afspelen").focus();
  });
  document.addEventListener("keydown",e=>{
    if(e.key==="Escape"){speel(false);for(const d of document.querySelectorAll("dialog[open]"))d.close();$("alles-open").focus();}
  });
  document.addEventListener("visibilitychange",()=>{if(document.hidden)speel(false);});
  new ResizeObserver(()=>{tekenModel(toestand());tekenStructuur();}).observe($("modelbeeld"));
  new ResizeObserver(tekenStructuur).observe($("structuurbeeld"));
  ververs();
})();
