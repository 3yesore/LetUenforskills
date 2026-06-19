# Landing Page Spec

This spec defines the first public website for Agent Skill Anatomy. The first version should be a dependency-free static site that can deploy to Cloudflare Pages.

## Target URL

Use a Cloudflare Pages free subdomain first:

```text
https://agent-skill-anatomy.pages.dev
```

Fallback project names if unavailable:

- `skill-anatomy`
- `agent-skill-lab`
- `skill-workflow-lab`

## Primary Message

```text
Deconstruct agent skills into evidence-grounded reusable workflow knowledge.
```

Chinese version:

```text
把 Agent Skills 拆解成有证据、可复用、可学习的工作流知识资产。
```

## Audience

- Agent skill authors
- AI coding tool users
- LLM workflow researchers
- open-source contributors
- teams building internal skill libraries

## Page Sections

### 1. Hero

Content:

- Name: `Agent Skill Anatomy`
- Tagline: evidence-grounded skill/workflow analysis toolkit.
- Primary CTA: `View on GitHub`
- Secondary CTA: `Explore Sample Vault`
- Tertiary CTA: `Read the Roadmap`

Visual:

- Small pipeline diagram.
- Minimal code block showing `asa run`.

### 2. Problem

Message:

Agent skills are becoming reusable infrastructure, but most repositories are hard to compare, audit, and learn from.

Bullets:

- Skills hide workflow logic in natural language.
- Evidence and confidence are rarely explicit.
- Different models vary widely in analysis quality.
- Knowledge outputs are hard to reuse across teams.

### 3. Solution

Show the analysis pipeline:

```text
Collector -> Structure Analyst -> Workflow Analyst -> Pattern Miner -> Reviewer -> Obsidian Vault
```

Explain:

- deterministic source collection
- schema-first artifacts
- evidence-grounded analysis
- quality checks and review gates
- reusable knowledge outputs

### 4. Quality System

Present the four quality layers:

1. Schema validation
2. Programmatic quality rules
3. LLM reviewer
4. Human calibration

Include example checks:

- high confidence without evidence
- quote not found in source file
- inferred step marked high confidence
- required tool without evidence

### 5. Outputs

Cards:

- Obsidian vault
- workflow diagrams
- pattern library
- reusable templates
- review summaries
- benchmark reports

Each card should link to the relevant docs or sample output.

### 6. Multi-Model Research

Explain provider roadmap:

- OpenAI
- Anthropic
- Gemini
- DeepSeek
- Qwen / DashScope
- Zhipu GLM
- Moonshot Kimi
- SiliconFlow
- OpenAI-compatible endpoints

Message:

The project is designed to compare models by role, not assume one model fits every task.

### 7. CLI Demo

Use concise commands:

```powershell
python -m asa plan-run --config anatomy.config.example.yaml --limit-skills 1
python -m asa run --config anatomy.config.example.yaml --limit-skills 1
python -m asa validate --run runs/<run-id>
python -m asa quality-run --run runs/<run-id>
python -m asa review-run --run runs/<run-id>
```

### 8. Roadmap

Show six phases:

1. Tooling foundation
2. Real-run calibration
3. Multi-provider runtime
4. Benchmark lab
5. Knowledge compiler
6. Open-source release

### 9. Footer

Links:

- GitHub
- Roadmap
- Architecture
- Provider Strategy
- Benchmark Spec
- Sample Vault

## Visual Style

- Professional research-tool look.
- Dark-on-light by default, with subtle dark section blocks.
- Use diagrams and cards, not heavy marketing copy.
- Bilingual-friendly typography.
- Avoid fake metrics before real benchmark data exists.

## First Implementation Scope

Files:

```text
site/
  index.html
  styles.css
```

No build step. No JavaScript required for v1.

## Future Enhancements

- Add generated sample report pages.
- Add screenshots from Obsidian vault.
- Add benchmark charts after benchmark lab exists.
- Add provider comparison cards after real evaluations.
- Add Cloudflare Web Analytics if desired.

