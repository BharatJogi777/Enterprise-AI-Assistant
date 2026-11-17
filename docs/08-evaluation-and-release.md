# Evaluation and release gates

## Offline dataset

The repository includes `evals/sample_dataset.json`. Replace the illustrative cases with approved, representative questions and expected source documents. Do not place confidential production content in the repository.

## Run evaluation

```bash
python -c "import asyncio; from enterprise_ai.evaluation.runner import evaluate_dataset; print(asyncio.run(evaluate_dataset('evals/sample_dataset.json')))"
```

The current runner reports:
- Grounded response rate (whether retrieved evidence existed).
- Expected-source recall based on filename substring matching.

These are basic retrieval checks, not a semantic answer-quality score. Extend the harness with answer correctness, citation precision, faithfulness, refusal behavior, prompt-injection resistance, latency and cost. Use human-reviewed gold labels.

## Release gates

1. Unit tests and static checks pass.
2. Integration tests pass against disposable PostgreSQL/pgvector and a deterministic model fake.
3. Retrieval quality meets agreed recall/precision thresholds.
4. No cross-tenant or unauthorized document retrieval in security tests.
5. Prompt injection and tool-abuse test suites pass.
6. Load tests meet latency/concurrency objectives.
7. Backup restore and data deletion have been exercised.
8. Observability alerts and incident runbooks are reviewed.

Never use a model's self-reported confidence as the sole release metric.
