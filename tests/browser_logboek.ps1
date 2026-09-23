param([string]$HtmlPad = (Join-Path $PSScriptRoot '../logs/quantumdynamica_master.html'))
$ErrorActionPreference = 'Stop'
$testMap = Join-Path $env:TEMP ('ophangen-logboek-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testMap | Out-Null
$profile = Join-Path $testMap 'profile'
$browser = Start-Process -FilePath 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',('--user-data-dir="'+$profile+'"'),'about:blank') -WindowStyle Hidden -PassThru
$portFile = Join-Path $profile 'DevToolsActivePort'
for($i=0;$i -lt 50 -and !(Test-Path -LiteralPath $portFile);$i++){Start-Sleep -Milliseconds 200}
$port = [int](Get-Content -LiteralPath $portFile -First 1)
$target = Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?about:blank"
$script:ws = [System.Net.WebSockets.ClientWebSocket]::new()
$script:ws.ConnectAsync([uri]$target.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null
$script:cdpId=0
$script:cdpEvents=[Collections.Generic.List[object]]::new()
function CDP([string]$method,$parameters=@{}) {
  $script:cdpId++
  $message=@{id=$script:cdpId;method=$method;params=$parameters}|ConvertTo-Json -Depth 40 -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($message)
  $cancel=[Threading.CancellationTokenSource]::new(20000)
  try {
    $script:ws.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,$cancel.Token).GetAwaiter().GetResult() | Out-Null
    do {
      $stream=[IO.MemoryStream]::new()
      do {
        $buffer=[byte[]]::new(65536)
        $result=$script:ws.ReceiveAsync([ArraySegment[byte]]::new($buffer),$cancel.Token).GetAwaiter().GetResult()
        $stream.Write($buffer,0,$result.Count)
      } while(!$result.EndOfMessage)
      $json=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json
      $stream.Dispose()
      if($json.method){$script:cdpEvents.Add($json)}
    } while($json.id -ne $script:cdpId)
    if($json.error){throw ($json.error|ConvertTo-Json -Compress)}
    return $json.result
  } finally {$cancel.Dispose()}
}
function JS([string]$code) {
  $r=CDP 'Runtime.evaluate' @{expression=$code;awaitPromise=$true;returnByValue=$true}
  if($r.exceptionDetails){throw ($r.exceptionDetails|ConvertTo-Json -Depth 12 -Compress)}
  return $r.result.value
}
try {
  $htmlBestand=(Resolve-Path -LiteralPath $HtmlPad).ProviderPath
  $uri=[uri]::new($htmlBestand).AbsoluteUri
  CDP 'Runtime.enable' | Out-Null
  CDP 'Page.enable' | Out-Null
  CDP 'Network.enable' | Out-Null
  CDP 'Emulation.setDeviceMetricsOverride' @{width=1600;height=1200;deviceScaleFactor=1;mobile=$false} | Out-Null
  CDP 'Page.navigate' @{url=$uri} | Out-Null
  JS '(async()=>{for(let n=0;n<100;n++){if(document.querySelector("#visualisatie svg"))return true;await new Promise(r=>setTimeout(r,100));}throw Error("Logweergave initialiseert niet binnen tien seconden");})()' | Out-Null
  $checks=JS @'

(async()=>{
 const checks=[], $=id=>document.getElementById(id), data=JSON.parse($("logdata").textContent);
 const assert=(ok,label)=>{if(!ok)throw new Error(label);checks.push(label);};
 const records=data.stappen, meta=data.meta;
 const controleer=(index)=>{
   const r=records[index];
   assert(Number($("stap").value)===index && Number($("stapkeuze").value)===index+1,"Stapindex en nummer: "+index);
   assert($("stapnummer").textContent.includes("t = "+r.tijd_exact+" s"),"Exacte tijd uit logregel "+index);
   assert($("contexttitel").textContent===r.context.nummer+". "+r.context.titel,"Context uit logregel "+index);
   const actual=Object.fromEntries(Array.from($("toestand").rows,tr=>[tr.cells[0].textContent,tr.cells[1].textContent]));
   for(const [k,v] of Object.entries(r.toestand)){
     const expected=typeof v==="number"?String(Number(v.toPrecision(12))):String(v);
     if(actual[k]!==expected)throw Error("Numerieke waarde wijkt af: "+index+" "+k);
   }
   assert(true,"Alle numerieke waarden uit logregel "+index);
   const temp=document.createElement("div");temp.innerHTML=r.visualisatie;
   assert($("visualisatie").firstElementChild.outerHTML===temp.firstElementChild.outerHTML,"Opgeslagen SVG uit logregel "+index);
   assert($("symbolisch").querySelectorAll("math").length===r.symbolisch.length,"MathML-formules uit logregel "+index);
   assert(Array.from($("symbolisch").querySelectorAll("pre")).every((p,i)=>p.textContent===r.symbolisch[i].latex),"LaTeX-bron uit logregel "+index);
   const expectedMath=r.symbolisch.map(f=>{temp.innerHTML=f.mathml;return temp.querySelector("math").outerHTML;});
   assert(Array.from($("symbolisch").querySelectorAll("math")).every((m,i)=>m.outerHTML===expectedMath[i]),"Symbolische toestand uit logregel "+index);
 };
 assert(records.length>1 && meta.aantal===records.length,"Metadata telt alle opgeslagen tijdstappen");
 assert($("titel").textContent===meta.titel,"JavaScript initialiseert de HTML-logweergave");
 assert($("eerste").disabled && $("vorige").disabled,"Begingrens schakelt terugknoppen uit");
 controleer(0);
 const svg=$("visualisatie").querySelector("svg"), rect=svg.getBoundingClientRect();
 assert(rect.width>300 && rect.height>80,"SVG is zichtbaar op desktop");
 const fraction=$("symbolisch").querySelector("mfrac"), power=$("symbolisch").querySelector("msup");
 assert(!!fraction && !!power,"LaTeX is geparseerd als breuk en macht");
 const num=fraction.children[0].getBoundingClientRect(),den=fraction.children[1].getBoundingClientRect();
 assert(num.width>0 && den.width>0 && num.top<den.top && fraction.getBoundingClientRect().height>num.height,"Native MathML plaatst teller boven noemer");
 const base=power.children[0].getBoundingClientRect(),exp=power.children[1].getBoundingClientRect();
 assert(exp.width>0 && exp.top<base.top,"Native MathML plaatst exponent hoger");
 assert($("algemeen").querySelectorAll("math").length===meta.formules.length,"Algemene formules zijn aanwezig");
 const startsvg=svg.outerHTML,startmath=$("symbolisch").querySelector("math").outerHTML;
 $("volgende").click();controleer(1);
 $("vorige").click();controleer(0);
 const midden=Math.floor(records.length/2);
 $("stapkeuze").value=midden+1;$("stapkeuze").dispatchEvent(new Event("change"));controleer(midden);
 $("stap").value=Math.min(midden+1,records.length-1);$("stap").dispatchEvent(new Event("input"));controleer(Number($("stap").value));
 $("laatste").click();controleer(records.length-1);
 assert($("volgende").disabled && $("laatste").disabled,"Eindgrens schakelt vooruitknoppen uit");
 if(meta.documenttype==="transcript" && Number(meta.begin)!==Number(meta.einde)){
   assert($("visualisatie").querySelector("svg").outerHTML!==startsvg,"Oscillatorbeeld verandert tussen opgeslagen tijden");
   assert($("symbolisch").querySelector("math").outerHTML!==startmath,"Symbolische toestand verandert tussen opgeslagen tijden");
 }
 const create=URL.createObjectURL,klik=HTMLAnchorElement.prototype.click;
 let blob,download;
 try{
   URL.createObjectURL=function(value){blob=value;return create.call(this,value);};
   HTMLAnchorElement.prototype.click=function(){download=this.download;};
   $("csv").click();
 }finally{URL.createObjectURL=create;HTMLAnchorElement.prototype.click=klik;}
 assert(blob instanceof Blob && download==="tijdstappen.csv","CSV-knop maakt een lokaal downloadbestand");
 const csv=(await blob.text()).split("\n");
 assert(csv.length===records.length+1 && csv[0].startsWith("tijd,"),"CSV bevat alle tijdstappen en kolomnamen");
 assert(Number(csv[1].split(",")[0])===records[0].tijd && Number(csv.at(-1).split(",")[0])===records.at(-1).tijd,"CSV bewaart begin- en eindtijd");
 assert(!document.querySelector("script[src],link[rel=stylesheet][href],img[src^=http]"),"Geen externe scripts of stijlen nodig");
 assert(performance.getEntriesByType("resource").every(e=>!/^https?:/.test(e.name)),"Geen netwerkassets geladen");
 $("eerste").click();controleer(0);
 return checks;
})()

'@
  $checks | ForEach-Object {Write-Output ("OK: "+$_)}
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'desktop.png'),[Convert]::FromBase64String($shot.data))
  JS '(()=>{const s=document.getElementById("stap");s.value=Math.floor(Number(s.max)/2);s.dispatchEvent(new Event("input"));return true;})()' | Out-Null
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'midden.png'),[Convert]::FromBase64String($shot.data))
  JS 'document.getElementById("eerste").click();true' | Out-Null
  CDP 'Emulation.setDeviceMetricsOverride' @{width=390;height=844;deviceScaleFactor=1;mobile=$true} | Out-Null
  JS 'new Promise(r=>setTimeout(()=>r(true),100))' | Out-Null
  $mobile=JS @'

(()=>{
 const $=id=>document.getElementById(id), width=innerWidth;
 if(document.documentElement.scrollWidth>width+1)throw Error("Horizontale overflow mobiel");
 for(const id of ["eerste","vorige","volgende","laatste","csv","stapkeuze"]){
  const r=$(id).getBoundingClientRect();
  if(r.left<0 || r.right>width+1 || !r.width || !r.height)throw Error("Onbereikbare mobiele bediening: "+id);
 }
 const svg=$("visualisatie").querySelector("svg").getBoundingClientRect();
 if(svg.width<200 || svg.right>width+1)throw Error("Mobiele SVG niet zichtbaar");
 $("laatste").click();
 if(Number($("stap").value)!==Number($("stap").max))throw Error("Mobiele eindknop werkt niet");
 $("eerste").click();
 return "Mobiele bediening werkt en SVG past, zonder horizontale pagina-overflow";
})()

'@
  Write-Output ("OK: "+$mobile)
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'mobile.png'),[Convert]::FromBase64String($shot.data))
  JS 'document.getElementById("symbolisch").scrollIntoView({block:"start"});true' | Out-Null
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'mobile-formules.png'),[Convert]::FromBase64String($shot.data))
  $fouten=@($script:cdpEvents | Where-Object {$_.method -eq 'Runtime.exceptionThrown'})
  if($fouten.Count){throw ($fouten|ConvertTo-Json -Depth 12)}
  $verzoeken=@($script:cdpEvents | Where-Object {$_.method -eq 'Network.requestWillBeSent' -and $_.params.request.url -match '^https?://'})
  if($verzoeken.Count){throw ("Onverwachte netwerkverzoeken: "+($verzoeken|ConvertTo-Json -Depth 8))}
  Write-Output ("Screenshots: "+$testMap)
} finally {
  try {CDP 'Browser.close' | Out-Null} catch {}
  $script:ws.Dispose()
  Start-Sleep -Milliseconds 250
  $resolvedProfile=[IO.Path]::GetFullPath($profile)
  $resolvedMap=[IO.Path]::GetFullPath($testMap)
  if($resolvedProfile.StartsWith($resolvedMap+[IO.Path]::DirectorySeparatorChar) -and (Test-Path -LiteralPath $resolvedProfile)){
    try {Remove-Item -LiteralPath $resolvedProfile -Recurse -Force -ErrorAction Stop}
    catch {Write-Output ("Tijdelijk browserprofiel nog in gebruik: " + $resolvedProfile)}
  }
}
Write-Output "HTML-logboekbrowsertest geslaagd."
