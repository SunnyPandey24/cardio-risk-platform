# Cloud Deployment Guide

This covers getting the **backend API** live on the internet. (For the static dashboard,
see `DEPLOYMENT.md` — that one's already covered by GitHub Pages.)

Three options, easiest first.

---

## Option 1: Render (easiest, free tier, recommended to start)

Render can read the included `render.yaml` and set up both the API and a Postgres database
automatically.

1. Push this repo to GitHub (see `DEPLOYMENT.md` if you haven't yet)
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect your GitHub repo — Render detects `render.yaml` automatically
4. Click **Apply** — Render builds the Docker image, provisions Postgres, and wires the
   `DATABASE_URL` and a random `SECRET_KEY` for you automatically
5. Wait for the build (first one takes a few minutes) — you'll get a URL like:
   ```
   https://cardio-risk-api.onrender.com
   ```
6. Test it:
   ```bash
   curl https://cardio-risk-api.onrender.com/health
   ```
7. In your dashboard's Risk Calculator tab, paste that URL into the "API base URL" field
   and toggle "Use live backend API" — now your live dashboard is calling your live API.

**Free tier note:** Render's free web services sleep after 15 minutes of inactivity and
take ~30 seconds to wake up on the next request. Fine for a demo; upgrade to a paid plan
($7/mo) for an always-on API.

---

## Option 2: Railway (also easy, usage-based free credits)

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select this repo, set the root/build to use `backend/Dockerfile`
3. Add a **Postgres** plugin from Railway's service catalog — it auto-injects
   `DATABASE_URL` into your API service's environment
4. Add a `SECRET_KEY` environment variable manually (any random string)
5. Railway gives you a public URL once deployed — same as Render, plug that into the
   dashboard's API URL field

---

## Option 3: AWS (production-grade, the "real" resume line)

This is more setup but is what a data engineering role actually expects. Two common paths:

### 3a. AWS App Runner (simplest AWS option)
1. Push your image to a registry (the included `docker-build.yml` already pushes to
   `ghcr.io/YOUR-USERNAME/cardiovascular-risk-analysis/cardio-api` on every push to `main`)
2. In the AWS Console → **App Runner** → **Create service** → source: **Container registry**
   → point it at your GHCR image (you'll need to make the GHCR package public, or set up a
   registry credential)
3. Set environment variables: `DATABASE_URL`, `SECRET_KEY`
4. For the database, provision **Amazon RDS for PostgreSQL** (free tier eligible) and use
   its connection string as `DATABASE_URL`

### 3b. ECS Fargate + RDS (more "real" data engineering setup)
1. Create an **ECR** repository, push the image there instead of GHCR
2. Create an **RDS Postgres** instance
3. Create an **ECS Fargate** service using the ECR image, with `DATABASE_URL` and
   `SECRET_KEY` as task-definition environment variables
4. Put an **Application Load Balancer** in front of the service for a stable public URL
5. (Optional, the resume-impressive version) Define all of the above in **Terraform**
   instead of clicking through the console — this is the single biggest signal of
   "data/platform engineer" versus "data analyst" on a resume

This repo intentionally doesn't include Terraform files yet — writing your own
infrastructure-as-code for this specific deployment is one of the best next skills to
practice, and doing it yourself teaches more than a pre-written file would.

---

## After deploying: point everything at the live API

1. Update the dashboard: open `docs/index.html` (or `dashboard/dashboard.html`), find the
   "API base URL" field in the Risk Calculator tab, and either type your live URL each
   time, or hardcode it as the default:
   ```html
   <input type="text" id="apiUrlInput" value="https://your-live-api-url.com" ...>
   ```
2. Update `CORS_ORIGINS` on your deployed API to your actual dashboard's GitHub Pages URL
   instead of `*`, once you've confirmed everything works — this is the difference between
   a demo and a production-minded setup.
3. Re-run `docker-build.yml`'s optional Render deploy hook by setting the
   `RENDER_DEPLOY_HOOK` repository variable (Settings → Secrets and variables → Actions →
   Variables) so every push to `main` auto-redeploys.
