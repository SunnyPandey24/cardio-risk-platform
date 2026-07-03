# Deployment Guide

This project has two things to "deploy":
1. **The GitHub repository itself** — the full structured codebase (data, SQL, notebook, model, Excel, dashboard).
2. **The live dashboard** — `docs/index.html`, hosted for free with GitHub Pages so anyone can open a link and use it (no download needed).

Total time: ~10 minutes.

---

## 0. Prerequisites

- A GitHub account
- Git installed locally (`git --version` to check)
- (Optional but recommended) the [GitHub CLI](https://cli.github.com/) — `gh --version`

---

## 1. Recommended repo structure

This is exactly how the project folder is already organized — you're just pushing it as-is:

```
cardiovascular-risk-analysis/
├── .github/workflows/ci.yml   # auto-runs the full pipeline on every push
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── docs/
│   └── index.html             # the dashboard — this is what GitHub Pages serves
├── dashboard/
│   └── dashboard.html         # same dashboard, kept here for local/offline use
├── data/
│   ├── generate_data.py
│   ├── clean_and_engineer.py
│   ├── cardio_raw.csv
│   └── excel_cleaned_cardio_data.csv
├── sql/
│   ├── schema.sql
│   └── kpi_queries.sql
├── python_analysis/
│   ├── build_notebook.py
│   └── Cardio_Statistical_Analysis.ipynb
├── model/
│   ├── train_model.py
│   └── model_results.json
└── excel/
    ├── build_excel.py
    └── cardio_project.xlsx
```

Why `docs/index.html` specifically: GitHub Pages can serve straight from a `/docs` folder on
your `main` branch with zero configuration — no separate branch, no build step, no GitHub
Actions permissions to set up.

---

## 2. Initialize git and make your first commit

Open a terminal in the project's root folder (the one containing `README.md`) and run:

```bash
git init
git add .
git commit -m "Initial commit: full cardiovascular risk analysis pipeline"
```

---

## 3. Create the GitHub repository

**Option A — GitHub CLI (fastest):**
```bash
gh repo create cardiovascular-risk-analysis --public --source=. --remote=origin --push
```
This creates the repo, sets the remote, and pushes in one step. Skip to Step 5.

**Option B — GitHub website:**
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `cardiovascular-risk-analysis`
3. Keep it **Public** (so Pages and the badges work), don't initialize with a README (you already have one)
4. Click **Create repository**

---

## 4. Connect and push (if you used Option B)

GitHub will show you commands — use the "push an existing repository" block:

```bash
git remote add origin https://github.com/YOUR-USERNAME/cardiovascular-risk-analysis.git
git branch -M main
git push -u origin main
```

---

## 5. Turn on GitHub Pages (this makes the dashboard a live link)

1. On your repo page, go to **Settings → Pages**
2. Under **Build and deployment → Source**, choose **Deploy from a branch**
3. **Branch:** `main`, folder: **`/docs`**
4. Click **Save**
5. Wait ~1 minute, then refresh — GitHub shows your live URL:
   ```
   https://YOUR-USERNAME.github.io/cardiovascular-risk-analysis/
   ```

That link is now the interactive dashboard — dark mode, risk calculator, patient explorer,
all of it — live on the internet, shareable with anyone.

---

## 6. Verify the CI pipeline

The included `.github/workflows/ci.yml` automatically re-runs the entire pipeline
(data generation → cleaning → model training → notebook execution → Excel build) on every
push, so anyone who forks the repo can trust it actually works. Check **Actions** tab on
GitHub after your first push — you should see a green checkmark.

---

## 7. Polish the repo page (optional but makes a strong impression)

Add these badges to the very top of `README.md` (replace `YOUR-USERNAME`):

```markdown
![CI](https://github.com/YOUR-USERNAME/cardiovascular-risk-analysis/actions/workflows/ci.yml/badge.svg)
[![Live Dashboard](https://img.shields.io/badge/dashboard-live-B3392C)](https://YOUR-USERNAME.github.io/cardiovascular-risk-analysis/)
![License](https://img.shields.io/badge/license-MIT-blue)
```

Also on GitHub:
- Click the ⚙️ gear next to "About" on your repo homepage
- Add a short description: *"End-to-end cardiovascular risk analysis — SQL, Python, ML, and a live interactive dashboard"*
- Add the Pages URL as the **Website** link
- Add topics: `data-analysis`, `machine-learning`, `healthcare`, `dashboard`, `python`, `sql`

---

## 8. Updating the project later

Whenever you change something (new chart, tweaked model, etc.):

```bash
# if you touched the dashboard, keep docs/ and dashboard/ in sync
cp dashboard/dashboard.html docs/index.html

git add .
git commit -m "Describe what you changed"
git push
```

GitHub Pages auto-redeploys within about a minute of every push to `main`.

---

## Quick troubleshooting

| Problem | Fix |
|---|---|
| Pages shows 404 | Double check Settings → Pages source is `main` / `/docs`, and that `docs/index.html` exists |
| Dashboard loads but charts are blank | Check the browser console — Chart.js loads from a CDN, so it needs internet access |
| CI workflow fails | Check the Actions log — usually a missing package; confirm `requirements.txt` is current |
| Excel file won't open cleanly on GitHub preview | That's expected — GitHub previews `.xlsx` as a static table; download it to see live formulas |
