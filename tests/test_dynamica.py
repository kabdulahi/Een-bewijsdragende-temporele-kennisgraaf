import math
import unittest
from taal.dynamica import CoherenteOscillator


class DynamicaTests(unittest.TestCase):
    def test_klassieke_baan_en_energie(self):
        model = CoherenteOscillator(1.5, 0, 1)
        kwart = model.toestand(math.pi/2)
        self.assertAlmostEqual(0, kwart["q"])
        self.assertAlmostEqual(-1.5, kwart["p"])
        for tijd in (0, .5, 12, 300):
            s = model.toestand(tijd)
            self.assertAlmostEqual(2.25, s["q"]**2 + s["p"]**2)
            self.assertAlmostEqual(1.625, s["energie"])
            self.assertEqual(.5, s["onzekerheidsproduct"])

    def test_normalisatie_gemiddelde_en_variantie(self):
        model = CoherenteOscillator(2, -1)
        dx = .01
        punten = [(-12 + i*dx) for i in range(2401)]
        for t in (0, 250):
            waarden = [abs(model.golffunctie(x, t))**2 for x in punten]
            norm = sum(waarden)*dx
            gemiddelde = sum(x*y for x,y in zip(punten,waarden))*dx
            var = sum((x-gemiddelde)**2*y for x,y in zip(punten,waarden))*dx
            self.assertAlmostEqual(1, norm, places=8)
            self.assertAlmostEqual(model.toestand(t)["q"], gemiddelde, places=8)
            self.assertAlmostEqual(.5, var, places=8)

    def test_schrodingervergelijking_inclusief_globale_fase(self):
        model = CoherenteOscillator(1.5, -.7, 1)
        dt = dx = 1e-4
        for x, t in ((.2, .8), (1.4, 2.2), (-1, 5)):
            psi = model.golffunctie(x,t)
            links = 1j*(model.golffunctie(x,t+dt)-model.golffunctie(x,t-dt))/(2*dt)
            rechts = -.5*(model.golffunctie(x+dx,t)-2*psi+model.golffunctie(x-dx,t))/dx**2 + .5*x*x*psi
            self.assertLess(abs(links-rechts), 1e-6)

    def test_ongeldige_parameters_en_tijd(self):
        for args in ((math.nan,0,1),(5,0,1),(0,0,0),(0,0,2)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                CoherenteOscillator(*args)
        for t in (-1, math.inf):
            with self.assertRaises(ValueError):
                CoherenteOscillator().toestand(t)

    def test_symbolische_toestand_en_grondtoestand(self):
        model = CoherenteOscillator(0,0,1)
        self.assertAlmostEqual(math.pi**(-.25), abs(model.golffunctie(0,3)))
        self.assertAlmostEqual(-math.pi**(-.25), model.golffunctie(0,2*math.pi).real)
        self.assertIn("exp(-i*tau/2)", model.symbolisch()["psi"])


if __name__ == "__main__":
    unittest.main()
