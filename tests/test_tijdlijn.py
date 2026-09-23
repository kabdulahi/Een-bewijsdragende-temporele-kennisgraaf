from pathlib import Path
import tempfile
import unittest

from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator

ROOT = Path(__file__).resolve().parents[1]
LES = """Titel: Qubits onderzoeken
Vak: Informatica
Niveau: 4 vwo
Onderwerp: Superpositie
Leerdoel: Meting en superpositie onderscheiden.
Duur: 10 minuten
Instructies:
1. Beschrijf een klassieke bit.
2. Vergelijk de bit met een qubit uit [1].
Tijdlijn:
Fase: 0-4 | Eerst een klassieke bit
Opdrachten: 1
Toelichting: Een klassieke bit heeft de waarde nul of een.
Toelichting: Gebruik een lichtschakelaar als eerste vergelijking.
Werkvorm: Bespreek de twee mogelijkheden met de klas.
Controle: Hoeveel waarden heeft een bit? Antwoord: twee.
Beeld: klassiek
Fase: 4-10 | Nu een qubit
Opdrachten: 2
Toelichting: De Bloch-bol toont de zuivere toestand van een qubit.
Werkvorm: Laat leerlingen de meetkansen voorspellen.
Controle: Wat betekent de evenaar? Antwoord: gelijke kansen bij een meting in de Z-basis.
Beeld: bloch | 90 | 0
Einde.
"""


class TijdlijnTests(unittest.TestCase):
    def setUp(self):
        self.validator = DocumentValidator(Woordenboek(ROOT / "woordenboek.txt"))

    def document(self, tekst=LES):
        with tempfile.TemporaryDirectory() as mapnaam:
            pad = Path(mapnaam) / "les.txt.invoer"
            pad.write_text(tekst, encoding="utf-8")
            return self.validator.valideer(DocumentParser().parse(pad))

    def assertFout(self, tekst, code):
        document = self.document(tekst)
        self.assertFalse(document.geldig)
        self.assertIn(code, {melding.code for melding in document.meldingen})
        return document

    def test_fasen_behouden_volgorde_en_uitgebreide_toelichting(self):
        document = self.document()
        self.assertTrue(document.geldig, document.meldingen)
        self.assertEqual([(0, 4), (4, 10)], [(f.start, f.einde) for f in document.fasen])
        self.assertEqual([[1], [2]], [f.opdrachten for f in document.fasen])
        self.assertEqual(2, len(document.fasen[0].toelichting))
        self.assertEqual("Nu een qubit", document.fasen[1].titel)
        self.assertEqual((90.0, 0.0), (document.fasen[1].theta, document.fasen[1].phi))
        self.assertEqual(11, document.fasen[0].regel)

    def test_tijdlijn_blijft_optioneel(self):
        document = self.document(LES.split("Tijdlijn:")[0] + "Einde.\n")
        self.assertTrue(document.geldig, document.meldingen)
        self.assertEqual([], document.fasen)

    def test_ondersteunde_vakken(self):
        for vak in ("Nederlands", "Engels", "Wiskunde B", "Natuurkunde", "Informatica"):
            with self.subTest(vak=vak):
                document = self.document(LES.replace("Vak: Informatica", "Vak: " + vak))
                self.assertTrue(document.geldig, document.meldingen)
        self.assertFout(LES.replace("Vak: Informatica", "Vak: Geschiedenis"), "V002")

    def test_lege_en_verkeerd_geplaatste_tijdlijn(self):
        self.assertFout(LES.split("Tijdlijn:")[0] + "Tijdlijn:\nEinde.", "E012")
        self.assertFout(LES.replace("Instructies:", "Tijdlijn:\nInstructies:"), "E008")
        self.assertFout(LES.replace("Fase: 4-10", "Tijdlijn:\nFase: 4-10"), "E008")
        self.assertFout(LES.replace("Fase: 4-10", "Instructies:\nFase: 4-10"), "E002")

    def test_fasen_dekken_de_volledige_duur_zonder_gaten_of_overlap(self):
        for oud, nieuw, code in (
            ("Fase: 0-4", "Fase: 1-4", "V011"),
            ("Fase: 4-10", "Fase: 5-10", "V011"),
            ("Fase: 4-10", "Fase: 3-10", "V011"),
            ("Fase: 0-4", "Fase: 0-0", "V011"),
            ("Fase: 4-10", "Fase: 4-3", "V011"),
            ("Fase: 4-10", "Fase: 4-11", "V012"),
            ("Duur: 10 minuten", "Duur: 9 minuten", "V012"),
        ):
            with self.subTest(nieuw=nieuw):
                self.assertFout(LES.replace(oud, nieuw), code)

    def test_iedere_opdracht_precies_een_keer(self):
        for oud, nieuw in (
            ("Opdrachten: 2", "Opdrachten: 99"),
            ("Opdrachten: 1", "Opdrachten: 1, 1"),
            ("Opdrachten: 2", "Opdrachten: 1, 2"),
            ("Opdrachten: 2", "Opdrachten: 1"),
        ):
            with self.subTest(nieuw=nieuw):
                self.assertFout(LES.replace(oud, nieuw), "V013")

    def test_fasevelden_verplicht_en_niet_leeg(self):
        for veld in ("Opdrachten", "Toelichting", "Werkvorm", "Controle", "Beeld"):
            with self.subTest(veld=veld):
                regels = [regel for regel in LES.splitlines() if not regel.startswith(veld + ":")]
                self.assertFout("\n".join(regels), "V014")
        self.assertFout(LES.replace("Fase: 0-4 | Eerst een klassieke bit", "Fase: 0-4 |"), "V014")
        self.assertFout(LES.replace("Werkvorm: Bespreek de twee mogelijkheden met de klas.", "Werkvorm:"), "V014")
        self.assertFout(LES.replace("Toelichting: Een klassieke bit heeft de waarde nul of een.", "Toelichting:"), "V014")

    def test_dubbele_fasevelden_verboden(self):
        for veld, waarde in (
            ("Opdrachten", "1"),
            ("Werkvorm", "Bespreek de twee mogelijkheden met de klas."),
            ("Controle", "Hoeveel waarden heeft een bit? Antwoord: twee."),
            ("Beeld", "klassiek"),
        ):
            with self.subTest(veld=veld):
                regel = veld + ": " + waarde
                self.assertFout(LES.replace(regel, regel + "\n" + regel), "E002")

    def test_onjuiste_tijdlijnsyntaxis(self):
        for oud, nieuw, code in (
            ("Fase: 0-4", "Fase: 0.5-4", "E009"),
            ("Fase: 0-4", "Fase: -1-4", "E009"),
            ("Fase: 0-4", "Fase: 0000000-4", "E009"),
            ("Fase: 0-4 | Eerst een klassieke bit", "Fase: 0-4", "E009"),
            ("Fase: 0-4 | Eerst een klassieke bit\n", "", "E010"),
            ("Werkvorm:", "Werkvormpje:", "E010"),
            ("Opdrachten: 1", "Opdrachten: 1, ", "E011"),
            ("Opdrachten: 1", "Opdrachten: -1", "E011"),
            ("Opdrachten: 1", "Opdrachten: 1000000", "E011"),
            ("Beeld: bloch | 90 | 0", "Beeld: bloch | negentig | 0", "E011"),
            ("Beeld: bloch | 90 | 0", "Beeld: bloch", "E011"),
            ("Beeld: klassiek", "Beeld: klassiek | 0 | 0", "E011"),
        ):
            with self.subTest(nieuw=nieuw):
                self.assertFout(LES.replace(oud, nieuw), code)

    def test_bloch_hoeken_en_andere_beelden(self):
        for beeld in ("klassiek", "bell", "samenvatting", "bloch | 0 | -360", "bloch | 180 | 360", "bloch | 45.5 | -12.75"):
            with self.subTest(beeld=beeld):
                document = self.document(LES.replace("Beeld: bloch | 90 | 0", "Beeld: " + beeld))
                self.assertTrue(document.geldig, document.meldingen)
        for beeld in ("onbekend", "bloch | -1 | 0", "bloch | 181 | 0", "bloch | 90 | 361", "bloch | nan | 0", "bloch | 90 | inf", "bloch | 1e999 | 0"):
            with self.subTest(beeld=beeld):
                self.assertFout(LES.replace("Beeld: bloch | 90 | 0", "Beeld: " + beeld), "V015")

    def test_verwijzingen_volgen_de_geplande_uitvoeringsvolgorde(self):
        tekst = LES.replace("Opdrachten: 1", "Opdrachten: tijdelijk").replace(
            "Opdrachten: 2", "Opdrachten: 1").replace("Opdrachten: tijdelijk", "Opdrachten: 2")
        self.assertFout(tekst, "V016")
        # Ook binnen een fase mag een opdracht haar voorwaarde niet vooruit plannen.
        tekst = LES.split("Tijdlijn:")[0] + """Tijdlijn:
Fase: 0-10 | Samen oefenen
Opdrachten: 2, 1
Toelichting: Oefenen met de opdrachten.
Werkvorm: Samen werken.
Controle: Bespreek het antwoord.
Beeld: klassiek
Einde.
"""
        self.assertFout(tekst, "V016")

    def test_tijdlijnvalidatie_is_idempotent_met_behoud_van_parsefouten(self):
        document = self.document(LES.replace("Fase: 4-10", "Fase: 5-9").replace("Werkvorm:", "Onbekend:"))
        meldingen = list(document.meldingen)
        self.validator.valideer(document)
        self.assertEqual(meldingen, document.meldingen)
        self.assertTrue(any(m.code.startswith("E") for m in meldingen))
        self.assertTrue(any(m.code.startswith("V") for m in meldingen))

    def test_foutieve_duur_met_tijdlijn_geeft_melding(self):
        self.assertFout(LES.replace("Duur: 10 minuten", "Duur: tien minuten"), "V004")


if __name__ == "__main__":
    unittest.main()