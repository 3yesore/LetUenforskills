# Graph And Data Surface Spec / 图谱与数据出口规范

## 1. Purpose

Graph and data exports are not decorative extras. They make the decomposition inspectable, reusable, and comparable across runs and models.

The web report explains the skill. The graph explains relationships. The data export enables research, benchmark, and downstream visualization.

## 2. Source Of Truth

Canonical source remains run artifacts and deterministic evidence. Data and graph files are compiled views.

Primary inputs:

- skill inventory
- source snapshots
- structure analysis
- workflow analysis
- reviewer output
- quality output
- pattern/reuse output
- model/provider metadata

Primary generated files:

- `skills.jsonl`
- `resource_roles.csv`
- `workflow_trace.jsonl`
- `evidence_audit.jsonl`
- `reuse_assets.jsonl`
- `graph-data.json`
- `graph.mmd`
- `data_manifest.json`

## 3. Graph Node Contract

Required node fields:

```json
{
  "id": "skill:algorithmic-art",
  "type": "skill",
  "label": "algorithmic-art",
  "summary": "...",
  "source_path": "...",
  "confidence": "medium",
  "metadata": {}
}
```

Recommended node types:

- `run`
- `repo`
- `skill`
- `file`
- `resource`
- `workflow_step`
- `evidence`
- `claim`
- `risk`
- `reuse`
- `model`

## 4. Graph Edge Contract

Required edge fields:

```json
{
  "id": "edge:skill:uses:resource",
  "source": "skill:algorithmic-art",
  "target": "resource:references/color.md",
  "type": "uses_resource",
  "confidence": "medium",
  "evidence_ids": [],
  "metadata": {}
}
```

Recommended edge types:

- `contains_skill`
- `contains_file`
- `uses_resource`
- `has_step`
- `next_step`
- `step_uses_resource`
- `supports_claim`
- `has_evidence_audit`
- `has_reuse_asset`
- `disagrees_with`
- `produced_by_model`

## 5. Graph UI Requirements

The graph page should be useful before it becomes complex.

Minimum UX:

- readable layout with no severe overlap
- node type legend
- edge type legend
- filter by node type
- filter by evidence status
- click node to show details
- links back to report sections and artifacts

Visual style:

- same dark glass language as Cinema/Repo/Report
- no noisy neon graph by default
- restrained accent colors by node type
- smooth hover/focus motion
- clear typography for labels and details

## 6. Data Page Requirements

The data page should expose what was exported without asking users to inspect folders manually.

Required panels:

- run metadata
- table/file manifest
- row counts
- direct file links
- schema notes
- benchmark readiness state

The page should first read `data_manifest.json`. If missing, it may fall back to static demo content, but the fallback must be labeled as demo/sample.

## 7. Research Use Cases

Data exports should support:

- comparing decomposition depth across models
- checking evidence coverage
- measuring workflow step extraction
- mining reusable patterns across repos
- building embeddings or retrieval indexes later
- importing into notebooks or BI tools

## 8. Obsidian Linkage

Graph/data exports should connect to Obsidian outputs.

Recommended mappings:

- skill node -> skill note
- workflow step node -> workflow note section
- reuse node -> pattern note
- evidence node -> source note or artifact path
- model node -> comparison note

## 9. Acceptance Checklist

Graph/data export is acceptable when:

- `data_manifest.json` lists every generated data file and row count
- graph nodes and edges have stable ids
- every graph edge has a valid source and target
- the graph page can load real exported data
- the data page links to actual files
- demo/fallback data is clearly labeled
- no API keys or secrets appear in exported data
