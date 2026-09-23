from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from taal.cli import AsciiRapport, Zoekmachine, main
from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator

ROOT = Path(__file__).resolve().parents[1]


class TaalTests(unittest.TestCase):
    def setUp(self):
        self.validator = DocumentValidator(Woordenboek(ROOT / "woordenboek.txt"))

    def test_voorbeeldlessen(self):
        for naam in ("nederlands.txt", "engels.txt.invoer", "wiskunde_b.txt.invoer"):
            with self.subTest(naam=naam):
                doc = self.validator.valideer(DocumentParser().parse(ROOT / "voorbeelden" / naam))
                self.assertTrue(doc.geldig, doc.meldingen)

    def test_ongeldig_en_idempotentie(self):
        doc = self.validator.valideer(DocumentParser().parse(ROOT / "voorbeelden/ongeldig.txt"))
        self.assertTrue({"V004", "V006", "V007", "V008", "V009", "V010"}.issubset({m.code for m in doc.meldingen}))
        aantal = len(doc.meldingen)
        self.validator.valideer(doc)
        self.assertEqual(aantal, len(doc.meldingen))

    def test_structuur_en_verwijzingen(self):
        basis = (ROOT / "voorbeelden/nederlands.txt").read_text()
        for oud, nieuw, code in [("Titel:", "Onbekend:", "E001"), ("Einde.", "", "E004"),
                                 ("Einde.", "Einde.\nLos op.", "E007"),
                                 ("[1]", "[99]", "V010"), ("[1]", "[1", "V010"),
                                 ("Vak: Nederlands", "Vak: Nederlands\nVak: Engels", "E002")]:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as mapnaam:
                pad = Path(mapnaam) / "test.txt"
                pad.write_text(basis.replace(oud, nieuw), encoding="utf-8")
                doc = self.validator.valideer(DocumentParser().parse(pad))
                self.assertIn(code, {m.code for m in doc.meldingen})

    def test_zoek_en_filter(self):
        zoek = Zoekmachine(self.validator)
        resultaten, fouten = zoek.zoek(ROOT / "voorbeelden", "AFGELEIDE", True)
        self.assertTrue(resultaten)
        self.assertFalse(fouten)
        self.assertTrue(all(r.geldig for r in resultaten))
        resultaten, _ = zoek.zoek(ROOT / "voorbeelden", "doe iets", True)
        self.assertEqual([], resultaten)

    def test_exitcodes(self):
        for bestand, code in [("nederlands.txt", 0), ("ongeldig.txt", 1), ("ontbreekt.txt", 2)]:
            with self.subTest(bestand=bestand), redirect_stdout(StringIO()) as uitvoer:
                self.assertEqual(code, main(["controleer", str(ROOT / "voorbeelden" / bestand)]))
                self.assertTrue(uitvoer.getvalue().isascii())

    def test_ascii_geen_terminalbesturing(self):
        with redirect_stdout(StringIO()) as uitvoer:
            AsciiRapport.toon(["Café \x1b[31m 日本"])
        self.assertTrue(uitvoer.getvalue().isascii())
        self.assertNotIn("\x1b", uitvoer.getvalue())

    def test_foutief_woordenboek_en_onleesbaar_document(self):
        with tempfile.TemporaryDirectory() as mapnaam:
            pad = Path(mapnaam) / "test.txt"
            pad.write_text("Lees | lezen\nlees | dubbel", encoding="utf-8")
            with self.assertRaises(ValueError):
                Woordenboek(pad)
            pad.write_bytes(b"\xff")
            _, fouten = Zoekmachine(self.validator).zoek(Path(mapnaam), "lees")
            self.assertEqual(1, len(fouten))


if __name__ == "__main__":
    unittest.main()
