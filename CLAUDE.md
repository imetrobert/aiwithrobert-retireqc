# aiwithrobert-retireqc (Quebec Retirement Planner) - read this first, it is the map

One static file: `index.html` (about 700 KB: HTML form for steps 1-3, results in step 4, one big
`<script>`). No build step. Data saved in localStorage keys `qcrp_*`. Recipes: `docs/common-edits.md`.
Line numbers: `docs/code-map.md` (generated). The first ~25 lines of `index.html` are an "AI MAP" comment
(functions, data flow, tax-rule location, edit rules). NEVER read index.html whole: use
`grep -n name index.html` or Read with offset and limit.

If something breaks (red check, wrong result, no access): `docs/if-something-breaks.md` (open it first).

## Rules (non-negotiable)
- Privacy: `index.html` makes NO network calls (checks fail on `fetch`, `XMLHttpRequest`, `sendBeacon`,
  `WebSocket`). Sign-in and saved plans live ONLY in `account.js`, which encrypts every plan in the
  browser before upload. Never send plain figures anywhere. Never put a secret key in either file.
- Never put a real person's figures, names or defaults into the file. This repo is public.
- Do not rename element ids (the JS reads them) or localStorage keys `qcrp_*` (users' saved data).
- Tax numbers are for Quebec/federal 2026. Never invent a rate: check the official table, then edit
  `getDefaultTaxRules()` and set `verifiedDate`.
- Free tier only. Pages from `main`; domain in `CNAME`.
- French: every English string you change needs a French entry. Add it to `Object.assign(EXACT, {...})` (exact text to French) or `P.push([...])` (pattern to French) near the end of the script. Test with `window.QCRP_I18N.toggle()` in the browser console.

## Two files, two jobs
- `index.html` = the planner (forms, tax, results). Almost every minor feature goes here.
- `account.js` = sign-in gate, "Welcome <email>" banner, the rows it adds to the planner menu `#toolMenu` (Logged in as, My plans, Documentation, Sign out), saved plans. Touch it only for those.
  Its documentation link is `CFG.docs` (now `guide.pdf`, the user guide in the repo root; blank = link hidden). `guide.pdf` is BUILT from `docs/guide/en.md` and `fr.md` plus screenshots in `docs/guide/img/` by the Build guide workflow: edit the .md (markup in `docs/guide/README.md`), commit, never edit the PDF. Screenshots: Actions, Guide screenshots, Run workflow. App id `retire-qc`; the other planner has its own copy.
- `statements.js` (+ `vendor/pdfjs/`) = reads a government statement PDF on the device and fills QPP fields after Preview/Apply (recipe 11 in docs/common-edits.md). No network calls. Test: `python3 scripts/test_statements.py`. Only FAKE sample PDFs in `tests/fixtures/` (public repo).
- Household mode: spouse fills in their own full form, results merge (common-edits recipe on household mode). Test: `python3 scripts/test_household.py`.
- Pension income splitting (household mode, on by default): `hhSplitPensions` moves up to 50% of the higher earner's eligible pension income each year via `p.hhTaxAdj`; recipe in `docs/common-edits.md` (recipe 14).
- Spousal rollover (household mode, on by default): `hhRollover` passes the first-dying spouse's savings to the survivor tax-free (`p.hhSurv`, `p.hhRollover`); recipe 14 in `docs/common-edits.md`.
- Expense list: optional list on Step 2 that fills and locks the spending fields (common-edits recipe on the expense list). Test: `python3 scripts/test_expenses.py`.
- Other income in retirement (optional): a Step 1 Yes/No question shows a Step 2 card with one yearly amount or a year-by-year list built from the ages (recipe 15 in `docs/common-edits.md`). It is taxable income in `runSimulation` (`otherIncY`, row field `otherInc`), per person. Test: `python3 scripts/test_other_income.py` (and the "other income" part of `scripts/test_tax.py`).
- Compare and stress-test tools, one-page summary, text size, life-event presets (v1.4): one block in `index.html` (`grep -n "COMPARE AND STRESS-TEST TOOLS" index.html`), recipe 16 in `docs/common-edits.md`. They call `runSimulation` with changed copies of the plan and never change a calculation. Test: `python3 scripts/test_planning_tools.py`.
- Monte Carlo run summary and re-run button: at the top of Step 4, `#mcRunBanner` is built by `mcRunBannerHtml` (grep it) from the headline run's yearly returns (`run.yearReturns`) and ranks that run among the 300 trials; `mcRerun()` bumps `mcSeedShift` and recalculates (Show my plan resets it). Display only; no calculation changes. Test: `python3 scripts/test_mc_run.py`. The results page also has a "Judge the plan by" toggle (This run / All markets, `mcJudge`, `mcSetJudge`) that makes the on-track badge follow the 300-run success rate (90%+ on track, 70-89% some risk, under 70% needs a change); default is This run. Recipe 17 in `docs/common-edits.md`.
- Sale of the family home (optional): Step 1 question `homeSaleDecl` (No / smaller home / rent) shows the Step 2 card `homeSaleCard`. The sale is tax-free (principal residence); `runSimulation` adds the net money (price - selling costs - mortgage - smaller home and buying costs) to the TFSA up to its room, the rest to non-registered (or all non-registered), and changes yearly spending from the sale year (`hsNetProceeds`, `hsCostDelta`, block `// ---- Optional sale of the family home`). Per person: in couple mode answer on one form only. Test: `python3 scripts/test_home_sale.py`. Recipe 18 in `docs/common-edits.md`.
- Tax check: `python3 scripts/test_tax.py` compares the tax engine and yearly plan with an independent calculation (own copy of the 2026 numbers at the top of the script). Update that copy whenever the tax numbers change (common-edits recipe on the tax check).
- Language start: the English address always opens in English (a new browser visit resets `qcrp_lang` to en); only `?lang=fr` (sent by retraiteqc.aiwithrobert.com) opens French. Logic sits at the top of `account.js` and in the i18n block of `index.html`; the browser language is ignored.
- Test the gate: `python3 scripts/test_account.py` (stubbed server, needs `pip install playwright`). CI runs it.
- Saved plans table: `migration/planner_profiles.sql` (run once via the Supabase AI prompt in the README).

## Words to keep the same everywhere
- **Everyday spending** is the one name for the normal day-to-day spending target (Step 2 field `spendAmountLabel` and its JS text, year-card lines "Everyday spending", "Goes to everyday spending"). Special, year-specific costs are Life events, never "spending" or "living costs". Do not reintroduce "living costs", "General living costs" or "Spending you want". If you rename it, change the English text, the info note under the field, the French entries (Quebec `EXACT` and `P.push`), the guide and the glossary row together; `scripts/test_home_sale.py` checks the label and the year cards.

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
