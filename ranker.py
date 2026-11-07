"""Score and rank resumes against a job description (TF-IDF + cosine similarity)."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocess import preprocess


def _top_job_keywords(vectorizer, jd_vector, limit=15):
    """Highest-weighted terms of the job description (what the role cares about)."""
    terms = vectorizer.get_feature_names_out()
    weights = jd_vector.toarray().ravel()
    order = weights.argsort()[::-1]
    return [terms[i] for i in order if weights[i] > 0][:limit]


def rank_resumes(job_description: str, resumes: list) -> list:
    """
    resumes: list of dicts with keys 'name' and 'text'.
    Returns the same candidates sorted best-first, each with
    score (0-100), matched_keywords and missing_keywords.
    """
    if not job_description.strip():
        raise ValueError("Job description is empty.")
    if not resumes:
        return []

    jd_clean = preprocess(job_description)
    cleaned = [preprocess(r["text"]) for r in resumes]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([jd_clean] + cleaned)
    jd_vec, resume_vecs = matrix[0], matrix[1:]

    scores = cosine_similarity(jd_vec, resume_vecs).ravel()
    keywords = _top_job_keywords(vectorizer, jd_vec)

    results = []
    for resume, clean, score in zip(resumes, cleaned, scores):
        words = set(clean.split())
        text = f" {clean} "
        matched = [k for k in keywords if (k in words if " " not in k else f" {k} " in text)]
        missing = [k for k in keywords if k not in matched]
        results.append(
            {
                "name": resume["name"],
                "filename": resume.get("filename", resume["name"]),
                "score": round(float(score) * 100, 1),
                "matched_keywords": matched,
                "missing_keywords": missing,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank
    return results
