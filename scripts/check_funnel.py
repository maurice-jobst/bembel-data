#!/usr/bin/env python3
"""Prüft, dass die Issue-Formulare die Feld-IDs tragen, auf die die BEMBEL-App
ihre Trichter-URLs baut (docs/app-funnel.md). Nur Standardbibliothek — die
YAML-Formulare werden zeilenweise nach `id:` abgesucht, nicht geparst.

Wer ein Feld umbenennt, bricht den Trichter, ohne dass irgendwo etwas
fehlschlägt — außer hier.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMS = ROOT / ".github" / "ISSUE_TEMPLATE"

CONTRACT = {
    "wasserhaeuschen.yml": {"name", "adresse", "quelle", "details"},
    "ebbelwei.yml": {"name", "adresse", "quelle", "details"},
    "verifizierung.yml": {"eintrag", "art", "quelle", "details"},
}

ID_RE = re.compile(r"^\s*id:\s*([a-z0-9_-]+)\s*$")


def main() -> int:
    problems: list[str] = []
    for form, expected in CONTRACT.items():
        path = FORMS / form
        if not path.is_file():
            problems.append(f"{form}: fehlt — die App verlinkt darauf")
            continue
        found = {m.group(1) for line in path.read_text(encoding="utf-8").splitlines() if (m := ID_RE.match(line))}
        if missing := expected - found:
            problems.append(f"{form}: Feld-IDs fehlen: {sorted(missing)}")

    if problems:
        print("Trichter-Vertrag verletzt (siehe docs/app-funnel.md):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"Trichter-Vertrag OK ({len(CONTRACT)} Formulare)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
