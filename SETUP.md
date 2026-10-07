# Setup (5 minutes)

This folder is the whole profile repo. Delete this file before you push, or leave it, it does no harm.

## 1. Put it in the right repo
GitHub shows a profile README only from a **public repo named exactly like your username**:
`Deepak420-GrandMaster/Deepak420-GrandMaster`. You already have one (your current README lives there).

Replace its contents with this folder:
- `README.md`
- `assets/` (all the SVGs)
- `scripts/`
- `.github/workflows/profile.yml`

## 2. Let the workflow write to the repo
Repo → Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.

## 3. Run it once
Actions tab → "Update profile cards" → Run workflow. This does two things:
- replaces the **sample numbers** in `assets/stats.svg` and `assets/languages.svg` with your real ones
- creates the `output` branch holding `snake.svg` (the contribution snake)

Until that first run finishes, the stats cards show demo data and the snake image is blank.
After that it refreshes daily.

## 4. Optional: count private contributions
Create a classic personal access token with `read:user`, add it as a repo secret named `PROFILE_TOKEN`,
and turn on "Include private contributions on my profile" in your GitHub profile settings.

## Editing the cards
- Header and about card: edit `assets/header.svg` and `assets/about.svg` directly (plain text and colours).
- Stack chips and project cards: edit the `STACK` and `PROJECTS` lists at the top of `scripts/build_static.py`,
  then run `python scripts/build_static.py` and commit the regenerated SVGs.
- Pastel palette: lavender `#B9A6F5`, pink `#FFB8D6`, sky `#9FD3F5`, mint `#9ADBBB`, peach `#FFCBA4`, ink `#3B3552`.
- The cards carry their own background, so they look the same in GitHub light and dark mode.
- Animations respect `prefers-reduced-motion`.

## Known limits
- SVGs shown through `<img>` can't be clickable, which is why the project cards are wrapped in links in the README.
- GitHub strips web fonts from SVGs, so the cards use system fonts (Segoe UI / SF / Menlo).
