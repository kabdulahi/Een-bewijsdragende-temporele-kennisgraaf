"""Zelfstandige SVG-momentopnamen van de bestaande onderwijsmodellen.

Alle beelden zijn rechtstreeks uit een modeltoestand afgeleid. Een lesfase
is een statisch didactisch voorbeeld: er wordt geen tijdsevolutie verzonnen.
"""
from html import escape
import math

from .dynamica import CoherenteOscillator
from .model import Fase


class LogBeelden:
    """Kleine SVG's die zonder JavaScript of externe bestanden werken."""

    @staticmethod
    def _tekst(x: float, y: float, inhoud: str, **attributen: str) -> str:
        extra = "".join(f' {naam.replace("_", "-")}="{escape(str(waarde), quote=True)}"'
                        for naam, waarde in attributen.items())
        return f'<text x="{x:g}" y="{y:g}"{extra}>{escape(str(inhoud))}</text>'

    @staticmethod
    def _lijn(punten, kleur="#607887", breedte=1, klasse="") -> str:
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in punten)
        return (f'<polyline class="{klasse}" points="{coords}" fill="none" '
                f'stroke="{kleur}" stroke-width="{breedte}"/>')

    @staticmethod
    def _svg(titel: str, onderdelen: list[str]) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 260" '
            f'role="img" aria-label="{escape(titel, quote=True)}">'
            f'<title>{escape(titel)}</title>'
            '<rect width="720" height="260" rx="10" fill="#10232e"/>'
            '<g font-family="system-ui, sans-serif" font-size="12" fill="#e0edf0">'
            + "".join(onderdelen) + '</g></svg>'
        )

    @staticmethod
    def oscillator(model: CoherenteOscillator, tijd: float) -> str:
        """Projecteer (x, Re psi, Im psi) en toon |psi|^2 op dezelfde x-schaal.

        De positie-as bestrijkt steeds de volledige baan plus drie
        dimensieloze lengte-eenheden aan elke kant; er is geen automatische
        herschaling per tijdstap. Ook de globale fase komt uit golffunctie().
        """
        s = model.toestand(tijd)
        grens = max(4.0, math.hypot(model.q0, model.p0) + 3)
        xs = [-grens + 2 * grens * i / 120 for i in range(121)]
        psi = [model.golffunctie(x, tijd) for x in xs]

        def project(x, re=0.0, im=0.0):
            return 214 + 154 * x / grens + 42 * re, 133 - 22 * re - 65 * im

        def dichtheid(x, waarde):
            return 510 + 180 * (x + grens) / (2 * grens), 201 - 170 * waarde

        stukken = [
            LogBeelden._tekst(18, 22, "Golffunctie: projectie van (x, Re ψ, Im ψ)"),
            LogBeelden._tekst(480, 22, "Kansdichtheid |ψ(x, τ)|²"),
            LogBeelden._lijn([project(-grens), project(grens)]),
            LogBeelden._lijn([project(0, -1), project(0, 1)]),
            LogBeelden._lijn([project(0, 0, -1), project(0, 0, 1)]),
            LogBeelden._tekst(373, 137, "x"),
            LogBeelden._tekst(260, 109, "Re ψ"),
            LogBeelden._tekst(220, 63, "Im ψ"),
            LogBeelden._tekst(50, 151, f"{-grens:.2f}"),
            LogBeelden._tekst(356, 151, f"{grens:.2f}"),
            LogBeelden._lijn([project(x, z.real, z.imag) for x, z in zip(xs, psi)],
                            "#99e9bf", 2, "golffunctie"),
            LogBeelden._lijn([dichtheid(-grens, .65), dichtheid(-grens, 0),
                              dichtheid(grens, 0)]),
            LogBeelden._tekst(694, 205, "x"),
            LogBeelden._tekst(502, 219, f"{-grens:.2f}"),
            LogBeelden._tekst(675, 219, f"{grens:.2f}"),
        ]
        for waarde in (0, .3, .6):
            x, y = dichtheid(-grens, waarde)
            stukken += [LogBeelden._lijn([(x-3, y), (x+3, y)]),
                        LogBeelden._tekst(x-30, y+4, f"{waarde:g}")]
        stukken += [
            LogBeelden._lijn([dichtheid(x, abs(z)**2) for x, z in zip(xs, psi)],
                            "#eec58b", 2, "kansdichtheid"),
            LogBeelden._tekst(18, 212, f"q = {s['q']:.4f}   p = {s['p']:.4f}   τ = {s['tau']:.4f}"),
            LogBeelden._tekst(18, 232, "Vaste asschalen; de projectie behoudt ook de globale fase."),
            LogBeelden._tekst(18, 251, "ℏ = m = ω = 1; dichtheid is per eenheid x; totale kans = 1."),
        ]
        return LogBeelden._svg(
            f"Coherente oscillator op collegetijd {tijd:g} s: golffunctie en kansdichtheid",
            stukken,
        )

    @staticmethod
    def _bol(cx: float, cy: float, straal: float, toestand=None) -> list[str]:
        """Orthografische projectie met orthonormale camera-assen."""
        yaw, pitch = -.45, .23

        def project(x, y, z):
            horizontaal = math.cos(yaw)*x + math.sin(yaw)*y
            diepte = -math.sin(yaw)*x + math.cos(yaw)*y
            verticaal = math.cos(pitch)*z - math.sin(pitch)*diepte
            return cx + straal*horizontaal, cy - straal*verticaal

        delen = [f'<circle cx="{cx:g}" cy="{cy:g}" r="{straal:g}" '
                 'fill="none" stroke="#607887"/>']
        for vlak in range(3):
            punten = []
            for i in range(25):
                a = 2*math.pi*i/24
                p = [(math.cos(a), math.sin(a), 0),
                     (math.cos(a), 0, math.sin(a)),
                     (0, math.cos(a), math.sin(a))][vlak]
                punten.append(project(*p))
            delen.append(LogBeelden._lijn(punten, "#355461"))
        for p, label in (((1.18,0,0), "x"), ((0,1.18,0), "y"), ((0,0,1.18), "z")):
            eind = project(*p)
            delen += [LogBeelden._lijn([project(*(-v for v in p)), eind]),
                      LogBeelden._tekst(eind[0]+4, eind[1]-2, label)]
        if toestand is not None:
            x, y = project(*toestand)
            delen += [LogBeelden._lijn([(cx, cy), (x, y)], "#99e9bf", 3),
                      f'<circle class="blochtoestand" cx="{x:.3f}" cy="{y:.3f}" '
                      'r="5" fill="#99e9bf"/>']
        return delen

    @staticmethod
    def _kansen(kansen: list[tuple[str, float]], x=500, y=70) -> list[str]:
        delen = []
        for i, (label, waarde) in enumerate(kansen):
            rij = y + 35*i
            delen += [
                LogBeelden._tekst(x-68, rij+11, label),
                f'<rect x="{x}" y="{rij}" width="125" height="13" fill="#294452"/>',
                f'<rect class="kans" x="{x}" y="{rij}" width="{125*waarde:.3f}" '
                'height="13" fill="#eec58b"/>',
                LogBeelden._tekst(x+132, rij+11, f"{100*waarde:g}%"),
            ]
        return delen

    @staticmethod
    def lesfase(fase: Fase) -> str:
        """Toon de vastgelegde fase; lesduur is geen fysieke evolutietijd."""
        stukken = [LogBeelden._tekst(18, 22, fase.titel[:96])]
        if fase.beeld == "bloch":
            theta, phi = math.radians(fase.theta), math.radians(fase.phi)
            xyz = (math.sin(theta)*math.cos(phi), math.sin(theta)*math.sin(phi),
                   math.cos(theta))
            stukken += LogBeelden._bol(210, 134, 76, xyz)
            stukken += LogBeelden._kansen([
                ("P(0)", math.cos(theta/2)**2), ("P(1)", math.sin(theta/2)**2)])
            stukken += [
                LogBeelden._tekst(420, 47, f"Zuivere qubit: θ = {fase.theta:g}°, φ = {fase.phi:g}°"),
                LogBeelden._tekst(420, 160, f"(x, y, z) = ({xyz[0]:.3f}, {xyz[1]:.3f}, {xyz[2]:.3f})"),
                LogBeelden._tekst(420, 187, "P(0), P(1): Z-meetkansen"),
            ]
        elif fase.beeld == "bell":
            for cx, naam in ((122, "A"), (324, "B")):
                stukken += LogBeelden._bol(cx, 129, 64, (0,0,0))
                stukken += [LogBeelden._tekst(cx-28, 214, f"Qubit {naam}: I/2")]
            stukken += LogBeelden._kansen(
                [("P(00)", .5), ("P(01)", 0), ("P(10)", 0), ("P(11)", .5)], 505, 68)
            stukken += [LogBeelden._tekst(425, 46, "Bellpaar: (|00⟩ + |11⟩) / √2"),
                        LogBeelden._tekst(421, 217, "Lokale Blochvectoren: (0, 0, 0).")]
        elif fase.beeld == "klassiek":
            stukken += [
                '<circle cx="220" cy="123" r="35" fill="#284c4c"/>',
                '<circle cx="470" cy="123" r="35" fill="#514530"/>',
                LogBeelden._tekst(211, 133, "0", font_size="28"),
                LogBeelden._tekst(461, 133, "1", font_size="28"),
                LogBeelden._tekst(173, 190, "Twee mogelijke bitwaarden; geen superpositie."),
                LogBeelden._tekst(173, 213, "Deze fase legt geen actuele bitwaarde of kans vast."),
            ]
        else:
            stukken += [
                LogBeelden._tekst(40, 78, "Lesstructuur: samenvatting van deze fase"),
                LogBeelden._lijn([(65, 128), (655, 128)], "#99e9bf", 4),
                '<circle cx="65" cy="128" r="6" fill="#99e9bf"/>',
                '<circle cx="655" cy="128" r="6" fill="#99e9bf"/>',
                LogBeelden._tekst(48, 160, f"{fase.start:g} min"),
                LogBeelden._tekst(625, 160, f"{fase.einde:g} min"),
                LogBeelden._tekst(40, 201, "Tijdas van het lesonderdeel; geen fysieke modeltoestand."),
            ]
        stukken += [LogBeelden._tekst(
            18, 246, f"Statisch lesvoorbeeld · fase {fase.start:g}–{fase.einde:g} min · beeld: {fase.beeld}")]
        return LogBeelden._svg(f"Lesfase: {fase.titel}; statisch voorbeeld", stukken)
