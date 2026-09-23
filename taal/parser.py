"""Regelgebaseerde grammatica zonder uitvoering van invoertekst."""
from collections import Counter
from math import isfinite
from pathlib import Path
import re
from .model import Document, Fase, Instructie, Melding, TranscriptFragment, Woordenboek
from .transcript import TranscriptAnalyse


class DocumentParser:
    VELDEN = ("Titel", "Vak", "Niveau", "Onderwerp", "Leerdoel", "Duur")
    TRANSCRIPTVELDEN = ("Soort", "Tempo", "Model", "Beginpositie", "Beginimpuls", "Modeltempo")
    FRAGMENTVELDEN = ("Tekst", "Formule", "Symbolen", "Pauze")
    FASEVELDEN = ("Opdrachten", "Toelichting", "Werkvorm", "Controle", "Beeld")

    def parse(self, pad: Path) -> Document:
        document = Document(pad, pad.read_text(encoding="utf-8-sig"))
        sectie = "velden"
        gezien: set[str] = set()
        fase: Fase | None = None
        fasevelden: set[str] = set()
        fragment: TranscriptFragment | None = None
        fragmentvelden: set[str] = set()
        for nummer, origineel in enumerate(document.tekst.splitlines(), 1):
            regel = origineel.strip()
            if not regel or regel.startswith("#"):
                continue
            if sectie == "einde":
                document.meldingen.append(Melding("E007", nummer, "Tekst na Einde. is niet toegestaan."))
                continue
            if regel == "Transcript:":
                if sectie != "velden" or "transcript" in gezien:
                    document.meldingen.append(Melding("E013", nummer, "Transcript: mag eenmaal voorkomen, direct na de velden."))
                    continue
                sectie = "transcript"
                gezien.add("transcript")
                continue
            if regel == "Instructies:":
                if document.is_transcript or "transcript" in gezien:
                    document.meldingen.append(Melding("E013", nummer, "Een transcript mag geen sectie Instructies: bevatten."))
                    continue
                if sectie != "velden":
                    document.meldingen.append(Melding("E002", nummer, "Dubbele of verkeerd geplaatste sectie Instructies."))
                    continue
                sectie = "instructies"
                gezien.add("instructies")
                continue
            if regel == "Tijdlijn:":
                if document.is_transcript or "transcript" in gezien:
                    document.meldingen.append(Melding("E013", nummer, "Een transcript krijgt zijn tijdlijn uit Tempo, Tekst en Pauze."))
                    continue
                if sectie != "instructies" or "tijdlijn" in gezien:
                    document.meldingen.append(Melding("E008", nummer, "Tijdlijn: mag eenmaal voorkomen, na de instructies."))
                    continue
                sectie = "tijdlijn"
                gezien.add("tijdlijn")
                continue
            if regel == "Einde.":
                sectie = "einde"
                gezien.add("einde")
                continue
            if sectie == "velden":
                sleutel, scheiding, waarde = regel.partition(":")
                if not scheiding or sleutel not in self.VELDEN + self.TRANSCRIPTVELDEN:
                    document.meldingen.append(Melding("E001", nummer, "Onbekend veld; verwacht Veld: waarde."))
                elif sleutel in document.velden:
                    document.meldingen.append(Melding("E002", nummer, f"Dubbel veld: {sleutel}."))
                else:
                    document.velden[sleutel] = waarde.strip()
            elif sectie == "transcript":
                sleutel, scheiding, waarde = regel.partition(":")
                waarde = waarde.strip()
                if sleutel == "Fragment" and scheiding:
                    match = re.fullmatch(r"([0-9]{1,6})\s*\|\s*(.*)", waarde)
                    fragment = None
                    fragmentvelden = set()
                    if not match:
                        document.meldingen.append(Melding("E014", nummer, "Verwacht Fragment: 1 | Titel."))
                    else:
                        fragment = TranscriptFragment(int(match[1]), match[2].strip(), [], float("nan"), [], [], nummer)
                        document.fragmenten.append(fragment)
                elif not scheiding or sleutel not in self.FRAGMENTVELDEN:
                    document.meldingen.append(Melding("E014", nummer, "Onbekend transcriptveld; verwacht Fragment, Tekst, Formule, Symbolen of Pauze."))
                elif fragment is None:
                    document.meldingen.append(Melding("E014", nummer, "Een transcriptveld moet na een geldig Fragment: staan."))
                elif sleutel in fragmentvelden and sleutel not in {"Tekst", "Formule"}:
                    document.meldingen.append(Melding("E002", nummer, f"Dubbel fragmentveld: {sleutel}."))
                else:
                    fragmentvelden.add(sleutel)
                    self._lees_fragmentveld(document, fragment, sleutel, waarde, nummer)
            elif sectie == "instructies":
                match = re.fullmatch(r"([0-9]{1,6})\.\s+(.+)", regel)
                if not match:
                    document.meldingen.append(Melding("E003", nummer, "Verwacht een genummerde instructie: 1. Lees de tekst."))
                else:
                    document.instructies.append(Instructie(int(match[1]), match[2], nummer))
            else:
                sleutel, scheiding, waarde = regel.partition(":")
                waarde = waarde.strip()
                if sleutel == "Fase" and scheiding:
                    match = re.fullmatch(r"([0-9]{1,6})-([0-9]{1,6})\s*\|\s*(.*)", waarde)
                    fase = None
                    fasevelden = set()
                    if not match:
                        document.meldingen.append(Melding("E009", nummer, "Verwacht Fase: 0-5 | Titel, met gehele minuten."))
                    else:
                        fase = Fase(int(match[1]), int(match[2]), match[3].strip(), [], [], "", "", "", regel=nummer)
                        document.fasen.append(fase)
                elif not scheiding or sleutel not in self.FASEVELDEN:
                    document.meldingen.append(Melding("E010", nummer, "Onbekend tijdlijnveld; verwacht Fase, Opdrachten, Toelichting, Werkvorm, Controle of Beeld."))
                elif fase is None:
                    document.meldingen.append(Melding("E010", nummer, "Een tijdlijnveld moet na een geldige Fase: staan."))
                elif sleutel in fasevelden and sleutel != "Toelichting":
                    document.meldingen.append(Melding("E002", nummer, f"Dubbel faseveld: {sleutel}."))
                else:
                    fasevelden.add(sleutel)
                    self._lees_faseveld(document, fase, sleutel, waarde, nummer)
        if "transcript" in gezien and not document.is_transcript:
            document.meldingen.append(Melding("E013", 0, "De sectie Transcript: vereist Soort: transcript."))
        for sectienaam in (("transcript", "einde") if document.is_transcript else ("instructies", "einde")):
            if sectienaam not in gezien:
                document.meldingen.append(Melding("E004", 0, f"Ontbrekende sectie: {sectienaam}."))
        if "tijdlijn" in gezien and not document.fasen:
            document.meldingen.append(Melding("E012", 0, "De sectie Tijdlijn: moet minimaal een fase bevatten."))
        return document

    @staticmethod
    def _lees_fragmentveld(document: Document, fragment: TranscriptFragment, sleutel: str, waarde: str, regel: int) -> None:
        if sleutel == "Tekst":
            fragment.alinea.append(waarde)
        elif sleutel == "Formule":
            fragment.formules.append(waarde)
        elif sleutel == "Symbolen":
            fragment.symbolen = [deel.strip() for deel in waarde.split(",")]
        elif sleutel == "Pauze":
            match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?) seconden", waarde)
            if not match:
                document.meldingen.append(Melding("E014", regel, "Verwacht Pauze: 20 seconden, eventueel met een decimale punt."))
            else:
                fragment.pauze = float(match[1])

    @staticmethod
    def _lees_faseveld(document: Document, fase: Fase, sleutel: str, waarde: str, regel: int) -> None:
        if sleutel == "Opdrachten":
            if not re.fullmatch(r"[0-9]{1,6}(?:\s*,\s*[0-9]{1,6})*", waarde):
                document.meldingen.append(Melding("E011", regel, "Opdrachten verwacht instructienummers, bijvoorbeeld 1, 2."))
            else:
                fase.opdrachten = [int(deel.strip()) for deel in waarde.split(",")]
        elif sleutel == "Toelichting":
            fase.toelichting.append(waarde)
        elif sleutel == "Werkvorm":
            fase.werkvorm = waarde
        elif sleutel == "Controle":
            fase.controle = waarde
        elif sleutel == "Beeld":
            delen = [deel.strip() for deel in waarde.split("|")]
            fase.beeld = delen[0]
            if fase.beeld == "bloch":
                try:
                    if len(delen) != 3:
                        raise ValueError
                    fase.theta, fase.phi = float(delen[1]), float(delen[2])
                except ValueError:
                    document.meldingen.append(Melding("E011", regel, "Verwacht Beeld: bloch | theta | phi, met hoeken in graden."))
            elif len(delen) != 1:
                document.meldingen.append(Melding("E011", regel, "Alleen het beeld bloch gebruikt de twee hoekwaarden."))


class DocumentValidator:
    def __init__(self, woordenboek: Woordenboek):
        self.woordenboek = woordenboek

    def valideer(self, document: Document) -> Document:
        # Alleen validatiemeldingen vervangen: herhaald valideren is idempotent.
        document.meldingen[:] = [m for m in document.meldingen if not m.code.startswith(("V", "T"))]

        def fout(code: str, tekst: str, regel: int = 0) -> None:
            document.meldingen.append(Melding(code, regel, tekst))

        for veld in DocumentParser.VELDEN:
            if document.is_transcript and veld == "Leerdoel":
                continue
            if not document.velden.get(veld):
                fout("V001", f"Verplicht veld ontbreekt of is leeg: {veld}.")
        if document.velden.get("Vak") not in {"Nederlands", "Engels", "Wiskunde B", "Natuurkunde", "Informatica"}:
            fout("V002", "Vak moet Nederlands, Engels, Wiskunde B, Natuurkunde of Informatica zijn.")
        if document.velden.get("Niveau") not in {"4 vwo", "wo master"}:
            fout("V003", "Niveau moet 4 vwo of wo master zijn.")
        duur = document.velden.get("Duur", "")
        geldige_duur = re.fullmatch(r"(?:[1-9]|[1-9][0-9]|[1-3][0-9]{2}|4[0-7][0-9]|480) minuten", duur)
        if not geldige_duur:
            fout("V004", "Duur moet 1 tot en met 480 minuten zijn, bijvoorbeeld 50 minuten.")
        if document.is_transcript:
            self._valideer_transcript(document, int(duur.split()[0]) if geldige_duur else None)
            return document
        if any(veld in document.velden for veld in DocumentParser.TRANSCRIPTVELDEN):
            fout("T001", "Transcriptvelden vereisen Soort: transcript.")
        if not document.instructies:
            fout("V005", "Er is minimaal een instructie vereist.")
        nummers = {opdracht.nummer for opdracht in document.instructies}
        for verwacht, opdracht in enumerate(document.instructies, 1):
            if opdracht.nummer != verwacht:
                fout("V006", f"Verwacht instructienummer {verwacht}, gevonden {opdracht.nummer}.", opdracht.regel)
            match = re.match(r"([^\W\d_]+)\s+\S", opdracht.tekst)
            if not match or match[1].casefold() not in self.woordenboek.woorden:
                fout("V007", "Begin met een werkwoord uit het woordenboek, gevolgd door een opdracht.", opdracht.regel)
            if not opdracht.tekst[0].isupper():
                fout("V008", "Begin de instructie met een hoofdletter.", opdracht.regel)
            if not opdracht.tekst.rstrip('\"\u201d\u2019\u00bb\u0027').endswith((".", "?", "!")):
                fout("V009", "Sluit de instructie af met een punt, vraagteken of uitroepteken.", opdracht.regel)
            for verwijzing in re.finditer(r"\[([^\]]*)\]", opdracht.tekst):
                doel = verwijzing[1]
                if not re.fullmatch(r"[0-9]{1,6}", doel) or int(doel) not in nummers or int(doel) >= opdracht.nummer:
                    fout("V010", f"Verwijzing [{doel}] moet een eerdere bestaande instructie aanwijzen.", opdracht.regel)
            zonder_verwijzingen = re.sub(r"\[[^\]]*\]", "", opdracht.tekst)
            if "[" in zonder_verwijzingen or "]" in zonder_verwijzingen:
                fout("V010", "Onvolledige verwijzing; gebruik [nummer].", opdracht.regel)
        if document.fasen:
            self._valideer_fasen(document, int(duur.split()[0]) if geldige_duur else None)
        return document

    def _valideer_transcript(self, document: Document, duur: int | None) -> None:
        def fout(code: str, tekst: str, regel: int = 0) -> None:
            document.meldingen.append(Melding(code, regel, tekst))

        for veld in DocumentParser.TRANSCRIPTVELDEN:
            if not document.velden.get(veld):
                fout("T001", f"Verplicht transcriptveld ontbreekt of is leeg: {veld}.")
        tempo = re.fullmatch(r"([0-9]{1,3}) woorden/minuut", document.velden.get("Tempo", ""))
        geldig_tempo = bool(tempo and 50 <= int(tempo[1]) <= 220)
        if not geldig_tempo:
            fout("T002", "Tempo moet een geheel getal van 50 tot en met 220 woorden/minuut zijn.")
        if document.velden.get("Model") != "harmonische_oscillator":
            fout("T007", "Model moet harmonische_oscillator zijn.")
        for veld in ("Beginpositie", "Beginimpuls", "Modeltempo"):
            try:
                waarde = float(document.velden.get(veld, ""))
                geldig = isfinite(waarde) and ((0 < waarde <= 1) if veld == "Modeltempo" else (-4 <= waarde <= 4))
            except ValueError:
                geldig = False
            if not geldig:
                bereik = "groter dan 0 en maximaal 1" if veld == "Modeltempo" else "van -4 tot en met 4"
                fout("T007", f"{veld} moet een eindig getal {bereik} zijn.")
        if document.instructies or document.fasen:
            fout("T001", "Een transcript bevat fragmenten, zonder instructies of handmatige tijdlijn.")
        if not document.fragmenten:
            fout("T003", "Een transcript vereist minimaal een fragment.")
        geldige_pauzes = True
        for verwacht, fragment in enumerate(document.fragmenten, 1):
            if fragment.nummer != verwacht:
                fout("T003", f"Verwacht fragmentnummer {verwacht}, gevonden {fragment.nummer}.", fragment.regel)
            if not fragment.titel or not fragment.alinea or not all(tekst.strip() for tekst in fragment.alinea):
                fout("T003", "Elk fragment vereist een titel en minimaal een niet-lege Tekst-alinea.", fragment.regel)
            if not isfinite(fragment.pauze) or fragment.pauze < 0:
                geldige_pauzes = False
                fout("T004", "Elk fragment vereist een expliciete, eindige, niet-negatieve Pauze in seconden.", fragment.regel)
            if any(not formule.strip() for formule in fragment.formules):
                fout("T003", "Een Formule mag niet leeg zijn.", fragment.regel)
            if len(fragment.symbolen) != len(set(fragment.symbolen)):
                fout("T006", "Een symbool mag per fragment slechts eenmaal worden gedeclareerd.", fragment.regel)
            for symbool in fragment.symbolen:
                if symbool not in self.woordenboek.symbolen:
                    fout("T006", f"Onbekend symbool: {symbool!r}; voeg een symbooldefinitie toe aan het woordenboek.", fragment.regel)
        if geldig_tempo and geldige_pauzes and document.fragmenten and duur is not None:
            try:
                analyse = TranscriptAnalyse(document)
            except ValueError as probleem:
                fout("T005", str(probleem))
                return
            if abs(analyse.duur - duur * 60) > 0.01:
                fout("T005", f"De transcriptduur is {analyse.duur:.3f} seconden "
                     f"({analyse.woorden} woorden en {analyse.pauzetijd:.3f} seconden pauze); "
                     f"Duur vereist {duur * 60} seconden.")

    @staticmethod
    def _valideer_fasen(document: Document, duur: int | None) -> None:
        """Controleer dekking van tijd en opdrachten zonder instructies uit te voeren."""
        verwacht_begin = 0
        toegewezen: Counter[int] = Counter()
        nummers = {opdracht.nummer for opdracht in document.instructies}
        for fase in document.fasen:
            def fout(code: str, tekst: str) -> None:
                document.meldingen.append(Melding(code, fase.regel, tekst))

            if fase.start != verwacht_begin:
                fout("V011", f"Fase moet beginnen op minuut {verwacht_begin}; gevonden {fase.start}.")
            if fase.einde <= fase.start:
                fout("V011", "Het eind van een fase moet na het begin liggen.")
            verwacht_begin = fase.einde
            for naam, aanwezig in (
                ("titel", bool(fase.titel.strip())),
                ("Opdrachten", bool(fase.opdrachten)),
                ("Toelichting", bool(fase.toelichting) and all(tekst.strip() for tekst in fase.toelichting)),
                ("Werkvorm", bool(fase.werkvorm.strip())),
                ("Controle", bool(fase.controle.strip())),
                ("Beeld", bool(fase.beeld.strip())),
            ):
                if not aanwezig:
                    fout("V014", f"Verplicht faseveld ontbreekt of is leeg: {naam}.")
            if fase.beeld not in {"klassiek", "bloch", "bell", "samenvatting"}:
                fout("V015", "Beeld moet klassiek, bloch, bell of samenvatting zijn.")
            if fase.beeld == "bloch" and not (
                isfinite(fase.theta) and isfinite(fase.phi)
                and 0 <= fase.theta <= 180 and -360 <= fase.phi <= 360
            ):
                fout("V015", "Bloch-hoeken moeten eindig zijn: theta van 0 tot en met 180 en phi van -360 tot en met 360 graden.")
            for nummer in fase.opdrachten:
                toegewezen[nummer] += 1
                if nummer not in nummers:
                    fout("V013", f"Opdrachten verwijst naar onbekende instructie {nummer}.")
                elif toegewezen[nummer] > 1:
                    fout("V013", f"Instructie {nummer} is meer dan eenmaal aan een fase toegewezen.")
        if duur is not None and verwacht_begin != duur:
            document.meldingen.append(Melding("V012", document.fasen[-1].regel, f"De tijdlijn moet eindigen op minuut {duur}; gevonden {verwacht_begin}."))
        planning = {nummer: positie for positie, nummer in enumerate(
            nummer for fase in document.fasen for nummer in fase.opdrachten
        )}
        for opdracht in document.instructies:
            for verwijzing in re.findall(r"\[([0-9]{1,6})\]", opdracht.tekst):
                doel = int(verwijzing)
                if doel in planning and opdracht.nummer in planning and planning[doel] >= planning[opdracht.nummer]:
                    document.meldingen.append(Melding(
                        "V016", opdracht.regel,
                        f"Instructie {opdracht.nummer} staat in de tijdlijn voor de benodigde instructie {doel}."
                    ))
        ontbrekend = sorted(nummers - toegewezen.keys())
        if ontbrekend:
            document.meldingen.append(Melding("V013", 0, "Instructies zonder fase: " + ", ".join(map(str, ontbrekend)) + "."))