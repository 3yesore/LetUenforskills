# Provider Strategy

Agent Skill Anatomy should stay provider-neutral while making high-quality structured analysis easy to run on the models users already have access to. Providers are thin adapters around a shared contract: accept role prompts, evidence payloads, JSON Schema, model options, and return validated JSON artifacts.

## Goals

- Keep the harness independent from any single model API or vendor SDK.
- Prefer structured-output features when a provider supports them natively.
- Fall back to strict prompt contracts and local schema validation when native JSON Schema is unavailable.
- Make cost, latency, context length, and multimodal support visible before a run starts.
- Let users swap providers by editing config, not agent code.

## Provider Families

### OpenAI

OpenAI is the reference provider for schema-first runs.

- Use Responses API structured outputs where available.
- Treat JSON Schema validation failures as provider-call failures, not soft warnings.
- Support reasoning-capable models for reviewer and pattern-mining roles, and lower-cost models for inventory expansion or summarization.
- Record model ID, response ID, token usage, schema name, and retry count in run metadata.

### OpenAI-Compatible Generic

The generic provider targets gateways and self-hosted endpoints that expose OpenAI-style chat or responses APIs.

- Configurable `base_url`, `api_key_env`, model name, timeout, and feature flags.
- Feature flags declare support for JSON Schema, JSON mode, tool calls, streaming, and usage accounting.
- The harness must not assume true OpenAI semantics just because the route shape is compatible.
- This provider is the preferred adapter for OpenRouter-like gateways, local vLLM deployments, and private proxy services.

### Anthropic

Anthropic should be supported as a first-class non-OpenAI provider.

- Use Messages API with strict JSON-only instructions and local validation.
- Prefer tool-use or structured-output mechanisms when stable for the target model.
- Favor larger-context models for source-heavy workflow analysis.
- Track prompt-cache behavior separately from normal input tokens when usage data is available.

### Gemini

Gemini support should optimize for long-context and multimodal use cases.

- Use Google Gemini APIs with structured response configuration when available.
- Mark support for large context windows and image/PDF inputs in the capability registry.
- Use Gemini as a candidate provider for visual asset extraction and future website/report generation checks.
- Keep safety-block and finish-reason metadata for reviewer diagnostics.

### DeepSeek

DeepSeek support should focus on cost-effective reasoning and OpenAI-compatible deployment paths.

- Prefer the OpenAI-compatible adapter when API semantics match.
- Maintain native provider configuration if DeepSeek-specific request or usage fields become important.
- Use capability registry entries to distinguish reasoning models from general chat models.
- Benchmark on evidence faithfulness because low cost can invite larger batch runs.

### Qwen / DashScope

Qwen models through DashScope are important for Chinese and bilingual output quality.

- Support native DashScope APIs or OpenAI-compatible endpoints depending on deployment.
- Track Chinese, English, and bilingual quality separately in benchmark reports.
- Mark long-context, tool-use, and multimodal capabilities per model rather than per provider.
- Treat DashScope workspace/project identifiers as provider config, not hard-coded runtime values.

### Zhipu

Zhipu support should cover GLM-family models for Chinese-first and bilingual analysis.

- Provide either native adapter or OpenAI-compatible configuration based on current API support.
- Benchmark terminology consistency and evidence grounding in Chinese output.
- Record provider-specific request IDs and moderation/safety outcomes when returned.
- Keep model capability entries explicit because GLM variants can differ substantially.

### Moonshot

Moonshot support should prioritize long-context repository reading and Chinese/English synthesis.

- Use Moonshot's OpenAI-compatible API shape when suitable.
- Mark context-window size and file-ingestion affordances in registry metadata.
- Benchmark workflow reconstruction on large `SKILL.md` plus referenced-file fixtures.
- Monitor latency and timeout behavior for large evidence payloads.

### SiliconFlow

SiliconFlow should be treated as a multi-model gateway rather than a single model family.

- Use the generic OpenAI-compatible provider with SiliconFlow-specific defaults.
- Registry entries should identify the upstream model family and served model ID.
- Benchmark gateway-served models independently from native-provider variants.
- Surface gateway limitations such as unavailable usage fields, context truncation, or unsupported JSON Schema.

## Model Capability Registry

The registry is a versioned YAML file that describes models as runnable targets. It is advisory metadata for planning and reporting; provider adapters remain the source of execution behavior.

Registry responsibilities:

- Declare provider, model ID, endpoint style, and default role suitability.
- Record context window, max output, structured-output mode, multimodal inputs, tool support, streaming, and usage accounting.
- Classify strengths such as `reasoning`, `long_context`, `bilingual`, `low_cost`, `vision`, or `strict_json`.
- Define recommended roles: `structure_analyst`, `workflow_analyst`, `pattern_miner`, `renderer`, `reviewer`, `translator`.
- Include operational defaults: temperature, timeout, retry count, rate-limit notes, and cost tier.

The planner should use the registry to warn before a run when a selected model lacks required capabilities, when estimated source payloads exceed the context window, or when a role is assigned to a model with weak benchmark history.

## Configuration Shape

Provider config should separate secrets, endpoints, model selection, and role routing.

```yaml
provider:
  name: openai
  api_key_env: OPENAI_API_KEY
  default_model: openai:gpt-5.2
models:
  registry: models/registry.yaml
roles:
  workflow_analyst:
    model: openai:gpt-5.2
  renderer:
    model: qwen:qwen-plus
```

Secrets must be referenced by environment variable name only. Example files must never contain real keys.

## Execution Policy

- Run planning resolves role-to-model assignments before the first model call.
- Each call records provider name, model key, served model ID, request metadata, and validation outcome.
- Schema validation is local and mandatory for every provider.
- Providers may retry transport failures, but schema repair belongs to the shared `generate_validated_json` flow.
- Provider-specific failures should be normalized into stable error categories: auth, rate limit, timeout, context limit, schema rejection, safety block, malformed output, and unknown.

## Long-Term Roadmap

1. Stabilize OpenAI and generic OpenAI-compatible adapters.
2. Add registry-driven role routing and capability warnings.
3. Implement Anthropic, Gemini, DashScope, and selected Chinese providers behind the same contract.
4. Add benchmark reports that compare providers by role, fixture type, language, and cost tier.
5. Support mixed-provider runs where expensive models review or mine patterns while cheaper models handle deterministic drafting.
