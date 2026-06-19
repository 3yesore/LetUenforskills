# UI Reference Projects

This document records reusable UI references for the public site, static report browser, and future local dashboard. The goal is not to copy a template, but to keep a high-quality visual vocabulary available when the project moves from CLI-first research tooling to user-facing interfaces.

## Selection Criteria

- **Open-source friendly:** projects should be easy to inspect, fork, or use as design references.
- **Static-first compatible:** early UI should deploy cleanly to Cloudflare Pages without a hosted backend.
- **Research-tool tone:** visual language should feel rigorous, calm, technical, and trustworthy.
- **Bilingual-ready:** typography and layout should work for Chinese and English labels.
- **Composable path:** the landing page, docs site, report browser, and dashboard should share design tokens.

## Landing Page References

| Project | Use As Reference For | Notes |
| --- | --- | --- |
| `mearashadowfax/ScrewFast` | Astro landing/docs/blog structure | Good reference for a polished open-source product site with docs-friendly navigation. |
| `Landstro` | Modern Astro marketing sections | Useful for hero rhythm, section spacing, and deployment-light static pages. |
| `leomirandaa/shadcn-landing-page` | shadcn/Tailwind component style | Good reference for cards, CTAs, and modern developer-tool aesthetics. |
| `mhyfritz/astro-landing-page` | Minimal static landing patterns | Useful if the public site later moves from raw HTML to Astro. |
| `netlify-templates/astro-landing-page` | Deployable static baseline | Useful for documentation around static hosting and simple project structure. |

## Docs And Handbook References

| Project | Use As Reference For | Notes |
| --- | --- | --- |
| `fumadocs` | Technical docs system | Strong fit for a future handbook with structured navigation, search, and MDX. |
| `vitepress` | Lightweight docs publishing | Good backup option when documentation should stay close to Markdown. |
| `Hello Astro` | Astro content site patterns | Useful for combining landing, docs, and generated pages in one static site. |

## Dashboard References

| Project | Use As Reference For | Notes |
| --- | --- | --- |
| `silicondeck/shadcn-dashboard-landing-template` | Dashboard + landing composition | Useful once report browsing and public marketing start sharing visual language. |
| `Qualiora/shadboard` | shadcn dashboard shell | Useful for future run comparison and quality issue triage screens. |
| `satnaing/shadcn-admin` | Admin navigation and tables | Strong reference for filters, tables, sidebars, and settings pages. |
| `NaveenDA/shacn-nextjs-dashboard` | Next.js dashboard conventions | Useful if the local dashboard later chooses Next.js instead of Vite. |

## Recommended UI Stack Path

### Current Public Site

- Use `site/index.html` and `site/styles.css`.
- Keep the first deploy no-build and Cloudflare Pages friendly.
- Treat the page as a high-fidelity product/research showcase, not an MVP placeholder.

### Future Docs Site

- Prefer Astro or Fumadocs when documentation navigation, search, and generated pages become important.
- Preserve the same design tokens: ink, muted text, violet accent, amber evidence accent, card radius, and grid backgrounds.

### Future Dashboard

- Prefer Vite + React + shadcn/ui for the local research dashboard.
- Keep dashboard data local and artifact-first: `runs/`, `benchmark/results/`, `models/registry.yaml`, and generated report JSON remain the source of truth.

## Design Direction For Agent Skill Anatomy

The project should feel like a research lab for agent workflows:

- precise diagrams instead of vague marketing illustrations
- visible evidence and quality gates instead of inflated metrics
- calm light UI with dark technical panels for CLI and artifact examples
- Chinese/English copy support from the beginning
- output-focused cards for Obsidian, workflow diagrams, reusable patterns, templates, reviews, and benchmark reports
