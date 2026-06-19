# UI Motion References

This note records animation and gradient references for the local UI direction. These are references for visual language and implementation patterns, not dependencies to copy blindly.

## Current Direction

- **Style:** minimal dark research interface with a distinctive neon evidence accent.
- **Visual focus:** structure anatomy, workflow line, quality gate, and vault output each get a different layout rhythm.
- **Motion ratio:** roughly 30% of the visual experience should move; the remaining 70% should stay calm and readable.
- **Motion purpose:** ambient depth, section reveal, hover emphasis, and workflow direction only.
- **Accessibility:** respect `prefers-reduced-motion` and avoid required information being animation-only.

## Animation References

| Reference | What To Borrow | Current Use |
| --- | --- | --- |
| [`LunarLogic/auroral`](https://github.com/LunarLogic/auroral) | Pure CSS animated aurora gradients, background containers, optional star-like depth | Inspired the current ambient orb layer and slow drift behavior. |
| [`firecmsco/neat`](https://github.com/firecmsco/neat) | Shader-like gradient editor, preset-driven gradient thinking, WebGL upgrade path | Good future option if the site needs a more premium hero background. |
| [`tsparticles/tsparticles`](https://github.com/tsparticles/tsparticles) | Rich animated backgrounds, particles, confetti, fireworks | Keep as optional; likely too noisy for the research-tool tone. |
| [`justin-chu/react-fast-marquee`](https://github.com/justin-chu/react-fast-marquee) | Smooth CSS marquee pattern with gradient masking | Useful later for provider/model strips, not used in current static base. |
| [`Gradients/awesome-gradient`](https://github.com/Gradients/awesome-gradient) | Curated list for gradient libraries and resources | Good discovery source when refining palette and background options. |

## Local Implementation Notes

The current `site/` base uses no external runtime dependency:

- `site/index.html` defines the information architecture and UI regions.
- `site/styles.css` implements dark shell, animated gradient orbs, section reveal states, hover motion, and responsive layout.
- `site/script.js` only handles IntersectionObserver-based reveal transitions.

## Next Design Review Questions

- Should the color system stay dark/neon, or move toward warm paper/minimal research notes?
- Should the hero feel more like a dashboard preview or more like an editorial manifesto?
- Should the workflow visualization become a real run timeline with statuses?
- Should Obsidian output be represented as files, graph, cards, or a split-pane preview?

## 2026-06-08 Typography And Workbench Pass

User feedback: animation direction is acceptable; typography needs more polish; continue toward a higher-completion local UI base.

Changes made:

- Replaced the previous generic heading feel with a display serif stack for major Chinese titles.
- Kept UI chrome, labels, navigation, buttons, and small controls in a cleaner sans stack.
- Added a static `Workbench` preview section as the bridge from landing page to future local WebUI.
- Workbench visual model: GitHub URL input, model route cards, agent stage list, and replayable artifact tree.
- Preserved the current motion direction: ambient gradient drift, scroll reveal, hover lift, active agent glow.

Current UI hypothesis:

- Large narrative titles can use a serif display style for calmer research/editorial tone.
- Operational UI panels should stay sans/mono for tool credibility.
- The local WebUI should not look like a generic dashboard first; it should look like a research instrument for skill anatomy.

Next refinement options:

- Replace static Workbench preview with real `runs/` artifact data.
- Add a second detail screen for one skill analysis result.
- Tune color away from neon if it feels too cyberpunk.
- Add a light/paper mode for Obsidian and research-document affinity.

## 2026-06-08 Bento Layout Pass

User preference: keep the previous animation/base style, do not continue typography changes, improve layout polish with open-source UI inspiration.

Current experiment:

- Use a Magic UI inspired approach without introducing React or package dependencies.
- Keep the existing dark ambient animation that the user liked.
- Add bento-style density to the `Anatomy` section.
- Add restrained border-beam motion to the hero and core card.
- Add terminal/file-tree style artifact preview to the run card.
- Add small pills, quote line, and skill map details to make cards feel designed rather than generic.

References to keep exploring:

- `magicuidesign/magicui` for bento grid, border beam, file tree, terminal text, animated grid pattern.
- `animata.design` for local section-level animation patterns.
- `shadcn/originui` for future dashboard/report browser component composition.

Design caution:

- Avoid copying the full AI SaaS look.
- Borrow interaction and layout primitives only.
- Keep the page closer to a research instrument than a marketing template.
