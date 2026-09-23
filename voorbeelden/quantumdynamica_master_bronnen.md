# Van klassieke dynamica naar quantumdynamica

Dit is een oorspronkelijk geschreven hoorcollegetranscript in Standaardnederlands voor wo-masterniveau, geen vertaling van een bestaande opname. Het bestand `quantumdynamica_master.txt.invoer` bevat gesproken doorlopende tekst, formules en expliciete stiltes. Het bevat geen opdrachten, werkvormen of docentaanwijzingen.

## Niveau en afbakening

Voorkennis: Hamilton- en Euler-Lagrangevergelijkingen, complexe lineaire algebra, differentiaalvergelijkingen en elementaire quantummechanica. De verdieping zit in de relatie tussen symplectische structuur en commutatoren, operatorendomeinen, zelfgeadjungeerdheid, operatorordening, het onderscheid tussen Schrödinger- en Heisenbergbeeld, exacte coherente dynamica, momenthiërarchieën, de Wigner/Weyltransformatie, Moyalcorrecties en stationaire fase.

Het is één samenhangend uur, geen volledige mastercursus. De opmerkingen over anharmoniciteit, open systemen, vele vrijheidsgraden en padintegralen plaatsen het exact doorgerekende model in zijn context. Ze zijn geen aanvullende door de animatie uitgevoerde simulaties.

## Spreektempo en controleerbare duur

De tekst bevat **6594 gesproken woorden** volgens de programmaregel: alle waarden achter `Tekst:` samenvoegen en op witruimte splitsen. Koppen, formules, symbolen en metadata tellen niet mee. De voor begrip noodzakelijke betekenis van de formules is daarom ook in de spreektekst uitgewerkt.

Bij **120 woorden per minuut** duurt de gesproken tekst 3297 seconden: **54 minuten en 57 seconden**. Elf stiltes van 25 seconden en één slotstilte van 28 seconden duren samen 303 seconden: **5 minuten en 3 seconden**. De geplande presentatie duurt daarmee exact **3600 seconden**.

Dit is een deterministische tijdsbegroting, geen meting van een geluidsopname. Een menselijke spreker kan tempo, uitspraak en natuurlijke adempauzes anders verdelen. Formuleringen met samengestelde woorden en wiskundige notatie tellen volgens bovenstaande lexicale regel, niet volgens een fonetisch model. De opgegeven stiltes zijn onderdeel van de geplande zestig minuten.

| Fragment | Inhoud | Woorden | Collegetijd inclusief slotstilte | Stilte |
| --- | --- | ---: | --- | ---: |
| 1 | Van een klassieke baan naar een quantumtoestand | 509 | 00:00–04:39.5 | 25 s |
| 2 | Hamiltonstructuur en de stroom in de faseruimte | 519 | 04:39.5–09:24 | 25 s |
| 3 | Canonieke kwantisatie, operatoren en hun domeinen | 523 | 09:24–14:10.5 | 25 s |
| 4 | Unitaire evolutie en het Heisenbergbeeld | 504 | 14:10.5–18:47.5 | 25 s |
| 5 | Het spectrum van de oscillator en dimensieloze eenheden | 503 | 18:47.5–23:24 | 25 s |
| 6 | Coherente toestanden en de volledige golffunctie | 577 | 23:24–28:37.5 | 25 s |
| 7 | De berekende modeltoestand en haar drie representaties | 516 | 28:37.5–33:20.5 | 25 s |
| 8 | Ehrenfest, momentvergelijkingen en anharmoniciteit | 518 | 33:20.5–38:04.5 | 25 s |
| 9 | Dichtheidsoperator, correlaties en meetbare informatie | 656 | 38:04.5–43:57.5 | 25 s |
| 10 | Wignerrepresentatie, Moyalhaakje en de klassieke limiet | 576 | 43:57.5–49:10.5 | 25 s |
| 11 | Actie, padintegralen en stationaire fase | 576 | 49:10.5–54:23.5 | 25 s |
| 12 | Wat het model verklaart en hoe de beschrijvingen samenhangen | 617 | 54:23.5–60:00 | 28 s |

## Exact model en de twee klokken

Het quantummechanische model is één gesloten harmonische oscillator op de gehele reële lijn. Er is geen interactie met een omgeving en er vindt geen toestandsreducerende meting plaats.

De dimensionale grootheden worden als volgt geschaald:

```text
ell = sqrt(hbar/(m*omega))
q_dimensionless = x_physical/ell
p_dimensionless = p_physical/sqrt(m*hbar*omega)
H_dimensionless = H_physical/(hbar*omega)
tau = omega*t_physical
```

De visualisatie gebruikt vervolgens numeriek `hbar = m = omega = 1`. Dit zijn eenheidskeuzen, geen fysieke waarden in SI-eenheden. De didactische koppeling is afzonderlijk vastgelegd:

```text
tau = 0.01*t_college
0 <= t_college <= 3600 seconden
0 <= tau <= 36
```

De factor 0.01 is een gekozen presentatieschaal en geen natuurkundige constante. Eén oscillatorperiode van `2*pi` modeltijd beslaat ongeveer 628.319 seconden collegetijd. De tijdlijn doorloopt circa 5.730 perioden.

## Formules en onafhankelijke controles

Voor `q0 = 1.5` en `p0 = 0` is de gebruikte exacte oplossing:

```text
q(tau) = 1.5*cos(tau)
p(tau) = -1.5*sin(tau)
alpha(tau) = (q(tau) + i*p(tau))/sqrt(2)
psi(x,tau) = pi^(-1/4)
             * exp(-(x-q(tau))^2/2)
             * exp(i*(p(tau)*(x-q(tau)/2)-tau/2))
rho(tau) = |psi(tau)><psi(tau)|
W(x,k,tau) = exp(-(x-q(tau))^2-(k-p(tau))^2)/pi
```

Hier zijn `x,k` vrije fasecoördinaten; `q,p` zijn de centra. De globale fase in `psi` is nodig voor de exacte Schrödingeroplossing in deze conventie. Ze valt weg uit `rho`, de dichtheid en de meetkansen.

```text
dq/dtau = p
dp/dtau = -q
q^2+p^2 = 2.25
<q_hat> = q
<p_hat> = p
(Deltaq)^2 = (Deltap)^2 = 0.5
C_qp = 0
<H> = (q^2+p^2)/2 + 0.5 = 1.625
|alpha|^2 = 1.125
Var(H) = 1.125
Tr(rho) = Tr(rho^2) = 1
psi(tau+2*pi) = -psi(tau)
rho(tau+2*pi) = rho(tau)
```

De fysieke configuratieruimte heeft **één dimensie**. De grafiek `(x, Re psi, Im psi)` heeft drie tekenassen, maar voegt geen fysieke vrijheidsgraden toe. Een fasegrafiek heeft positie en impuls als assen; een dichtheidshoogte is evenmin een extra ruimtelijke coördinaat.

De Poissonconventie is `{f,g}=f_q*g_p-f_p*g_q`. Daarmee is de toestandsvergelijking `partial_t W={H,W}_M` en, voor een gladde positiepotentiaal, de eerste correctie op de Liouvilleterm:

```text
partial_t W = {H,W} - (hbar^2/24)*V'''(q)*partial_p^3 W + O(hbar^4)
```

Het minteken hoort bij deze expliciet genoemde volgorde. Voor een kwadratische Hamiltoniaan verdwijnen de hogere afgeleiden exact. Dat maakt het transport van W klassiek, maar heft de quantumvoorwaarden aan toegestane toestanden en operatorproducten niet op.

## Geraadpleegde primaire bronnen

De tekst en voorbeelden zijn oorspronkelijk geformuleerd. Onderstaande bronnen zijn geraadpleegd voor de technische conventies en als verdiepende verwijzingen; er zijn geen passages uit overgenomen. Geraadpleegd op 22 september 2026.

- David Tong, [Classical Dynamics, hoofdstuk 4: The Hamiltonian Formalism](https://www.damtp.cam.ac.uk/user/tong/dynamics/dynhtml/S4.html). Met name paragrafen 4.3 en 4.8 voor Poissonhaakjes en de relatie met quantummechanica.
- Barton Zwiebach, MIT 8.05, [Quantum Dynamics, Lecture Notes 6](https://ocw.mit.edu/courses/8-05-quantum-physics-ii-fall-2013/79a8091ef4f18d8e3ff76a097e8db33c_MIT8_05F13_Chap_06.pdf), 2013. Referentie voor de oscillatoralgebra, unitaire evolutie, Heisenbergbeeld, coherente en geknepen toestanden.
- MIT 22.51, [Quantum Theory of Radiation Interactions: Complete Course Notes](https://ocw.mit.edu/courses/22-51-quantum-theory-of-radiation-interactions-fall-2012/693972cea9cf9da5e4e9e86fbc72c9e7_MIT22_51F12_Notes.pdf), 2012. Verdieping bij dichtheidsoperatoren, open systemen en oscillatorrepresentaties.
- Anatoli Polkovnikov, [Phase space representation of quantum dynamics](https://arxiv.org/abs/0905.3384), arXiv:0905.3384. Met name de definities van Weylsymbolen en Moyalproducten en de vergelijking met klassieke fase-evolutie; de tekens zijn afgestemd op de expliciete Poissonconventie hierboven.
- Richard P. Feynman, [Space-Time Approach to Non-Relativistic Quantum Mechanics](https://authors.library.caltech.edu/records/9h858-5hv71), Reviews of Modern Physics 20, 367–387 (1948), DOI 10.1103/RevModPhys.20.367. Primaire historische bron voor de amplitudeformulering met paden en actie.
