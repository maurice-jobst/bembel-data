# Mitmachen

Danke! So kommt dein Beitrag rein.

## Neuer Eintrag (Wasserhäuschen / Ebbelwei-Wirtschaft)

1. Datei anlegen: `data/wasserhaeuschen/<slug>.json` (Slug = Kleinbuchstaben,
   Ziffern, Bindestriche; gleich dem `id`-Feld).
2. Schema einhalten — `schemas/wasserhaeuschen.schema.json` bzw.
   `schemas/ebbelwei.schema.json`. Vorlage: `data/wasserhaeuschen/yok-yok.json`.
3. **Jede Angabe braucht eine Quelle** (`sources`). Koordinaten aus
   OpenStreetMap sind okay (dann OSM als Quelle verlinken). Keine
   kopierten Texte — `note` ist ein neutraler Satz, keine Werbung.
4. `verified` bleibt `false`; ein Maintainer setzt es nach Prüfung.
5. PR stellen. CI (`scripts/validate.py`) muss grün sein.

Kein Bock auf JSON? [Issue-Formular](../../issues/new/choose) ausfüllen,
wir übernehmen den Rest.

## Bewertung

Eine Datei pro Eintrag und GitHub-Account:
`data/bewertungen/<eintrag-id>/<dein-github-login>.json` nach
`schemas/bewertung.schema.json`:

```json
{
  "entry": "yok-yok",
  "login": "deinlogin",
  "stars": 5,
  "date": "2026-08-13",
  "comment": "Nachts um drei die letzte Rettung."
}
```

**Der PR muss von dem Account kommen, dessen Login im Dateinamen steht** —
`scripts/check_authorship.py` prüft das in der CI und lehnt jeden PR ab, der
eine fremde Bewertungsdatei anfasst. Es gibt keinen Weg, stellvertretend zu
bewerten, auch nicht für Maintainer: die Zusage „eine Bewertung, ein Konto,
selbst abgegeben“ ist genau so viel wert wie ihre Ausnahmen.

Ändern oder zurückziehen geht jederzeit per neuem PR auf die eigene Datei.
Bewertungen sind ehrlich, konkret, ohne Beleidigungen und ohne Werbung —
Maintainer lehnen im Review ab, was das verletzt.

## Beiträge aus der App

Wer „Bewerten“ oder „verifizieren“ in der BEMBEL-App tippt, landet mit
vorausgefüllten Feldern hier — als ganz normaler Pull Request oder Issue aus
dem eigenen Account. Dieselben Regeln, derselbe Review. Die genauen Vorlagen
stehen in [docs/app-funnel.md](docs/app-funnel.md); wer ein Formularfeld
umbenennt, ändert damit stillschweigend den Trichter der App.

Lokal vorab prüfen:

```bash
scripts/check   # validate.py, check_funnel.py und build_bundle.py der Reihe nach
python3 scripts/check_authorship.py --author "$(gh api user --jq .login)" \
  $(git diff --name-only origin/main...HEAD)
```

## Was hier nicht reinkommt

- Erfundene oder ungeprüfte Angaben ohne Quelle
- Personenbezogene Daten über Dritte
- Werbung, Rankings gegen Bezahlung, Fake-Bewertungen

## Lizenz

Mit deinem PR stellst du den Beitrag unter [ODbL 1.0](LICENSE.md).
