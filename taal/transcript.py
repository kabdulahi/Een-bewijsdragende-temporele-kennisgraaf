"""Deterministische spreektijd en cumulatieve tijdlijn van een hoorcollege."""
from math import fsum, isfinite
import re

from .model import Document


class TranscriptAnalyse:
    """Bereken tijd uit whitespacewoorden en expliciete pauzes, zonder TTS.

    Alleen Tekst-alinea's worden uitgesproken. Titels, formules en symboolnamen
    zijn metagegevens en tellen niet mee in het opgegeven spreektempo.
    """

    def __init__(self, document: Document):
        if not document.is_transcript:
            raise ValueError("Een transcriptanalyse vereist Soort: transcript.")
        match = re.fullmatch(r"([0-9]{1,3}) woorden/minuut", document.velden.get("Tempo", ""))
        if not match or not 50 <= int(match[1]) <= 220:
            raise ValueError("Tempo moet 50 tot en met 220 woorden/minuut zijn.")
        if not document.fragmenten:
            raise ValueError("Een transcript moet minimaal een fragment bevatten.")
        try:
            eindige_pauzetijd = fsum(fragment.pauze for fragment in document.fragmenten)
        except OverflowError as fout:
            raise ValueError("De totale pauzetijd moet eindig zijn.") from fout
        if not isfinite(eindige_pauzetijd):
            raise ValueError("De totale pauzetijd moet eindig zijn.")
        self.document = document
        self.tempo = float(match[1])
        self.woorden = 0
        self.segmenten: list[dict] = []
        pauzes: list[float] = []
        for fragment in document.fragmenten:
            if not isfinite(fragment.pauze) or fragment.pauze < 0:
                raise ValueError("Elk fragment vereist een eindige, niet-negatieve Pauze.")
            aantal = len(" ".join(fragment.alinea).split())
            begin = self.woorden * 60.0 / self.tempo + fsum(pauzes)
            self.woorden += aantal
            spreekeinde = self.woorden * 60.0 / self.tempo + fsum(pauzes)
            pauzes.append(fragment.pauze)
            einde = self.woorden * 60.0 / self.tempo + fsum(pauzes)
            self.segmenten.append({
                "nummer": fragment.nummer,
                "titel": fragment.titel,
                "alinea": list(fragment.alinea),
                "formules": list(fragment.formules),
                "symbolen": list(fragment.symbolen),
                "start": begin,
                "einde": einde,
                "spreekeinde": spreekeinde,
                "pauze": fragment.pauze,
                "woorden": aantal,
            })
        self.spreektijd = self.woorden * 60.0 / self.tempo
        self.pauzetijd = fsum(pauzes)
        self.duur = self.spreektijd + self.pauzetijd
