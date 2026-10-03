SKILL_ALIASES = {
    "python programming": "python",
    "python development": "python",

    "sql server": "sql",
    "mysql": "sql",
    "postgresql": "sql",
    "query languages": "sql",
    "database querying": "sql",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "powerbi": "power bi",
    "power bi desktop": "power bi",
    "business intelligence": "power bi",
    "data visualization": "power bi",

    "data analytics": "data analysis",
    "data analyst": "data analysis",
    "data analysing": "data analysis",
    "analytics": "data analysis",
    "cloud reporting and analytics": "data analysis",
    "reporting": "data analysis",

    "machine-learning": "machine learning",
    "ml": "machine learning",
    "data mining": "machine learning",

    "amazon web services": "aws",
    "microsoft azure": "azure",

    "github": "git",

    "html5": "html",
    "css3": "css",

    "javascript programming": "javascript",

    "data warehouse": "data warehousing",
    "database management systems": "database management"
}


TECHNICAL_SKILLS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "javascript",
    "java",
    "html",
    "css",
    "git",
    "machine learning",
    "data analysis",
    "statistics",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "data warehousing",
    "data governance",
    "database management"
}


SOFT_SKILLS = {
    "communication",
    "teamwork",
    "leadership",
    "adaptability",
    "problem solving",
    "attention to detail",
    "time management"
}


def normalize_skill(skill):
    skill = str(skill).strip().lower()

    return SKILL_ALIASES.get(skill, skill)


def skills_are_similar(user_skill, required_skill):
    user_skill = normalize_skill(user_skill)
    required_skill = normalize_skill(required_skill)

    if user_skill == required_skill:
        return True

    if user_skill in required_skill:
        return True

    if required_skill in user_skill:
        return True

    return False


def get_skill_weight(skill):
    normalized_skill = normalize_skill(skill)

    if normalized_skill in TECHNICAL_SKILLS:
        return 3

    if normalized_skill in SOFT_SKILLS:
        return 1

    return 2


def calculate_skill_match(user_skills, required_skills):
    matched_skills = []
    missing_skills = []

    total_weight = 0
    matched_weight = 0

    for required_skill in required_skills:
        weight = get_skill_weight(required_skill)

        total_weight += weight

        found_match = False

        for user_skill in user_skills:
            if skills_are_similar(user_skill, required_skill):
                matched_skills.append(required_skill)

                matched_weight += weight

                found_match = True

                break

        if not found_match:
            missing_skills.append(required_skill)

    if total_weight == 0:
        match_score = 0
    else:
        match_score = (
            matched_weight / total_weight
        ) * 100

    return {
        "match_score": round(match_score, 2),
        "matched_skills": sorted(
            set(matched_skills)
        ),
        "missing_skills": sorted(
            set(missing_skills)
        )
    }


if __name__ == "__main__":
    user_skills = [
        "Python",
        "SQL",
        "Excel",
        "Power BI"
    ]

    required_skills = [
        "Python Programming",
        "SQL Server",
        "Data Analysis",
        "PowerBI",
        "Communication"
    ]

    result = calculate_skill_match(
        user_skills,
        required_skills
    )

    print("Match Score:", result["match_score"], "%")
    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])