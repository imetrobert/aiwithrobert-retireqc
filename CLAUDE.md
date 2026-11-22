# aiwithrobert-retireqc (Quebec Retirement Planner) - read this first, it is the map

One static file: `index.html` (about 400-600 KB: HTML form for steps 1-3, results in step 4, one big
`<script>`). No build step. Data saved in localStorage keys `qcrp_*`. Recipes: `docs/common-edits.md`.
Line numbers: `docs/code-map.md` (generated). The first ~25 lines of `index.html` are an "AI MAP" comment
(functions, data flow, tax-rule location, edit rules). NEVER read index.html whole: use
`grep -n name index.html` or Read with offset and limit.

## Rules (non-negotiable)
- Privacy: no network calls that send user data, no analytics, no third-party scripts. The checks fail
  on `fetch`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`. Saving to an account must be a deliberate,
  reviewed change, with browser-side encryption, never plain figures on a server.
- Never put a real person's figures, names or defaults into the file. This repo is public.
- Do not rename element ids (the JS reads them) or localStorage keys `qcrp_*` (users' saved data).
- Tax numbers are for Quebec/federal 2026. Never invent a rate: check the official table, then edit
  `getDefaultTaxRules()` and set `verifiedDate`.
- Free tier only. Pages from `main`; domain in `CNAME`.
- French: every English string you change needs a French entry. Add it to `Object.assign(EXACT, {...})` (exact text to French) or `P.push([...])` (pattern to French) near the end of the script. Test with `window.QCRP_I18N.toggle()` in the browser console.

## Where things are (grep the name)
- Tax rules: `getDefaultTaxRules`, `getTaxRules`, `validateTaxRulesShape`; engine `calculateTax`;
  withholding `calcWithholdingTax`; LIF/RRIF `rrifMinFactor`, `federalLifMaxPct`.
- Simulation: `calculateRetirementPlan` -> `runSimulation` (year by year) -> `renderResultsUi` -> `yearCardsHtml`.
- Form data: `getProfileData`, `populateForm`, `MONEY_FIELDS`. Pop-up notes: `showInfo`, `initInfoNotes`.
- Hard-coded: `TFSA_ANNUAL_LIMIT`, 50% capital-gains inclusion, RRIF 1/(90-age) before 71, QPP/OAS factors.
- Version string: `APP_VERSION` and the `<title>`.

## Before and after any edit
1. Make the change in one place (see recipes). 2. `python3 scripts/check_planner.py` must say OK.
3. Open the page, press "Show my plan", scroll the schedule: money in = spending + tax + clawback +
   reinvested every year. The Checks workflow also refreshes `docs/code-map.md` after a push.
