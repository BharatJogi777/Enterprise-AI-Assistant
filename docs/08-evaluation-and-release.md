# Evaluation and release gates

The illustrative dataset is `evals/sample_dataset.json`. Replace it with reviewed, representative questions and expected source names. Never commit confidential production content.

Run:

```bash
python -c "import asyncio; from enterprise_ai.evaluation.runner import evaluate_dataset; print(asyncio.run(evaluate_dataset('evals/sample_dataset.json')))"
```

The starter reports grounded-response rate and expected-source recall based on filename substring matching. It is not a semantic correctness or faithfulness score. Extend it with answer correctness, citation precision, faithfulness, refusal behavior, prompt-injection resistance, tool policy compliance, latency and cost. Use human-reviewed labels.

Release gates:
1. Unit and static checks pass.
2. Integration tests pass against disposable PostgreSQL/pgvector and deterministic model fakes.
3. Retrieval precision/recall meets agreed thresholds.
4. No unauthorized cross-tenant/document retrieval in security tests.
5. Prompt injection and tool-abuse suites pass.
6. Load tests meet latency/concurrency objectives.
7. Backup restore and data deletion are exercised.
8. Monitoring, alerting and incident runbooks are reviewed.

Never use a model's self-reported confidence as the sole quality metric.
