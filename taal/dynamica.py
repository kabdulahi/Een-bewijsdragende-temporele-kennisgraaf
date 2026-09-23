"""Exacte coherente harmonische oscillator in dimensieloze eenheden.

hbar = m = omega = 1; tau = modeltempo * collegetijd_in_seconden.
De oplossing bevat ook de globale fase, zodat de Schrodingervergelijking geldt.
"""
import cmath
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CoherenteOscillator:
    q0: float = 1.5
    p0: float = 0.0
    modeltempo: float = 0.01

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.q0, self.p0, self.modeltempo)):
            raise ValueError("Modelparameters moeten eindig zijn.")
        if abs(self.q0) > 4 or abs(self.p0) > 4 or not 0 < self.modeltempo <= 1:
            raise ValueError("Beginpositie en beginimpuls moeten binnen [-4, 4] liggen; modeltempo binnen (0, 1].")

    @classmethod
    def uit_document(cls, document):
        if not document.is_transcript or not document.geldig:
            raise ValueError("De modeltoestand vereist een geldig transcript.")
        return cls(float(document.velden["Beginpositie"]), float(document.velden["Beginimpuls"]),
                   float(document.velden["Modeltempo"]))

    def toestand(self, collegetijd: float) -> dict:
        if not math.isfinite(collegetijd) or collegetijd < 0:
            raise ValueError("De collegetijd moet eindig en niet-negatief zijn.")
        tau = self.modeltempo * collegetijd
        q = self.q0 * math.cos(tau) + self.p0 * math.sin(tau)
        p = self.p0 * math.cos(tau) - self.q0 * math.sin(tau)
        return {"collegetijd": collegetijd, "tau": tau, "q": q, "p": p,
                "alpha_re": q / math.sqrt(2), "alpha_im": p / math.sqrt(2),
                "energie": (self.q0**2 + self.p0**2 + 1) / 2,
                "variantie_q": 0.5, "variantie_p": 0.5,
                "onzekerheidsproduct": 0.5, "norm": 1.0}

    def golffunctie(self, x: float, collegetijd: float) -> complex:
        if not math.isfinite(x):
            raise ValueError("De positie moet eindig zijn.")
        s = self.toestand(collegetijd)
        return math.pi**(-0.25) * cmath.exp(-(x-s["q"])**2 / 2
                                          + 1j * (s["p"] * (x-s["q"]/2) - s["tau"]/2))

    def symbolisch(self) -> dict[str, str]:
        return {
            "H": "H_hat = (p_hat^2 + q_hat^2)/2 = adag*a + 1/2",
            "commutator": "[q_hat, p_hat] = i*I ; [a, adag] = I",
            "U": "U(tau) = exp(-i*tau*H_hat)",
            "alpha": f"alpha(tau) = ({self.q0:g} + i*{self.p0:g})/sqrt(2) * exp(-i*tau)",
            "psi": "|psi(tau)> = exp(-i*tau/2) |alpha(0)*exp(-i*tau)>",
            "golffunctie": "psi(x,tau) = pi^(-1/4)*exp(-(x-q(tau))^2/2)*exp(i*(p(tau)*(x-q(tau)/2)-tau/2))",
            "rho": "rho(tau) = |psi(tau)><psi(tau)| = U(tau)*rho(0)*U(tau)^dagger",
            "q": f"q(tau) = {self.q0:g}*cos(tau) + {self.p0:g}*sin(tau)",
            "p": f"p(tau) = {self.p0:g}*cos(tau) - {self.q0:g}*sin(tau)",
            "W": "W(x,k;tau) = exp(-(x-q(tau))^2-(k-p(tau))^2)/pi",
            "kansdichtheid": "|psi(x,tau)|^2 = exp(-(x-q(tau))^2)/sqrt(pi)",
            "E": "<H_hat> = (q0^2+p0^2+1)/2 ; Deltaq*Deltap = 1/2",
            "tau": f"tau = {self.modeltempo:g} * collegetijd_in_seconden",
        }
