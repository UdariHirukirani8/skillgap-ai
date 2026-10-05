from esco_service import (
    search_occupations,
    get_occupation_skills
)

from career_discovery import calculate_career_fit
from skill_impact import rank_skill_impacts


def get_career_comparison_data(
    user_skills,
    occupation_keyword
):
    """
    Build a comparison profile for one occupation.
    """

    occupations = search_occupations(
        occupation_keyword,
        limit=1
    )

    if occupations.empty:
        return {
            "error": (
                f"Occupation not found: "
                f"{occupation_keyword}"
            )
        }

    occupation = occupations.iloc[0]

    occupation_uri = occupation[
        "conceptUri"
    ]

    occupation_name = occupation[
        "preferredLabel"
    ]

    description = occupation.get(
        "description",
        ""
    )

    skills_df = get_occupation_skills(
        occupation_uri
    )


    # ==========================================
    # ESSENTIAL SKILLS
    # ==========================================

    essential_skills = (
        skills_df[
            skills_df["relationType"]
            == "essential"
        ]["preferredLabel"]
        .dropna()
        .tolist()
    )


    # ==========================================
    # OPTIONAL SKILLS
    # ==========================================

    optional_skills = (
        skills_df[
            skills_df["relationType"]
            == "optional"
        ]["preferredLabel"]
        .dropna()
        .tolist()
    )


    # ==========================================
    # CAREER FIT
    # ==========================================

    fit_result = calculate_career_fit(
        user_skills,
        essential_skills,
        optional_skills
    )


    # ==========================================
    # SKILL IMPACT
    # ==========================================

    impact_result = rank_skill_impacts(
        user_skills,
        occupation_name,
        limit=3
    )


    best_skill = None
    best_improvement = 0
    projected_score = (
        fit_result[
            "career_fit_score"
        ]
    )


    if (
        "error" not in impact_result
        and
        impact_result.get(
            "best_skills_to_learn"
        )
    ):
        best = (
            impact_result[
                "best_skills_to_learn"
            ][0]
        )

        best_skill = best[
            "skill"
        ]

        best_improvement = best[
            "improvement"
        ]

        projected_score = best[
            "new_score"
        ]


    return {
        "occupation":
            occupation_name,

        "description":
            description,

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

        "best_next_skill":
            best_skill,

        "potential_improvement":
            best_improvement,

        "projected_score":
            projected_score
    }


def compare_careers(
    user_skills,
    occupations
):
    """
    Compare multiple careers and identify
    the strongest overall career option.
    """

    results = []


    for occupation in occupations:

        result = (
            get_career_comparison_data(
                user_skills,
                occupation
            )
        )

        if "error" not in result:
            results.append(
                result
            )


    if not results:
        return {
            "error":
                "No valid occupations found."
        }


    # ==========================================
    # RANK CAREERS
    # ==========================================

    results = sorted(
        results,
        key=lambda item: (
            item["career_fit_score"],
            item["essential_coverage"],
            item["projected_score"]
        ),
        reverse=True
    )


    # ==========================================
    # ADD RANK
    # ==========================================

    for index, career in enumerate(
        results,
        start=1
    ):
        career["rank"] = index


    best_career = results[0]


    # ==========================================
    # EXPLANATION
    # ==========================================

    explanation = (
        f"{best_career['occupation']} "
        f"is currently your strongest match "
        f"with a career fit score of "
        f"{best_career['career_fit_score']}/100."
    )


    if best_career[
        "best_next_skill"
    ]:
        explanation += (
            f" Learning "
            f"{best_career['best_next_skill']} "
            f"could improve the score to "
            f"{best_career['projected_score']}/100."
        )


    return {
        "user_skills":
            user_skills,

        "careers_compared":
            len(results),

        "recommended_career":
            best_career[
                "occupation"
            ],

        "recommendation_reason":
            explanation,

        "comparisons":
            results
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    user_skills = [
        "Python",
        "SQL",
        "Statistics",
        "Data Analysis",
        "Communication",
        "Problem Solving"
    ]


    careers = [
        "database designer",
        "data analyst",
        "business analyst"
    ]


    result = compare_careers(
        user_skills,
        careers
    )


    print("\n")
    print("=" * 70)
    print(
        "SKILLGAP AI - CAREER COMPARISON"
    )
    print("=" * 70)


    if "error" in result:

        print(
            result["error"]
        )

    else:

        print(
            "\nRecommended Career:"
        )

        print(
            result[
                "recommended_career"
            ]
        )


        print(
            "\nReason:"
        )

        print(
            result[
                "recommendation_reason"
            ]
        )


        print(
            "\nCAREER COMPARISON"
        )


        for career in result[
            "comparisons"
        ]:

            print(
                "\n" + "-" * 60
            )

            print(
                f"#{career['rank']} "
                f"{career['occupation']}"
            )

            print(
                "Fit Score:",
                career[
                    "career_fit_score"
                ]
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
                ]
            )

            print(
                "Best Next Skill:",
                career[
                    "best_next_skill"
                ]
            )

            print(
                "Potential Improvement:",
                career[
                    "potential_improvement"
                ]
            )

            print(
                "Projected Score:",
                career[
                    "projected_score"
                ]
            )


    print("\n")
    print("=" * 70)