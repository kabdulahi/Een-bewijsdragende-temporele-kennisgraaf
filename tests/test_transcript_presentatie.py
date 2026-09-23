from contextlib import redirect_stdout
from io import StringIO
import json
import math
from pathlib import Path
import tempfile
import unittest

from taal.cli import main
from taal.dynamica import CoherenteOscillator
from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator
from taal.presentatie import LesPresentatie
from taal.transcript import TranscriptAnalyse
from test_presentatie import HtmlInspectie
from test_transcript import COLLEGE

ROOT = Path(__file__).resolve().parents[1]


class TranscriptPresentatieTests(unittest.TestCase):
    def setUp(self):
        self.tijdelijk = tempfile.TemporaryDirectory()
        self.addCleanup(self.tijdelijk.cleanup)
        self.map = Path(self.tijdelijk.name)
        self.woordenboek = Woordenboek(ROOT / "woordenboek.txt")
        self.validator = DocumentValidator(self.woordenboek)

    def document(self, tekst=COLLEGE):
        pad = self.map / "college.txt.invoer"
        pad.write_text(tekst, encoding="utf-8")
        document = self.validator.valideer(DocumentParser().parse(pad))
        self.assertTrue(document.geldig, document.meldingen)
        return document

    def test_transcriptexport_bevat_drie_vensters_en_gedeelde_toestand(self):
        document = self.document()
        html = LesPresentatie(document, begintijd=31, woordenboek=self.woordenboek).html()
        inspectie = HtmlInspectie(html)
        data = json.loads(inspectie.gegevens()["tekst"])
        analyse = TranscriptAnalyse(document)
        self.assertEqual("transcript", data["type"])
        self.assertEqual(31, data["begintijd"])
        self.assertEqual(analyse.segmenten, data["segmenten"])
        for veld in ("tempo", "woorden", "spreektijd", "pauzetijd", "duur"):
            self.assertEqual(getattr(analyse, veld), data[veld])
        self.assertEqual({"q0": 1.5, "p0": 0.0, "modeltempo": 0.01}, data["model"])
        self.assertEqual(CoherenteOscillator.uit_document(document).symbolisch(), data["symbolisch"])
        self.assertEqual(self.woordenboek.symbolen, data["symbolen"])
        self.assertEqual(3, inspectie.tags.count("dialog"))
        self.assertEqual(2, inspectie.tags.count("canvas"))
        self.assertEqual(2, len(inspectie.scripts))
        self.assertNotIn("__LESGEGEVENS__", html)
        self.assertNotIn("/*__SCRIPT__*/", html)
        self.assertNotIn("/*__STIJL__*/", html)
        self.assertFalse(any("src" in script["attributen"] for script in inspectie.scripts))

    def test_transcripttekst_formules_en_symbolen_blijven_data(self):
        vijandig = '</script><img src=x onerror=alert(1)> &'
        document = self.document(COLLEGE.replace("Fragment: 1 | De toestand", "Fragment: 1 | " + vijandig).replace(
            "Formule: H = (p^2 + q^2)/2", "Formule: " + vijandig
        ))
        self.woordenboek.symbolen["H"] = vijandig
        html = LesPresentatie(document, woordenboek=self.woordenboek).html()
        inspectie = HtmlInspectie(html)
        data = json.loads(inspectie.gegevens()["tekst"])
        self.assertEqual(2, len(inspectie.scripts))
        self.assertNotIn("img", inspectie.tags)
        self.assertNotIn(vijandig, html)
        self.assertEqual(vijandig, data["segmenten"][0]["titel"])
        self.assertEqual(vijandig, data["segmenten"][0]["formules"][0])
        self.assertEqual(vijandig, data["symbolen"]["H"])

    def test_begintijd_moet_eindig_en_binnen_college_liggen(self):
        document = self.document()
        for tijd in (-1, 60.1, math.inf, math.nan):
            with self.subTest(tijd=tijd), self.assertRaises(ValueError):
                LesPresentatie(document, begintijd=tijd, woordenboek=self.woordenboek)
        for tijd in (0, 60):
            with self.subTest(tijd=tijd):
                data = json.loads(HtmlInspectie(LesPresentatie(document, begintijd=tijd).html()).gegevens()["tekst"])
                self.assertEqual(tijd, data["begintijd"])

    def test_cli_visualiseert_transcript_op_gevraagde_tijd(self):
        document = self.document()
        uitvoer = self.map / "presentaties" / "college.html"
        with redirect_stdout(StringIO()) as rapport:
            code = main(["visualiseer", str(document.pad), "--tijd", "31", "--uitvoer", str(uitvoer)])
        self.assertEqual(0, code, rapport.getvalue())
        self.assertTrue(rapport.getvalue().isascii())
        self.assertTrue(uitvoer.is_file())
        data = json.loads(HtmlInspectie(uitvoer.read_text(encoding="utf-8")).gegevens()["tekst"])
        self.assertEqual(31, data["begintijd"])
        self.assertEqual(60, data["duur"])
        self.assertEqual("transcript", data["type"])

    def test_cli_geeft_numerieke_en_symbolische_toestand(self):
        document = self.document()
        with redirect_stdout(StringIO()) as rapport:
            code = main(["toestand", str(document.pad), "--tijd", "31"])
        self.assertEqual(0, code, rapport.getvalue())
        uitvoer = rapport.getvalue()
        self.assertTrue(uitvoer.isascii())
        self.assertIn("tau", uitvoer)
        self.assertIn("psi", uitvoer)
        self.assertIn("H_hat", uitvoer)
        self.assertIn("0.31", uitvoer)
        self.assertIn("cos", uitvoer)

    def test_cli_weigert_toestand_buiten_tijd_en_ongeldig_document(self):
        document = self.document()
        for tijd in ("-1", "61", "nan", "inf"):
            for opdracht in ("toestand", "visualiseer"):
                with self.subTest(tijd=tijd, opdracht=opdracht), redirect_stdout(StringIO()) as rapport:
                    code = main([opdracht, str(document.pad), "--tijd", tijd])
                self.assertEqual(2, code, rapport.getvalue())
                self.assertTrue(rapport.getvalue().isascii())
        document.pad.write_text(COLLEGE.replace("Duur: 1 minuten", "Duur: 2 minuten"), encoding="utf-8")
        with redirect_stdout(StringIO()) as rapport:
            code = main(["toestand", str(document.pad), "--tijd", "0"])
        self.assertEqual(1, code, rapport.getvalue())

    def test_interpretatie_transcript_bevat_gesproken_tekst(self):
        document = self.document()
        with redirect_stdout(StringIO()) as rapport:
            code = main(["interpreteer", str(document.pad)])
        self.assertEqual(0, code)
        self.assertIn("De klassieke toestand bestaat uit positie en impuls.", rapport.getvalue())
        self.assertNotIn("OPDRACHT 001", rapport.getvalue())


if __name__ == "__main__":
    unittest.main()
