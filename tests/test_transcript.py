from pathlib import Path
import tempfile
import unittest

from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator
from taal.transcript import TranscriptAnalyse


COLLEGE = """Titel: Van klassieke naar quantumdynamica
Vak: Natuurkunde
Niveau: wo master
Onderwerp: De harmonische oscillator
Duur: 1 minuten
Soort: transcript
Tempo: 120 woorden/minuut
Model: harmonische_oscillator
Beginpositie: 1.5
Beginimpuls: 0
Modeltempo: 0.01
Transcript:
Fragment: 1 | De toestand
Tekst: De klassieke toestand bestaat uit positie en impuls.
Tekst: De quantumtoestand beschrijven we met een vector.
Formule: H = (p^2 + q^2)/2
Formule: |psi(t)> = exp(-i H t) |psi(0)>
Symbolen: H, q, p
Pauze: 22.5 seconden
Fragment: 2 | Evolutie
Tekst: De Hamiltoniaan bepaalt de evolutie.
Pauze: 27.5 seconden
Einde.
"""


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.tijdelijk = tempfile.TemporaryDirectory()
        self.addCleanup(self.tijdelijk.cleanup)
        self.map = Path(self.tijdelijk.name)
        self.woordenboekpad = self.map / "woordenboek.txt"
        self.woordenboekpad.write_text(
            "Beschrijf | Een beschrijving geven.\n"
            "begrip | harmonische oscillator | Een systeem met kwadratische potentiaal.\n"
            "symbool | H | Hamiltoniaan\nsymbool | q | positie\nsymbool | p | impuls\n"
            "symbool | I | identiteit\nsymbool | i | imaginaire eenheid\n", encoding="utf-8"
        )
        self.woordenboek = Woordenboek(self.woordenboekpad)
        self.validator = DocumentValidator(self.woordenboek)

    def document(self, tekst=COLLEGE):
        pad = self.map / "college.txt.invoer"
        pad.write_text(tekst, encoding="utf-8")
        return self.validator.valideer(DocumentParser().parse(pad))

    def codes(self, tekst):
        return {melding.code for melding in self.document(tekst).meldingen}

    def test_transcript_zonder_leerdoelen_of_instructies(self):
        document = self.document()
        self.assertTrue(document.geldig, document.meldingen)
        self.assertTrue(document.is_transcript)
        self.assertEqual([], document.instructies)
        self.assertEqual([], document.fasen)
        self.assertEqual(2, len(document.fragmenten))
        self.assertEqual(2, len(document.fragmenten[0].alinea))
        self.assertEqual(2, len(document.fragmenten[0].formules))
        self.assertEqual(["H", "q", "p"], document.fragmenten[0].symbolen)

    def test_spreektijd_en_pauzes_bepalen_exacte_tijdlijn(self):
        analyse = TranscriptAnalyse(self.document())
        self.assertEqual(20, analyse.woorden)
        self.assertEqual(120, analyse.tempo)
        self.assertEqual(10, analyse.spreektijd)
        self.assertEqual(50, analyse.pauzetijd)
        self.assertEqual(60, analyse.duur)
        eerste, tweede = analyse.segmenten
        self.assertEqual(0, eerste["start"])
        self.assertEqual(7.5, eerste["spreekeinde"])
        self.assertEqual(30, eerste["einde"])
        self.assertEqual(30, tweede["start"])
        self.assertEqual(32.5, tweede["spreekeinde"])
        self.assertEqual(60, tweede["einde"])
        self.assertEqual(15, eerste["woorden"])

    def test_slechts_uitgesproken_tekst_telt_mee(self):
        tekst = COLLEGE.replace("De toestand", "Een veel langere titel telt niet mee").replace(
            "Formule: H = (p^2 + q^2)/2", "Formule: Een formule met willekeurig veel symbolen en woorden"
        )
        self.assertEqual(20, TranscriptAnalyse(self.document(tekst)).woorden)

    def test_duur_moet_aansluiten_op_tempo(self):
        self.assertIn("T005", self.codes(COLLEGE.replace("Duur: 1 minuten", "Duur: 2 minuten")))
        self.assertIn("T005", self.codes(COLLEGE.replace("120 woorden/minuut", "100 woorden/minuut")))
        self.assertNotIn("T005", self.codes(COLLEGE.replace("27.5 seconden", "27.509 seconden")))
        self.assertIn("T005", self.codes(COLLEGE.replace("27.5 seconden", "27.52 seconden")))

    def test_verplicht_en_begrensd_tempo(self):
        for tempo in ("0", "49", "221", "120.5", "nan", "inf", "1200"):
            with self.subTest(tempo=tempo):
                self.assertIn("T002", self.codes(COLLEGE.replace("120 woorden/minuut", tempo + " woorden/minuut")))
        for veld in ("Tempo: 120 woorden/minuut\n", "Model: harmonische_oscillator\n", "Beginpositie: 1.5\n",
                     "Beginimpuls: 0\n", "Modeltempo: 0.01\n"):
            with self.subTest(veld=veld):
                self.assertIn("T001", self.codes(COLLEGE.replace(veld, "")))

    def test_niet_eindige_en_buiten_bereik_modelparameters(self):
        for waarde in ("nan", "inf", "-inf", "fout", "-4.01", "4.01"):
            for veld, oud in (("Beginpositie", "1.5"), ("Beginimpuls", "0")):
                with self.subTest(veld=veld, waarde=waarde):
                    self.assertIn("T007", self.codes(COLLEGE.replace(f"{veld}: {oud}", f"{veld}: {waarde}")))
        for waarde in ("0", "-1", "1.01", "nan", "inf"):
            with self.subTest(waarde=waarde):
                self.assertIn("T007", self.codes(COLLEGE.replace("Modeltempo: 0.01", "Modeltempo: " + waarde)))
        self.assertIn("T007", self.codes(COLLEGE.replace("harmonische_oscillator", "willekeurig")))

    def test_pauze_is_verplicht_eindig_en_niet_negatief(self):
        self.assertIn("T004", self.codes(COLLEGE.replace("Pauze: 22.5 seconden\n", "")))
        for waarde in ("nan", "inf", "-1", "22,5", "1e2", "9" * 400):
            with self.subTest(waarde=waarde):
                codes = self.codes(COLLEGE.replace("22.5 seconden", waarde + " seconden"))
                self.assertTrue({"E014", "T004"}.intersection(codes))
        enorm = "1" + "0" * 308
        self.assertIn("T005", self.codes(COLLEGE.replace("22.5 seconden", enorm + " seconden").replace(
            "27.5 seconden", enorm + " seconden")))

    def test_geen_gemengde_documentsoorten(self):
        for tekst in (
            COLLEGE.replace("Transcript:", "Instructies:\n1. Beschrijf de toestand.\nTranscript:"),
            COLLEGE.replace("Einde.", "Instructies:\n1. Beschrijf de toestand.\nEinde."),
            COLLEGE.replace("Einde.", "Tijdlijn:\nEinde."),
            COLLEGE.replace("Soort: transcript\n", ""),
        ):
            with self.subTest(tekst=tekst):
                self.assertIn("E013", self.codes(tekst))
        self.assertIn("E004", self.codes(COLLEGE.replace("Transcript:\n", "")))
        self.assertIn("E004", self.codes(COLLEGE.replace("Einde.", "")))

    def test_fragmentvolgorde_en_verplichte_tekst(self):
        for oud, nieuw in (
            ("Fragment: 2", "Fragment: 1"),
            ("Fragment: 1 | De toestand", "Fragment: 1 |"),
            ("Tekst: De Hamiltoniaan bepaalt de evolutie.\n", ""),
            ("Tekst: De Hamiltoniaan bepaalt de evolutie.", "Tekst:"),
            ("Formule: H = (p^2 + q^2)/2", "Formule:"),
        ):
            with self.subTest(oud=oud):
                self.assertIn("T003", self.codes(COLLEGE.replace(oud, nieuw)))
        self.assertIn("T003", self.codes(COLLEGE.split("Fragment:")[0] + "Einde.\n"))

    def test_fragmentstructuur_en_dubbele_velden(self):
        for oud, nieuw, code in (
            ("Fragment: 1 | De toestand", "Fragment: onjuist", "E014"),
            ("Transcript:", "Transcript:\nTekst: Losse tekst", "E014"),
            ("Pauze: 22.5 seconden", "Pauze: 22.5 seconden\nPauze: 0 seconden", "E002"),
            ("Symbolen: H, q, p", "Symbolen: H, q, p\nSymbolen: H", "E002"),
            ("Transcript:", "Transcript:\nTranscript:", "E013"),
            ("Einde.", "Einde.\nTekst: Na het einde", "E007"),
        ):
            with self.subTest(oud=oud):
                self.assertIn(code, self.codes(COLLEGE.replace(oud, nieuw)))

    def test_symbolen_bekend_uniek_en_hoofdlettergevoelig(self):
        for symbolen in ("H, onbekend", "h, q, p", "H, H", "", "H,"):
            with self.subTest(symbolen=symbolen):
                self.assertIn("T006", self.codes(COLLEGE.replace("H, q, p", symbolen)))
        self.assertTrue(self.document(COLLEGE.replace("H, q, p", "I, i")).geldig)
        self.assertTrue(self.document(COLLEGE.replace("Symbolen: H, q, p\n", "")).geldig)

    def test_herhaald_valideren_behoudt_parsefouten_zonder_verdubbelen(self):
        document = self.document(COLLEGE.replace("27.5 seconden", "nee").replace("H, q, p", "onbekend"))
        meldingen = list(document.meldingen)
        self.validator.valideer(document)
        self.assertEqual(meldingen, document.meldingen)
        self.assertTrue({"E014", "T004", "T006"}.issubset({m.code for m in meldingen}))

    def test_getypeerd_woordenboek_behoudt_oude_werkwoorden(self):
        self.assertEqual({"beschrijf": "Een beschrijving geven."}, self.woordenboek.woorden)
        self.assertIn("harmonische oscillator", self.woordenboek.begrippen)
        self.assertNotEqual(self.woordenboek.symbolen["I"], self.woordenboek.symbolen["i"])
        self.woordenboekpad.write_text("werkwoord | Lees | Lezen\nbegrip | Lees | Een naam", encoding="utf-8")
        woordenboek = Woordenboek(self.woordenboekpad)
        self.assertIn("lees", woordenboek.woorden)
        self.assertIn("lees", woordenboek.begrippen)

    def test_foutieve_getypeerde_woordenboekregels(self):
        for tekst in (
            "begrip | toestand | een vector\nbegrip | Toestand | dubbel",
            "symbool | H | energie\nsymbool | H | dubbel",
            "onbekend | H | betekenis", "begrip | | leeg", "symbool | q p | spaties",
            "symbool | q,p | komma", "werkwoord | lees nu | spaties", "begrip | term |", "# leeg\n",
        ):
            with self.subTest(tekst=tekst):
                self.woordenboekpad.write_text(tekst, encoding="utf-8")
                with self.assertRaises(ValueError):
                    Woordenboek(self.woordenboekpad)

    def test_analyse_geweigerd_bij_ongeldige_basis(self):
        for tekst in (
            COLLEGE.replace("Soort: transcript", "Soort: anders"),
            COLLEGE.replace("120 woorden/minuut", "0 woorden/minuut"),
            COLLEGE.split("Fragment:")[0] + "Einde.\n",
            COLLEGE.replace("Pauze: 22.5 seconden\n", ""),
        ):
            with self.subTest(tekst=tekst), self.assertRaises(ValueError):
                TranscriptAnalyse(self.document(tekst))


if __name__ == "__main__":
    unittest.main()
