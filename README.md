# tradesbysci social alert bot

Checks Instagram, X (Twitter), and YouTube for new posts from **tradesbysci**
every 5 minutes and sends you a push notification via ntfy.sh the moment
something new goes up.

## Setup (one time)

1. **Create a new repo on GitHub** (e.g. `social-alerts`) under your account `bread138`.
   - Can be private or public, doesn't matter.

2. **Upload these files** to the repo, keeping the folder structure exactly as-is:
   ```
   .github/workflows/check-posts.yml
   check.py
   requirements.txt
   state.json
   ```
   Easiest way: on the repo page, click "Add file" → "Upload files", drag all of
   them in (make sure the `.github/workflows` folder path is preserved).

3. **Add your ntfy topic as a secret:**
   - In the repo, go to **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `NTFY_TOPIC`
   - Value: `braden-alerts-tradesbysci-all`
   - Save.

4. **Enable Actions** (usually on by default for new repos):
   - Go to the **Actions** tab → if prompted, click "I understand my workflows, go ahead and enable them"

5. **Do a manual test run:**
   - Actions tab → "Check for new posts" workflow → **Run workflow** button → Run workflow
   - Wait ~30 seconds, then check the run log. You should see lines like
     `[YouTube] ...` and no fatal errors. First run won't send an alert
     (it just records the current latest post as the baseline) — that's expected.

6. **Confirm ntfy is receiving:**
   - Make sure you're subscribed to topic `braden-alerts-tradesbysci-all` in the
     ntfy app or at https://ntfy.sh/braden-alerts-tradesbysci-all in a browser.

After that, it runs automatically every 5 minutes — no further action needed.

## Known limitations (read this)

- **YouTube** uses YouTube's official public RSS feed — this is stable and
  should basically never break.
- **Instagram and X/Twitter checks scrape unofficial endpoints.** Neither
  platform offers a free public API for "did this account just post"
  anymore. This means:
  - They can break if Instagram/X change their page structure — if that
    happens, the log will show `[ERROR]` or "could not locate post data,"
    and I can patch the script.
  - If Instagram/X detect repeated automated requests from GitHub's IP
    ranges, they may serve a login wall or CAPTCHA instead of the real page,
    which would also show up as an error in the logs rather than a silent
    failure.
- If IG/X scraping becomes unreliable, the more robust (but paid) fix is a
  third-party scraping API (e.g. a Rapid API Instagram/Twitter scraper,
  ~$10-20/mo) that handles the anti-bot side for you — happy to wire that in
  if the free version starts failing often.

## Checking logs / troubleshooting

Actions tab → click into any run → expand "Run checker" step to see exactly
what each platform check found or errored on.
