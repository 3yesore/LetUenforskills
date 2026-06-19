# Security Policy

## Supported Versions

LetUen is currently in developer preview. Security fixes target the `main` branch and the latest prerelease package.

## Reporting a Vulnerability

Please do not open a public issue for secrets, credential exposure, prompt-injection bypasses, or unsafe file-system behavior.

If GitHub private vulnerability reporting is enabled for this repository, use that channel. Otherwise, contact the repository owner directly and include:

- affected command, UI route, or generated artifact;
- reproduction steps;
- expected impact;
- whether real provider API keys or private repositories were involved.

## Handling Model and Key Safety

- Do not commit `.env`, local run outputs, API keys, or provider credentials.
- Prefer environment variables such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, and `DASHSCOPE_API_KEY`.
- The local bridge is intended for local development only and should not be exposed publicly without authentication and hardening.
