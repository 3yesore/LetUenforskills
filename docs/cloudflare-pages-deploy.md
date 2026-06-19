# Cloudflare Pages Deploy

This project can publish the static public UI and generated reports with Cloudflare Pages free hosting.

## Deploy The Public Site

The current no-build static site lives in `site/`.

```powershell
npx wrangler pages deploy site --project-name agent-skill-anatomy
```

Cloudflare will provide a free `*.pages.dev` domain. A custom domain can be attached later from the Pages dashboard.

## Deploy A Generated Report

Generate a report first:

```powershell
$env:PYTHONPATH='src'
python -m asa export-report --run runs/<run-id> --output site/report
```

Then either:

- deploy the whole `site/` directory so `/report/` is included, or
- deploy only `site/report` as a separate Pages project for a specific run report.

```powershell
npx wrangler pages deploy site/report --project-name agent-skill-anatomy-report
```

## Notes

- `site/report/` is generated output and is ignored by git by default.
- Canonical JSON artifacts are copied into `site/report/artifacts/` during export.
- Do not publish private runs or proprietary source snapshots unless they are safe to share.
- For open-source releases, prefer publishing curated sample reports rather than raw private research runs.
