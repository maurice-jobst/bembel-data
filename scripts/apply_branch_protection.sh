#!/bin/sh
# Branch protection on main: a PR, both CI checks green, and no way around it
# for anyone — enforce_admins is on because the README promises exactly that
# ("Niemand bewertet stellvertretend"). A maintainer who could merge a red
# authorship check would make that claim false.
#
# 0 required approvals: a small team shouldn't be blocked from merging its own
# solo tickets. Raise it once there's a second active contributor.
#
# strict:false on purpose — data files are independent of each other, so
# forcing every contributor to rebase onto a moving main buys nothing. CI
# already runs against the merge result.
#
# GitHub Free supports this only on PUBLIC repos; it 403s if the repo goes
# private again.
set -eu
gh api -X PUT repos/maurice-jobst/bembel-data/branches/main/protection --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": [
      "Schema validation (stdlib only, no pip)",
      "A rating file must be named after the PR author"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
