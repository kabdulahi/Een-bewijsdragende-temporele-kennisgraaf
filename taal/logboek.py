"""Reproduceerbaar HTML-log met opgeslagen toestanden, SVG en geparseerde LaTeX."""
from bisect import bisect_right
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import json
import math
from pathlib import Path

from .dynamica import CoherenteOscillator
from .model import Document
from .transcript import TranscriptAnalyse
from .logbeelden import LogBeelden


class LatexWeergave:
    """LaTeX wordt bij generatie MathML; de browser hoeft niets te downloaden."""

    @staticmethod
    @lru_cache(maxsize=512)
    def parse(bron: str) -> str:
        try:
            from latex2mathml.converter import convert
        except ImportError as exc:
            raise ValueError("LaTeX-renderer ontbreekt. Voer eerst ./setup.sh uit.") from exc
        return convert(bron, display="block")

    @classmethod
    def formule(cls, titel: str, bron: str) -> dict:
        return {"titel": titel, "latex": bron, "mathml": cls.parse(bron)}


def _getal(waarde: float) -> str:
    return f"{waarde:.6f}".rstrip("0").rstrip(".") if abs(waarde) >= 0.0000005 else "0"


class TijdstapLog:
    MAX_STAPPEN = 10001

    def __init__(self, document: Document, stap=1, begin=0, einde=None):
        if not document.geldig:
            raise ValueError("Een log vereist een geldig document.")
        if not document.is_transcript and not document.fasen:
            raise ValueError("Een log vereist een transcript of een expliciete Tijdlijn.")
        self.document = document
        self.duur = int(document.velden["Duur"].split()[0]) * 60
        try:
            self.stap = Decimal(str(stap))
            self.begin = Decimal(str(begin))
            self.einde = Decimal(str(self.duur if einde is None else einde))
        except InvalidOperation as exc:
            raise ValueError("Tijden en stap moeten geldige decimale getallen zijn.") from exc
        if not all(v.is_finite() for v in (self.stap, self.begin, self.einde)):
            raise ValueError("Tijden en stap moeten eindig zijn.")
        if self.stap <= 0 or not 0 <= self.begin <= self.einde <= self.duur:
            raise ValueError("Gebruik een positieve stap en 0 <= begin <= einde <= collegeduur.")
        if (self.einde - self.begin) / self.stap > self.MAX_STAPPEN - 1:
            raise ValueError(f"Maximaal {self.MAX_STAPPEN} logregels; kies een grotere --stap of kleiner tijdvak.")
        self.tijden = [self.begin + i * self.stap for i in range(int((self.einde-self.begin)//self.stap)+1)]
        if self.tijden[-1] != self.einde:
            self.tijden.append(self.einde)
        if len(self.tijden) > self.MAX_STAPPEN:
            raise ValueError(f"Maximaal {self.MAX_STAPPEN} logregels; kies een grotere --stap.")
        self.model = CoherenteOscillator.uit_document(document) if document.is_transcript else None
        if self.model:
            self.segmenten = TranscriptAnalyse(document).segmenten
        else:
            self.segmenten = [{"start": f.start*60, "einde": f.einde*60, "titel": f.titel}
                             for f in document.fasen]
        self.grenzen = [s["start"] for s in self.segmenten]

    def _segment(self, tijd):
        return min(bisect_right(self.grenzen, tijd)-1, len(self.segmenten)-1)

    def gemeenschappelijke_formules(self):
        if self.model:
            return [
                LatexWeergave.formule("Toestandsvector", r"\left|\psi(\tau)\right\rangle=e^{-i\tau/2}\left|\alpha_0e^{-i\tau}\right\rangle"),
                LatexWeergave.formule("Golffunctie", r"\psi(x,\tau)=\pi^{-1/4}\exp\left[-\frac{(x-q(\tau))^2}{2}+i\left(p(\tau)\left(x-\frac{q(\tau)}{2}\right)-\frac{\tau}{2}\right)\right]"),
                LatexWeergave.formule("Hamiltoniaan en dichtheidsoperator", r"\hat H=\frac{\hat p^2+\hat q^2}{2},\quad \rho(\tau)=|\psi(\tau)\rangle\langle\psi(\tau)|,\quad \hbar=m=\omega=1"),
            ]
        return [LatexWeergave.formule("Zuivere qubit op de Blochbol",
                    r"|\psi\rangle=\cos\frac{\theta}{2}|0\rangle+e^{i\phi}\sin\frac{\theta}{2}|1\rangle")]

    def record(self, index: int) -> dict:
        tijd = float(self.tijden[index])
        i = self._segment(tijd)
        segment = self.segmenten[i]
        context = {"nummer": i+1, "titel": segment["titel"]}
        if self.model:
            staat = self.model.toestand(tijd)
            waarde = self.model.golffunctie(0, tijd)
            staat.update({"psi_x0_re": waarde.real, "psi_x0_im": waarde.imag})
            context["activiteit"] = ("afgerond" if tijd >= self.duur else
                                     "stilte" if tijd >= segment["spreekeinde"] else "spreekgedeelte")
            tau, q, p = (_getal(staat[k]) for k in ("tau", "q", "p"))
            ar, ai = _getal(staat["alpha_re"]), _getal(staat["alpha_im"])
            symbolisch = [
                LatexWeergave.formule("Toestand op deze tijdstap",
                    rf"\tau\simeq {tau},\quad |\psi(\tau)\rangle\simeq e^{{-i({tau})/2}}|({ar})+i({ai})\rangle"),
                LatexWeergave.formule("Golffunctie met ingevulde modelwaarden",
                    rf"\psi(x,{tau})\simeq\pi^{{-1/4}}\exp\left[-\frac{{(x-({q}))^2}}{{2}}+i\left(({p})\left(x-\frac{{{q}}}{{2}}\right)-\frac{{{tau}}}{{2}}\right)\right]"),
            ]
            svg = LogBeelden.oscillator(self.model, tijd)
        else:
            fase = self.document.fasen[i]
            context["activiteit"] = "afgerond" if tijd >= self.duur else "statische lesfase"
            staat = {"beeld": fase.beeld, "collegetijd": tijd}
            if fase.beeld == "bloch":
                theta, phi = math.radians(fase.theta), math.radians(fase.phi)
                a = math.cos(theta/2)
                br, bi = math.sin(theta/2)*math.cos(phi), math.sin(theta/2)*math.sin(phi)
                staat.update({"theta_graden": fase.theta, "phi_graden": fase.phi,
                              "x": math.sin(theta)*math.cos(phi), "y": math.sin(theta)*math.sin(phi),
                              "z": math.cos(theta), "amplitude_0": a, "amplitude_1_re": br,
                              "amplitude_1_im": bi, "P0": a*a, "P1": br*br+bi*bi})
                symbolisch = [LatexWeergave.formule("Zuivere qubittoestand",
                        rf"|\psi\rangle\simeq({_getal(a)})|0\rangle+\left(({_getal(br)})+i({_getal(bi)})\right)|1\rangle")]
            elif fase.beeld == "bell":
                staat.update({"P00": .5, "P01": 0, "P10": 0, "P11": .5,
                              "lokale_blochlengte": 0})
                symbolisch = [LatexWeergave.formule("Gezamenlijke en lokale toestand",
                            r"|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt{2}},\quad \rho_A=\rho_B=\frac{I}{2}")]
            else:
                staat["toelichting"] = ("Geen specifieke quantumtoestand: klassieke bitwaarden."
                                        if fase.beeld == "klassiek" else "Geen specifieke quantumtoestand: lesoverzicht.")
                symbolisch = [LatexWeergave.formule("Domein van het lesbeeld",
                              r"b\in\{0,1\}" if fase.beeld == "klassiek" else r"\mathrm{Lesoverzicht}")]
            svg = LogBeelden.lesfase(fase)
        return {"index": index, "tijd": tijd, "tijd_exact": str(self.tijden[index]),
                "context": context, "toestand": staat, "visualisatie": svg, "symbolisch": symbolisch}

    def metadata(self):
        return {"titel": self.document.velden["Titel"], "bron": str(self.document.pad),
                "documenttype": "transcript" if self.model else "les",
                "stap": str(self.stap), "begin": str(self.begin), "einde": str(self.einde),
                "aantal": len(self.tijden), "formules": self.gemeenschappelijke_formules(),
                "model": "coherente harmonische oscillator" if self.model else "statische lesbeelden"}

    @staticmethod
    def _json(waarde):
        return json.dumps(waarde, ensure_ascii=False, allow_nan=False, separators=(",", ":")).replace(
            "<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    def schrijf(self, uitvoer: Path) -> Path:
        if uitvoer.suffix.lower() != ".html":
            raise ValueError("Het logbestand moet de extensie .html hebben.")
        if uitvoer.resolve() == self.document.pad.resolve():
            raise ValueError("Het invoerbestand mag niet worden overschreven.")
        web = Path(__file__).with_name("web")
        template = (web/"logboek.html").read_text(encoding="utf-8")
        template = template.replace("/*__STIJL__*/", (web/"logboek.css").read_text(encoding="utf-8"))
        template = template.replace("/*__SCRIPT__*/", (web/"logboek.js").read_text(encoding="utf-8"))
        vooraf, achteraf = template.split("__LOGDATA__")
        meta = self.metadata()  # Controleer LaTeX-dependency voordat er iets wordt geschreven.
        eerste = self.record(0)
        uitvoer.parent.mkdir(parents=True, exist_ok=True)
        # Een tijdelijke sibling voorkomt een halfgeschreven bestaand log bij een fout.
        import os
        import tempfile
        tijdelijk = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=uitvoer.parent,
                                             prefix=".log-", suffix=".tmp", delete=False) as handle:
                tijdelijk = Path(handle.name)
                handle.write(vooraf)
                handle.write('{"meta":'+self._json(meta)+',"stappen":[')
                handle.write(self._json(eerste))
                for index in range(1, len(self.tijden)):
                    handle.write(","+self._json(self.record(index)))
                handle.write("]}")
                handle.write(achteraf)
            os.replace(tijdelijk, uitvoer)
        finally:
            if tijdelijk is not None:
                tijdelijk.unlink(missing_ok=True)
        return uitvoer.resolve()
