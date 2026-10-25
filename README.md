# Research Funding Radar · v0.1

A Swedish-language PWA for discovering and ranking research-funding opportunities in industrial electrification, thermal plasma, cement and high-temperature processes.

## Quick start

Requires Node.js 22+ and Python 3.12+.

```bash
npm install
npm run dev
```

Open the local URL shown by Vite. The initial dataset is intentionally empty. Populate it with:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/collect.py
```

The collector performs **best-effort discovery of links from public listing pages**. It does not verify deadlines, eligibility or whether a link is truly an open call. All discovered items are marked `unverified`. A high relevance score only reflects keyword matches. Pages that render links exclusively through JavaScript may return no results. Source endpoints can change, and automated requests may be blocked. No claim of exhaustive coverage is made.

## Publish on GitHub Pages

1. Create a new **public** repository named `research-funding-radar` on GitHub.
2. Upload all files **including `.github/workflows/`** to the root of the repo, on branch `main`.
3. In **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
4. Run **Actions → Collect funding opportunities → Run workflow** once.
5. Wait for the `Deploy PWA to GitHub Pages` workflow. The site should appear at `https://YOUR-USERNAME.github.io/research-funding-radar/`.
6. If Actions cannot push changes, check **Settings → Actions → General → Workflow permissions** and permit read/write as needed.

The collector runs weekdays at 06:23 UTC (GitHub scheduled runs can be delayed). GitHub Pages requires an eligible plan for private repositories; this setup assumes a public repo. If you rename the repo, Vite reads the repository name automatically in CI.

## How it works

- `data/sources.json`: configurable listing pages. Disabled EU Funding & Tenders placeholder is intentionally not scraped; a dedicated official API connector is needed.
- `scripts/collect.py`: downloads listing pages, extracts candidate links, de-duplicates by URL and calculates a deterministic 0–100 relevance score.
- `public/calls.json`: static dataset consumed by the PWA.
- `src/`: React UI, search, sorting, source links, and favorites in localStorage.
- `.github/workflows/collect.yml`: scheduled data refresh and commit.
- `.github/workflows/deploy.yml`: build and deploy to GitHub Pages.

## Data quality and next steps

**v0.1 is a working technical foundation, not a validated funding database.** Some links may be informational rather than open calls, and no reliable deadlines are extracted yet. Before relying on it for applications, add source-specific parsers or APIs, verified opening/closing dates, closed-call detection, application eligibility and a human-review flag. Also add coverage for EU Funding & Tenders using its official data interface, and test each Swedish source against its current page structure.

AI analysis can be added as an **optional GitHub Actions job** after source extraction and verification. Put any API key in GitHub Actions Secrets; never expose it in the frontend or commit it. Keep deterministic scoring as fallback and label AI-inferred details separately from source-confirmed facts.

Favorites live in the current browser only. GitHub Pages does not provide a user database or cross-device sync.

## Development

```bash
npm run build
python -m compileall -q scripts
```

## License

MIT (see LICENSE).
