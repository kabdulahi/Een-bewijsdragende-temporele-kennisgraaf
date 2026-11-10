# Ophangen

## Auteur en gebruiksvoorwaarden

Auteur: **Karim Abdulahi**. Homepage: [https://karim.1e100.nl/](https://karim.1e100.nl/).
E-mail: [karim.abdulahi@outlook.com](mailto:karim.abdulahi@outlook.com).

Ophangen heeft een eigen restrictieve
[licentie voor niet-commercieel wetenschappelijk onderzoek](LICENSE).
Je mag de bron lezen en een noodzakelijke privékopie downloaden of klonen om
het programma lokaal voor dat onderzoek uit te voeren. Instellingen kiezen en
eigen onderzoeksinvoer aanbieden via de bestaande interfaces zijn toegestaan.
Presentaties en logs maken, opslaan en bekijken voor dat eigen onderzoek mag ook.
Wijzigen, verspreiden, hergebruiken in andere projecten, aanbieden als dienst
en commercieel gebruik vereisen voorafgaande schriftelijke toestemming.
Eigen bevindingen en numerieke resultaten uit toegestaan softwaregebruik mogen
met naamsvermelding worden gepubliceerd; de licentie bevat de voorwaarden.

Dit is **source-available, geen opensourceproject**:
[opensource staat geen beperking tot een onderzoeksdoel toe](https://opensource.org/osd).
De onderstaande uitvoervoorbeelden vallen onder deze gebruiksvoorwaarden.
Bestaande rechten, wettelijke uitzonderingen en rechten uit toepasselijke
hostingvoorwaarden blijven gelden. Meegeleverde onderdelen van derden behouden
hun eigen licentie; zie [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Afzonderlijke voorwaarden voor onderzoek.pdf

[onderzoek.pdf](onderzoek.pdf), *Een bewijsdragende temporele kennisgraaf*,
vermeldt **Karim Abdulahi** als auteur en rechthebbende op zijn oorspronkelijke
bijdrage. De PDF bevat een auteursvoorblad en auteursmetadata. Voor dit document
gelden de [afzonderlijke inzagevoorwaarden](ONDERZOEK_LICENSE.txt):
uitsluitend persoonlijke inzage voor niet-commerciële wetenschappelijke
doeleinden. Ander gebruik van beschermde inhoud vereist voorafgaande
schriftelijke toestemming, behoudens toepasselijke wettelijke uitzonderingen.
De softwarelicentie en haar toestemming voor eigen softwareonderzoeksresultaten
geven geen aanvullende rechten op dit manuscript.

De huidige PDF is gemarkeerd als **voorpublicatie**. Karim behoudt het recht
zijn eigen oorspronkelijke werk later te herzien en als bachelor- of
masterscriptie aan te bieden. Voor het beoogde BSc-traject Computing Science
aan Radboud moet de opleiding vooraf met het eindproject instemmen; deze
licentie vervangt die goedkeuring niet. De voorwaarden staan verwerking bij
latere schriftelijke indiening toe voor begeleiding, beoordeling,
integriteitscontrole en overeengekomen archivering.
[ONDERZOEK_HERKOMST.md](ONDERZOEK_HERKOMST.md) bevat de geraadpleegde
opleidingsregels, een herkomstverklaring en een conceptverzoek om het
voorgenomen hergebruik schriftelijk af te stemmen.

Wetenschappelijke feiten en ideeën op zichzelf worden hiermee geen exclusief
eigendom; auteursrecht beschermt de oorspronkelijke uitwerking.
[Uitleg van de Federatie Auteursrechtbelangen](https://www.auteursrecht.nl/auteursrecht/wat-wordt-niet-beschermd).
Voor aanvullende afspraken over gebruik van verstrekte onderzoeksinformatie
staat een [nog te ondertekenen inzageovereenkomst](ONDERZOEK_INZAGEOVEREENKOMST.txt)
klaar. Deze moet vooraf daadwerkelijk worden overeengekomen. De repository
bevat geen toegangsscherm dat instemming vastlegt; een openbare PDF wordt door
deze documenten niet achteraf vertrouwelijk. Voor vertrouwelijke verstrekking
is gecontroleerde toegang nodig, na aanvaarding van de overeenkomst.

[onderzoek.rechten.json](onderzoek.rechten.json) registreert de voor- en
naversie met SHA-256, paginatallen en de toegevoegde vermeldingen. Dit is lokale
versie-identificatie, geen onafhankelijke tijdstempel of bewijs van auteurschap.
Bewaar oorspronkelijke bronbestanden en ontstaansgeschiedenis.
Een [i-DEPOT](https://ondernemersplein.overheid.nl/product-dienst-en-innovatie/idee-vastleggen-en-beschermen/uw-idee-vastleggen/)
kan helpen een bestaansdatum vast te leggen, maar vestigt geen eigendomsrecht.
Laat de rechtenpositie en de overeenkomst vóór gebruik juridisch beoordelen.

Ophangen leest een formele Nederlandse instructietaal, controleert lesdocumenten
en maakt een interactieve lespresentatie. Python 3.11 of hoger en uv zijn nodig.
De kern gebruikt de standaardbibliotheek; de logexport gebruikt daarnaast
latex2mathml, dat lokaal wordt meegeleverd en via uv wordt geïnstalleerd.
Presentaties en logs werken offline in een moderne browser, zonder server of
externe webbestanden.

## HTML-log per tijdstap

De opdracht **log** schrijft een zelfstandig HTML-bestand met alle gekozen
tijdstappen. Elke logregel bevat de numerieke toestand, een opgeslagen SVG en
de symbolische modeltoestand als geparseerde LaTeX (MathML).

~~~bash
cd ophangen
./setup.sh
./run.sh log voorbeelden/quantumdynamica_master.txt.invoer --stap 1 --uitvoer logs/quantumdynamica_master.html
./run.sh log voorbeelden/quantumcomputing.txt.invoer --stap 60 --uitvoer logs/quantumcomputing.html
~~~

Een volledig uur met stap 1 levert **3601 snapshots**, inclusief 0 en 3600
seconden. Een uur met stap 60 levert 61 snapshots. Een voorbeeldlog van beide
documenten staat in logs/. Open de HTML in een moderne browser; --open probeert
dit automatisch. In WSL kun je het bestand ook via de bestandsverkenner openen.

Voor een kleiner tijdvak of een decimale stap:

~~~bash
./run.sh log voorbeelden/quantumdynamica_master.txt.invoer --van 900 --tot 960 --stap 0.5 --uitvoer logs/detail.html
~~~

--van, --tot en --stap gebruiken collegeseconden. De stap is standaard 1 en
moet positief zijn. Begin en einde moeten binnen de collegeduur liggen.
De eindtijd wordt altijd eenmaal opgenomen, ook als de laatste stap korter is.
Er worden maximaal 10001 snapshots per bestand geschreven. Een gelijk begin
en einde levert één snapshot. Zonder --uitvoer verschijnt een .log.html naast
het invoerbestand. Bestaande uitvoer wordt pas vervangen wanneer de volledige
export succesvol is geschreven.

De browser toont één opgeslagen record tegelijk, met Vorige/Volgende, een
tijdstapschuif, direct stapnummer en begin/einde. Alle records staan in de HTML;
de browser berekent het model niet opnieuw. De LaTeX-bron kan per formule worden
uitgeklapt. Met **Download numerieke waarden** exporteer je de opgeslagen
getallen als CSV. Een log met elke seconde van het mastercollege is ongeveer
39 MB, omdat elke stap zijn eigen afbeelding en MathML bewaart. Kies een groter
interval of kleiner tijdvak voor compactere bestanden.

Voor transcripten gebruikt het log dezelfde analytische coherente oscillator
als de presentatie, inclusief globale fase, verwachtingen, varianties, energie
en golffunctiewaarde bij x=0. De visualisatie toont de complexe golf en de
kansdichtheid. Voor de bestaande quantumles worden de Bloch-, Bell- en klassieke
lesbeelden per tijdstap vastgelegd. Binnen een lesfase verandert dat didactische
beeld niet; voor een klassieke bit of lesoverzicht wordt geen quantumtoestand
verzonnen. De symbolische formules beschrijven het model; vrije bordnotities uit
Formule-regels worden niet automatisch vertaald of symbolisch opgelost.

LaTeX wordt tijdens export door
[latex2mathml](https://github.com/roniemartinez/latex2mathml) naar native MathML
geparseerd. Er zijn geen CDN's, webfonts of LaTeX-installatie nodig. De officiële
wheel staat met licentie en hashverantwoording in vendor/ en is via uv.lock
vastgelegd; setup.sh installeert deze offline. Numeriek ingevulde formules ronden
coëfficiënten af op zes decimalen en gebruiken daarom het benaderingsteken.
De gegevens in het log behouden de Python-floatprecisie; de zichtbare tabel
toont maximaal twaalf significante cijfers.

De logexport genereert een berekend tijdsverloop. Het is geen registratie van
browserklikken, camerabewegingen of de werkelijke speeltijd van een sessie.
De SVG's gebruiken een vast gezichtspunt en vaste asschalen, zodat tijdstappen
vergelijkbaar blijven.


## Masterhoorcollege: transcript, model en symbolische toestand

Het nieuwe bestand **voorbeelden/quantumdynamica_master.txt.invoer** bevat een
doorlopend hoorcollegetranscript op wo-masterniveau over de overgang van klassieke
Hamiltoniaanse dynamica naar quantumdynamica. Het bevat gesproken tekst en
afzonderlijke bordformules; er zijn geen leerlingopdrachten of werkvormen.
Bronnen en inhoudelijke conventies staan in
**voorbeelden/quantumdynamica_master_bronnen.md**.

~~~bash
cd ophangen
./setup.sh
./run.sh controleer voorbeelden/quantumdynamica_master.txt.invoer
./run.sh visualiseer voorbeelden/quantumdynamica_master.txt.invoer --uitvoer presentaties/quantumdynamica_master.html --open
~~~

De gegenereerde HTML opent **drie gelijktijdig bedienbare dialoogvensters**:

1. **Transcript en lesstructuur**: de bestaande ruimtelijke lesstructuur, met
   fragmentkeuze en een woordmarkering op spreektempo.
2. **Modeltoestand**: een draaibare 3D-golffunctie, kansdichtheid of faseruimte,
   naast numerieke verwachtingswaarden.
3. **Symbolische toestand**: ketnotatie, golffunctie, operatoren, de gekozen
   symbooldefinitie en de formules bij het huidige fragment.

Alle vensters delen de collegeklok. Ze beginnen gepauzeerd. Vorige, Volgende,
Begin, de tijdschuif en fragmentkeuze zetten de drie weergaven samen naar een
tijdstip. Afspelen ondersteunt 1×, 10× en 60×. Sluiten van een venster pauzeert;
**Open drie vensters** heropent ze met behoud van de tijd. Escape sluit de drie
vensters en pauzeert. Op een klein scherm staan de vensters onder elkaar in een
scrollbaar gebied; de tijdknoppen blijven bereikbaar. Het zijn gelijktijdig
interactieve dialogen, zodat niet alleen het voorste venster bedienbaar is.

Open bijvoorbeeld de weergave op college-minuut vijftien, of vraag de numerieke
en symbolische modeltoestand op in de terminal:

~~~bash
./run.sh visualiseer voorbeelden/quantumdynamica_master.txt.invoer --tijd 900 --uitvoer presentaties/quantumdynamica_master.html --open
./run.sh toestand voorbeelden/quantumdynamica_master.txt.invoer --tijd 900
./run.sh toestand voorbeelden/quantumdynamica_master.txt.invoer --tijd 900 --positie 0 --symbool psi
./run.sh woordenboek --categorie begrip --zoek hamilton
./run.sh woordenboek --categorie symbool --zoek psi
~~~

Tijden bij --tijd zijn **collegeseconden** en moeten binnen de collegeduur vallen.
Het spreektempo is onderdeel van het document. De afspeelsnelheid verandert
alleen hoe snel de klok loopt. Er is geen audio of automatische spraaksynthese.

### Transcriptgrammatica, taalversie 2

Een transcript gebruikt Soort: transcript en heeft geen sectie Instructies of
Tijdlijn nodig. De volgende compacte invoer is geldig en duurt één minuut:
de acht gesproken woorden nemen vier seconden in beslag, gevolgd door 56 seconden
stilte. Het mastervoorbeeld gebruikt uiteraard uitgebreide gesproken alinea's.

~~~text
Titel: Een korte demonstratie
Vak: Natuurkunde
Niveau: wo master
Onderwerp: Hamiltoniaanse dynamica
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
Formule: H = (p^2 + q^2)/2
Symbolen: H, q, p
Pauze: 56 seconden
Einde.
~~~

De vaste Duur-eenheid blijft in deze formele taal altijd minuten, ook bij 1.
Titel, Vak, Niveau, Onderwerp, Duur, Soort, Tempo en de vier modelvelden zijn
verplicht; Leerdoel is bij transcripten optioneel. Een Fragment begint met een
opeenvolgend nummer vanaf 1, een verticale streep en een titel.
Een of meer Tekst-regels bevatten vrije gesproken tekst, elk op één fysieke
regel. Formule mag worden herhaald en blijft veilige, niet-uitgevoerde tekst.
Symbolen is optioneel en bevat unieke, bekende, hoofdlettergevoelige
symboolsleutels, gescheiden door komma's. Een niet-negatieve eindige Pauze in
seconden is verplicht en volgt na het spreekgedeelte van het fragment.
Decimalen gebruiken een punt.

Het programma telt whitespacewoorden uit uitsluitend Tekst-regels:
spreektijd = woordenaantal × 60 / spreektempo. Formules, titels en symbolen
tellen niet mee. Tempo is 50 tot en met 220 woorden/minuut. De totale spreektijd
plus alle pauzes moet de opgegeven Duur tot op 0,01 seconde benaderen.
Dit is een expliciet planningsmodel: werkelijk uitspreken van formules of lange
woorden kan afwijken. De pauzes in het voorbeeld zijn gereserveerd voor het
verwerken van afleidingen. Spreekfragmenten en stiltes blijven apart zichtbaar.

Nieuwe foutcodes: E013/E014 voor transcriptstructuur; T001 voor metadata,
T002 voor tempo, T003 voor fragmenten, T004 voor pauzes, T005 voor totale duur,
T006 voor symbolen en T007 voor het model. Bestaande instructielessen en de
oorspronkelijke quantumcomputingpresentatie blijven ondersteund.

### Analytisch model en symbolen

Het uitvoerbare model is de **coherente harmonische oscillator** in dimensieloze
eenheden met hbar = m = omega = 1. Beginpositie en Beginimpuls liggen elk
binnen [-4, 4]. Modeltempo ligt in (0, 1] en bepaalt de dimensieloze tijd:

~~~text
tau = Modeltempo * collegetijd_in_seconden
q(tau) = q0*cos(tau) + p0*sin(tau)
p(tau) = p0*cos(tau) - q0*sin(tau)
alpha(tau) = (q(tau) + i*p(tau))/sqrt(2)
|psi(tau)> = exp(-i*tau/2) |alpha(0)*exp(-i*tau)>
psi(x,tau) = pi^(-1/4) exp(-(x-q(tau))^2/2)
             * exp(i*(p(tau)*(x-q(tau)/2)-tau/2))
rho(tau) = |psi(tau)><psi(tau)|
~~~

De globale fase is opgenomen. De dichtheid beweegt met het klassieke centrum,
met constante varianties Deltaq² = Deltap² = 1/2 en
energie (q0²+p0²+1)/2. De 3D-golf toont de assen x, Re psi en Im psi.
De faseruimte toont de klassieke baan en contouren van de Wignerfunctie van
deze coherente toestand. Deze Wignerfunctie is positief; dat geldt niet voor
elke quantumtoestand. Het model is exact analytisch en ondersteunt deze
modelklasse; vrije Formule-tekst wordt niet symbolisch opgelost of uitgevoerd.

De symbolische formules en numerieke toestanden zijn gekoppeld aan dezelfde
modelparameters. In het derde venster selecteer je een symbool, bijvoorbeeld
psi, q, p, H of rho. De definitie komt uit het woordenboek. Wanneer het model
voor een begrip geen berekende waarde heeft, wordt dat expliciet vermeld.

### Uitgebreid woordenboek

Naast de bestaande regels werkwoord | betekenis ondersteunt het woordenboek:

~~~text
werkwoord | Integreer | Bepaal een integraal.
begrip | canonieke transformatie | Een transformatie die de symplectische structuur behoudt.
symbool | H | De Hamiltoniaan.
symbool | I | De identiteitsoperator.
symbool | i | De imaginaire eenheid.
~~~

Werkwoorden en begrippen zijn hoofdletterongevoelig; symbolen behouden hun
hoofdletters. I en i zijn dus verschillende symbolen. Het woordenboek is een
uitgebreid vakspecifiek lexicon, geen volledige spellingcontrole van het Nederlands.
De parser controleert alleen gedeclareerde symboolverwijzingen; woorden in vrije
transcriptalinea's hoeven niet allemaal in het lexicon te staan.

Het meegeleverde woordenboek bevat 353 lemma's: 75 werkwoorden, 226 begrippen en
52 symbolen. De Python-tests controleren ook normalisatie, energie en de
Schrödingervergelijking van de coherente toestand. De browsertest
tests/browser_presentatie.ps1 controleert de echte gegenereerde masterpresentatie
in een geïsoleerde Edge-browser op Windows, inclusief JavaScript-initialisatie,
knoppen, tijdgrenzen, numerieke/symbolische synchronisatie en mobiel formaat.
Gebruik na een aanpassing aan het sjabloon zowel de Python-tests als deze
browsertest. Alleen het opnieuw uitvoeren van Python-tests kan een
JavaScript-syntaxfout niet vinden.

Bij een pagina die al openstond tijdens het genereren: vernieuw die pagina om de
opnieuw gegenereerde scripts te laden. Gebruik het echte bestandspad, zonder
Markdown-escape-tekens voor underscores.



## Het college quantumcomputing starten

**voorbeelden/quantumcomputing.txt.invoer** bevat een college van 60 minuten in
tien fasen voor 4 vwo: uitgebreide spreekaantekeningen, uitgewerkte voorbeelden,
oefentijd en docentantwoorden. Bronnen en voorbereiding staan in
**voorbeelden/quantumcomputing_bronnen.md**.

Open **presentaties/quantumcomputing.html** in je browser voor de kant-en-klare
presentatie. Na wijzigingen in de invoer maak je de HTML opnieuw:

~~~bash
cd ophangen
./setup.sh
./run.sh controleer voorbeelden/quantumcomputing.txt.invoer
./run.sh visualiseer voorbeelden/quantumcomputing.txt.invoer --uitvoer presentaties/quantumcomputing.html
~~~

Voeg --open toe om de standaardbrowser te starten. Als WSL geen browser kan
openen, open je het HTML-bestand via de bestandsverkenner. Zonder --uitvoer
verschijnt het HTML-bestand naast de invoer. Een bestaand bestand op het gekozen
uitvoerpad wordt vervangen.

Het dialoogvenster begint gepauzeerd bij 00:00. **Vorige** en **Volgende** springen
naar het begin van een fase; **Begin** zet de klok terug. Je kunt een fase
aanklikken of de tijdschuif verplaatsen. Navigeren pauzeert het afspelen.
**Afspelen/Pauzeren** regelt de klok. Op 1× duurt de les werkelijk 60 minuten,
op 10× zes minuten en op 60× één minuut. Het einde stopt de klok.
Sluiten, Escape of het verbergen van het browsertabblad pauzeert de les.
De tijd blijft behouden bij heropenen. Knoppen en tijdschuif zijn ook met
het toetsenbord bedienbaar.

- **3D-model** toont het beeld bij de huidige fase. Sleep op het canvas om de
  camera te draaien; **Herstel camera** herstelt het gezichtspunt.
- **Lesstructuur** toont fasen als punten in een 3D-tijdlijn, met een bewegende
  tijdmarkering. De horizontale as geeft de lestijd; hoogte en diepte zijn
  uitsluitend een ruimtelijke ordening voor de leesbaarheid.
- Onder het beeld staan toelichting, werkvorm en opdrachten.
  Het docentantwoord is per fase uitklapbaar en begint ingeklapt.

De Blochbol toont een **zuivere qubittoestand**, geen fysiek deeltje in een bol.
Hoeken bepalen de toestandspijl en de Z-meetkansen. Het Bellbeeld toont twee
lokaal maximaal gemengde toestanden in het midden van de bollen, plus de
gezamenlijke kansen 00/11; een verstrengeld paar is geen tweetal zuivere
Blochvectoren. De beelden zijn lesvoorbeelden. Overgangen tussen fasen stellen
geen tijdsafhankelijke quantumpoort of echte hardware voor. De tekst beschrijft
de inhoud ook zonder de 3D-tekening.

## CLI en virtuele omgeving

~~~bash
./run.sh controleer voorbeelden/nederlands.txt
./run.sh interpreteer voorbeelden/quantumcomputing.txt.invoer
./run.sh zoek voorbeelden "superpositie" --alleen-geldig
./run.sh woordenboek
.venv/bin/python -m unittest discover -s tests -v
~~~

setup.sh en run.sh hebben een Bash-shebang. setup.sh voert uv sync --locked uit.
run.sh kiest expliciet de Python uit de lokale .venv, ook bij starten vanuit een
andere map. Bestandsargumenten zijn relatief aan de huidige werkmap.
Voor direct gebruik van main.py: activeer eerst met source .venv/bin/activate.

## Formele taal, versie 1.1

UTF-8, eventueel met BOM, en extensie .txt of .invoer. Lege regels en volledige
commentaarregels die met # beginnen zijn toegestaan. Iedere instructie, elk veld
en elke alinea staan op één fysieke regel. Veldnamen, sectienamen en vaste
veldwaarden zijn hoofdlettergevoelig. De zes documentvelden zijn verplicht,
uniek en niet leeg; hun volgorde is vrij.

~~~text
Titel: Een korte titel
Vak: Nederlands
Niveau: 4 vwo
Onderwerp: Een onderwerp
Leerdoel: Je kunt het geleerde toepassen.
Duur: 10 minuten
Instructies:
1. Lees een tekst naar keuze.
2. Vat de tekst van [1] samen in drie zinnen.
Einde.
~~~

Vakken: Nederlands, Engels, Wiskunde B, Natuurkunde, Informatica.
Niveau: 4 vwo. Duur: een geheel getal van 1 tot en met 480, gevolgd door
een spatie en minuten. Nummer opdrachten vanaf 1 zonder onderbreking (maximaal
zes cijfers). Begin met een hoofdletter en een werkwoord uit het woordenboek,
gevolgd door spaties en niet-lege opdrachttekst. Eindig met een punt, vraagteken
of uitroepteken, eventueel gevolgd door sluitende aanhalingstekens.
Vierkante haken in opdrachten verwijzen naar eerdere opdrachten: [1].

### Optionele tijdlijn

Voor een presentatie voeg je **na alle instructies en voor Einde.** een tijdlijn
toe. Oude documenten zonder tijdlijn blijven geldig; voor visualisatie moet je
eerst een tijdlijn toevoegen. Het programma bedenkt geen lestijden.

~~~text
Tijdlijn:
Fase: 0-4 | Lezen en verkennen
Opdrachten: 1
Toelichting: De docent legt het doel van het lezen uit.
Toelichting: Elke extra Toelichting-regel wordt een nieuwe alinea.
Werkvorm: Twee minuten lezen en twee minuten bespreken.
Controle: Wat is het onderwerp? Antwoord: de centrale kwestie van de tekst.
Beeld: klassiek
Fase: 4-10 | Samenvatten
Opdrachten: 2
Toelichting: Een samenvatting benoemt de kern en laat details weg.
Werkvorm: Vier minuten schrijven en twee minuten vergelijken.
Controle: Bevat de samenvatting de kern? Antwoord: controleer dit aan de hand van de tekst.
Beeld: samenvatting
Einde.
~~~

Alle fasevelden zijn verplicht. Alleen Toelichting mag worden herhaald.
De fasen beginnen op minuut 0, sluiten zonder overlap of gat aan en eindigen
op de opgegeven lesduur. Start/einde zijn gehele minuten met een positieve
duur per fase. Iedere opdracht wordt precies eenmaal toegewezen met Opdrachten.
Verwijzingen moeten ook in de geplande uitvoeringsvolgorde naar eerdere
opdrachten wijzen, zowel tussen fasen als binnen een fase.
Toelichting, werkvorm en controle zijn vrije tekst; subminuten in Werkvorm
worden niet automatisch opgeteld of beoordeeld.

~~~text
Beeld: klassiek
Beeld: bloch | 90 | 0
Beeld: bell
Beeld: samenvatting
~~~

Klassiek toont twee mogelijke bitwaarden. Bloch toont een zuivere qubittoestand:
theta ligt tussen 0 en 180 graden, phi tussen -360 en 360, beide eindig.
Gebruik een punt voor decimalen. De richting is
(sin(theta) cos(phi), sin(theta) sin(phi), cos(theta)).
Bij een Z-meting: P(0) = cos(theta/2)^2 en P(1) = sin(theta/2)^2.
Voorbeelden: 0/0 is |0>, 180/0 is |1>, 90/0 is |+>, 90/180 is |->.
Bell toont (|00> + |11>)/sqrt(2) met lokale gemengde toestanden.
Samenvatting toont het 3D-fasenoverzicht.
De klok kiest de fase; de toestand blijft gedurende die fase gelijk.

## Woordenboek, geldigheid en uitvoer

woordenboek.txt bevat regels werkwoord | betekenis. Een eigen woordenboek
geef je voor de subopdracht op:

~~~bash
./run.sh --woordenboek eigen.txt controleer les.txt
~~~

Dubbele woorden, lege betekenissen en ongeldige regels worden afgewezen.
controleer toetst structuur, verplichte velden, verwijzingen en tijdlijn.
Het controleert geen volledige Nederlandse spelling, zinsbouw, didactische
kwaliteit of juistheid van antwoorden. interpreteer toont opdrachten en
fasegegevens. Het voert geen code of leerlingopdrachten uit. visualiseer
exporteert uitsluitend geldige documenten met een tijdlijn.
Invoertekst blijft tekst in de browser.

zoek doorzoekt recursief .txt en .invoer. Alle zoektermen moeten op dezelfde
regel voorkomen, als hoofdletterongevoelige deeltekst. Iedere treffer bevat pad,
regelnummer en de geldigheid van het hele document. Verborgen paden en symbolische
bestandslinks worden overgeslagen. Leesfouten staan in het rapport.
Geen treffers is een succesvolle zoekactie.

Terminalrapporten zijn ASCII; overige tekens worden getranslitereerd of zichtbaar
gecodeerd. De HTML-presentatie toont Unicode.

| Codes | Controle |
| --- | --- |
| E001–E007 | Documentstructuur |
| E008–E012 | Tijdlijnstructuur en fasevelden |
| V001–V010 | Documentwaarden en opdrachten |
| V011–V012 | Aansluitende fasen en totale lesduur |
| V013 | Iedere opdracht precies eenmaal ingedeeld |
| V014–V015 | Verplichte fasegegevens en geldige beelden/hoeken |

Regel - duidt een documentbrede fout aan. Exitcodes: **0** geslaagd/geldig,
**1** ongeldig document, **2** gebruiks-, lees- of configuratiefout.
voorbeelden/ongeldig.txt demonstreert exitcode 1.

De OOP-onderdelen zijn Document, Instructie, Fase, Woordenboek, DocumentParser,
DocumentValidator, Zoekmachine, AsciiRapport en LesPresentatie.
De webbestanden onder taal/web worden bij export volledig ingebed in één HTML.
