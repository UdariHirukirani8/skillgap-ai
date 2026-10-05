from esco_service import (
    occupations,
    get_occupation_skills
)

from skill_matcher import (
    skills_are_similar_for_discovery,
    get_discovery_skill_weight,
    normalize_skill
)


def calculate_weighted_match(
    user_skills,
    required_skills
):
    total_weight = 0
    matched_weight = 0

    matched_skills = []
    missing_skills = []

    for required_skill in required_skills:

        weight = get_discovery_skill_weight(
            required_skill
        )

        total_weight += weight

        found_match = False

        for user_skill in user_skills:

            if skills_are_similar_for_discovery(
                user_skill,
                required_skill
            ):
                matched_weight += weight
                matched_skills.append(
                    required_skill
                )
                found_match = True
                break

        if not found_match:
            missing_skills.append(
                required_skill
            )

    if total_weight == 0:
        coverage_score = 0

    else:
        coverage_score = (
            matched_weight / total_weight
        ) * 100

    return {
        "coverage_score":
            round(coverage_score, 2),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "matched_weight":
            matched_weight,

        "total_weight":
            total_weight
    }


def calculate_career_fit(
    user_skills,
    essential_skills,
    optional_skills
):
    essential_result = (
        calculate_weighted_match(
            user_skills,
            essential_skills
        )
    )

    optional_result = (
        calculate_weighted_match(
            user_skills,
            optional_skills
        )
    )

    essential_matches = len(
        essential_result[
            "matched_skills"
        ]
    )

    optional_matches = len(
        optional_result[
            "matched_skills"
        ]
    )

    total_matches = (
        essential_matches
        +
        optional_matches
    )

    # ----------------------------------------
    # SCORE COMPONENT 1:
    # Essential skill coverage
    # ----------------------------------------

    essential_component = min(
        essential_result[
            "coverage_score"
        ],
        100
    ) * 0.55

    # ----------------------------------------
    # SCORE COMPONENT 2:
    # Number of strong matches
    # ----------------------------------------

    match_strength_score = min(
        essential_matches * 12,
        30
    )

    # ----------------------------------------
    # SCORE COMPONENT 3:
    # Optional skill bonus
    # ----------------------------------------

    optional_bonus = min(
        optional_matches * 3,
        10
    )

    # ----------------------------------------
    # SCORE COMPONENT 4:
    # Domain-specific bonus
    # ----------------------------------------

    normalized_user_skills = {
        normalize_skill(skill)
        for skill in user_skills
    }

    domain_specific_skills = {
        skill
        for skill in normalized_user_skills
        if get_discovery_skill_weight(skill)
        >= 3
    }

    domain_bonus = min(
        len(domain_specific_skills) * 2,
        5
    )

    career_fit_score = (
        essential_component
        +
        match_strength_score
        +
        optional_bonus
        +
        domain_bonus
    )

    career_fit_score = min(
        career_fit_score,
        100
    )

    # ----------------------------------------
    # CONFIDENCE
    # ----------------------------------------

    if (
        essential_matches >= 4
        and career_fit_score >= 60
    ):
        confidence = "High"

    elif (
        essential_matches >= 2
        and career_fit_score >= 30
    ):
        confidence = "Medium"

    else:
        confidence = "Low"

    # ----------------------------------------
    # KEY GAPS
    # ----------------------------------------

    key_gaps = (
        essential_result[
            "missing_skills"
        ][:5]
    )

    # ----------------------------------------
    # EXPLANATION
    # ----------------------------------------

    if confidence == "High":

        explanation = (
            "You already match several core "
            "skills required for this career."
        )

    elif confidence == "Medium":

        explanation = (
            "You have a useful foundation for "
            "this career, but several important "
            "skills are still missing."
        )

    else:

        explanation = (
            "This career has some connection "
            "to your current skills, but you "
            "would need significant upskilling."
        )

    return {
        "career_fit_score":
            round(
                career_fit_score,
                2
            ),

        "confidence":
            confidence,

        "essential_coverage":
            essential_result[
                "coverage_score"
            ],

        "matched_essential_skills":
            essential_result[
                "matched_skills"
            ],

        "matched_optional_skills":
            optional_result[
                "matched_skills"
            ],

        "key_gaps":
            key_gaps,

        "total_matches":
            total_matches,

        "explanation":
            explanation
    }


def discover_careers(
    user_skills,
    limit=10
):
    results = []

    for _, occupation in occupations.iterrows():

        occupation_uri = (
            occupation[
                "conceptUri"
            ]
        )

        skills_df = get_occupation_skills(
            occupation_uri
        )

        if skills_df.empty:
            continue

        essential_skills = (
            skills_df[
                skills_df[
                    "relationType"
                ]
                == "essential"
            ]["preferredLabel"]
            .dropna()
            .tolist()
        )

        optional_skills = (
            skills_df[
                skills_df[
                    "relationType"
                ]
                == "optional"
            ]["preferredLabel"]
            .dropna()
            .tolist()
        )

        fit_result = calculate_career_fit(
            user_skills,
            essential_skills,
            optional_skills
        )

        if fit_result[
            "total_matches"
        ] < 2:
            continue

        results.append({
            "occupation":
                occupation[
                    "preferredLabel"
                ],

            "description":
                occupation[
                    "description"
                ],

            "career_fit_score":
                fit_result[
                    "career_fit_score"
                ],

            "confidence":
                fit_result[
                    "confidence"
                ],

            "essential_coverage":
                fit_result[
                    "essential_coverage"
                ],

            "matched_essential_skills":
                fit_result[
                    "matched_essential_skills"
                ],

            "matched_optional_skills":
                fit_result[
                    "matched_optional_skills"
                ],

            "key_gaps":
                fit_result[
                    "key_gaps"
                ],

            "explanation":
                fit_result[
                    "explanation"
                ],

            "total_matches":
                fit_result[
                    "total_matches"
                ]
        })

    results = sorted(
        results,
        key=lambda item: (
            item[
                "career_fit_score"
            ],
            item[
                "total_matches"
            ]
        ),
        reverse=True
    )

    return results[:limit]


if __name__ == "__main__":

    user_skills = [
        "python",
        "sql",
        "statistics",
        "data analysis",
        "communication",
        "problem solving"
    ]

    matches = discover_careers(
        user_skills,
        limit=10
    )

    print("\n")
    print("=" * 70)
    print(
        "SKILLGAP AI - CAREER DISCOVERY V3"
    )
    print("=" * 70)

    if not matches:
        print(
            "\nNo suitable careers found."
        )

    for index, career in enumerate(
        matches,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{career['occupation']}"
        )

        print(
            "Career Fit Score:",
            career[
                "career_fit_score"
            ],
            "/100"
        )

        print(
            "Confidence:",
            career[
                "confidence"
            ]
        )

        print(
            "Essential Coverage:",
            career[
                "essential_coverage"
            ],
            "%"
        )

        print(
            "Matched Essential Skills:"
        )

        print(
            career[
                "matched_essential_skills"
            ]
        )

        print(
            "Key Gaps:"
        )

        print(
            career[
                "key_gaps"
            ]
        )

        print(
            "Why Recommended:"
        )

        print(
            career[
                "explanation"
            ]
        )

        print(
            "-" * 70
        )