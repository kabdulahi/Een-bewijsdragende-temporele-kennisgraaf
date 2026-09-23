# Docentnotities en bronnen bij het quantumcollege

Het college in quantumcomputing.txt.invoer is geschreven voor 4 vwo en duurt 60 minuten. De tien aaneengesloten fasen bevatten uitleg, zelfstandig rekenen, overleg en controles met verwachte antwoorden. De tekst is een spreekleidraad: laat de genoemde denktijd en oefentijd daadwerkelijk beschikbaar. Alle opdrachten, rekenkeuzes, werkvormen en het verzonnen meetverslag zijn voor deze les geformuleerd.

Benodigd: papier, pen, bord en een rekenmachine in gradenstand. Veronderstelde voorkennis: breuken, kwadraten, vierkantswortels, kansen en de sinus en cosinus van 30 graden. Geef zo nodig cos(30 graden) = sqrt(3)/2 en sin(30 graden) = 1/2 vooraf. Complexe amplitudes worden erkend, maar de berekeningen beperken zich tot reële getallen. Relatieve fase wordt uitgelegd met tekens en de Blochbol.

De broncontrole is uitgevoerd op 22 september 2026. De onderstaande primaire bronnen onderbouwen de technische begrippen; de les bevat geen letterlijk overgenomen passages. Links staan apart zodat ze de formele instructies en de leesbare lesweergave niet onderbreken.

| Lesdeel | Technische onderbouwing |
| --- | --- |
| 0-5 minuten: kader | Quantumtoestanden, metingen en bewerkingen als wiskundig model: [IBM Quantum Learning, Single systems: Introduction](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/introduction). |
| 5-11 minuten: bits en onzekerheid | Klassieke waarden en kansbeschrijvingen: [IBM Quantum Learning, Classical information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/classical-information). |
| 11-18 minuten: amplitudes | Toestandsvectoren, normalisatie en de Bornregel: [IBM Quantum Learning, Quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information). |
| 18-24 minuten: ruimtelijk beeld | Blochcoördinaten en relatieve fase: [IBM Quantum Learning, Superposition with Qiskit](https://quantum.cloud.ibm.com/learning/en/modules/quantum-mechanics/superposition-with-qiskit). |
| 24-31 minuten: H | De Hadamardmatrix, waaruit de gebruikte rekenregel volgt: [IBM Quantum Documentation, HGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.HGate). |
| 31-38 minuten: Z en interferentie | Faseomkering door de Z-matrix: [IBM Quantum Documentation, ZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.ZGate). De uitkomsten van H, H en H, Z, H zijn in de les stap voor stap afgeleid. |
| 38-45 minuten: het Bellcircuit | Poortvolgorde, circuitnotatie en het maken van een Belltoestand: [IBM Quantum Learning, Circuits](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/circuits). |
| 38-45 minuten: samenhang | Gezamenlijke quantumtoestanden en verstrengeling: [IBM Quantum Learning, Multiple systems: Quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information). |
| 38-45 minuten: afzonderlijke qubits | Waarom een deel van een Bellpaar geen zuivere Blochpijl krijgt: [IBM Quantum Learning, Multiple systems and reduced states](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/multiple-systems). |
| 38-45 minuten: communicatie | Verstrengeling in een protocol dat ook klassieke communicatie vereist: [IBM Quantum Learning, Quantum Teleportation](https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-teleportation). |
| 45-51 minuten: meetrondes | Afzonderlijke metingen en frequenties bij verschillende aantallen shots: [IBM Quantum Learning, Stern-Gerlach measurements with Qiskit](https://quantum.cloud.ibm.com/learning/en/modules/quantum-mechanics/stern-gerlach-measurements-with-qiskit). |
| 45-51 minuten: uitkomstgegevens | Resultaten als samples van een circuituitvoer: [IBM Quantum Documentation, Sampler inputs and outputs](https://quantum.cloud.ibm.com/docs/en/guides/sampler-input-output). |
| 45-51 minuten: foutanalyse | Fouten en onzekerheden bij quantumsimulaties: [U.S. Department of Energy, Mitigating errors in analog quantum simulations](https://www.energy.gov/science/articles/scientists-take-important-step-toward-mitigating-errors-analog-quantum-simulations). |
| 51-57 minuten: zoeken | Orakelaanroepen en de vierkantswortelschaal: [IBM Quantum Learning, Grover's algorithm description](https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/grover-algorithm/grover-algorithm-description). |
| 51-57 minuten: moleculen | Quantumchemie als onderzoekstoepassing: [U.S. Department of Energy, Quantum Computing: Learning to Speak a Whole New Technology](https://www.energy.gov/science/articles/quantum-computing-learning-speak-whole-new-technology). |

Bij het presenteren gelden de volgende afspraken:

- **Lesklok:** de tijdlijn geeft onderwijstijd aan. De navigatie of animatie is geen simulatie van werkelijke poortduur of van de bewegingsvergelijking van een quantumapparaat.
- **Ruimte:** een camera draaien verandert de afbeelding, niet de quantumtoestand. De bol is een toestandskaart. Een pijl op het oppervlak beschrijft hier uitsluitend een zuivere toestand van een enkele qubit.
- **Fasetoestand:** de bol bij 24-31 minuten toont de toestand na de eerste H, en bij 31-38 minuten die na H en Z. De laatste H en de eindmeting worden in de opdrachten doorgerekend. Alle ingevoerde hoeken zijn in graden.
- **Bellpaar:** het gezamenlijke uitkomstenbeeld is geen verzameling van twee zuivere Blochvectoren. Correlatie in de 0/1-basis toont op zichzelf geen verstrengeling aan; daarvoor zijn aanvullende meetinstellingen nodig.
- **Volgorde:** de les schrijft de qubits als A gevolgd door B. Dat is een expliciete lesafspraak; Qiskit hanteert bij standaardlabels een andere tekenvolgorde. Er wordt in deze les geen Qiskit-code uitgevoerd.
- **Kansen:** percentages zijn ideale voorspellingen tenzij uitdrukkelijk als verzonnen meetgegevens aangeduid. Eindige aantallen shots hoeven niet precies de theoretische verhouding te hebben.
- **Reikwijdte:** de ingebouwde documentzoekmachine is klassiek. De Groverpassage beschrijft een algoritmisch schaalvoordeel onder voorwaarden, geen snelheidsclaim over dit programma.

De laatste drie minuten leveren een korte formatieve beoordeling op. Let op drie criteria: amplitude en meetkans onderscheiden; het effect van een fasebewerking aan een berekening koppelen; een toepassing noemen met een relevante beperking. Gebruik de afsluitende antwoorden om een volgende les te kiezen: herhaling van meetkansen, extra circuits of een experiment met verschillende meetbasissen.
