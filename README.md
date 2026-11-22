# Quebec Retirement Planner

Free, private retirement calculator for Quebec employees. One static file (`index.html`), no build step,
no server. Planned address: **https://retireqc.aiwithrobert.com** (access by invitation through access.imetrobert.com,
app id `retire-qc`; see "Access" below).

## How it is hosted
GitHub Pages, branch `main`, folder `/ (root)`. Custom domain comes from `CNAME`.
DNS record at the domain provider: `CNAME  retireqc  ->  imetrobert.github.io`.
Settings -> Pages -> Source: "Deploy from a branch", main, /(root); then Enforce HTTPS.

## Privacy (what the app promises)
All figures stay in the browser (localStorage keys `qcrp_*`) or in a file the user saves. Nothing is
uploaded. `scripts/check_planner.py` fails if a network call is added. The only outside request is
the Google Fonts stylesheet. Saving profiles to an account is a separate, reviewed change.

## Access
Not gated yet: until the login gate ships, do not publish the address or turn on Pages. Gate plan:
Supabase login plus `has_app_access('retire-qc')`, saved profiles encrypted in the browser.

## Files
- `index.html` the whole app. `CLAUDE.md` the map for editing. `docs/common-edits.md` recipes.
- `docs/code-map.md` generated line numbers. `scripts/check_planner.py`, `scripts/code_map.py`.
- `.github/workflows/checks.yml` weekly and on change: runs both scripts.

## Accounts and saved plans
Access is by invitation (access.imetrobert.com, app id `retire-qc`). Signed-in users see "Welcome <email> to your retirement
planner" and a "My plans" button; each saved plan is encrypted in the browser with the user's own passphrase
(unrecoverable if forgotten). One-time setup: run `migration/planner_profiles.sql` via the Supabase AI assistant
(the file lives in the Quebec repo, `aiwithrobert-retireqc`).
