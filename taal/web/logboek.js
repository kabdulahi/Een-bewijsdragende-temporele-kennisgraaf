"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const data=JSON.parse($("logdata").textContent), records=data.stappen, meta=data.meta;
  let actief=0;
  $("titel").textContent=meta.titel;
  document.title=meta.titel+" · Tijdstaplog";
  $("samenvatting").textContent=meta.aantal+" opgeslagen tijdstappen · "+meta.begin+"–"+meta.einde+" collegeseconden · stap "+meta.stap+" s · "+meta.model;
  $("stap").max=records.length-1;$("stapkeuze").max=records.length;
  function formules(id, items){
    $(id).replaceChildren(...items.map(item=>{
      const vak=document.createElement("section");vak.className="formule";
      const titel=document.createElement("h3");titel.textContent=item.titel;
      const formule=document.createElement("div");formule.innerHTML=item.mathml;
      const details=document.createElement("details"),summary=document.createElement("summary"),pre=document.createElement("pre");
      summary.textContent="LaTeX-bron";pre.textContent=item.latex;details.append(summary,pre);
      vak.append(titel,formule,details);return vak;
    }));
  }
  function toon(index){
    actief=Math.max(0,Math.min(records.length-1,Math.trunc(index)));
    const r=records[actief];
    $("stap").value=actief;$("stapkeuze").value=actief+1;
    $("stapnummer").textContent=(actief+1)+" / "+records.length+" · t = "+r.tijd_exact+" s";
    $("contexttitel").textContent=r.context.nummer+". "+r.context.titel;
    $("contextdetails").textContent=r.context.activiteit+" · college t = "+r.tijd_exact+" s"+("tau" in r.toestand?" · modeltijd τ = "+r.toestand.tau.toFixed(6):"");
    $("visualisatie").innerHTML=r.visualisatie;
    $("visuitleg").textContent=meta.documenttype==="transcript"?
      "Analytische coherente oscillator: 3D-projectie van x, Re ψ en Im ψ naast de kansdichtheid. ℏ = m = ω = 1.":
      "Momentopname van het lesbeeld. Binnen een lesfase blijft deze toestand gelijk; dit is geen gesimuleerde poortdynamica.";
    $("toestand").replaceChildren(...Object.entries(r.toestand).map(([k,v])=>{
      const tr=document.createElement("tr"),th=document.createElement("th"),td=document.createElement("td");
      th.scope="row";th.textContent=k;td.textContent=typeof v==="number"?String(Number(v.toPrecision(12))):v;
      tr.append(th,td);return tr;
    }));
    formules("symbolisch",r.symbolisch);
    $("eerste").disabled=$("vorige").disabled=actief===0;
    $("laatste").disabled=$("volgende").disabled=actief===records.length-1;
  }
  $("stap").addEventListener("input",e=>toon(Number(e.target.value)));
  $("stapkeuze").addEventListener("change",e=>{const n=Number(e.target.value);if(Number.isFinite(n))toon(n-1);});
  $("eerste").addEventListener("click",()=>toon(0));$("laatste").addEventListener("click",()=>toon(records.length-1));
  $("vorige").addEventListener("click",()=>toon(actief-1));$("volgende").addEventListener("click",()=>toon(actief+1));
  $("csv").addEventListener("click",()=>{
    const velden=Array.from(new Set(records.flatMap(r=>Object.keys(r.toestand).filter(k=>typeof r.toestand[k]==="number"))));
    const regels=[["tijd",...velden].join(","),...records.map(r=>[r.tijd,...velden.map(k=>r.toestand[k]??"")].join(","))];
    const url=URL.createObjectURL(new Blob([regels.join("\n")],{type:"text/csv;charset=utf-8"}));
    const a=document.createElement("a");a.href=url;a.download="tijdstappen.csv";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  formules("algemeen",meta.formules);toon(0);
})();
