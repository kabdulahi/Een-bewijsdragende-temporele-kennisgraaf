import math
import unittest
import xml.etree.ElementTree as ET

from taal.dynamica import CoherenteOscillator
from taal.logbeelden import LogBeelden
from taal.model import Fase


NS = {"s": "http://www.w3.org/2000/svg"}


def polyline(svg, klasse):
    root = ET.fromstring(svg)
    node = root.find(f".//s:polyline[@class='{klasse}']", NS)
    return [tuple(map(float, p.split(","))) for p in node.attrib["points"].split()]


def fase(beeld="bloch", **waarden):
    return Fase(start=0, einde=6, titel=waarden.pop("titel", "Voorbeeld"),
                opdrachten=[], toelichting=[], werkvorm="college", controle="",
                beeld=beeld, **waarden)


class LogBeeldenTests(unittest.TestCase):
    def test_golffunctie_projectioneert_werkelijke_complexe_amplitude(self):
        model = CoherenteOscillator(0, 0, 1)
        svg = LogBeelden.oscillator(model, 0)
        punten = polyline(svg, "golffunctie")
        self.assertEqual(121, len(punten))
        amplitude = math.pi**(-.25)
        self.assertAlmostEqual(214+42*amplitude, punten[60][0], delta=.051)
        self.assertAlmostEqual(133-22*amplitude, punten[60][1], delta=.051)
        self.assertEqual((60.0, 133.0), punten[0])
        self.assertEqual((368.0, 133.0), punten[-1])

    def test_globale_fase_verandert_golf_maakt_dichtheid_ongewijzigd(self):
        model = CoherenteOscillator(0, 0, 1)
        begin = LogBeelden.oscillator(model, 0)
        later = LogBeelden.oscillator(model, 2*math.pi)
        self.assertNotEqual(polyline(begin, "golffunctie"), polyline(later, "golffunctie"))
        self.assertEqual(polyline(begin, "kansdichtheid"), polyline(later, "kansdichtheid"))
        self.assertAlmostEqual(214-42*math.pi**(-.25),
                               polyline(later, "golffunctie")[60][0], delta=.051)

    def test_dichtheid_is_genormaliseerd_en_centrum_volgt_model(self):
        model = CoherenteOscillator(1.5, -.8)
        grens = max(4, math.hypot(model.q0, model.p0)+3)
        dx = 2*grens/120
        for tijd in (0, 75, 300):
            with self.subTest(tijd=tijd):
                svg = LogBeelden.oscillator(model, tijd)
                punten = polyline(svg, "kansdichtheid")
                dichtheden = [(201-y)/170 for _, y in punten]
                norm = dx*(sum(dichtheden)-.5*(dichtheden[0]+dichtheden[-1]))
                gemiddelde = dx*sum((-grens+i*dx)*v for i,v in enumerate(dichtheden))
                self.assertAlmostEqual(1, norm, delta=.003)
                self.assertAlmostEqual(model.toestand(tijd)["q"], gemiddelde, delta=.01)
                self.assertIn(f"q = {model.toestand(tijd)['q']:.4f}", svg)
                self.assertLess(len(svg.encode("utf-8")), 8000)

    def test_zelfstandig_met_betekenisvolle_assen(self):
        svg = LogBeelden.oscillator(CoherenteOscillator(), 10)
        root = ET.fromstring(svg)
        self.assertEqual("0 0 720 260", root.attrib["viewBox"])
        for label in ("Re ψ", "Im ψ", "Kansdichtheid", "totale kans = 1", "ℏ = m = ω = 1"):
            self.assertIn(label, svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("href=", svg)
        for ongeldig in (-1, math.inf, math.nan):
            with self.subTest(tijd=ongeldig), self.assertRaises(ValueError):
                LogBeelden.oscillator(CoherenteOscillator(), ongeldig)

    def test_bloch_assen_en_z_meetkansen_kloppen(self):
        noord = LogBeelden.lesfase(fase(theta=0))
        zuid = LogBeelden.lesfase(fase(theta=180))
        for svg in (noord, zuid):
            self.assertIn("Z-meetkansen", svg)
            self.assertIn("Statisch lesvoorbeeld", svg)
            self.assertLess(len(svg.encode("utf-8")), 8000)
        root = ET.fromstring(noord)
        punt = root.find(".//s:circle[@class='blochtoestand']", NS)
        self.assertAlmostEqual(210, float(punt.attrib["cx"]), places=3)
        self.assertAlmostEqual(134-76*math.cos(.23), float(punt.attrib["cy"]), delta=.001)
        self.assertEqual(["125.000", "0.000"], [
            n.attrib["width"] for n in root.findall(".//s:rect[@class='kans']", NS)])
        self.assertEqual(["0.000", "125.000"], [
            n.attrib["width"] for n in ET.fromstring(zuid).findall(".//s:rect[@class='kans']", NS)])
        yplus = LogBeelden.lesfase(fase(theta=90, phi=90))
        self.assertIn("(x, y, z) = (0.000, 1.000, 0.000)", yplus)

    def test_bell_is_lokaal_gemengd_met_correcte_gezamenlijke_kansen(self):
        svg = LogBeelden.lesfase(fase("bell"))
        root = ET.fromstring(svg)
        punten = root.findall(".//s:circle[@class='blochtoestand']", NS)
        self.assertEqual([("122.000", "129.000"), ("324.000", "129.000")],
                         [(p.attrib["cx"], p.attrib["cy"]) for p in punten])
        self.assertEqual(["62.500", "0.000", "0.000", "62.500"], [
            n.attrib["width"] for n in root.findall(".//s:rect[@class='kans']", NS)])
        self.assertIn("Qubit A: I/2", svg)
        self.assertIn("Qubit B: I/2", svg)
        self.assertLess(len(svg.encode("utf-8")), 8000)

    def test_klassiek_en_samenvatting_verzinnen_geen_dynamica(self):
        klassiek = LogBeelden.lesfase(fase("klassiek"))
        self.assertIn("Twee mogelijke bitwaarden", klassiek)
        self.assertIn("geen actuele bitwaarde", klassiek)
        self.assertNotIn('class="kans"', klassiek)
        samenvatting = LogBeelden.lesfase(fase("samenvatting"))
        self.assertIn("Tijdas", samenvatting)
        self.assertIn("0 min", samenvatting)
        self.assertIn("6 min", samenvatting)
        self.assertNotIn('class="golffunctie"', samenvatting)

    def test_onbetrouwbare_labels_blijven_tekst(self):
        titel = '<script>alert("x")</script> & naam'
        svg = LogBeelden.lesfase(fase('vreemd" onclick="alert(1)', titel=titel))
        root = ET.fromstring(svg)
        self.assertIn(titel, root.find("s:title", NS).text)
        self.assertNotIn("<script", svg)
        self.assertNotIn("onclick", root.attrib)
        self.assertIn("&lt;script&gt;", svg)
        self.assertIn("&amp; naam", svg)


if __name__ == "__main__":
    unittest.main()
