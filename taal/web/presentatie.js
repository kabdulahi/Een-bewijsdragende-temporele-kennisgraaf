"use strict";
(() => {
  const data = JSON.parse(document.getElementById("lesgegevens").textContent);
  const el = id => document.getElementById(id);
  const tekst = (id, waarde) => { el(id).textContent = waarde; };
  const fases = data.fasen;
  const klok = s => Math.floor(s / 60).toString().padStart(2, "0") + ":" + Math.floor(s % 60).toString().padStart(2, "0");
  let tijd = data.begintijd || 0, actief = -1, speelt = false, weergave = "model", vorigeFrame = null;
  const canvas = el("beeld"), ctx = canvas.getContext("2d");
  let breedte = 600, hoogte = 290, yaw = -0.45, pitch = 0.23, sleep = null;
  let kader = null;

  tekst("voorblad-titel", data.velden.Titel);
  tekst("les-titel", data.velden.Titel);
  document.title = data.velden.Titel + " · Ophangen";
  tekst("voorblad-doel", data.velden.Leerdoel);
  const meta = data.velden.Vak + " · " + data.velden.Niveau + " · " + data.velden.Duur;
  tekst("voorblad-meta", meta);
  tekst("les-meta", data.velden.Duur + " / " + fases.length + " fasen");
  el("tijd").max = data.duur;
  const faseknoppen = fases.map((fase, index) => {
    const knop = document.createElement("button");
    knop.className = "faseknop";
    const nummer = document.createElement("span"); nummer.className = "nummer"; nummer.textContent = String(index + 1).padStart(2, "0");
    const label = document.createElement("span"); label.textContent = fase.titel;
    const duur = document.createElement("small"); duur.textContent = fase.start + "–" + fase.einde + " min";
    label.append(duur); knop.append(nummer, label);
    knop.addEventListener("click", () => gaNaar(fase.start * 60));
    el("fasen").append(knop);
    return knop;
  });

  function faseBij(seconden) {
    const index = fases.findIndex(f => seconden < f.einde * 60);
    return index < 0 ? fases.length - 1 : index;
  }
  function zetSpeelt(waarde) {
    speelt = waarde;
    vorigeFrame = null;
    tekst("afspelen", speelt ? "Pauzeren" : "Afspelen");
    tekst("status", tijd >= data.duur ? "Les afgerond" : speelt ? "Afspelen" : "Gepauzeerd");
    if (speelt && kader === null) kader = requestAnimationFrame(tik);
  }
  function gaNaar(waarde) {
    zetSpeelt(false);
    tijd = Math.max(0, Math.min(data.duur, waarde));
    ververs();
  }
  function ververs() {
    const index = faseBij(tijd), fase = fases[index];
    if (index !== actief) {
      actief = index;
      tekst("fase-label", "FASE " + String(index + 1).padStart(2, "0") + " / " + String(fases.length).padStart(2, "0"));
      tekst("fase-titel", fase.titel);
      tekst("werkvorm", fase.werkvorm);
      tekst("controle", fase.controle);
      el("toelichting").replaceChildren(...fase.toelichting.map(t => {
        const p = document.createElement("p"); p.textContent = t; return p;
      }));
      el("opdrachten").replaceChildren(...fase.opdrachten.map(n => {
        const opdracht = data.instructies.find(i => i.nummer === n);
        const li = document.createElement("li"); li.value = n; li.textContent = opdracht.tekst; return li;
      }));
      faseknoppen.forEach((knop, i) => {
        if (i === index) knop.setAttribute("aria-current", "step");
        else knop.removeAttribute("aria-current");
      });
      el("docent").open = false;
      document.querySelector(".inhoud").scrollTop = 0;
      beeldInfo();
    }
    tekst("klok", klok(tijd) + " / " + klok(data.duur));
    tekst("voortgang", fase.start + "–" + fase.einde + " MIN · " + Math.round(100 * Math.min(1, (tijd / 60 - fase.start) / (fase.einde - fase.start))) + "%");
    el("tijd").value = Math.floor(tijd);
    el("tijd").setAttribute("aria-valuetext", klok(tijd) + ", " + fase.titel);
    el("vorige").disabled = tijd === 0;
    el("volgende").disabled = tijd >= data.duur;
    tekst("status", tijd >= data.duur ? "Les afgerond" : speelt ? "Afspelen" : "Gepauzeerd");
    teken();
  }
  function kans(label, waarde) {
    const div = document.createElement("div"); div.className = "kans";
    div.textContent = label + "  " + (100 * waarde).toFixed(1).replace(".", ",") + "%";
    const meter = document.createElement("meter"); meter.min = 0; meter.max = 1; meter.value = waarde;
    meter.setAttribute("aria-label", label); div.append(meter); el("kansen").append(div);
  }
  function beeldInfo() {
    const fase = fases[actief];
    el("kansen").replaceChildren();
    let label, uitleg;
    if (weergave === "structuur" || fase.beeld === "samenvatting") {
      label = "Lesfasen in ruimte en tijd";
      uitleg = "De horizontale as is de lestijd. Hoogte en diepte scheiden de fasen voor de leesbaarheid; ze zijn geen meetwaarden. De stip op de as volgt de tijdschuif.";
    } else if (fase.beeld === "bloch") {
      const theta = fase.theta * Math.PI / 180;
      label = "Blochbol · θ = " + fase.theta + "° · φ = " + fase.phi + "°";
      uitleg = "De pijl beschrijft één zuivere qubittoestand: x = sin(θ)cos(φ), y = sin(θ)sin(φ), z = cos(θ). De balken geven kansen bij een Z-meting. De lestijd kiest een voorbeeldtoestand; tussen fasen wordt geen fysieke poortbeweging gesimuleerd.";
      kans("P(0)", Math.cos(theta / 2) ** 2); kans("P(1)", Math.sin(theta / 2) ** 2);
    } else if (fase.beeld === "bell") {
      label = "Bellpaar · (|00⟩ + |11⟩) / √2";
      uitleg = "Beide lokale toestanden liggen in het midden van hun Blochbol: afzonderlijk maximaal gemengd. De bollen zijn geen volledige voorstelling van het verstrengelde paar. De formule en gezamenlijke Z-meetkansen beschrijven de correlatie; er wordt geen signaal overgedragen.";
      kans("P(00)", .5); kans("P(01)", 0); kans("P(10)", 0); kans("P(11)", .5);
    } else {
      label = "Klassieke informatie · 0 of 1";
      uitleg = "Twee verschillende klassieke bitwaarden. De verbindingslijn ordent de mogelijkheden en stelt geen superpositie voor. Via Lesstructuur bekijk je de fasen in 3D.";
    }
    tekst("beeld-tekst", label); tekst("beeld-uitleg", uitleg);
    canvas.setAttribute("aria-label", label + ". " + uitleg);
  }

  // Echte 3D-coordinaten worden geroteerd en met perspectief op canvas geprojecteerd.
  function project(p, schaal = 105, midden = [breedte / 2, hoogte / 2]) {
    const x = Math.cos(yaw) * p[0] + Math.sin(yaw) * p[1];
    const diepte = -Math.sin(yaw) * p[0] + Math.cos(yaw) * p[1];
    const z = Math.cos(pitch) * p[2] - Math.sin(pitch) * diepte;
    const d = Math.sin(pitch) * p[2] + Math.cos(pitch) * diepte;
    const factor = 5 / (5 + d);
    return [midden[0] + x * schaal * factor, midden[1] - z * schaal * factor, d];
  }
  function lijn(punten, kleur, dikte = 1, schaal = 105, midden) {
    ctx.beginPath();
    punten.forEach((p, i) => { const q = project(p, schaal, midden); if (!i) ctx.moveTo(q[0], q[1]); else ctx.lineTo(q[0], q[1]); });
    ctx.strokeStyle = kleur; ctx.lineWidth = dikte; ctx.stroke();
  }
  function punt(p, label, kleur = "#b7ebba", schaal = 105, midden, straal = 5) {
    const q = project(p, schaal, midden);
    ctx.beginPath(); ctx.arc(q[0], q[1], straal, 0, Math.PI * 2);
    ctx.fillStyle = kleur; ctx.fill();
    if (label) { ctx.font = "12px system-ui"; ctx.textAlign = "left"; ctx.fillText(label, q[0] + 10, q[1] - 8); }
  }
  function bol(schaal, midden, gemengd = false) {
    for (let ring = 1; ring < 6; ring++) {
      const theta = Math.PI * ring / 6;
      lijn(Array.from({length: 65}, (_, i) => {
        const phi = i * Math.PI / 32; return [Math.sin(theta) * Math.cos(phi), Math.sin(theta) * Math.sin(phi), Math.cos(theta)];
      }), "#334d5a", 1, schaal, midden);
    }
    for (let ring = 0; ring < 6; ring++) {
      const phi = ring * Math.PI / 6;
      lijn(Array.from({length: 65}, (_, i) => {
        const theta = i * Math.PI / 32; return [Math.sin(theta) * Math.cos(phi), Math.sin(theta) * Math.sin(phi), Math.cos(theta)];
      }), "#334d5a", 1, schaal, midden);
    }
    [[1.25, 0, 0], [0, 1.25, 0], [0, 0, 1.25]].forEach((p, i) => {
      lijn([p.map(v => -v), p], "#58747e", 1, schaal, midden);
      punt(p, ["x", "y", "z · |0⟩"][i], "#9ab4bd", schaal, midden, 2);
    });
    punt([0, 0, -1], "|1⟩", "#9ab4bd", schaal, midden, 2);
    if (gemengd) punt([0, 0, 0], "I / 2", "#edca95", schaal, midden, 7);
  }
  function structuur() {
    const schaal = Math.min(breedte / 7.4, hoogte / 2.8);
    const punten = fases.map((f, i) => [
      -2.6 + 5.2 * ((f.start + f.einde) * 30 / data.duur),
      .62 * Math.sin(i * 1.5), .6 * Math.cos(i * 1.5) + .1
    ]);
    lijn([[-2.8, 0, -1], [2.8, 0, -1]], "#63838b", 1, schaal);
    punt([-2.8, 0, -1], "0 min", "#a8b9bc", schaal, undefined, 2);
    punt([2.8, 0, -1], data.duur / 60 + " min", "#a8b9bc", schaal, undefined, 2);
    lijn(punten, "#58747e", 2, schaal);
    punten.forEach((p, i) => {
      lijn([p, [p[0], 0, -1]], "#2f454f", 1, schaal);
      punt(p, String(i + 1).padStart(2, "0"), i === actief ? "#b7ebba" : i < actief ? "#77959c" : "#547180", schaal, undefined, i === actief ? 9 : 5);
    });
    punt([-2.6 + 5.2 * tijd / data.duur, 0, -1], "", "#b7ebba", schaal, undefined, 6);
  }
  function teken() {
    if (!ctx || !el("les").open) return;
    ctx.clearRect(0, 0, breedte, hoogte);
    const fase = fases[actief];
    if (!fase) return;
    if (weergave === "structuur" || fase.beeld === "samenvatting") { structuur(); return; }
    const schaal = Math.min(hoogte / 2.9, breedte / 4);
    if (fase.beeld === "bloch") {
      bol(schaal, undefined);
      const theta = fase.theta * Math.PI / 180, phi = fase.phi * Math.PI / 180;
      const p = [Math.sin(theta) * Math.cos(phi), Math.sin(theta) * Math.sin(phi), Math.cos(theta)];
      lijn([[0, 0, 0], p], "#b7ebba", 3.5, schaal);
      punt(p, "|ψ⟩", "#b7ebba", schaal, undefined, 7);
    } else if (fase.beeld === "bell") {
      const maat = Math.min(hoogte / 3.7, breedte / 5.8);
      bol(maat, [breedte * .27, hoogte * .47], true);
      bol(maat, [breedte * .72, hoogte * .47], true);
      ctx.font = "13px system-ui"; ctx.textAlign = "center"; ctx.fillStyle = "#edca95";
      ctx.fillText("qubit A", breedte * .27, hoogte - 18); ctx.fillText("qubit B", breedte * .72, hoogte - 18);
    } else {
      lijn([[-1.4, 0, 0], [1.4, 0, 0]], "#45616c", 2, schaal);
      punt([-1.4, 0, 0], "0", "#b7ebba", schaal, undefined, 14);
      punt([1.4, 0, 0], "1", "#edca95", schaal, undefined, 14);
      ctx.font = "14px system-ui"; ctx.textAlign = "center"; ctx.fillStyle = "#a8b9bc";
      ctx.fillText("Twee mogelijke bitwaarden", breedte / 2, hoogte - 30);
    }
  }
  function formaat() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height || !ctx) return;
    breedte = rect.width; hoogte = rect.height;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(breedte * ratio); canvas.height = Math.round(hoogte * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); teken();
  }
  function tik(nu) {
    kader = null;
    if (!speelt || !el("les").open) return;
    if (vorigeFrame !== null) tijd = Math.min(data.duur, tijd + (nu - vorigeFrame) / 1000 * Number(el("snelheid").value));
    vorigeFrame = nu;
    if (tijd >= data.duur) zetSpeelt(false);
    ververs();
    if (speelt) kader = requestAnimationFrame(tik);
  }
  el("afspelen").addEventListener("click", () => { if (tijd >= data.duur) gaNaar(0); zetSpeelt(!speelt); });
  el("tijd").addEventListener("input", event => gaNaar(Number(event.target.value)));
  el("herstart").addEventListener("click", () => gaNaar(0));
  el("vorige").addEventListener("click", () => gaNaar(fases[Math.max(0, actief - 1)].start * 60));
  el("volgende").addEventListener("click", () => gaNaar(actief < fases.length - 1 ? fases[actief + 1].start * 60 : data.duur));
  el("snelheid").addEventListener("change", () => { vorigeFrame = null; });
  for (const naam of ["model", "structuur"]) el(naam).addEventListener("click", () => {
    weergave = naam;
    el("model").setAttribute("aria-pressed", String(naam === "model"));
    el("structuur").setAttribute("aria-pressed", String(naam === "structuur"));
    beeldInfo(); teken();
  });
  el("camera").addEventListener("click", () => { yaw = -.45; pitch = .23; teken(); });
  canvas.addEventListener("pointerdown", e => { sleep = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener("pointermove", e => {
    if (!sleep) return;
    yaw += (e.clientX - sleep[0]) * .008;
    pitch = Math.max(-1.1, Math.min(1.1, pitch + (e.clientY - sleep[1]) * .008));
    sleep = [e.clientX, e.clientY]; teken();
  });
  canvas.addEventListener("pointerup", () => { sleep = null; });
  canvas.addEventListener("pointercancel", () => { sleep = null; });
  el("sluiten").addEventListener("click", () => el("les").close());
  el("les").addEventListener("close", () => { zetSpeelt(false); el("openen").focus(); });
  el("les").addEventListener("cancel", () => zetSpeelt(false));
  el("openen").addEventListener("click", () => { el("les").showModal(); formaat(); el("afspelen").focus(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden) zetSpeelt(false); });
  new ResizeObserver(formaat).observe(canvas);
  ververs();
  el("les").showModal(); formaat(); el("afspelen").focus();
})();
