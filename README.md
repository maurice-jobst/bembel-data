# bembel-data

Community-gepflegte Frankfurt/Rhein-Main-Datensätze für die
[BEMBEL-App](https://github.com/maurice-jobst/bembel) — **wie Yelp, nur in
GitHub.** Einträge und Bewertungen sind Pull Requests; die App lädt
versionierte Releases dieses Repos. Kein Backend, keine Konten in der App —
wer beitragen will, tut es hier, öffentlich und nachvollziehbar.

## Datensätze

| Ordner | Inhalt | Status |
|---|---|---|
| `data/wasserhaeuschen/` | Frankfurts Kiosk-Kultur: ein JSON pro Wasserhäuschen | im Aufbau |
| `data/ebbelwei/` | Traditionelle Apfelwein-Wirtschaften | geplant |
| `data/bewertungen/` | Bewertungen, ein JSON pro Eintrag und GitHub-Account | im Aufbau |

## Mitmachen

- **Wasserhäuschen melden / Bewertung abgeben:** am einfachsten über die
  [Issue-Formulare](../../issues/new/choose) — Maintainer machen daraus einen PR.
- **Direkt per PR:** Datei nach Schema anlegen (siehe `schemas/` und
  [CONTRIBUTING.md](CONTRIBUTING.md)), CI validiert automatisch.
- Jeder Eintrag braucht eine **Quelle** (`source`-URL) — keine erfundenen
  Daten, keine kopierten Texte. Fakten, Namen, Koordinaten, Links.

## Wie die Daten in die App kommen

Releases dieses Repos sind versionierte Daten-Bundles. Die App holt sie per
Conditional GET (siehe BEMBEL-Ticket
[BEM-S11](https://github.com/maurice-jobst/bembel/issues/46)); ein
Bundle-Snapshot ist in der App gebündelt, damit alles offline funktioniert.
Aggregierte Bewertungen werden hier in CI berechnet — nicht von einem Server.

## Lizenz

Datenbank und Inhalte stehen unter der
[Open Database License (ODbL) v1.0](LICENSE.md). Beiträge erfolgen unter
dieser Lizenz.
