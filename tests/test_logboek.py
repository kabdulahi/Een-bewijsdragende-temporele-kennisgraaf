from contextlib import redirect_stdout
from decimal import Decimal
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from taal.cli import main
from taal.dynamica import CoherenteOscillator
from taal.logboek import LatexWeergave, TijdstapLog
from taal.model import Woordenboek
from taal.parser import DocumentParser, DocumentValidator

ROOT = Path(__file__).resolve().parents[1]


class LogData(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_data = False
        self.data = ""
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "logdata":
            self.in_data = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_data = False

    def handle_data(self, text):
        if self.in_data:
            self.data += text


class LogboekTests(unittest.TestCase):
    def setUp(self):
        self.validator = DocumentValidator(Woordenboek(ROOT/"woordenboek.txt"))
        self.master = self.validator.valideer(DocumentParser().parse(ROOT/"voorbeelden/quantumdynamica_master.txt.invoer"))
        self.les = self.validator.valideer(DocumentParser().parse(ROOT/"voorbeelden/quantumcomputing.txt.invoer"))

    def test_exacte_decimale_stappen_met_eindpunt(self):
        log = TijdstapLog(self.master, stap=".3", begin=0, einde=1)
        self.assertEqual([Decimal(x) for x in ("0", ".3", ".6", ".9", "1")], log.tijden)
        self.assertEqual("0.9", log.record(3)["tijd_exact"])
        self.assertEqual([Decimal("1")], TijdstapLog(self.master, begin=1, einde=1).tijden)

    def test_standaard_logt_iedere_seconde(self):
        log = TijdstapLog(self.master)
        self.assertEqual(3601, len(log.tijden))
        self.assertEqual(Decimal("3600"), log.tijden[-1])

    def test_ongeldige_intervallen_worden_afgewezen(self):
        for args in ({"stap":0}, {"stap":-1}, {"stap":"nan"}, {"stap":"one"},
                     {"einde":"inf"}, {"begin":-1}, {"begin":3,"einde":2},
                     {"einde":3601}, {"stap":".0001"}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                TijdstapLog(self.master, **args)

    def test_toestand_en_tijdcontext_kloppen(self):
        r = TijdstapLog(self.master, begin=900, einde=900).record(0)
        s = CoherenteOscillator.uit_document(self.master).toestand(900)
        for sleutel, waarde in s.items():
            self.assertEqual(waarde, r["toestand"][sleutel])
        self.assertEqual(9, r["toestand"]["tau"])
        self.assertIn("<svg", r["visualisatie"])
        end = TijdstapLog(self.master, begin=3600).record(0)
        self.assertEqual("afgerond", end["context"]["activiteit"])

    def test_lesfasen_bloch_bell_en_klassiek(self):
        klassiek = TijdstapLog(self.les, begin=0, einde=0).record(0)
        self.assertNotIn("P0", klassiek["toestand"])
        self.assertIn("Geen specifieke quantumtoestand", klassiek["toestand"]["toelichting"])
        bloch = TijdstapLog(self.les, begin=660, einde=660).record(0)
        self.assertEqual("bloch", bloch["toestand"]["beeld"])
        self.assertAlmostEqual(.36, bloch["toestand"]["P0"])
        bell = TijdstapLog(self.les, begin=2280, einde=2280).record(0)
        self.assertEqual("bell", bell["toestand"]["beeld"])
        self.assertEqual(.5, bell["toestand"]["P00"])
        self.assertEqual(0, bell["toestand"]["P01"])

    def test_latex_wordt_mathml_met_breuken_en_exponenten(self):
        mathml = LatexWeergave.parse(r"\psi=\frac{1}{\sqrt{2}}e^{-i\tau}")
        root = ET.fromstring(mathml)
        ns = "{http://www.w3.org/1998/Math/MathML}"
        self.assertEqual(ns+"math", root.tag)
        self.assertTrue(list(root.iter(ns+"mfrac")))
        self.assertTrue(list(root.iter(ns+"msup")))
        for log in (TijdstapLog(self.master,einde=0),TijdstapLog(self.les,begin=660,einde=660),
                    TijdstapLog(self.les,begin=2280,einde=2280)):
            for item in log.record(0)["symbolisch"]:
                self.assertTrue(item["latex"])
                self.assertEqual(ns+"math", ET.fromstring(item["mathml"]).tag)

    def test_html_bewaart_alle_snapshots_en_ontsnapt_invoer(self):
        vijandig = '</script><img src=x onerror=alert(1)>'
        self.master.velden["Titel"] = vijandig
        self.master.fragmenten[0].titel = vijandig
        with tempfile.TemporaryDirectory() as mapnaam:
            pad = Path(mapnaam)/"sub/log.html"
            log = TijdstapLog(self.master,stap=.3,einde=1)
            self.assertEqual(pad.resolve(), log.schrijf(pad))
            html = pad.read_text(encoding="utf-8")
            self.assertNotIn(vijandig, html)
            data = json.loads(LogData(html).data)
            self.assertEqual(vijandig, data["meta"]["titel"])
            self.assertEqual(5, len(data["stappen"]))
            self.assertEqual(vijandig, data["stappen"][0]["context"]["titel"])
            for r in data["stappen"]:
                self.assertIn("<svg",r["visualisatie"])
                self.assertIn("<math",r["symbolisch"][0]["mathml"])
            self.assertNotIn("__LOGDATA__", html)

    def test_ongeldig_document_uitvoerpad_en_atomiciteit(self):
        ongeldig = self.validator.valideer(DocumentParser().parse(ROOT/"voorbeelden/ongeldig.txt"))
        with self.assertRaises(ValueError):
            TijdstapLog(ongeldig)
        with tempfile.TemporaryDirectory() as mapnaam:
            pad=Path(mapnaam)/"log.txt"
            with self.assertRaises(ValueError):
                TijdstapLog(self.master,einde=0).schrijf(pad)
            self.assertFalse(pad.exists())
            pad=Path(mapnaam)/"log.html"
            self.master.pad=pad
            pad.write_text("bewaren")
            with self.assertRaises(ValueError):
                TijdstapLog(self.master,einde=0).schrijf(pad)
            self.assertEqual("bewaren",pad.read_text())

    def test_cli_log_en_foutcode(self):
        with tempfile.TemporaryDirectory() as mapnaam:
            pad=Path(mapnaam)/"log.html"
            with redirect_stdout(StringIO()) as uitvoer:
                code=main(["log",str(self.master.pad),"--stap",".5","--tot","1","--uitvoer",str(pad)])
            self.assertEqual(0,code,uitvoer.getvalue())
            self.assertTrue(uitvoer.getvalue().isascii())
            self.assertEqual(3,len(json.loads(LogData(pad.read_text()).data)["stappen"]))
            with redirect_stdout(StringIO()):
                self.assertEqual(2,main(["log",str(self.master.pad),"--stap","0"]))


if __name__ == "__main__":
    unittest.main()
