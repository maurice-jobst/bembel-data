#!/usr/bin/env python3
"""Every rating file must be named after the account that opened the PR.

This is the rule the whole trust model rests on: one rating per entry per
GitHub account, and nobody rates on someone else's behalf. `validate.py`
cannot check it — it only sees files, not who proposed them — so this script
takes the PR author and the changed paths and decides.

    python3 scripts/check_authorship.py --author <login> <changed paths...>

Only paths under data/bewertungen/ are judged; everything else is ignored,
so the same call is safe for a mixed PR. Additions, edits and deletions are
treated alike: you may withdraw your own rating, not someone else's.

GitHub logins are case-insensitive, so the comparison is too.

Exit 0 on success, 1 with a readable report otherwise.
"""

import argparse
import sys
from pathlib import PurePosixPath

RATINGS = "data/bewertungen"


def problems(author: str, paths: list[str]) -> list[str]:
    found = []
    for raw in paths:
        if not raw.strip():
            continue
        path = PurePosixPath(raw.strip())
        if path.parts[:2] != ("data", "bewertungen"):
            continue
        if path.name.startswith("."):
            continue
        if len(path.parts) != 4 or path.suffix != ".json":
            found.append(
                f"{path}: ratings live at {RATINGS}/<eintrag-id>/<github-login>.json"
            )
            continue
        if path.stem.lower() != author.lower():
            found.append(
                f"{path}: named for '{path.stem}', but this PR comes from "
                f"'{author}' — rate under your own login, or ask "
                f"'{path.stem}' to open the PR"
            )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author", required=True, help="GitHub login of the PR author")
    parser.add_argument("paths", nargs="*", help="paths changed by the PR")
    args = parser.parse_args()

    found = problems(args.author, args.paths)
    if found:
        print(f"{len(found)} problem(s):")
        for line in found:
            print(f"  - {line}")
        return 1
    print(f"rating authorship OK (author: {args.author})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
