from __future__ import annotations


from collections import Counter
from typing import Any, Dict, Iterable, List




def aggregate_and_summarize(results: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    results_list = list(results)


    valid = [r for r in results_list if r.get("valid")]
    invalid = [r for r in results_list if not r.get("valid")]


    registries = [r.get("registry") for r in results_list if r.get("registry")]
    counts = dict(Counter(registries))


    total_issues = sum(len(r.get("errors", [])) for r in results_list)


    report: Dict[str, Any] = {
        "summary": {
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "total_issues": total_issues,
        "registry_counts": counts,
        },
        "files": results_list,
        }
    return report