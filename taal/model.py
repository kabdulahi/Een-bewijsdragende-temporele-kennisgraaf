"""Domeinobjecten en het uitbreidbare instructiewoordenboek."""
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True)
class Melding:
    code: str
    regel: int
    tekst: str


@dataclass(frozen=True)
class Instructie:
    nummer: int
    tekst: str
    regel: int


@dataclass
class Fase:
    """Een aaneengesloten lesonderdeel met een visuele toestand."""

    start: int
    einde: int
    titel: str
    opdrachten: list[int]
    toelichting: list[str]
    werkvorm: str
    controle: str
    beeld: str
    theta: float = 0.0
    phi: float = 0.0
    regel: int = 0


@dataclass
class TranscriptFragment:
    """Een uitgesproken fragment; formules zijn afzonderlijke bordnotities."""

    nummer: int
    titel: str
    alinea: list[str]
    pauze: float
    formules: list[str]
    symbolen: list[str]
    regel: int = 0


@dataclass
class Document:
    pad: Path
    tekst: str
    velden: dict[str, str] = field(default_factory=dict)
    instructies: list[Instructie] = field(default_factory=list)
    meldingen: list[Melding] = field(default_factory=list)
    fasen: list[Fase] = field(default_factory=list)
    fragmenten: list[TranscriptFragment] = field(default_factory=list)

    @property
    def is_transcript(self) -> bool:
        return self.velden.get("Soort") == "transcript"

    @property
    def geldig(self) -> bool:
        return not self.meldingen


class Woordenboek:
    """Een lexicon met opdrachten, begrippen en hoofdlettergevoelige symbolen."""

    def __init__(self, pad: Path):
        self.woorden: dict[str, str] = {}
        self.begrippen: dict[str, str] = {}
        self.symbolen: dict[str, str] = {}
        categorieen = {
            "werkwoord": self.woorden,
            "begrip": self.begrippen,
            "symbool": self.symbolen,
        }
        for nummer, regel in enumerate(pad.read_text(encoding="utf-8-sig").splitlines(), 1):
            regel = regel.strip()
            if not regel or regel.startswith("#"):
                continue
            delen = [deel.strip() for deel in regel.split("|", 2)]
            if len(delen) == 2:
                categorie, woord, betekenis = "werkwoord", *delen
            elif len(delen) == 3 and delen[0] in categorieen:
                categorie, woord, betekenis = delen
            else:
                raise ValueError(
                    f"Ongeldige woordenboekregel {nummer}: verwacht woord | betekenis "
                    "of werkwoord/begrip/symbool | term | betekenis."
                )
            if not woord or not betekenis or (
                categorie == "werkwoord" and not re.fullmatch(r"[^\W\d_]+", woord)
            ) or (categorie == "symbool" and any(teken.isspace() or teken == "," for teken in woord)):
                raise ValueError(f"Ongeldige woordenboekregel {nummer}: ongeldige term of lege betekenis.")
            sleutel = woord if categorie == "symbool" else woord.casefold()
            verzameling = categorieen[categorie]
            if sleutel in verzameling:
                raise ValueError(f"Dubbel woordenboekwoord op regel {nummer}: {sleutel} ({categorie}).")
            verzameling[sleutel] = betekenis
        if not any(categorieen.values()):
            raise ValueError("Het woordenboek is leeg.")
