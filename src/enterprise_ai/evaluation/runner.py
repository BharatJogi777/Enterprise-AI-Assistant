import json
from pathlib import Path
from enterprise_ai.services.rag import answer_question

async def evaluate_dataset(dataset_path: str) -> dict:
    rows = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    outcomes = []
    for case in rows:
        result = await answer_question(case["question"])
        expected = [x.lower() for x in case.get("expected_sources", [])]
        actual = [x["filename"].lower() for x in result.get("citations", [])]
        source_recall = (sum(any(e in a for a in actual) for e in expected) / len(expected)
                         if expected else None)
        outcomes.append({"id":case.get("id"), "grounded":result.get("grounded",False),
                         "source_recall":source_recall, "answer":result.get("answer","")})
    scored = [x["source_recall"] for x in outcomes if x["source_recall"] is not None]
    return {"cases":len(outcomes), "grounded_rate":sum(x["grounded"] for x in outcomes)/max(1,len(outcomes)),
            "mean_source_recall":sum(scored)/len(scored) if scored else None, "results":outcomes}
