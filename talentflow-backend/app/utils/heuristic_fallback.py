import re

def heuristic_extract(text: str) -> dict:
    """Very simple heuristic extraction when no LLM is available."""
    # Normalize line endings
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.strip().split("\n") if text else []
    name = lines[0].strip() if lines else "Unknown"

    # email
    email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', text or "")
    email = email_match.group(0) if email_match else None

    # phone
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{7,15}', text or "")
    phone = phone_match.group(0).strip() if phone_match else None

    # skills — look for common tech keywords
    tech_keywords = [
        "Python", "FastAPI", "Django", "Flask", "PostgreSQL", "Redis", "Docker",
        "Kubernetes", "AWS", "GCP", "Azure", "Celery", "GraphQL", "REST",
        "JavaScript", "TypeScript", "React", "Node.js", "Go", "Rust", "Java",
        "C++", "SQL", "MongoDB", "Elasticsearch", "Kafka", "RabbitMQ",
        "TensorFlow", "PyTorch", "LangChain", "LangGraph", "CI/CD", "Git",
        "Linux", "Terraform", "Ansible", "Prometheus", "Grafana", "gRPC",
        "Microservices", "Machine Learning", "Deep Learning", "NLP",
        "pgvector", "Vector Search", "Embeddings", "RAG",
    ]

    found_skills = []
    text_lower = (text or "").lower()
    for kw in tech_keywords:
        if kw.lower() in text_lower:
            found_skills.append({"name": kw, "years_experience": None, "proficiency": None})

    # experience count — multiple patterns for date ranges
    # Pattern 1: 2019-2022 or 2020 - Present
    exp_ranges = re.findall(r'(20\d{2})\s*(?:[^0-9a-zA-Z\s]|to)+\s*(20\d{2}|[Pp]resent|[Cc]urrent)', text)
    # Pattern 2: Month Year - Month Year (e.g. Jan 2019 - Dec 2022)
    exp_ranges2 = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(20\d{2})\s*(?:[^0-9a-zA-Z\s]|to)+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20\d{2}|[Pp]resent|[Cc]urrent)', text, re.IGNORECASE)
    all_ranges = exp_ranges + exp_ranges2
    
    total_years = 0.0
    for start_yr, end_yr in all_ranges:
        start = int(start_yr)
        end = 2026 if end_yr.lower() in ("present", "current") else int(end_yr)
        total_years += max(0, end - start)

    # seniority
    if total_years < 2:
        seniority = "junior"
    elif total_years < 5:
        seniority = "mid"
    elif total_years < 10:
        seniority = "senior"
    elif total_years < 15:
        seniority = "lead"
    else:
        seniority = "executive"

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": None,
        "skills": found_skills,
        "experience": [],
        "education": [],
        "certifications": [],
        "languages": [],
        "total_years_experience": total_years,
        "seniority_level": seniority,
        "extraction_confidence": 0.7,
        "needs_manual_review": False,
    }

def heuristic_score(profile: dict, semantic_score: float) -> dict:
    """Score without LLM — uses rule-based heuristics."""
    # Convert skills array to lower-case names based on extraction dict shape
    # The heuristic_extract creates {"name": "skill"}
    # The true extraction creates Pydantic Skill objects if it was successful,
    # but since this is fallback, it might receive dicts or Pydantic models.
    skills = []
    for s in profile.get("skills", []):
        if isinstance(s, dict) and s.get("name"):
            skills.append(s["name"].lower())
        elif hasattr(s, "name"):
            skills.append(s.name.lower())

    years = profile.get("total_years_experience", 0)

    # Skills match (0-10)
    required = ["python", "fastapi", "postgresql", "docker", "redis", "celery"]
    match_count = sum(1 for r in required if r in skills)
    skills_score = min(10, int(match_count / len(required) * 10))

    # Experience relevance (0-10)
    if years >= 7:
        exp_score = 9
    elif years >= 5:
        exp_score = 7
    elif years >= 3:
        exp_score = 5
    elif years >= 1:
        exp_score = 3
    else:
        exp_score = 1

    # Education (default moderate)
    edu_score = 6

    # Growth trajectory
    growth_score = min(10, int(len(skills) / 3))

    # LLM score equivalent
    weights = {"skills_match": 4000, "experience_relevance": 3000, "education_fit": 1500, "growth_trajectory": 1500}
    total_weight = sum(weights.values())
    llm_score = (
        (skills_score * 10) * (weights["skills_match"] / total_weight)
        + (exp_score * 10) * (weights["experience_relevance"] / total_weight)
        + (edu_score * 10) * (weights["education_fit"] / total_weight)
        + (growth_score * 10) * (weights["growth_trajectory"] / total_weight)
    )
    total_score = 0.60 * llm_score + 0.40 * semantic_score * 100

    if total_score >= 70:
        rec = "strong_yes"
    elif total_score >= 55:
        rec = "yes"
    elif total_score >= 40:
        rec = "maybe"
    else:
        rec = "no"

    return {
        "score_breakdown": {
            "skills_match": {"score": skills_score, "justification": f"Matched {match_count}/{len(required)} required skills", "weight_bps": 4000},
            "experience_relevance": {"score": exp_score, "justification": f"{years:.1f} years experience", "weight_bps": 3000},
            "education_fit": {"score": edu_score, "justification": "Default moderate score", "weight_bps": 1500},
            "growth_trajectory": {"score": growth_score, "justification": f"{len(skills)} total skills detected", "weight_bps": 1500},
            "llm_score": round(llm_score, 2),
            "overall_recommendation": rec,
            "outlier_flag": False,
        },
        "llm_score": round(llm_score, 2),
        "total_score": round(total_score, 2),
        "auto_rejected": False,
    }
