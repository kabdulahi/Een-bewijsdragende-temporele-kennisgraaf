param([string]$HtmlPad = (Join-Path $PSScriptRoot '../presentaties/quantumdynamica_master.html'))
$ErrorActionPreference = 'Stop'
$testMap = Join-Path $env:TEMP ('ophangen-generator-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testMap | Out-Null
$profile=Join-Path $testMap 'profile'
$browser=Start-Process -FilePath 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',('--user-data-dir="'+$profile+'"'),'about:blank') -WindowStyle Hidden -PassThru
$portFile=Join-Path $profile 'DevToolsActivePort'
for($i=0;$i -lt 50 -and !(Test-Path -LiteralPath $portFile);$i++){Start-Sleep -Milliseconds 200}
$port=[int](Get-Content -LiteralPath $portFile -First 1)
$target=Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?about:blank"
$state=[pscustomobject]@{socket=$target.webSocketDebuggerUrl}
$script:ws = [System.Net.WebSockets.ClientWebSocket]::new()
$script:ws.ConnectAsync([uri](@($state.socket)[0]),[Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null
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
  CDP 'Emulation.setDeviceMetricsOverride' @{width=1600;height=1000;deviceScaleFactor=1;mobile=$false} | Out-Null
  CDP 'Page.navigate' @{url=$uri} | Out-Null
  JS 'new Promise(r=>setTimeout(()=>r(true),500))' | Out-Null
  $checks=JS @'
(async()=>{
 const checks=[], $=id=>document.getElementById(id), data=JSON.parse($("lesgegevens").textContent);
 const assert=(ok,label)=>{if(!ok)throw new Error(label);checks.push(label);};
 const ga=t=>{$("tijd").value=t;$("tijd").dispatchEvent(new Event("input"));};
 assert(document.querySelectorAll("dialog[open]").length===3,"Drie vensters geopend");
 assert($("titel").textContent===data.velden.Titel,"Generator-JavaScript initialiseert zonder syntaxfout");
 assert($("klok").textContent==="00:00 / 60:00","Klok begint gepauzeerd");
 assert(document.querySelector(".nu")?.textContent===data.segmenten[0].alinea[0].split(/\s+/)[0],"Transcriptmarkering actief");
 const startbeeld=$("modelbeeld").toDataURL();
 $("volgende").click();
 assert(Number($("tijd").value)===data.segmenten[1].start,"Volgende gebruikt berekende fragmentgrens");
 $("vorige").click();assert(Number($("tijd").value)===0,"Vorige springt terug");
 ga(900);
 const index=data.segmenten.findIndex(s=>900<s.einde);
 assert($("fragmenttitel").textContent===data.segmenten[index].titel,"Tijdschuif synchroniseert transcript");
 assert($("modelbeeld").toDataURL()!==startbeeld,"Modelvisualisatie verandert met tijd");
 const q=Number(document.querySelector("#meetwaarden dd").textContent);
 assert(Math.abs(q-(1.5*Math.cos(9)))<.0001,"Browsermodel komt overeen met Pythonmodel");
 $("symbool").value="q";$("symbool").dispatchEvent(new Event("change"));
 assert($("symboolwaarde").textContent.includes(q.toFixed(4)),"Symbolische en numerieke toestand gesynchroniseerd");
 for(const mode of ["dichtheid","faseruimte","golf"]){$(mode).click();assert($(mode).getAttribute("aria-pressed")==="true","Weergave "+mode+" werkt");}
 $("snelheid").value=60;$("afspelen").click();await new Promise(r=>setTimeout(r,350));$("afspelen").click();
 const t=Number($("tijd").value);assert(t>900,"Afspelen verplaatst tijd");
 await new Promise(r=>setTimeout(r,150));assert(Number($("tijd").value)===t,"Pauzeren bevriest tijd");
 document.querySelector('[data-sluit="modelvenster"]').click();
 assert(document.querySelectorAll("dialog[open]").length===2,"Venster afzonderlijk sluiten");
 $("alles-open").click();assert(document.querySelectorAll("dialog[open]").length===3,"Drie vensters opnieuw openen");
 assert(Number($("tijd").value)===t,"Heropenen behoudt tijd");
 ga(3600);assert($("status").textContent==="College afgerond"&&$("volgende").disabled,"Eindgrens stopt het college");
 ga(3599);$("afspelen").click();await new Promise(r=>setTimeout(r,200));
 assert($("status").textContent==="College afgerond"&&$("afspelen").textContent==="Afspelen","Automatisch stoppen werkt");
 $("begin").click();
 return checks;
})()
'@
  $checks | ForEach-Object {Write-Output ("OK: "+$_)}
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'desktop.png'),[Convert]::FromBase64String($shot.data))
  CDP 'Emulation.setDeviceMetricsOverride' @{width=390;height=844;deviceScaleFactor=1;mobile=$true} | Out-Null
  JS 'new Promise(r=>setTimeout(()=>r(true),100))' | Out-Null
  $mobile=JS @'
(()=>{
 const voet=document.querySelector(".bediening").getBoundingClientRect();
 if(voet.bottom>innerHeight+1||voet.top<0)throw Error("Bediening valt buiten mobiele viewport");
 if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Horizontale overflow mobiel");
 for(const id of ["begin","vorige","afspelen","volgende"]){
  const r=document.getElementById(id).getBoundingClientRect();
  if(r.right>innerWidth||r.bottom>innerHeight)throw Error("Onbereikbare knop "+id);
 }
 return "Mobiele bediening bereikbaar, zonder horizontale overflow";
})()
'@
  Write-Output ("OK: "+$mobile)
  $shot=CDP 'Page.captureScreenshot' @{format='png'}
  [IO.File]::WriteAllBytes((Join-Path $testMap 'mobile.png'),[Convert]::FromBase64String($shot.data))
  $fouten=@($script:cdpEvents | Where-Object {$_.method -eq 'Runtime.exceptionThrown'})
  if($fouten.Count){throw ($fouten|ConvertTo-Json -Depth 12)}
  Write-Output ("Screenshots: "+$testMap)
} finally {
  try {CDP 'Browser.close' | Out-Null} catch {}
  $script:ws.Dispose()
  # Alleen het door deze test gemaakte, gecontroleerde profiel opruimen.
  Start-Sleep -Milliseconds 250
  $resolvedProfile=[IO.Path]::GetFullPath($profile)
  $resolvedMap=[IO.Path]::GetFullPath($testMap)
  if($resolvedProfile.StartsWith($resolvedMap+[IO.Path]::DirectorySeparatorChar) -and (Test-Path -LiteralPath $resolvedProfile)){
    try {Remove-Item -LiteralPath $resolvedProfile -Recurse -Force -ErrorAction Stop}
    catch {Write-Output ("Tijdelijk browserprofiel nog in gebruik: " + $resolvedProfile)}
  }
}

Write-Output "Browsertest geslaagd."
