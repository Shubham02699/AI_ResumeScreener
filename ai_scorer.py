"""
ai_scorer.py
AI scoring using the Google Gemini API.
Sends each resume + job description to Gemini and parses a score + reason.
"""

import os
import json
import time
import google.generativeai as genai
from typing import Dict, Optional

# Load API key from environment (set in .env file)
GEMINI_API_KEY ='AIzaSyCW3P__q07fdi8Zb1XEAE8tvEW_GoIztR4'

# Rate limit: Gemini free tier allows ~15 requests/min
RATE_LIMIT_DELAY = 4  # seconds between API calls to stay safe


def _configure_gemini():
    """Configure the Gemini client with the API key."""
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY not found. Please add it to your .env file."
        )
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")


def _build_prompt(job_description: str, resume_text: str) -> str:
    """
    Build the prompt sent to Gemini for scoring.
    Instructs the model to return clean JSON only.
    """
    return f"""
You are an expert HR recruiter. Carefully read the job description and the resume below, then evaluate how well the candidate fits the role.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Respond ONLY with a valid JSON object — no markdown, no explanation outside the JSON. Use this exact format:
{{
  "score": <integer between 0 and 100>,
  "reason": "<2-3 sentence explanation of why the candidate does or does not fit this role>"
}}
"""


def score_resume_with_ai(
    job_description: str,
    resume_text: str,
    model,
) -> Dict:
    """
    Score a single resume using the Gemini API.

    Returns:
        dict with keys 'ai_score' (int) and 'ai_reason' (str).
        On failure, returns score=0 and an error reason.
    """
    prompt = _build_prompt(job_description, resume_text)
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)
        score = max(0, min(100, int(parsed.get("score", 0))))
        reason = parsed.get("reason", "No reason provided.")
        return {"ai_score": score, "ai_reason": reason}

    except json.JSONDecodeError:
        return {
            "ai_score": 0,
            "ai_reason": "Could not parse Gemini response. Raw output was not valid JSON.",
        }
    except Exception as e:
        return {
            "ai_score": 0,
            "ai_reason": f"API error: {str(e)}",
        }


def score_all_resumes_ai(
    job_description: str,
    resumes: list,
    progress_callback=None,
) -> list:
    """
    Score a list of resumes using the Gemini AI API.

    Args:
        job_description: The job description text.
        resumes: List of dicts with 'name' and 'text'.
        progress_callback: Optional callable(current, total, name) for UI updates.

    Returns:
        List of dicts with 'name', 'text', 'ai_score', 'ai_reason'.
    """
    model = _configure_gemini()
    results = []
    total = len(resumes)

    for i, resume in enumerate(resumes):
        if progress_callback:
            progress_callback(i + 1, total, resume["name"])

        result = score_resume_with_ai(job_description, resume["text"], model)
        results.append(
            {
                "name": resume["name"],
                "text": resume["text"],
                "ai_score": result["ai_score"],
                "ai_reason": result["ai_reason"],
            }
        )

        # Respect rate limit — pause between calls (skip after last item)
        if i < total - 1:
            time.sleep(RATE_LIMIT_DELAY)

    results.sort(key=lambda x: x["ai_score"], reverse=True)
    return results
