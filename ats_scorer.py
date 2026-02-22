"""
ats_scorer.py
ATS scoring using TF-IDF vectorization and cosine similarity.
No AI API calls — works fully offline and is very fast.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


def compute_ats_score(job_description: str, resume_text: str) -> float:
    """
    Compute a single ATS score for one resume against a job description.

    Steps:
    1. Combine JD + resume into a corpus.
    2. Vectorize using TF-IDF.
    3. Compute cosine similarity between the two vectors.
    4. Scale to 0–100.

    Returns:
        float: Score between 0 and 100.
    """
    corpus = [job_description, resume_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def score_all_resumes_ats(
    job_description: str,
    resumes: List[Dict],
) -> List[Dict]:
    """
    Score a list of resumes using ATS (TF-IDF) mode.

    Args:
        job_description: The job description text.
        resumes: List of dicts with keys 'name' and 'text'.

    Returns:
        List of dicts with 'name', 'text', 'ats_score'.
    """
    results = []
    for resume in resumes:
        ats_score = compute_ats_score(job_description, resume["text"])
        results.append(
            {
                "name": resume["name"],
                "text": resume["text"],
                "ats_score": ats_score,
            }
        )
    # Sort descending by ATS score
    results.sort(key=lambda x: x["ats_score"], reverse=True)
    return results
