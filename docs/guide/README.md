# User guide: how to change it

`guide.pdf` (in the repo root) is **built automatically** from the text file(s) in this folder and the screenshots in `img/`.
Do not edit the PDF. Edit the text, commit to `main`, and the **Build guide** workflow rebuilds and commits `guide.pdf` (about 1 minute).

## Everyday edits (phone friendly)
1. Open `docs/guide/en.md` (and `fr.md` if this planner has one) in the GitHub web editor.
2. Find the chapter by its `# Title` line. Change the words. Keep the same French and English chapters in step.
3. Commit to `main`. Check the Actions tab: "Build guide" must be green. Open `guide.pdf` to see it.

## Markup (one chapter = one page or more)
```
# Chapter title                  starts a chapter (also appears in the contents list)
eyebrow: STEP 1 OF 3             small red label above the title (optional)
side: step1.png, menu.png        screenshots from img/<lang>/ shown beside the text (optional, at most two)
## Sub-heading                   bold blue heading
Plain paragraph text.            **bold** and *italic* work
- bullet            1. numbered  (no nested lists)
> **Box title**                  a shaded note box; the next "> " lines are its text
| Head A | Head B |             a table (first row is the header, second column is the wider one)
```
The first lines of each file (between `---`) hold the cover text: `app`, `doc`, `tagline`, `notice`, `lang_label`, `toc`.

## Screenshots
`img/en/` and `img/fr/` hold phone-size PNGs. When the planner screens change, run the **Guide screenshots** workflow
(Actions, Run workflow). It retakes them from the live code and commits them; then **Build guide** runs by itself.

## What to do when a feature changes
Change only the chapter that describes it (search the `.md` for the button's name). If a button is renamed in the planner,
search the guide for the old name and replace it everywhere (both languages).

## After retaking screenshots, rebuild the PDF by hand

The "Guide screenshots" workflow commits the new pictures as a bot, and a bot commit does NOT start "Build guide" by itself. Order: Actions, Guide screenshots, Run workflow; when it is green, Actions, Build guide, Run workflow. `guide.pdf` is then rebuilt and committed. (Editing a chapter by hand in `docs/guide/*.md` starts "Build guide" on its own.)
