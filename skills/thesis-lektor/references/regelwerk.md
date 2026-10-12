# Regelwerk thesis-lektor

Version 1.1.0. Erzeugt aus `regelwerk.toml`, nicht von Hand bearbeiten.

Schweregrade: **Fehler** muss vor der Abgabe behoben sein. **Warnung** sollte behoben oder begründet werden. **Hinweis** ist eine Empfehlung. **Offen** sind Marker des Schreibenden.

Prüfung: `linter` und `bib` laufen deterministisch über Skripte. `umfeld` prüft die Versionierung mit Git und zählt nicht zum Lektoratsindex. `agent` prüfen die Gutachter-Agenten.

Herkunft: SR = Schreibregeln aus der Betreuung einer Masterarbeit, FB = Festlegung im Schreibprozess, APA7 = APA Publication Manual, WI = Konvention der Wirtschaftsinformatik, DUDEN = Duden-Empfehlung, TYPO = Typografie-Konvention.

## Übersicht

| ID | Regel | Schwere | Prüfung | Farbe |
|---|---|---|---|---|
| `TYP-SEMIKOLON` | Kein Semikolon | Fehler | linter | stil |
| `TYP-GEDANKENSTRICH` | Kein Geviertstrich als Einschub | Fehler | linter | stil |
| `TYP-HALBGEVIERT` | Halbgeviertstrich nur für Bereiche | Warnung | linter | stil |
| `TYP-ANFUEHRUNG` | Anführungszeichen über \enquote | Warnung | linter | stil |
| `TYP-ABKUERZUNG` | Mehrteilige Abkürzungen mit schmalem Abstand | Warnung | linter | stil |
| `TYP-PROZENT` | Schmaler Abstand vor Prozentzeichen | Warnung | linter | stil |
| `TYP-EINHEIT` | Schmaler Abstand bei Gleichungen im Text | Hinweis | linter | stil |
| `TYP-ZAHLWORT` | Zahlen bis zwölf ausschreiben | Hinweis | linter | stil |
| `TYP-AUFZAEHLUNG-LEER` | Keine Leerzeilen zwischen Aufzählungspunkten | Hinweis | linter | stil |
| `SPR-ICH-WIR` | Keine Ich- oder Wir-Form | Fehler | linter | stil |
| `SPR-WERTUNG` | Keine wertenden Adjektive | Warnung | linter | stil |
| `SPR-SELBSTVERSTAENDLICH` | Keine Scheinselbstverständlichkeiten | Warnung | linter | stil |
| `SPR-FLOSKEL` | Keine Floskeln | Warnung | linter | stil |
| `SPR-HEDGING` | Keine gestapelten Einschränkungen | Warnung | linter | stil |
| `SPR-FUELLWORT` | Füllwörter vermeiden | Hinweis | linter | stil |
| `SPR-DOPPELUNG` | Keine doppelten Partikeln | Warnung | linter | stil |
| `SPR-SIGNIFIKANT` | Signifikant nur im statistischen Sinn | Hinweis | linter | stil |
| `SPR-NOMINALSTIL` | Nominalstil auflösen | Hinweis | linter | stil |
| `SPR-TEMPUS` | Zeitform passend zum Inhalt | Hinweis | agent | stil |
| `SPR-WERTUNG-IMPLIZIT` | Keine versteckten Wertungen | Warnung | agent | stil |
| `SPR-KLARHEIT` | Verständlich und eindeutig formulieren | Warnung | agent | stil |
| `SAT-LAENGE` | Sätze unter 35 Wörtern | Warnung | linter | stil |
| `SAT-SCHACHTEL` | Keine Schachtelsätze | Warnung | linter | stil |
| `SAT-GENITIV` | Keine Genitivketten | Hinweis | linter | stil |
| `SAT-HAUPTAUSSAGE` | Hauptaussage im Hauptsatz | Hinweis | agent | stil |
| `TERM-VERBOTEN` | Festgelegte Begriffe verwenden | Warnung | linter | stil |
| `TERM-VARIANTEN` | Keine rotierenden Synonyme | Hinweis | linter | stil |
| `TERM-KOMPOSITUM` | Komposita mit Bindestrich | Warnung | linter | stil |
| `TERM-ABKUERZUNG` | Abkürzungen über \gls | Warnung | linter | stil |
| `TERM-EMPH` | \emph nur bei Erstnennung | Hinweis | linter | stil |
| `TERM-ANGLIZISMUS` | Deutsch bevorzugen | Hinweis | agent | stil |
| `TERM-KONSISTENZ` | Einmal eingeführte Begriffe beibehalten | Warnung | agent | stil |
| `ZIT-SCHLUESSEL` | Zitierschlüssel existiert in der Bibliografie | Fehler | bib | beleg |
| `ZIT-MANUELL` | Keine von Hand gesetzten Zitate | Warnung | linter | beleg |
| `ZIT-BELEG` | Belegsignal ohne Quelle | Hinweis | linter | beleg |
| `ZIT-BEFEHL` | \textcite und \parencite statt \cite | Warnung | linter | stil |
| `ZIT-URL` | Keine URLs im Fließtext | Warnung | linter | stil |
| `ZIT-WOERTLICH` | Wörtliche Zitate sparsam und mit Seitenzahl | Warnung | linter | beleg |
| `ZIT-FUSSNOTE` | Fußnoten nur für Ergänzungen | Hinweis | agent | stil |
| `ZIT-TREUE` | Quelle stützt die Aussage | Warnung | agent | beleg |
| `INH-BELEGPFLICHT` | Belegpflichtige Aussage ohne Quelle | Warnung | agent | beleg |
| `BIB-UNGENUTZT` | Eintrag wird nicht zitiert | Hinweis | bib | keine |
| `BIB-FELDER` | Pflichtfelder vollständig | Warnung | bib | keine |
| `BIB-DOI` | DOI angeben | Hinweis | bib | keine |
| `BIB-DUPLIKAT` | Keine doppelten Einträge | Warnung | bib | keine |
| `BIB-PREPRINT` | Preprint auf veröffentlichte Fassung prüfen | Hinweis | bib | keine |
| `FMT-FETT` | Kein Fettdruck zur Betonung | Warnung | linter | stil |
| `FMT-REF` | \cref statt \ref | Warnung | linter | stil |
| `FMT-VLINIE` | Tabellen ohne senkrechte Linien | Fehler | linter | stil |
| `FMT-CAPTION` | Gleitobjekt mit Beschriftung | Fehler | linter | struktur |
| `FMT-LABEL` | Gleitobjekt mit Label | Fehler | linter | struktur |
| `FMT-VERWEIS-FEHLT` | Gleitobjekt wird im Text referenziert | Warnung | linter | struktur |
| `FMT-VERWEIS-REIHENFOLGE` | Verweis vor dem Gleitobjekt | Warnung | linter | struktur |
| `FMT-VERWEIS-UNBEKANNT` | Verweisziel existiert | Fehler | linter | struktur |
| `FMT-ABB-QUELLE` | Herkunft jeder Abbildung angeben | Warnung | linter | beleg |
| `FMT-QUELLTEXT-ZEILE` | Ein Satz pro Quelltextzeile | Hinweis | linter | keine |
| `STR-ORIENTIERUNG` | Jeder Abschnitt beginnt mit einem Orientierungssatz | Warnung | linter | struktur |
| `STR-KURZ` | Kein Abschnitt unter drei Sätzen | Hinweis | linter | struktur |
| `STR-VERZEICHNIS` | Abbildungs-, Tabellen- und Abkürzungsverzeichnis vorhanden | Warnung | linter | struktur |
| `STR-ROTER-FADEN` | Roter Faden | Warnung | agent | struktur |
| `STR-DOPPELUNG` | Keine Doppelung zwischen Kapiteln | Warnung | agent | struktur |
| `STR-DETAILTIEFE` | Details in den Anhang | Hinweis | agent | struktur |
| `STR-UEBERLEITUNG` | Übergänge zwischen Abschnitten | Hinweis | agent | struktur |
| `STR-KAPITELINHALT` | Kapitel enthält seine Pflichtbestandteile | Warnung | agent | struktur |
| `INH-FORSCHUNGSFRAGEN` | Forschungsfragen werden beantwortet | Fehler | agent | struktur |
| `INH-HYPOTHESEN` | Hypothesen gerichtet, operationalisiert und geprüft | Warnung | agent | struktur |
| `INH-SETZUNG` | Setzungen offen benennen | Warnung | agent | struktur |
| `INH-LIMITATION` | Grenzen benannt | Warnung | agent | struktur |
| `INH-ZAHLEN` | Zahlen stimmen überall überein | Fehler | agent | struktur |
| `INH-BEGRUENDUNG` | Entscheidungen begründet | Warnung | agent | struktur |
| `INH-PROJEKT` | Projektregeln eingehalten | Warnung | agent | struktur |
| `FORM-ERKLAERUNG` | Formel mit Variablenliste und Rechenbeispiel | Hinweis | linter | struktur |
| `FORM-VERSTAENDLICH` | Formeln einfach und notwendig | Warnung | agent | struktur |
| `FORM-NOTATION` | Einheitliche Notation | Warnung | agent | struktur |
| `ABB-GESTALTUNG` | Abbildungen klar und symmetrisch | Hinweis | agent | struktur |
| `ABG-VERSIONIERUNG` | Arbeit in einem privaten Git-Repository versionieren | Hinweis | umfeld | keine |
| `ABG-GIT-STAND` | Gesicherter Stand entspricht dem Arbeitsstand | Hinweis | umfeld | keine |
| `MARK-QUELLE-FEHLT` | Markierte fehlende Quelle | Offen | linter | quelle |
| `MARK-OFFEN` | Markierter offener Punkt | Offen | linter | offen |

## Typografie

### `TYP-SEMIKOLON` Kein Semikolon

Fehler, Prüfung: linter, Herkunft: SR, FB

Semikolons verlängern Satzgefüge und verwischen die Gliederung. Ein Punkt oder ein Nebensatz trennt Gedanken klarer. Die Regel gilt auch in Tabellen, Bildunterschriften und Markern.

- Falsch: Die Stränge laufen parallel; die Fusion folgt danach.
- Richtig: Die Stränge laufen parallel. Die Fusion folgt danach.

### `TYP-GEDANKENSTRICH` Kein Geviertstrich als Einschub

Fehler, Prüfung: linter, Herkunft: SR

Der Geviertstrich (—) ist ein Stilmittel des Journalismus und der Prosa. Im wissenschaftlichen Text trägt ein Nebensatz oder ein Komma dieselbe Information sachlicher.

- Falsch: ein System — das adaptiert — wurde entwickelt
- Richtig: ein System, das adaptiert, wurde entwickelt

### `TYP-HALBGEVIERT` Halbgeviertstrich nur für Bereiche

Warnung, Prüfung: linter, Herkunft: SR, TYPO

Der Halbgeviertstrich (--) steht für Bereiche wie S. 12--15. Mit Leerzeichen eingesetzt ersetzt er einen Gedankenstrich und fällt unter dieselbe Regel.

- Falsch: Die Adaption -- so die Annahme -- wirkt.
- Richtig: Die Adaption wirkt, so die Annahme.

### `TYP-ANFUEHRUNG` Anführungszeichen über \enquote

Warnung, Prüfung: linter, Herkunft: SR

\enquote setzt sprachabhängig korrekte Zeichen und hält verschachtelte Zitate konsistent. Von Hand gesetzte Zeichen mischen leicht deutsche und englische Formen.

- Falsch: der sogenannte "Persona Collapse"
- Richtig: der sogenannte \enquote{Persona Collapse}

### `TYP-ABKUERZUNG` Mehrteilige Abkürzungen mit schmalem Abstand

Warnung, Prüfung: linter, Herkunft: SR, TYPO

Ohne Abstand kleben die Teile zusammen, mit normalem Leerzeichen kann der Umbruch sie trennen. \, löst beides.

- Falsch: z.B., d. h., u.~a.
- Richtig: z.\,B., d.\,h., u.\,a.

### `TYP-PROZENT` Schmaler Abstand vor Prozentzeichen

Warnung, Prüfung: linter, Herkunft: SR, DUDEN

Zahl und Prozentzeichen werden durch einen schmalen, nicht umbrechenden Abstand getrennt. Ein unmaskiertes % beginnt in LaTeX zudem einen Kommentar und verschluckt den Rest der Zeile.

- Falsch: 15\% oder 15 %
- Richtig: 15\,\%

### `TYP-EINHEIT` Schmaler Abstand bei Gleichungen im Text

Hinweis, Prüfung: linter, Herkunft: SR

Angaben wie N = 40 im Fließtext brechen sonst am Gleichheitszeichen um.

- Falsch: N = 40
- Richtig: $N = 40$ oder N\,=\,40

### `TYP-ZAHLWORT` Zahlen bis zwölf ausschreiben

Hinweis, Prüfung: linter, Herkunft: FB, DUDEN

Im Fließtext werden die Zahlen null bis zwölf als Wort geschrieben. Ausnahmen sind Maßeinheiten, Prozent, Kennungen (Kapitel 5, Item 3, H1), Tabellen und Reihen mit größeren Zahlen.

- Falsch: Die Studie umfasst 3 Phasen.
- Richtig: Die Studie umfasst drei Phasen.

### `TYP-AUFZAEHLUNG-LEER` Keine Leerzeilen zwischen Aufzählungspunkten

Hinweis, Prüfung: linter, Herkunft: SR

Leerzeilen zwischen \item erzeugen je nach Klasse uneinheitliche Abstände.

- Falsch: \item A\n\n\item B
- Richtig: \item A\n\item B


## Sprache und Ton

### `SPR-ICH-WIR` Keine Ich- oder Wir-Form

Fehler, Prüfung: linter, Herkunft: SR

Die Arbeit stellt Ergebnisse und Vorgehen in den Mittelpunkt, nicht die schreibende Person. Wörtliche Zitate und Prompt-Auszüge sind ausgenommen.

- Falsch: Wir zeigen, dass die Adaption wirkt.
- Richtig: Die Ergebnisse zeigen, dass die Adaption wirkt.

### `SPR-WERTUNG` Keine wertenden Adjektive

Warnung, Prüfung: linter, Herkunft: SR

Wertungen ersetzen keinen Beleg. Ein Befund überzeugt durch Zahl, Vergleich oder Quelle, nicht durch Adjektive.

- Falsch: Das System liefert beeindruckende Ergebnisse.
- Richtig: Das System erreicht eine Übereinstimmung von r = 0,61 mit der Selbstauskunft.

### `SPR-SELBSTVERSTAENDLICH` Keine Scheinselbstverständlichkeiten

Warnung, Prüfung: linter, Herkunft: SR

Wörter wie natürlich oder offensichtlich unterstellen Konsens und überspringen die Begründung. Was offensichtlich ist, braucht das Wort nicht. Was es nicht ist, braucht eine Begründung.

- Falsch: Natürlich beeinflusst die Stimme die Wahrnehmung.
- Richtig: Die Stimme beeinflusst die Wahrnehmung \parencite{...}.

### `SPR-FLOSKEL` Keine Floskeln

Warnung, Prüfung: linter, Herkunft: SR

Floskeln kündigen an, statt auszusagen. Querverweise ersetzen Wendungen wie wie bereits erwähnt.

- Falsch: Es ist wichtig zu beachten, dass die Stränge gewichtet werden.
- Richtig: Die Stränge werden gewichtet.

### `SPR-HEDGING` Keine gestapelten Einschränkungen

Warnung, Prüfung: linter, Herkunft: SR

Mehrere Abschwächungen in einem Satz verwässern die Aussage. Eine benannte Einschränkung ist präziser.

- Falsch: Dies könnte möglicherweise eventuell zutreffen.
- Richtig: Dies trifft nur für die adaptive Bedingung zu.

### `SPR-FUELLWORT` Füllwörter vermeiden

Hinweis, Prüfung: linter, Herkunft: SR

Füllwörter tragen keine Information und verlängern Sätze.

- Falsch: Die Fusion ist eigentlich relativ einfach.
- Richtig: Die Fusion bildet einen gewichteten Mittelwert.

### `SPR-DOPPELUNG` Keine doppelten Partikeln

Warnung, Prüfung: linter, Herkunft: SR

Pleonasmen wie zuerst zunächst sagen dasselbe zweimal.

- Falsch: Zuerst wird zunächst der Selbsttest bearbeitet.
- Richtig: Zunächst wird der Selbsttest bearbeitet.

### `SPR-SIGNIFIKANT` Signifikant nur im statistischen Sinn

Hinweis, Prüfung: linter, Herkunft: SR

In einer empirischen Arbeit ist signifikant für Testergebnisse reserviert. Umgangssprachlich verwendet führt es Lesende in die Irre.

- Falsch: Die Stimme hat einen signifikanten Einfluss auf das Erleben.
- Richtig: Die Stimme hat einen deutlichen Einfluss, der Test ist nicht signifikant (p = 0,12).

### `SPR-NOMINALSTIL` Nominalstil auflösen

Hinweis, Prüfung: linter, Herkunft: SR, WI

Ketten aus Substantiven auf -ung, -heit, -keit und -ion verstecken die Handlung. Ein Verb macht sichtbar, wer was tut.

- Falsch: Die Durchführung der Erhebung erfolgt nach Abschluss der Implementierung.
- Richtig: Die Erhebung beginnt, sobald der Prototyp fertig ist.

### `SPR-TEMPUS` Zeitform passend zum Inhalt

Hinweis, Prüfung: agent, Herkunft: WI, APA7

Präsens für Theorie, Literaturwiedergabe, Systembeschreibung, Verweise und Diskussion. Präteritum für abgeschlossene Handlungen und konkrete Befunde der eigenen Erhebung. Innerhalb eines Absatzes wird nicht ohne Grund gewechselt.

- Falsch: Die Teilnehmenden bewerten den Agenten. Danach füllten sie den Fragebogen aus.
- Richtig: Die Teilnehmenden bewerteten den Agenten. Danach füllten sie den Fragebogen aus.

### `SPR-WERTUNG-IMPLIZIT` Keine versteckten Wertungen

Warnung, Prüfung: agent, Herkunft: SR

Wertungen stecken auch in Verben und Konstruktionen (scheitert kläglich, gelingt mühelos, leider). Die Wortliste erfasst sie nicht vollständig.

- Falsch: Bisherige Ansätze scheitern daran, ...
- Richtig: Bisherige Ansätze berücksichtigen nicht, ...

### `SPR-KLARHEIT` Verständlich und eindeutig formulieren

Warnung, Prüfung: agent, Herkunft: SR, FB

Ein Satz muss beim ersten Lesen verständlich sein. Unklare Bezüge (dies, diese, es), unerklärte Fachbegriffe und Mehrdeutigkeit kosten Gutachtende Zeit und Wohlwollen.

- Falsch: Dies führt dazu, dass es stabiler wird.
- Richtig: Die Glättung führt dazu, dass der Zustand über die Beiträge stabiler wird.


## Satzbau

### `SAT-LAENGE` Sätze unter 35 Wörtern

Warnung, Prüfung: linter, Herkunft: SR

Ab etwa 35 Wörtern sinkt die Verständlichkeit deutlich. Lange Sätze lassen sich fast immer an einem Und oder einem Relativsatz teilen.

- Falsch: (Satz mit 48 Wörtern)
- Richtig: (zwei Sätze mit 22 und 26 Wörtern)

### `SAT-SCHACHTEL` Keine Schachtelsätze

Warnung, Prüfung: linter, Herkunft: SR

Ab drei Nebensätzen müssen Lesende zu viele offene Bezüge im Kopf halten.

- Falsch: Der Agent, der die Werte, die der Strang, der ... liefert, nutzt, ...
- Richtig: Der Strang liefert Werte. Der Agent nutzt sie, um ...

### `SAT-GENITIV` Keine Genitivketten

Hinweis, Prüfung: linter, Herkunft: SR

Drei und mehr Genitive hintereinander verschleiern, worauf sich der Satz bezieht.

- Falsch: die Ergebnisse der Evaluation der Nutzerstudie des Systems
- Richtig: die Ergebnisse, die die Nutzerstudie zum System liefert

### `SAT-HAUPTAUSSAGE` Hauptaussage im Hauptsatz

Hinweis, Prüfung: agent, Herkunft: SR

Was der Satz behauptet, gehört in den Hauptsatz. Im Nebensatz versteckt wird es überlesen.

- Falsch: Es zeigte sich, dass die Adaption das Vertrauen erhöht, was erwartet wurde.
- Richtig: Die Adaption erhöht das Vertrauen, wie in H1 erwartet.


## Begriffe

### `TERM-VERBOTEN` Festgelegte Begriffe verwenden

Warnung, Prüfung: linter, Herkunft: FB

Die Projektkonfiguration legt Begriffe fest, die durch andere ersetzt werden. Ein Begriff pro Sache verhindert, dass Lesende zwei Dinge vermuten.

- Falsch: Werkzeugaufruf
- Richtig: Toolcall

### `TERM-VARIANTEN` Keine rotierenden Synonyme

Hinweis, Prüfung: linter, Herkunft: SR

Wechseln Nutzer, User und Anwender ohne Grund, fragen sich Lesende, ob verschiedene Gruppen gemeint sind.

- Falsch: Nutzer ... User ... Anwender
- Richtig: durchgehend Person oder teilnehmende Person

### `TERM-KOMPOSITUM` Komposita mit Bindestrich

Warnung, Prüfung: linter, Herkunft: SR, DUDEN

Zusammensetzungen mit Abkürzungen, Eigennamen oder englischen Bestandteilen werden im Deutschen durchgekoppelt.

- Falsch: KI Voice Agent, Big Five Modell
- Richtig: KI-Voice-Agent, Big-Five-Modell

### `TERM-ABKUERZUNG` Abkürzungen über \gls

Warnung, Prüfung: linter, Herkunft: FB

\gls schreibt die Abkürzung beim ersten Vorkommen aus und trägt sie ins Abkürzungsverzeichnis ein. Von Hand gesetzte Kurzformen umgehen beides.

- Falsch: Das LLM antwortet ...
- Richtig: Das \gls{a:LLM} antwortet ...

### `TERM-EMPH` \emph nur bei Erstnennung

Hinweis, Prüfung: linter, Herkunft: SR

Kursivsatz markiert die Einführung eines fremdsprachigen Fachbegriffs. Wiederholt kursiv gesetzt verliert er diese Funktion.

- Falsch: \emph{Persona Collapse} ... später erneut \emph{Persona Collapse}
- Richtig: \emph{Persona Collapse} ... später Persona Collapse

### `TERM-ANGLIZISMUS` Deutsch bevorzugen

Hinweis, Prüfung: agent, Herkunft: SR

Wo ein etablierter deutscher Begriff existiert, ist er vorzuziehen. Ausgenommen sind englische Begriffe, die in der Fachgemeinschaft Standard sind oder per Projektglossar festgelegt wurden.

- Falsch: Speech Synthesis
- Richtig: Sprachsynthese

### `TERM-KONSISTENZ` Einmal eingeführte Begriffe beibehalten

Warnung, Prüfung: agent, Herkunft: SR

Der Linter erkennt nur konfigurierte Synonymgruppen. Inhaltliche Begriffswechsel (Stufe, Level, Grad) erkennt nur ein lesender Blick.

- Falsch: Adaptionsstufe ... Anpassungslevel
- Richtig: durchgehend Adaptionsstufe


## Zitation

### `ZIT-SCHLUESSEL` Zitierschlüssel existiert in der Bibliografie

Fehler, Prüfung: bib, Herkunft: APA7

Ein unbekannter Schlüssel erscheint im PDF als fett gesetzter Schlüssel statt als Quelle.

- Falsch: \textcite{doenellan2006}
- Richtig: \textcite{donnellanMiniIPIPScales2006}

### `ZIT-MANUELL` Keine von Hand gesetzten Zitate

Warnung, Prüfung: linter, Herkunft: APA7

Autor und Jahr von Hand geschrieben (Peters et al. 2024) erscheinen nicht im Literaturverzeichnis und folgen nicht dem Zitierstil.

- Falsch: Peters et al. (2024) zeigen ...
- Richtig: \textcite{petersLargeLanguageModels2024c} zeigen ...

### `ZIT-BELEG` Belegsignal ohne Quelle

Hinweis, Prüfung: linter, Herkunft: SR

Formulierungen wie Studien zeigen oder in der Literatur kündigen einen Beleg an. Fehlt im Satz die Quelle, ist die Aussage unbelegt. Der Linter findet nur Signalwörter, die Entscheidung bleibt beim Menschen.

- Falsch: Studien zeigen, dass Extraversion an der Stimme erkennbar ist.
- Richtig: Extraversion ist an der Stimme erkennbar \parencite{...}.

### `ZIT-BEFEHL` \textcite und \parencite statt \cite

Warnung, Prüfung: linter, Herkunft: SR

\cite erzeugt je nach Stil eine uneinheitliche Form. \textcite steht im Satz, \parencite in Klammern.

- Falsch: \cite{goldberg1990}
- Richtig: \textcite{goldberg1990} oder \parencite{goldberg1990}

### `ZIT-URL` Keine URLs im Fließtext

Warnung, Prüfung: linter, Herkunft: SR

URLs gehören ins Literaturverzeichnis oder in eine Fußnote, im Fließtext unterbrechen sie den Lesefluss.

- Falsch: unter https://example.org beschrieben
- Richtig: in der Dokumentation beschrieben \parencite{...}

### `ZIT-WOERTLICH` Wörtliche Zitate sparsam und mit Seitenzahl

Warnung, Prüfung: linter, Herkunft: SR, APA7

Wörtliche Zitate brauchen eine Seitenangabe. Ab 40 Wörtern verlangt APA ein abgesetztes Blockzitat, besser ist eine Paraphrase.

- Falsch: \enquote{...} \parencite{key}
- Richtig: \enquote{...} \parencite[S.~12]{key}

### `ZIT-FUSSNOTE` Fußnoten nur für Ergänzungen

Hinweis, Prüfung: agent, Herkunft: SR

Inhaltliche Aussagen in Fußnoten werden überlesen. Fußnoten tragen nur ergänzende Hinweise und URLs.

- Falsch: \footnote{Die Adaption wirkt nur bei hoher Extraversion.}
- Richtig: Aussage in den Fließtext, Fußnote für den Link zur Dokumentation

### `ZIT-TREUE` Quelle stützt die Aussage

Warnung, Prüfung: agent, Herkunft: APA7, WI

Eine Quelle, die die Aussage nicht trägt, wiegt schwerer als eine fehlende. Geprüft wird gegen Titel, Abstract und, sofern vorhanden, den Volltext.

- Falsch: Eine Studie zu Text wird für eine Aussage über Stimme zitiert.
- Richtig: Die zitierte Quelle untersucht genau die behauptete Beziehung.


## Inhalt

### `INH-BELEGPFLICHT` Belegpflichtige Aussage ohne Quelle

Warnung, Prüfung: agent, Herkunft: SR

Jede Aussage, die nicht Allgemeinwissen und nicht eigenes Ergebnis ist, braucht eine Quelle. Der Agent findet auch Aussagen ohne Signalwort.

- Falsch: Menschen vertrauen ähnlichen Gesprächspartnern stärker.
- Richtig: Menschen vertrauen ähnlichen Gesprächspartnern stärker \parencite{...}.

### `INH-FORSCHUNGSFRAGEN` Forschungsfragen werden beantwortet

Fehler, Prüfung: agent, Herkunft: WI

Jede in der Einleitung gestellte Forschungsfrage braucht eine ausdrückliche Antwort im Fazit, und der Weg dorthin muss nachvollziehbar sein.

- Falsch: FF 3b wird im Fazit nicht erwähnt
- Richtig: Fazit beantwortet FF 1 bis 3b einzeln mit Verweis auf die Kapitel

### `INH-HYPOTHESEN` Hypothesen gerichtet, operationalisiert und geprüft

Warnung, Prüfung: agent, Herkunft: WI

Eine Hypothese braucht eine theoretische Herleitung, ein Messinstrument, einen festgelegten Test und einen Ergebnisbericht in derselben Benennung.

- Falsch: H2 in Kapitel 4, in Kapitel 7 nicht mehr erwähnt
- Richtig: H2 hergeleitet, operationalisiert, getestet und diskutiert

### `INH-SETZUNG` Setzungen offen benennen

Warnung, Prüfung: agent, Herkunft: FB

Festgelegte Parameter (Gewichte, Schwellen, Glättung) sind Entscheidungen, keine Befunde. Sie werden als Setzung bezeichnet und so weit möglich begründet.

- Falsch: Der optimale Glättungsfaktor beträgt 0,4.
- Richtig: Der Glättungsfaktor ist auf 0,4 gesetzt, das entspricht einem Fenster von etwa vier Beiträgen.

### `INH-LIMITATION` Grenzen benannt

Warnung, Prüfung: agent, Herkunft: WI

Jede methodische Entscheidung mit erkennbarem Nachteil gehört in die Limitationen. Fehlt sie dort, wirkt die Arbeit unkritisch.

- Falsch: Eine konstante Stimme ohne Erwähnung in den Limitationen
- Richtig: Limitation mit Begründung und Quelle

### `INH-ZAHLEN` Zahlen stimmen überall überein

Fehler, Prüfung: agent, Herkunft: WI

Weicht eine Zahl zwischen Text, Tabelle und Abbildung ab, ist offen, welche gilt. Das trifft die Glaubwürdigkeit der ganzen Auswertung.

- Falsch: Text: N = 48, Tabelle: N = 46
- Richtig: überall derselbe Wert, Abweichungen mit Grund

### `INH-BEGRUENDUNG` Entscheidungen begründet

Warnung, Prüfung: agent, Herkunft: FB, WI

Technische und methodische Entscheidungen brauchen eine Begründung. Die Modellwahl nennt immer Geschwindigkeit und Qualität.

- Falsch: Als Modell wird gpt-5.5 eingesetzt.
- Richtig: gpt-5.5 antwortet im Replay im Median nach 1,1 s und erreicht die höchste Bewertung.

### `INH-PROJEKT` Projektregeln eingehalten

Warnung, Prüfung: agent, Herkunft: FB

Die Projektkonfiguration kann inhaltliche Regeln festlegen, etwa den Verzicht auf fremde Normwerte. Sie gelten wie die allgemeinen Regeln.

- Falsch: (abhängig von der Konfiguration)
- Richtig: (abhängig von der Konfiguration)


## Bibliografie

### `BIB-UNGENUTZT` Eintrag wird nicht zitiert

Hinweis, Prüfung: bib, Herkunft: APA7

Nicht zitierte Einträge erscheinen nur bei \nocite im Verzeichnis. Sie deuten auf vergessene Belege oder Altlasten hin.

- Falsch: Eintrag in Main.bib ohne Zitat
- Richtig: zitieren oder entfernen

### `BIB-FELDER` Pflichtfelder vollständig

Warnung, Prüfung: bib, Herkunft: APA7

Ohne Autor, Titel, Jahr oder Zeitschrift erzeugt biblatex-apa unvollständige Einträge.

- Falsch: @article ohne journaltitle
- Richtig: @article mit author, title, date, journaltitle

### `BIB-DOI` DOI angeben

Hinweis, Prüfung: bib, Herkunft: APA7

APA 7 verlangt den DOI, sofern einer existiert. Er macht die Quelle eindeutig auffindbar.

- Falsch: @article ohne doi
- Richtig: doi = {10.1037/0022-3514.59.6.1216}

### `BIB-DUPLIKAT` Keine doppelten Einträge

Warnung, Prüfung: bib, Herkunft: APA7

Zwei Schlüssel für dieselbe Quelle führen zu doppelten Einträgen im Verzeichnis und zu Buchstabenzusätzen (2024a, 2024b) ohne Grund.

- Falsch: petersLargeLanguageModels2024 und petersLargeLanguageModels2024c
- Richtig: ein Schlüssel

### `BIB-PREPRINT` Preprint auf veröffentlichte Fassung prüfen

Hinweis, Prüfung: bib, Herkunft: WI

Begutachtete Fassungen wiegen schwerer als Preprints. Viele arXiv-Arbeiten erscheinen später in Zeitschrift oder Konferenzband.

- Falsch: arXiv:2505.14356 zitiert, obwohl eine Konferenzfassung existiert
- Richtig: Konferenzfassung zitieren, Preprint nur ohne veröffentlichte Fassung


## Formatierung und Verweise

### `FMT-FETT` Kein Fettdruck zur Betonung

Warnung, Prüfung: linter, Herkunft: SR

Betonung entsteht im wissenschaftlichen Text durch Satzbau. Fettdruck im Fließtext wirkt wie Werbung.

- Falsch: Die Adaption ist \textbf{entscheidend}.
- Richtig: Entscheidend für das Ergebnis ist die Adaption.

### `FMT-REF` \cref statt \ref

Warnung, Prüfung: linter, Herkunft: SR

\cref setzt den Objekttyp (Abbildung, Tabelle, Kapitel) automatisch und einheitlich.

- Falsch: Abbildung \ref{fig:x}
- Richtig: \cref{fig:x}

### `FMT-VLINIE` Tabellen ohne senkrechte Linien

Fehler, Prüfung: linter, Herkunft: SR

booktabs-Tabellen gliedern über Abstände und drei waagrechte Linien. Senkrechte Linien und \hline machen Tabellen unruhig.

- Falsch: \begin{tabular}{|l|r|} \hline
- Richtig: \begin{tabular}{lr} \toprule

### `FMT-CAPTION` Gleitobjekt mit Beschriftung

Fehler, Prüfung: linter, Herkunft: SR

Ohne \caption erscheint das Objekt in keinem Verzeichnis und lässt sich nicht beschreiben.

- Falsch: \begin{figure} ... ohne \caption
- Richtig: \caption{...}

### `FMT-LABEL` Gleitobjekt mit Label

Fehler, Prüfung: linter, Herkunft: SR

Ohne \label kann der Text nicht auf das Objekt verweisen.

- Falsch: \caption{...} ohne \label
- Richtig: \caption{...}\label{fig:...}

### `FMT-VERWEIS-FEHLT` Gleitobjekt wird im Text referenziert

Warnung, Prüfung: linter, Herkunft: SR

Jede Abbildung und Tabelle braucht einen Verweis, der sagt, was Lesende darin sehen sollen.

- Falsch: Tabelle ohne \cref im Text
- Richtig: wie \cref{tab:x} zeigt, ...

### `FMT-VERWEIS-REIHENFOLGE` Verweis vor dem Gleitobjekt

Warnung, Prüfung: linter, Herkunft: SR

Lesende sollen erst erfahren, warum ein Objekt folgt, und es dann sehen.

- Falsch: \begin{figure}...\end{figure} danach erst \cref{fig:x}
- Richtig: \cref{fig:x} im Absatz vor der Abbildung

### `FMT-VERWEIS-UNBEKANNT` Verweisziel existiert

Fehler, Prüfung: linter, Herkunft: SR

Ein Verweis auf ein unbekanntes Label erscheint im PDF als ??.

- Falsch: \cref{fig:architektur} ohne passendes \label
- Richtig: Label anlegen oder Schreibweise angleichen

### `FMT-ABB-QUELLE` Herkunft jeder Abbildung angeben

Warnung, Prüfung: linter, Herkunft: FB, WI

Jede Abbildung nennt ihre Herkunft. Eigene Abbildungen tragen Eigene Darstellung, angepasste Vorlagen Eigene Darstellung nach \textcite{...}, übernommene Abbildungen Quelle: \textcite{...}.

- Falsch: \caption{Architektur des Prototyps}
- Richtig: \caption{Architektur des Prototyps. Eigene Darstellung}

### `FMT-QUELLTEXT-ZEILE` Ein Satz pro Quelltextzeile

Hinweis, Prüfung: linter, Herkunft: SR

Ein Satz pro Zeile macht Änderungen im Versionsverlauf satzgenau sichtbar und erleichtert Kommentare.

- Falsch: Satz eins. Satz zwei. (in einer Zeile)
- Richtig: Satz eins.\nSatz zwei.


## Struktur

### `STR-ORIENTIERUNG` Jeder Abschnitt beginnt mit einem Orientierungssatz

Warnung, Prüfung: linter, Herkunft: SR

Folgt eine Unterüberschrift direkt auf eine Überschrift, fehlt die Einordnung, was der Abschnitt leistet und wie seine Teile zusammenhängen.

- Falsch: \section{Methodik}\n\subsection{Design}
- Richtig: \section{Methodik}\nDer Abschnitt beschreibt Design, Stichprobe und Auswertung.\n\subsection{Design}

### `STR-KURZ` Kein Abschnitt unter drei Sätzen

Hinweis, Prüfung: linter, Herkunft: SR

Ein Abschnitt mit ein oder zwei Sätzen trägt keine eigene Gliederungsebene. Er gehört in den benachbarten Abschnitt.

- Falsch: \subsection{Zeitlimit}\nEs gibt kein Zeitlimit.
- Richtig: Satz in den Abschnitt zum Ablauf übernehmen

### `STR-VERZEICHNIS` Abbildungs-, Tabellen- und Abkürzungsverzeichnis vorhanden

Warnung, Prüfung: linter, Herkunft: WI, APA7

Enthält die Arbeit Abbildungen, Tabellen oder Abkürzungen, gehört je ein Verzeichnis nach dem Inhaltsverzeichnis. Geprüft wird der letzte Build über die Recorder-Datei (.fls), ohne Build der Quelltext einschließlich Vorlagen- und Klassendateien.

- Falsch: Zwölf Abbildungen mit \caption, aber kein \listoffigures
- Richtig: \listoffigures und \listoftables nach \tableofcontents, Abkürzungen über \printglossary[type=\acronymtype]

### `STR-ROTER-FADEN` Roter Faden

Warnung, Prüfung: agent, Herkunft: WI

Jedes Kapitel muss erkennbar zur Beantwortung der Forschungsfragen beitragen und an das vorige anschließen.

- Falsch: Ein Grundlagenabschnitt, auf den später nichts zurückgreift
- Richtig: Grundlagen, die Methodik und Diskussion ausdrücklich aufgreifen

### `STR-DOPPELUNG` Keine Doppelung zwischen Kapiteln

Warnung, Prüfung: agent, Herkunft: FB

Wiederholte Inhalte kosten Platz und erzeugen Widersprüche, sobald nur eine Stelle geändert wird. Ein Querverweis genügt.

- Falsch: Kapitel 6 erklärt die Fusion erneut wie Kapitel 5
- Richtig: Kapitel 6 verweist auf \cref{sec:fusion} und ergänzt nur die Umsetzung

### `STR-DETAILTIEFE` Details in den Anhang

Hinweis, Prüfung: agent, Herkunft: FB

Vollständige Tabellen, Feldnamen, ER-Diagramme und Prompt-Volltexte belasten den Lesefluss. Im Text steht die Kernaussage mit Verweis auf den Anhang.

- Falsch: Alle 14 Tools mit Parametern im Fließtext
- Richtig: Kurzüberblick im Text, vollständige Tabelle in \cref{app:tools}

### `STR-UEBERLEITUNG` Übergänge zwischen Abschnitten

Hinweis, Prüfung: agent, Herkunft: WI

Ein Kapitel endet mit einer Brücke zum nächsten, sonst wirkt die Arbeit wie eine Sammlung einzelner Texte.

- Falsch: Kapitelende mitten in einer Detailbeschreibung
- Richtig: ein Satz, der festhält, was das Kapitel liefert und wofür das nächste es braucht

### `STR-KAPITELINHALT` Kapitel enthält seine Pflichtbestandteile

Warnung, Prüfung: agent, Herkunft: WI

Jeder Kapiteltyp hat erwartete Bestandteile (references/kapitel-checklisten.md). Fehlt einer, fällt das im Gutachten auf.

- Falsch: Ergebniskapitel ohne Beschreibung der Stichprobe
- Richtig: Stichprobe, deskriptive Werte, Hypothesentests


## Formeln

### `FORM-ERKLAERUNG` Formel mit Variablenliste und Rechenbeispiel

Hinweis, Prüfung: linter, Herkunft: FB

Jede abgesetzte Formel braucht eine Erklärung aller Variablen und ein Rechenbeispiel mit echten Werten. Erst dann lässt sie sich im Kolloquium verteidigen.

- Falsch: Formel ohne nachfolgende Erklärung
- Richtig: Formel, dann wobei ... und ein Beispiel mit Werten aus der Studie

### `FORM-VERSTAENDLICH` Formeln einfach und notwendig

Warnung, Prüfung: agent, Herkunft: FB

Eine Formel ist nur dann gerechtfertigt, wenn Text allein mehrdeutig wäre. Überflüssige Indizes und dichte Notation erschweren die Verteidigung.

- Falsch: $\hat{s}_{t,d}^{(k)}$ für einen einfachen Mittelwert
- Richtig: $s_d$ mit Erklärung im Text

### `FORM-NOTATION` Einheitliche Notation

Warnung, Prüfung: agent, Herkunft: WI

Ein Symbol bedeutet in der ganzen Arbeit dasselbe, und dieselbe Größe hat überall dasselbe Symbol.

- Falsch: alpha als Glättungsfaktor und als Signifikanzniveau
- Richtig: unterschiedliche Symbole oder ausdrückliche Klarstellung


## Abbildungen

### `ABB-GESTALTUNG` Abbildungen klar und symmetrisch

Hinweis, Prüfung: agent, Herkunft: FB

Diagramme mit gleich großen Boxen, geraden Pfeilen und wenig Text lassen sich erklären. Verschachtelte Schichten mit vielen Nebenpfeilen verwirren.

- Falsch: UML-Sequenzdiagramm mit 14 Nachrichten
- Richtig: Fluss mit vier Stationen und je einem Satz Erklärung


## Abgabe und Datensicherung

### `ABG-VERSIONIERUNG` Arbeit in einem privaten Git-Repository versionieren

Hinweis, Prüfung: umfeld, Herkunft: FB

Eine Abschlussarbeit entsteht über Monate. Ein Git-Repository mit privatem Remote sichert jeden Zwischenstand, macht Änderungen nachvollziehbar und schützt vor Datenverlust. Privat, weil die Arbeit bis zur Bewertung unveröffentlicht ist.

- Falsch: Thesis nur lokal oder in einem öffentlichen Repository
- Richtig: git init, .gitignore für Hilfsdateien und .lektorat/, gh repo create --private --source . --push

### `ABG-GIT-STAND` Gesicherter Stand entspricht dem Arbeitsstand

Hinweis, Prüfung: umfeld, Herkunft: FB

Nicht committete Änderungen und nicht gepushte Commits sind nicht gesichert. Vor jeder Pause und vor der Abgabe sollte der geprüfte Stand committet und gepusht sein, damit der Bericht zu einem nachvollziehbaren Stand gehört.

- Falsch: 12 geänderte Kapiteldateien seit dem letzten Commit
- Richtig: git status ist leer, git push ist erfolgt


## Arbeitsmarker

### `MARK-QUELLE-FEHLT` Markierte fehlende Quelle

Offen, Prüfung: linter, Herkunft: FB

Vom Schreibenden gesetzter Marker für einen bekannten, noch fehlenden Beleg. Vor der Abgabe muss die Liste leer sein.

- Falsch: \quellefehlt{Windsor et al. 2019}
- Richtig: \textcite{windsorTranslation2019}

### `MARK-OFFEN` Markierter offener Punkt

Offen, Prüfung: linter, Herkunft: FB

Vom Schreibenden gesetzter Marker für eine offene Entscheidung oder fehlende Zahl. Vor der Abgabe muss die Liste leer sein.

- Falsch: \offen{Zahl der Ausschlüsse}
- Richtig: Es wurden 4 Personen ausgeschlossen.


## Wortlisten

**wertung:** toll*, revolutionär*, beeindruckend*, bahnbrechend*, hervorragend*, exzellent*, perfekt*, fantastisch*, großartig*, wunderbar*, genial*, sensationell*, unglaublich*, enorm*, gewaltig*, massiv*, dramatisch*, spektakulär*, erstaunlich*, faszinierend*, spannend*, interessanterweise, leider, glücklicherweise, erfreulicherweise, bedauerlicherweise, erschreckend*, einzigartig*, unvergleichlich*, optimal*, ideal*, brillant*, katastrophal*, kläglich*, mühelos*, äußerst, extrem, absolut, zutiefst, überaus, bemerkenswert*, beachtlich*, vielversprechend*, überzeugend*, eindrucksvoll*, hochinteressant*, wegweisend*, herausragend*, verblüffend*

**selbstverstaendlich:** natürlich, offensichtlich, selbstverständlich, bekanntlich, zweifellos, zweifelsohne, zweifelsfrei, unbestritten*, klarerweise, logischerweise, selbstredend, fraglos, ohne Zweifel, wie jeder weiß

**floskel:** wie bereits erwähnt, wie oben erwähnt, wie schon erwähnt, wie bereits beschrieben, wie bereits dargestellt, wie bereits gesagt, wie oben beschrieben, es ist wichtig zu beachten, es ist zu beachten, dass, es sei darauf hingewiesen, es sei angemerkt, an dieser Stelle sei, an dieser Stelle ist, in diesem Kapitel wird, in diesem Abschnitt wird, im Folgenden wird, im Folgenden soll, es lässt sich festhalten, zusammenfassend lässt sich sagen, abschließend lässt sich sagen, es ist anzumerken, nicht zuletzt, last but not least, es versteht sich von selbst, auf den ersten Blick, im Endeffekt, unterm Strich, Fakt ist, Tatsache ist

**hedging:** könnte, könnten, möglicherweise, eventuell, vielleicht, unter Umständen, gegebenenfalls, vermutlich, wohl, scheinbar, anscheinend, gewissermaßen, tendenziell, durchaus, unter Umständen, womöglich, mitunter, gewisse*, in gewisser Weise, eher

**fuellwort:** eigentlich, quasi, sozusagen, halt, irgendwie, ziemlich, relativ, an sich, grundsätzlich, letztendlich, schlussendlich, im Prinzip, regelrecht, geradezu, gänzlich, letztlich, ja, nun mal

**doppelung:** zuerst zunächst, zunächst zuerst, bereits schon, schon bereits, zunächst erst, erst zunächst, wieder erneut, erneut wieder, nochmals wieder, wieder nochmals, lediglich nur, nur lediglich, einzig und allein, bereits vorher, vorher bereits, gegenseitig miteinander, miteinander gegenseitig, zusammen gemeinsam, gemeinsam zusammen, neu renoviert, bereits im Vorfeld, vorab bereits, Rückantwort, Grundprinzip, Zukunftsprognose, weiter fortsetzen, aufoktroyieren

**beleg_signal:** Studien zeigen, Studien belegen, Untersuchungen zeigen, Untersuchungen belegen, die Forschung zeigt, Forschung zeigt, in der Literatur, die Literatur, nachweislich, es ist bekannt, zahlreiche Studien, viele Studien, mehrere Studien, bisherige Arbeiten, frühere Arbeiten, bisherige Studien, frühere Studien, empirisch belegt, wissenschaftlich belegt, wie Studien, Befunde zeigen, Befunde deuten

