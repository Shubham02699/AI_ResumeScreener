"""
hybrid_scorer.py
Combines ATS and AI scores into a single weighted final score.
Default weights: 40% ATS, 60% AI (configurable by the user).
"""

from typing import List, Dict


def combine_scores(
    ats_results: List[Dict],
    ai_results: List[Dict],
    ats_weight: float = 0.4,
    ai_weight: float = 0.6,
) -> List[Dict]:
    """
    Merge ATS and AI results by candidate name and compute a final weighted score.

    Args:
        ats_results: Output from ats_scorer (list of dicts with 'name', 'ats_score').
        ai_results:  Output from ai_scorer  (list of dicts with 'name', 'ai_score', 'ai_reason').
        ats_weight:  Weight applied to ATS score (default 0.4).
        ai_weight:   Weight applied to AI  score (default 0.6).

    Returns:
        List of merged dicts sorted by final_score descending.
    """
    # Index AI results by candidate name for fast lookup
    ai_map = {r["name"]: r for r in ai_results}

    merged = []
    for ats in ats_results:
        name = ats["name"]
        ai = ai_map.get(name, {"ai_score": 0, "ai_reason": "AI scoring not available."})

        ats_score = ats.get("ats_score", 0)
        ai_score = ai.get("ai_score", 0)
        final_score = round((ats_score * ats_weight) + (ai_score * ai_weight), 2)

        merged.append(
            {
                "name": name,
                "text": ats.get("text", ""),
                "ats_score": ats_score,
                "ai_score": ai_score,
                "ai_reason": ai.get("ai_reason", ""),
                "final_score": final_score,
            }
        )

    merged.sort(key=lambda x: x["final_score"], reverse=True)
    return merged


def add_final_score_ats_only(results: List[Dict]) -> List[Dict]:
    """
    For ATS-only mode, copy ats_score into final_score for consistent display.
    """
    for r in results:
        r["final_score"] = r["ats_score"]
        r.setdefault("ai_score", None)
        r.setdefault("ai_reason", "")
    return results


def add_final_score_ai_only(results: List[Dict]) -> List[Dict]:
    """
    For AI-only mode, copy ai_score into final_score for consistent display.
    """
    for r in results:
        r["final_score"] = r["ai_score"]
        r.setdefault("ats_score", None)
    return results
