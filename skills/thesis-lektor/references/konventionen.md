# Konventionen

Erläuterungen zu Regeln, die mehr Kontext brauchen als eine Zeile im Regelwerk.

## Zeitformen (`SPR-TEMPUS`)

Im deutschsprachigen wissenschaftlichen Schreiben folgt die Zeitform dem Inhalt, nicht dem Kapitel. Die Grundregel lautet: Präsens für das, was gilt, Präteritum für das, was in der eigenen Untersuchung geschehen ist.

| Inhalt | Zeitform | Beispiel |
|---|---|---|
| Theorie, Definitionen, allgemein anerkannte Befunde | Präsens | Extraversion beschreibt die Neigung zu Geselligkeit. |
| Wiedergabe von Literatur | Präsens | \textcite{goldberg1990} zeigt, dass ... |
| Konkretes Vorgehen einer früheren Einzelstudie | Präteritum möglich | In der Studie bewerteten 388 Personen vier Stimmen. |
| Aufbau und Inhalt der eigenen Arbeit, Verweise | Präsens | \cref{tab:x} zeigt die Kennwerte. Kapitel 5 beschreibt ... |
| Beschreibung des Systems oder Prototyps | Präsens | Das Backend speichert jede Runde. |
| Studiendesign, Instrumente, Auswertungsplan | Präsens | Die Zuweisung erfolgt nach Anmeldeposition. |
| Durchführung der eigenen Erhebung, Stichprobe | Präteritum | Es nahmen 48 Personen teil. Vier brachen ab. |
| Konkrete eigene Ergebnisse | Präteritum oder Präsens, einheitlich | Die adaptive Bedingung erzielte höhere Werte. |
| Deutung, Diskussion, Fazit | Präsens | Das Ergebnis spricht dafür, dass ... |
| Ausblick | Präsens oder Futur | Künftige Arbeiten können prüfen, ob ... |

Wichtiger als jede einzelne Zuordnung ist Einheitlichkeit. Innerhalb eines Absatzes wechselt die Zeitform nur, wenn der Inhalt wechselt. Das Perfekt wirkt mündlich und bleibt die Ausnahme.

Für ein Methodenkapitel, das vor der Erhebung entsteht und danach fertiggestellt wird, gilt: Design und Instrumente im Präsens, weil sie die Untersuchung beschreiben, wie sie angelegt ist. Was tatsächlich passiert ist (Rekrutierung, Abbrüche, Abweichungen vom Plan), im Präteritum.

## Zahlen (`TYP-ZAHLWORT`)

Im Fließtext werden die Zahlen null bis zwölf als Wort geschrieben, ab 13 als Ziffer. Das ist eine verbreitete Konvention deutscher Schreibratgeber und Duden-Empfehlungen. APA 7 setzt die Grenze im Englischen bei zehn, die Arbeit folgt der deutschen Konvention.

Ziffern stehen trotzdem bei:

- Maßeinheiten und Prozent: 8\,s, 5\,\%
- Kennungen: Kapitel 5, Item 3, H1, Stufe 2, Version 19
- Skalenwerten, Messwerten, Gewichten und Ergebnissen: Skalenmitte 3, Gewicht 0,5
- Reihen mit größeren Zahlen: zwischen 5 und 40 Personen
- Tabellen, Abbildungen, Formeln und Datumsangaben

## Herkunft von Abbildungen (`FMT-ABB-QUELLE`)

Jede Abbildung nennt ihre Herkunft am Ende der Bildunterschrift.

| Fall | Angabe |
|---|---|
| vollständig selbst erstellt | `Eigene Darstellung` |
| selbst erstellt nach einer Vorlage, verändert | `Eigene Darstellung nach \textcite{key}` |
| unverändert übernommen | `Quelle: \textcite{key}` (Nutzungsrechte beachten) |
| Bildschirmfoto der eigenen Software | `Eigene Darstellung` |

Beispiel:

```latex
\caption{Architektur des Prototyps. Eigene Darstellung}
\caption{Forschungsmodell. Eigene Darstellung nach \textcite{davis1989}}
```

Für Tabellen gilt dasselbe, sobald sie Inhalte aus einer Quelle übernehmen oder anpassen. Tabellen mit eigenen Daten brauchen keine Angabe.

## Zitierweise (`ZIT-*`)

- `\textcite{key}` im Satz: \textcite{goldberg1990} zeigt ...
- `\parencite{key}` am Satzende vor dem Punkt: ... \parencite{goldberg1990}.
- mehrere Quellen: `\parencites{a}{b}` oder `\parencite{a,b}`, chronologisch oder alphabetisch, aber einheitlich
- Seitenangabe bei wörtlichem Zitat: `\parencite[S.~12]{key}`
- Belege beziehen sich auf den Satz. Gilt eine Quelle für einen ganzen Absatz, steht sie im ersten Satz und der Absatz macht deutlich, dass er sie weiter referiert.
- Sekundärzitate (zitiert nach) nur, wenn das Original nicht zugänglich ist.

## Abkürzungen und Typografie

| Fall | Schreibweise |
|---|---|
| mehrteilige Abkürzung | `z.\,B.`, `d.\,h.`, `u.\,a.`, `i.\,d.\,R.` |
| Prozent | `15\,\%` |
| Gleichung im Text | `$N = 40$` |
| Bereich | `S.~12--15`, `2020--2026` |
| Anführungszeichen | `\enquote{...}` |
| Fachabkürzung | `\gls{a:LLM}` aus dem Glossar, erster Aufruf schreibt aus |
| Dezimalzahl | Komma: 0,5. In Formeln über `{,}` oder das Paket icomma |

## Gendergerechte Sprache

Die Regeln enthalten keine Vorgabe dazu. Wenn die Arbeit eine Form wählt (Doppelnennung, Partizip wie Teilnehmende, neutrale Formen wie Person), prüft `TERM-VARIANTEN` nur, dass sie einheitlich bleibt.
