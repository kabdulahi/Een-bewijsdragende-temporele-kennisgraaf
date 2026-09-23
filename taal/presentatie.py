"""Exporteer geldige lessen en transcripten als zelfstandige offline HTML."""
from dataclasses import asdict
import json
import math
from pathlib import Path

from .model import Document, Woordenboek
from .transcript import TranscriptAnalyse
from .dynamica import CoherenteOscillator


class LesPresentatie:
    def __init__(self, document: Document, begintijd: float = 0,
                 woordenboek: Woordenboek | None = None):
        if not document.geldig:
            raise ValueError("Een ongeldig document kan niet worden gevisualiseerd.")
        if not document.is_transcript and not document.fasen:
            raise ValueError("Visualiseren vereist een expliciete Tijdlijn met lesfasen.")
        duur = int(document.velden["Duur"].split()[0]) * 60
        if not math.isfinite(begintijd) or not 0 <= begintijd <= duur:
            raise ValueError("De begintijd moet eindig zijn en binnen de collegeduur liggen.")
        self.document = document
        self.begintijd = begintijd
        self.woordenboek = woordenboek

    def html(self) -> str:
        document = self.document
        gegevens = {"velden": document.velden,
                    "duur": int(document.velden["Duur"].split()[0]) * 60,
                    "begintijd": self.begintijd,
                    "instructies": [asdict(i) for i in document.instructies],
                    "fasen": [asdict(f) for f in document.fasen]}
        naam = "presentatie"
        if document.is_transcript:
            naam = "transcript"
            analyse = TranscriptAnalyse(document)
            model = CoherenteOscillator.uit_document(document)
            woordenboek = self.woordenboek or Woordenboek(Path(__file__).resolve().parents[1] / "woordenboek.txt")
            gegevens.update({"type": "transcript", "segmenten": analyse.segmenten,
                             "tempo": analyse.tempo, "woorden": analyse.woorden,
                             "spreektijd": analyse.spreektijd, "pauzetijd": analyse.pauzetijd,
                             "model": asdict(model), "symbolisch": model.symbolisch(),
                             "symbolen": woordenboek.symbolen})
        inhoud = json.dumps(gegevens, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        map_pad = Path(__file__).with_name("web")
        sjabloon = (map_pad / f"{naam}.html").read_text(encoding="utf-8")
        cssnaam = "stijl.css" if naam == "presentatie" else "transcript.css"
        return (sjabloon.replace("/*__STIJL__*/", (map_pad / cssnaam).read_text(encoding="utf-8"))
                .replace("/*__SCRIPT__*/", (map_pad / f"{naam}.js").read_text(encoding="utf-8"))
                .replace("__LESGEGEVENS__", inhoud))

    def schrijf(self, uitvoer: Path) -> Path:
        if uitvoer.suffix.lower() != ".html":
            raise ValueError("Gebruik een uitvoerbestand met de extensie .html.")
        if uitvoer.resolve() == self.document.pad.resolve():
            raise ValueError("Het invoerbestand mag niet worden overschreven.")
        inhoud = self.html()
        uitvoer.parent.mkdir(parents=True, exist_ok=True)
        uitvoer.write_text(inhoud, encoding="utf-8")
        return uitvoer.resolve()
