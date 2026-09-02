#!/usr/bin/env python3
"""Baut das veröffentlichte Daten-Bundle aus Einträgen, Bewertungen und der
Git-Historie. Nur Standardbibliothek und git — keine Abhängigkeiten.

Ausgabe: dist/bembel-data.json, die Datei, die die BEMBEL-App per Conditional
GET lädt (BEM-S11).

Deterministisch: derselbe Commit erzeugt dieselben Bytes. `generatedAt` ist das
Datum von HEAD, nicht die Uhrzeit des Laufs; alle Listen sind sortiert.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/maurice-jobst/bembel-data"
REGISTERS = ("wasserhaeuschen", "ebbelwei")
SCHEMA_VERSION = 1
NOREPLY = "@users.noreply.github.com"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def load_logins() -> dict[str, str]:
    """E-Mail -> GitHub-Login für Autoren ohne noreply-Adresse.

    Die Tabelle ist PII und liegt nie im Repo: in der CI kommt sie aus dem
    Secret BEMBEL_LOGINS (JSON-Objekt), lokal wahlweise aus einer
    unversionierten logins.json (.gitignore). Fehlt beides, bleiben
    Autoren mit Klartext-Mail ungenannt (null) — nie geraten.
    """
    raw = os.environ.get("BEMBEL_LOGINS", "").strip()
    if not raw:
        path = ROOT / "logins.json"
        if not path.is_file():
            return {}
        raw = path.read_text(encoding="utf-8")
    return {k.lower(): v for k, v in json.loads(raw).items()}


def resolve_login(email: str, table: dict[str, str]) -> str | None:
    """GitHub-Login aus der Autor-Mail. Nur ableiten, nie raten."""
    email = email.strip().lower()
    if email.endswith(NOREPLY):
        local = email[: -len(NOREPLY)]
        return local.split("+", 1)[1] if "+" in local else local
    return table.get(email)


def history(rel: str) -> list[tuple[str, str, str]]:
    """Commits, die rel berühren, älteste zuerst: (sha, ISO-Datum, Autor-Mail)."""
    out = git("log", "--reverse", "--format=%H%x1f%aI%x1f%ae", "--", rel)
    rows = []
    for line in out.splitlines():
        if line.strip():
            sha, date, email = line.split("\x1f")
            rows.append((sha, date, email))
    return rows


def blob_at(sha: str, rel: str):
    try:
        return json.loads(git("show", f"{sha}:{rel}"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def provenance(rel: str, table: dict[str, str]) -> tuple[dict, str | None, str | None]:
    """(provenance-Block, Login des Ersterstellers, Login des Verifizierers)."""
    commits = history(rel)
    creator = resolve_login(commits[0][2], table) if commits else None

    verified_at = None
    verifier = None
    was_verified = False
    for sha, date, email in commits:
        doc = blob_at(sha, rel)
        if doc is None:
            continue
        now_verified = bool(doc.get("verified"))
        if now_verified and not was_verified:
            verified_at, verifier = date, resolve_login(email, table)
        elif not now_verified:
            verified_at, verifier = None, None
        was_verified = now_verified

    last = commits[-1] if commits else None
    return (
        {
            "lastEditor": resolve_login(last[2], table) if last else None,
            "lastChangedAt": last[1] if last else None,
            "verifiedAt": verified_at,
            "historyURL": f"{REPO_URL}/commits/main/{rel}",
            "fileURL": f"{REPO_URL}/blob/main/{rel}",
        },
        creator,
        verifier,
    )


def merkmale_for(kind: str, doc: dict) -> list[str]:
    tags = set(doc.get("features") or [])
    if kind == "ebbelwei":
        if doc.get("garden"):
            tags.add("garten")
        if doc.get("eigenkelterei"):
            tags.add("eigenkelterei")
    return sorted(tags)


def collect_ratings() -> dict[str, list[dict]]:
    """entry-id -> Bewertungen, sortiert nach (Datum, Login)."""
    by_entry: dict[str, list[dict]] = {}
    for path in sorted((ROOT / "data" / "bewertungen").glob("*/*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        by_entry.setdefault(path.parent.name, []).append(
            {
                "login": doc["login"],
                "stars": doc["stars"],
                "date": doc["date"],
                "comment": doc.get("comment"),
            }
        )
    for ratings in by_entry.values():
        ratings.sort(key=lambda r: (r["date"], r["login"]))
    return by_entry


def summarise(ratings: list[dict]) -> dict:
    total = sum(r["stars"] for r in ratings)
    return {
        "average": round(total / len(ratings), 2),
        "count": len(ratings),
        "ratings": ratings,
    }


def main() -> int:
    table = load_logins()
    ratings_by_entry = collect_ratings()
    tallies: dict[str, dict] = {}

    def tally(login: str | None) -> dict | None:
        if not login:
            return None
        return tallies.setdefault(
            login,
            {"login": login, "entries": 0, "verifications": 0, "ratings": 0, "firstRatings": []},
        )

    entries = []
    for kind in REGISTERS:
        for path in sorted((ROOT / "data" / kind).glob("*.json")):
            rel = str(path.relative_to(ROOT))
            doc = json.loads(path.read_text(encoding="utf-8"))
            prov, creator, verifier = provenance(rel, table)

            if (row := tally(creator)) is not None:
                row["entries"] += 1
            if (row := tally(verifier)) is not None:
                row["verifications"] += 1

            ratings = ratings_by_entry.get(doc["id"], [])
            if ratings and (row := tally(ratings[0]["login"])) is not None:
                row["firstRatings"].append(doc["id"])

            entries.append(
                {
                    "id": doc["id"],
                    "kind": kind,
                    "name": doc["name"],
                    "address": doc["address"],
                    "district": doc.get("district"),
                    "latitude": doc["latitude"],
                    "longitude": doc["longitude"],
                    "openingHours": doc.get("openingHours"),
                    "since": doc.get("since"),
                    "merkmale": merkmale_for(kind, doc),
                    "note": doc.get("note"),
                    "sources": doc["sources"],
                    "verified": bool(doc.get("verified")),
                    "provenance": prov,
                    "rating": summarise(ratings) if ratings else None,
                }
            )

    for entry_id, ratings in ratings_by_entry.items():
        for rating in ratings:
            if (row := tally(rating["login"])) is not None:
                row["ratings"] += 1

    coverage: dict[str, dict] = {}
    for entry in entries:
        area = entry["district"] or entry["address"]["city"]
        row = coverage.setdefault(area, {"district": area, "verified": 0, "candidates": 0})
        row["verified" if entry["verified"] else "candidates"] += 1

    head_date = git("log", "-1", "--format=%aI").strip()
    head_sha = git("log", "-1", "--format=%h").strip()

    bundle = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": head_date,
        "commit": head_sha,
        "entries": sorted(entries, key=lambda e: (e["kind"], e["id"])),
        "contributors": sorted(tallies.values(), key=lambda c: c["login"]),
        "coverage": sorted(coverage.values(), key=lambda c: c["district"]),
    }
    for contributor in bundle["contributors"]:
        contributor["firstRatings"].sort()

    out = ROOT / "dist" / "bembel-data.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"dist/bembel-data.json: {len(bundle['entries'])} Einträge, "
        f"{len(bundle['contributors'])} Mitwirkende, {len(bundle['coverage'])} Stadtteile"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
