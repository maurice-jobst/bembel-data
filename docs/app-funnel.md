# Der Trichter aus der App

„Bewerten“, „Eintrag fehlt“ und „verifizieren“ in der BEMBEL-App sind keine
API-Aufrufe — es sind vorausgefüllte GitHub-Links. Kein Backend, keine Konten,
kein Token. Die App baut die folgenden URLs; dieses Dokument ist der Vertrag.

## Bewerten (neue Bewertungsdatei)

```
https://github.com/maurice-jobst/bembel-data/new/main
  ?filename=data/bewertungen/<eintrag-id>/<login>.json
  &value=<URL-kodiertes JSON>
```

`<login>` ist der in den App-Einstellungen hinterlegte GitHub-Benutzername;
ohne Eintrag setzt die App `DEIN-LOGIN` und der Beitragende korrigiert den
Dateinamen im Browser. `value` ist der Inhalt nach
[`bewertung.schema.json`](../schemas/bewertung.schema.json), mit `stars` und
`date` vorbelegt, `comment` leer. GitHub legt Fork und Pull Request selbst an.

## Eintrag fehlt

```
https://github.com/maurice-jobst/bembel-data/issues/new
  ?template=wasserhaeuschen.yml        (oder ebbelwei.yml)
  &title=[Wasserhäuschen] <name>
  &name=<name>&adresse=<adresse>
```

Feld-IDs beider Formulare: `name`, `adresse`, `quelle`, `details`.

## Verifizieren / korrigieren

```
https://github.com/maurice-jobst/bembel-data/issues/new
  ?template=verifizierung.yml
  &title=[Verifizierung] <name>
  &eintrag=<eintrag-id>
```

Feld-IDs: `eintrag`, `art`, `quelle`, `details`.

## Regeln

- Feld-IDs sind Teil des Vertrags. Wer sie umbenennt, bricht den Trichter,
  ohne dass irgendetwas rot wird — das Formular öffnet sich dann einfach leer.
  Deshalb prüft [`scripts/check_funnel.py`](../scripts/check_funnel.py) die
  Feld-IDs in der CI.
- Die App schickt nie einen Token und niemals personenbezogene Daten. Alles,
  was in der URL steht, steht ohnehin öffentlich im Repo.
