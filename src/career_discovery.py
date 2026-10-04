from esco_service import (
    occupations,
    get_occupation_skills
)

from skill_matcher import (
    skills_are_similar_for_discovery,
    get_discovery_skill_weight
)


def calculate_weighted_match(
    user_skills,
    required_skills
):
    total_weight = 0
    matched_weight = 0
    matched_skills = []

    for required_skill in required_skills:

        weight = get_discovery_skill_weight(
            required_skill
        )

        total_weight += weight

        for user_skill in user_skills:

            if skills_are_similar_for_discovery(
                user_skill,
                required_skill
            ):
                matched_weight += weight
                matched_skills.append(
                    required_skill
                )
                break

    if total_weight == 0:
        return 0, []

    score = (
        matched_weight
        / total_weight
    ) * 100

    return (
        round(score, 2),
        matched_skills
    )


def discover_careers(
    user_skills,
    limit=10
):
    results = []

    for _, occupation in occupations.iterrows():

        occupation_uri = occupation[
            "conceptUri"
        ]

        skills_df = get_occupation_skills(
            occupation_uri
        )

        if skills_df.empty:
            continue

        essential_skills = (
            skills_df[
                skills_df["relationType"]
                == "essential"
            ]["preferredLabel"]
            .dropna()
            .tolist()
        )

        optional_skills = (
            skills_df[
                skills_df["relationType"]
                == "optional"
            ]["preferredLabel"]
            .dropna()
            .tolist()
        )

        (
            essential_score,
            matched_essential
        ) = calculate_weighted_match(
            user_skills,
            essential_skills
        )

        (
            optional_score,
            matched_optional
        ) = calculate_weighted_match(
            user_skills,
            optional_skills
        )

        final_score = (
            essential_score * 0.85
            +
            optional_score * 0.15
        )

        meaningful_matches = (
            len(matched_essential)
            +
            len(matched_optional)
        )

        if (
            final_score > 0
            and meaningful_matches >= 2
        ):
            results.append({
                "occupation":
                    occupation[
                        "preferredLabel"
                    ],

                "description":
                    occupation[
                        "description"
                    ],

                "match_score":
                    round(
                        final_score,
                        2
                    ),

                "matched_essential_skills":
                    matched_essential,

                "matched_optional_skills":
                    matched_optional,

                "meaningful_matches":
                    meaningful_matches
            })

    results = sorted(
        results,
        key=lambda x: (
            x["match_score"],
            x["meaningful_matches"]
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
        "SKILLGAP AI - CAREER DISCOVERY V2"
    )
    print("=" * 70)

    if not matches:
        print(
            "\nNo suitable career matches found."
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
            "Match Score:",
            career["match_score"],
            "%"
        )

        print(
            "Meaningful Matches:",
            career[
                "meaningful_matches"
            ]
        )

        print(
            "Matched Essential Skills:",
            career[
                "matched_essential_skills"
            ]
        )

        print(
            "Matched Optional Skills:",
            career[
                "matched_optional_skills"
            ]
        )

        print("-" * 70)