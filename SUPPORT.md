# Support

LetUen is a developer-preview research tool. For now:

- Use GitHub Issues for reproducible bugs and scoped feature requests.
- Use GitHub Discussions, if enabled, for design questions, model comparisons, and workflow ideas.
- Include the provider route, config file, source repository, and whether the run used `mock` or real model calls.

For local debugging, start with:

```powershell
$env:PYTHONPATH='src'
python -m asa plan-run --config anatomy.config.example.yaml --limit-skills 1
python -m asa run --config anatomy.config.example.yaml --limit-skills 1
python -m asa quality-run --run runs\<run-id> --output runs\<run-id>\quality_report.json
```
