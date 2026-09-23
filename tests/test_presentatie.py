from contextlib import redirect_stdout
from dataclasses import asdict
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from taal.cli import main
from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator
from taal.presentatie import LesPresentatie

ROOT = Path(__file__).resolve().parents[1]
LES = """Titel: Qubits begrijpen
Vak: Informatica
Niveau: 4 vwo
Onderwerp: Meten
Leerdoel: De meetkansen van een qubit uitleggen.
Duur: 5 minuten
Instructies:
1. Beschrijf de meetkansen.
Tijdlijn:
Fase: 0-5 | Een qubit meten
Opdrachten: 1
Toelichting: Bij een meting in de Z-basis geeft deze toestand gelijke kansen.
Werkvorm: Laat leerlingen hun antwoord toelichten.
Controle: Wat is de kans op nul? Antwoord: een half.
Beeld: bloch | 90 | 45
Einde.
"""


class HtmlInspectie(HTMLParser):
    """Lees scriptdata als een browser, zodat ontsnapte eindtags worden getest."""

    def __init__(self, inhoud):
        super().__init__()
        self.scripts = []
        self.tags = []
        self.huidig = None
        self.feed(inhoud)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "script":
            self.huidig = {"attributen": dict(attrs), "tekst": ""}
            self.scripts.append(self.huidig)

    def handle_endtag(self, tag):
        if tag == "script":
            self.huidig = None

    def handle_data(self, data):
        if self.huidig is not None:
            self.huidig["tekst"] += data

    def gegevens(self):
        return next(script for script in self.scripts if script["attributen"].get("id") == "lesgegevens")


class PresentatieTests(unittest.TestCase):
    def setUp(self):
        self.tijdelijk = tempfile.TemporaryDirectory()
        self.addCleanup(self.tijdelijk.cleanup)
        self.map = Path(self.tijdelijk.name)
        self.validator = DocumentValidator(Woordenboek(ROOT / "woordenboek.txt"))

    def document(self, tekst=LES):
        pad = self.map / "les.txt.invoer"
        pad.write_text(tekst, encoding="utf-8")
        return self.validator.valideer(DocumentParser().parse(pad))

    def test_html_bevat_volledige_lesgegevens(self):
        document = self.document()
        self.assertTrue(document.geldig, document.meldingen)
        html = LesPresentatie(document).html()
        inspectie = HtmlInspectie(html)
        gegevens = json.loads(inspectie.gegevens()["tekst"])
        self.assertEqual(document.velden, gegevens["velden"])
        self.assertEqual(300, gegevens["duur"])
        self.assertEqual([asdict(opdracht) for opdracht in document.instructies], gegevens["instructies"])
        self.assertEqual([asdict(fase) for fase in document.fasen], gegevens["fasen"])
        self.assertEqual("application/json", inspectie.gegevens()["attributen"]["type"])
        self.assertIn("dialog", inspectie.tags)
        self.assertIn("canvas", inspectie.tags)
        self.assertNotIn("__LESGEGEVENS__", html)
        self.assertNotIn("/*__STIJL__*/", html)
        self.assertNotIn("/*__SCRIPT__*/", html)
        self.assertFalse(any("src" in script["attributen"] for script in inspectie.scripts))

    def test_tekst_kan_geen_script_of_html_invoegen(self):
        vijandig = '</script><script>alert("les")</script><img src=x onerror=alert(1)> & café'
        document = self.document(LES.replace("Titel: Qubits begrijpen", "Titel: " + vijandig).replace(
            "Toelichting: Bij een meting in de Z-basis geeft deze toestand gelijke kansen.",
            "Toelichting: " + vijandig,
        ))
        self.assertTrue(document.geldig, document.meldingen)
        html = LesPresentatie(document).html()
        inspectie = HtmlInspectie(html)
        self.assertEqual(2, len(inspectie.scripts))
        self.assertNotIn("img", inspectie.tags)
        self.assertNotIn(vijandig, html)
        self.assertNotIn("</script>", inspectie.gegevens()["tekst"])
        gegevens = json.loads(inspectie.gegevens()["tekst"])
        self.assertEqual(vijandig, gegevens["velden"]["Titel"])
        self.assertEqual([vijandig], gegevens["fasen"][0]["toelichting"])

    def test_ongeldig_document_en_ontbrekende_tijdlijn_geweigerd(self):
        with self.assertRaisesRegex(ValueError, "ongeldig"):
            LesPresentatie(self.document(LES.replace("Opdrachten: 1", "Opdrachten: 99")))
        with self.assertRaisesRegex(ValueError, "Tijdlijn"):
            LesPresentatie(self.document(LES.split("Tijdlijn:")[0] + "Einde.\n"))

    def test_html_bestand_wordt_geschreven_met_bovenliggende_map(self):
        presentatie = LesPresentatie(self.document())
        uitvoer = self.map / "presentaties" / "les.html"
        self.assertEqual(uitvoer.resolve(), presentatie.schrijf(uitvoer))
        self.assertEqual(presentatie.html(), uitvoer.read_text(encoding="utf-8"))

    def test_verkeerde_extensie_wordt_niet_geschreven(self):
        presentatie = LesPresentatie(self.document())
        uitvoer = self.map / "presentaties" / "les.txt"
        with self.assertRaisesRegex(ValueError, "html"):
            presentatie.schrijf(uitvoer)
        self.assertFalse(uitvoer.exists())
        self.assertFalse(uitvoer.parent.exists())

    def test_invoer_wordt_niet_overschreven(self):
        document = self.document()
        document.pad = self.map / "bestaand.html"
        document.pad.write_text("Bewaar deze inhoud.", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overschreven"):
            LesPresentatie(document).schrijf(document.pad)
        self.assertEqual("Bewaar deze inhoud.", document.pad.read_text(encoding="utf-8"))

    def test_cli_visualiseert_geldig_document(self):
        document = self.document()
        uitvoer = self.map / "college.html"
        with redirect_stdout(StringIO()) as rapport:
            code = main(["visualiseer", str(document.pad), "--uitvoer", str(uitvoer)])
        self.assertEqual(0, code, rapport.getvalue())
        self.assertTrue(uitvoer.is_file())
        self.assertTrue(rapport.getvalue().isascii())
        self.assertEqual(300, json.loads(HtmlInspectie(uitvoer.read_text(encoding="utf-8")).gegevens()["tekst"])["duur"])

    def test_cli_schrijft_niets_bij_ongeldige_invoer(self):
        for tekst, verwachte_code in (
            (LES.replace("Duur: 5 minuten", "Duur: 6 minuten"), 1),
            (LES.split("Tijdlijn:")[0] + "Einde.\n", 2),
        ):
            with self.subTest(verwachte_code=verwachte_code):
                document = self.document(tekst)
                uitvoer = self.map / "college.html"
                with redirect_stdout(StringIO()) as rapport:
                    code = main(["visualiseer", str(document.pad), "--uitvoer", str(uitvoer)])
                self.assertEqual(verwachte_code, code, rapport.getvalue())
                self.assertFalse(uitvoer.exists())
                self.assertTrue(rapport.getvalue().isascii())

    def test_cli_verkeerde_uitvoerextensie(self):
        document = self.document()
        uitvoer = self.map / "college.txt"
        with redirect_stdout(StringIO()) as rapport:
            code = main(["visualiseer", str(document.pad), "--uitvoer", str(uitvoer)])
        self.assertEqual(2, code, rapport.getvalue())
        self.assertFalse(uitvoer.exists())


if __name__ == "__main__":
    unittest.main()