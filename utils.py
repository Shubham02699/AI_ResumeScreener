"""
utils.py
Helper utilities: CSV/Excel export, result formatting, badge generation.
"""

import pandas as pd
import io
from typing import List, Dict, Optional


def results_to_dataframe(results: List[Dict], mode: str) -> pd.DataFrame:
    """
    Convert the results list into a clean pandas DataFrame for display/export.

    Args:
        results: List of scored resume dicts.
        mode: One of 'ATS Only', 'AI Only', 'Hybrid'.

    Returns:
        pd.DataFrame ready for display or export.
    """
    rows = []
    for rank, r in enumerate(results, start=1):
        row = {
            "Rank": rank,
            "Candidate": r["name"],
            "Final Score": r.get("final_score", 0),
        }

        if mode in ("ATS Only", "Hybrid"):
            row["ATS Score"] = r.get("ats_score", "—")

        if mode in ("AI Only", "Hybrid"):
            row["AI Score"] = r.get("ai_score", "—")
            row["AI Reasoning"] = r.get("ai_reason", "")

        rows.append(row)

    return pd.DataFrame(rows)


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Return a CSV byte string from a DataFrame."""
    return df.to_csv(index=False).encode("utf-8")


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Return an Excel byte string from a DataFrame."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    return buffer.getvalue()


def get_score_color(score: float) -> str:
    """Return a hex color based on score value (for UI use)."""
    if score >= 75:
        return "#28a745"   # green
    elif score >= 50:
        return "#ffc107"   # amber
    else:
        return "#dc3545"   # red


def validate_job_description(jd: str) -> Optional[str]:
    """
    Validate the job description input.
    Returns an error message string, or None if valid.
    """
    if not jd or not jd.strip():
        return "Job description cannot be empty."
    if len(jd.strip()) < 50:
        return "Job description is too short (minimum 50 characters). Please provide more detail."
    return None


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Truncate long text with an ellipsis for display."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."
