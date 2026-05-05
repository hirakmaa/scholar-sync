# Live Google Scholar sync for Dr. Hirak Mazumdar's dashboard

This tiny repo turns your `publications.html` dashboard into a **truly live** one.
It scrapes your Google Scholar profile every 6 hours via a free GitHub Action,
saves the result to `scholar-stats.json`, and your dashboard fetches that file
from GitHub's CDN — completely bypassing the CORS / CAPTCHA problems you were
hitting before.

---

## Why the old setup didn't work

The dashboard tried to fetch `scholar.google.com` directly from the visitor's
browser, which fails because:

1. Google Scholar has no public API.
2. Browsers block direct cross-origin fetches (CORS).
3. The free CORS proxies (allorigins, corsproxy.io, thingproxy) get rate-limited
   and Scholar shows them CAPTCHA pages — your parser then sees garbage and
   silently falls back to hardcoded numbers.
4. Google Sites is static — there's no backend to host a `/api/scholar-stats`
   endpoint.

The fix: do the scraping from **GitHub's servers** (which Scholar treats
politely), then serve the result as a plain JSON file.

---

## One-time setup (≈ 10 minutes)

### Step 1 — Create a GitHub repo
1. Sign in at https://github.com (free account is fine).
2. Click **+ → New repository**.
3. Name it something like `scholar-sync`. Make it **Public** (so your dashboard
   can read the JSON without auth).
4. Tick **"Add a README file"** so the repo is initialised, then click
   **Create repository**.

### Step 2 — Upload these three files
Upload these into the repo (use the **Add file → Upload files** button on GitHub):

| File                                       | Where it goes                              |
| ------------------------------------------ | ------------------------------------------ |
| `update_scholar.py`                        | Repo root                                  |
| `scholar-stats.json`                       | Repo root (initial seed values)            |
| `update-scholar.yml`                       | Inside `.github/workflows/` folder         |

To create the `.github/workflows/` folder on the GitHub website:
when uploading, type `.github/workflows/update-scholar.yml` in the filename
field — GitHub will create the folders automatically.

### Step 3 — Enable Actions write permission
1. In your repo, go to **Settings → Actions → General**.
2. Scroll to **Workflow permissions**.
3. Choose **Read and write permissions** → **Save**.

This lets the bot commit `scholar-stats.json` back to the repo after each run.

### Step 4 — Run it once manually to confirm it works
1. Go to the **Actions** tab in your repo.
2. Click **"Update Google Scholar stats"** in the left sidebar.
3. Click **Run workflow → Run workflow** (green button).
4. After ~30–60 seconds, refresh the page. You should see a green check.
5. Click into the run; the log should show your real citation numbers.
6. Go back to the repo's main page — `scholar-stats.json` should now contain
   live numbers instead of the seed values.

From now on the action runs automatically every 6 hours — no further work needed.

### Step 5 — Wire your dashboard to the JSON
1. Open `publications.html`.
2. Find this line near the top of the `<script>` block:

   ```js
   apiUrl: 'https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/scholar-stats.json',
   ```

3. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username and
   `YOUR_REPO_NAME` with whatever you named the repo (e.g. `scholar-sync`).
4. Save and re-embed `publications.html` in your Google Site.

You're done. Whenever your real Scholar numbers go up, the action picks it up
within 6 hours and your dashboard reflects it — no manual editing.

---

## How to verify it's actually live (not cached)

Open the embedded dashboard and press **F12 → Console**. You should see:

```
[Dashboard] Scholar stats refreshed from GitHub  {citations: 802, hIndex: 17, ...}
```

The "LIVE" badge in the top-right of the dashboard should stay **LIVE**, and
the `Updated:` timestamp in the footer should show **(Scholar live)**, not
**(cached fallback)**.

---

## Troubleshooting

**The action runs but `scholar-stats.json` doesn't update.**
Scholar occasionally throttles `scholarly`. Wait an hour and click
**Re-run all jobs** in the Actions tab. If it fails repeatedly, see the
"Optional: SerpAPI fallback" section below.

**Dashboard still shows old numbers after the action succeeded.**
Browsers and `raw.githubusercontent.com` cache for ~5 minutes. The
`?t=Date.now()` cache-buster I added handles this — but if you're really
impatient, hard-refresh with Ctrl+Shift+R.

**I get a 404 fetching the JSON.**
Double-check the username/repo name in the `apiUrl` and that the repo is
**Public** (Settings → General → Danger Zone → Change visibility).

---

## Optional: SerpAPI fallback (more reliable, free 100 calls/month)

If `scholarly` keeps getting blocked, swap it for SerpAPI's Google Scholar
Author API. With a 6-hour schedule you'd use 4 calls/day = 120/month, just
over the free tier — make it 8-hourly (`0 */8 * * *`) for 90/month.

1. Sign up at https://serpapi.com → copy your API key.
2. In your GitHub repo, go to **Settings → Secrets and variables → Actions →
   New repository secret**. Name: `SERPAPI_KEY`, value: your key.
3. Replace `update_scholar.py` with a version that calls SerpAPI (ask Claude
   for the swap when you're ready).

For most people, the default `scholarly`-based version is fine.
