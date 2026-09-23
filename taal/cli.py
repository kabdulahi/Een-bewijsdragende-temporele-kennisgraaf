"""CLI, zoekmachine en formele ASCII-uitvoer."""
import argparse
import math
from dataclasses import dataclass
from pathlib import Path
import unicodedata
from .model import Document, Woordenboek
from .parser import DocumentParser, DocumentValidator
from .presentatie import LesPresentatie
from .transcript import TranscriptAnalyse
from .dynamica import CoherenteOscillator

STANDAARD_WOORDENBOEK = Path(__file__).resolve().parents[1] / "woordenboek.txt"


class AsciiRapport:
    @staticmethod
    def toon(regels: list[str]) -> None:
        print("+" + "-" * 76 + "+")
        for regel in regels:
            ascii_tekst = unicodedata.normalize("NFKD", regel).encode("ascii", "backslashreplace").decode("ascii")
            ascii_tekst = "".join(teken if 32 <= ord(teken) <= 126 else f"\\x{ord(teken):02x}" for teken in ascii_tekst)
            for start in range(0, max(1, len(ascii_tekst)), 74):
                print("| " + ascii_tekst[start:start + 74].ljust(74) + " |")
        print("+" + "-" * 76 + "+")

    def document(self, document: Document, interpreteer: bool = False) -> None:
        regels = ["OPHANGEN | TAALVERSIE 2 | FORMELE DOCUMENTCONTROLE",
                  f"Bestand: {document.pad}",
                  f"Status: {'GELDIG' if document.geldig else 'ONGELDIG'}",
                  (f"Transcript | Fragmenten: {len(document.fragmenten)} | Fouten: {len(document.meldingen)}"
                   if document.is_transcript else
                   f"Instructies: {len(document.instructies)} | Fasen: {len(document.fasen)} | Fouten: {len(document.meldingen)}")]
        regels.extend(f"{m.code} | regel {m.regel or '-'} | {m.tekst}" for m in document.meldingen)
        if document.is_transcript and document.geldig:
            analyse = TranscriptAnalyse(document)
            regels.extend([f"Woorden: {analyse.woorden} | Tempo: {analyse.tempo:g} woorden/minuut",
                           f"Spreektijd: {analyse.spreektijd:g} s | Pauzes: {analyse.pauzetijd:g} s | Totaal: {analyse.duur:g} s"])
            if interpreteer:
                for segment in analyse.segmenten:
                    regels.append(f"FRAGMENT {segment['nummer']} | {segment['start']:g}-{segment['einde']:g} s | {segment['titel']}")
                    regels.extend(segment["alinea"])
                    regels.extend("FORMULE: " + formule for formule in segment["formules"])
                    regels.append(f"STILTE: {segment['pauze']:g} s")
        if interpreteer and document.geldig and not document.is_transcript:
            regels.extend(f"{sleutel}: {waarde}" for sleutel, waarde in document.velden.items())
            regels.extend(f"OPDRACHT {i.nummer:03d} | {i.tekst}" for i in document.instructies)
            for fase in document.fasen:
                regels.append(f"FASE {fase.start:02d}-{fase.einde:02d} min | {fase.titel}")
                regels.append("Opdrachten: " + ", ".join(map(str, fase.opdrachten)))
                regels.extend("Toelichting: " + tekst for tekst in fase.toelichting)
                regels.extend([f"Werkvorm: {fase.werkvorm}", f"Controle: {fase.controle}",
                               f"Beeld: {fase.beeld} | theta={fase.theta} | phi={fase.phi}"])
        self.toon(regels)


@dataclass(frozen=True)
class Zoekresultaat:
    pad: Path
    regel: int
    tekst: str
    geldig: bool


class Zoekmachine:
    def __init__(self, validator: DocumentValidator):
        self.validator = validator

    def zoek(self, map_pad: Path, zoektekst: str, alleen_geldig: bool = False) -> tuple[list[Zoekresultaat], list[str]]:
        termen = zoektekst.casefold().split()
        if not termen:
            raise ValueError("Geef minimaal een zoekterm op.")
        if not map_pad.is_dir():
            raise ValueError(f"Geen bestaande zoekmap: {map_pad}.")
        resultaten: list[Zoekresultaat] = []
        fouten: list[str] = []
        for pad in sorted(map_pad.rglob("*")):
            if pad.is_symlink() or not pad.is_file() or pad.suffix.lower() not in {".txt", ".invoer"} or any(p.startswith(".") for p in pad.relative_to(map_pad).parts):
                continue
            try:
                document = self.validator.valideer(DocumentParser().parse(pad))
            except (OSError, UnicodeError, ValueError) as exc:
                fouten.append(f"{pad}: {exc}")
                continue
            if alleen_geldig and not document.geldig:
                continue
            for nummer, regel in enumerate(document.tekst.splitlines(), 1):
                if all(term in regel.casefold() for term in termen):
                    resultaten.append(Zoekresultaat(pad, nummer, regel.strip(), document.geldig))
        return resultaten, fouten


class NederlandseArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        AsciiRapport.toon(["STATUS: FOUT", f"Ongeldige opdrachtregel: {message}", "Gebruik --help voor de beschikbare opdrachten."])
        self.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = NederlandseArgumentParser(description="Controleer, interpreteer en doorzoek formele Nederlandse lesdocumenten.", add_help=False)
    parser.add_argument("-h", "--help", action="help", help="toon deze uitleg")
    parser.add_argument("--woordenboek", type=Path, default=STANDAARD_WOORDENBOEK, help="pad naar een eigen woordenboek")
    sub = parser.add_subparsers(dest="opdracht", required=True, title="opdrachten")
    for naam in ("controleer", "interpreteer"):
        opdracht = sub.add_parser(naam, help=f"{naam} een UTF-8-lesdocument", add_help=False)
        opdracht.add_argument("-h", "--help", action="help", help="toon deze uitleg")
        opdracht.add_argument("bestand", type=Path)
    visualiseer = sub.add_parser("visualiseer", help="maak een offline 3D-lespresentatie", add_help=False)
    visualiseer.add_argument("-h", "--help", action="help", help="toon deze uitleg")
    visualiseer.add_argument("bestand", type=Path)
    visualiseer.add_argument("--uitvoer", type=Path, help="HTML-uitvoerpad (standaard: naast de invoer)")
    visualiseer.add_argument("--tijd", type=float, default=0, help="begintijd in collegeseconden")
    visualiseer.add_argument("--open", action="store_true", help="open het resultaat in de standaardbrowser")
    log = sub.add_parser("log", help="schrijf per tijdstap een HTML-log met SVG en geparseerde LaTeX")
    log.add_argument("bestand", type=Path)
    log.add_argument("--stap", default="1", help="interval in collegeseconden (standaard 1)")
    log.add_argument("--van", default="0", help="begintijd in collegeseconden")
    log.add_argument("--tot", help="eindtijd in collegeseconden (standaard volledige duur)")
    log.add_argument("--uitvoer", type=Path, help="HTML-logbestand")
    log.add_argument("--open", action="store_true", help="open het log na het schrijven")
    toestand = sub.add_parser("toestand", help="toon numerieke en symbolische modeltoestand")
    toestand.add_argument("bestand", type=Path)
    toestand.add_argument("--tijd", type=float, default=0, help="collegetijd in seconden")
    toestand.add_argument("--positie", type=float, default=0, help="positie x voor de golffunctiewaarde")
    toestand.add_argument("--symbool", help="toon een specifieke symbolische modelformule, bijvoorbeeld psi")
    zoek = sub.add_parser("zoek", help="zoek per regel in .txt en .invoer", add_help=False)
    zoek.add_argument("-h", "--help", action="help", help="toon deze uitleg")
    zoek.add_argument("map", type=Path)
    zoek.add_argument("zoektekst")
    zoek.add_argument("--alleen-geldig", action="store_true", help="toon uitsluitend geldige documenten")
    lexicon = sub.add_parser("woordenboek", help="toon werkwoorden, begrippen en symbolen")
    lexicon.add_argument("--zoek", default="", help="filter termen en betekenissen")
    lexicon.add_argument("--categorie", choices=["alles", "werkwoord", "begrip", "symbool"], default="alles")
    args = parser.parse_args(argv)
    rapport = AsciiRapport()
    try:
        woordenboek = Woordenboek(args.woordenboek)
        validator = DocumentValidator(woordenboek)
        if args.opdracht == "woordenboek":
            regels = ["HET WOORDENBOEK"]
            for categorie, inhoud in (("werkwoord", woordenboek.woorden), ("begrip", woordenboek.begrippen), ("symbool", woordenboek.symbolen)):
                if args.categorie not in ("alles", categorie):
                    continue
                regels.extend(f"{categorie} | {term}: {betekenis}" for term, betekenis in sorted(inhoud.items())
                              if args.zoek.casefold() in (term + " " + betekenis).casefold())
            rapport.toon(regels)
            return 0
        if args.opdracht == "zoek":
            resultaten, fouten = Zoekmachine(validator).zoek(args.map, args.zoektekst, args.alleen_geldig)
            rapport.toon([f"ZOEKRAPPORT | Resultaten: {len(resultaten)} | Leesfouten: {len(fouten)}"] +
                         [f"{r.pad}:{r.regel} | {'GELDIG' if r.geldig else 'ONGELDIG'} | {r.tekst}" for r in resultaten] +
                         [f"LEESFOUT | {fout}" for fout in fouten])
            return 2 if fouten else 0
        if args.bestand.suffix.lower() not in {".txt", ".invoer"}:
            raise ValueError("Een lesdocument moet de extensie .txt of .invoer hebben.")
        document = validator.valideer(DocumentParser().parse(args.bestand))
        if args.opdracht == "log":
            if not document.geldig:
                rapport.document(document)
                return 1
            from .logboek import TijdstapLog
            logboek = TijdstapLog(document, stap=args.stap, begin=args.van, einde=args.tot)
            uitvoer = args.uitvoer or args.bestand.with_suffix(".log.html")
            pad = logboek.schrijf(uitvoer)
            regels = ["HTML-TIJDSTAPLOG | GESLAAGD", f"Bestand: {pad}",
                      f"Opgeslagen tijdstappen: {len(logboek.tijden)} | Stap: {logboek.stap} s",
                      "Per stap: toestand, SVG-visualisatie en LaTeX geparseerd naar MathML."]
            if args.open:
                import webbrowser
                try:
                    geopend = webbrowser.open(pad.as_uri())
                except (OSError, webbrowser.Error):
                    geopend = False
                if not geopend:
                    regels.append("Open het HTML-log handmatig in de browser.")
            rapport.toon(regels)
            return 0
        if args.opdracht == "toestand":
            if not document.geldig:
                rapport.document(document)
                return 1
            if not math.isfinite(args.tijd) or not 0 <= args.tijd <= int(document.velden["Duur"].split()[0]) * 60:
                raise ValueError("De collegetijd moet eindig zijn en binnen de collegeduur liggen.")
            model = CoherenteOscillator.uit_document(document)
            staat = model.toestand(args.tijd)
            waarde = model.golffunctie(args.positie, args.tijd)
            formules = model.symbolisch()
            if args.symbool and args.symbool not in formules:
                raise ValueError("Geen modelformule voor dit symbool. Beschikbaar: " + ", ".join(formules))
            regels = ["MODELTOESTAND | COHERENTE HARMONISCHE OSCILLATOR", "Eenheden: hbar = m = omega = 1"]
            regels.extend(f"{naam}: {waarde:.9g}" for naam, waarde in staat.items())
            regels.append(f"psi(x={args.positie:g}): {waarde.real:.9g} + i*({waarde.imag:.9g})")
            selectie = {args.symbool: formules[args.symbool]} if args.symbool else formules
            regels.extend(f"{sleutel}: {formule}" for sleutel, formule in selectie.items())
            rapport.toon(regels)
            return 0
        if args.opdracht == "visualiseer":
            if not document.geldig:
                rapport.document(document)
                return 1
            uitvoer = args.uitvoer if args.uitvoer is not None else args.bestand.with_suffix(".html")
            pad = LesPresentatie(document, begintijd=args.tijd, woordenboek=woordenboek).schrijf(uitvoer)
            regels = ["STATUS: GELDIG", f"Presentatie: {pad}", f"Lesduur: {document.velden['Duur']}",
                      (f"Drie vensters | Fragmenten: {len(document.fragmenten)}" if document.is_transcript else f"Fasen: {len(document.fasen)}"), "Open het HTML-bestand in een browser voor de interactieve les."]
            if args.open:
                import webbrowser
                try:
                    geopend = webbrowser.open(pad.as_uri())
                except (OSError, webbrowser.Error):
                    geopend = False
                if not geopend:
                    regels.append("De browser kon niet worden gestart. Open het HTML-bestand handmatig.")
            rapport.toon(regels)
            return 0
        rapport.document(document, args.opdracht == "interpreteer")
        return 0 if document.geldig else 1
    except (OSError, UnicodeError, ValueError) as exc:
        rapport.toon(["STATUS: FOUT", str(exc)])
        return 2
