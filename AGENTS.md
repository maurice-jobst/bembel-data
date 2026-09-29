# AGENTS.md — bembel-data

Open data for the BEMBEL iPhone app (Frankfurt kiosks, cider taverns, ratings).
Public GitHub repo, ODbL 1.0. Human docs are German; this file is for agents.

## What this repo is

- `data/wasserhaeuschen/`, `data/ebbelwei/`: one JSON per entry, `id` = file name.
- `data/bewertungen/<entry-id>/<github-login>.json`: one rating per entry per account.
- `schemas/*.schema.json`: the contract for every data folder. Change a schema
  only together with the app (`docs/app-funnel.md` documents the form contract).
- `dist/` is build output (gitignored); the `dist` branch is written by `publish.yml`.

## Commands

```bash
python3 scripts/validate.py        # schema + id/login/file-name checks (stdlib only)
python3 scripts/check_funnel.py    # issue/PR form contract with the app
python3 scripts/build_bundle.py    # -> dist/bembel-data.json, deterministic per commit
python3 scripts/check_authorship.py --author <login> $(git diff --name-only origin/main...HEAD)
```

`scripts/check` runs the first three in order and stops at the first failure; run it
before every PR. `check_authorship.py` stays in CI (it needs the PR author and the diff).
No pip, no dependencies. All four must be green before a PR.

## Rules

- **PR is the only entry.** `main` is protected; every change, including the
  maintainer's, lands via pull request with `validate.yml` and
  `rating-authorship.yml` green. Never push to `main`, never edit the `dist` branch.
- **A rating file is named after the PR author.** CI rejects a PR touching
  someone else's rating file. No exceptions, not for maintainers.
- **Every entry needs `sources`.** No unsourced facts, no copied text, no ads.
- **No PII in tracked files.** No email addresses, no data about third parties.
  The email-to-login table for entry provenance lives outside git: CI reads the
  repo secret `BEMBEL_LOGINS` (JSON object `{"email": "login"}`), local builds may
  use an untracked `logins.json`. Commits with `@users.noreply.github.com`
  addresses resolve without it; unknown emails render as `null`, never guessed.
- Keep the bundle deterministic: sorted lists, dates from git, no run-time clocks.
