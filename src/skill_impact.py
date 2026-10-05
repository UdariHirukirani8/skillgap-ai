from career_discovery import calculate_career_fit
from esco_service import (
    search_occupations,
    get_occupation_skills
)


def simulate_skill_impact(
    user_skills,
    occupation_keyword,
    new_skill
):
    """
    Simulate how much one new skill can improve
    the user's career fit score.
    """

    occupations = search_occupations(
        occupation_keyword,
        limit=1
    )

    if occupations.empty:
        return {
            "error": "Occupation not found"
        }

    occupation = occupations.iloc[0]

    occupation_uri = occupation[
        "conceptUri"
    ]

    skills_df = get_occupation_skills(
        occupation_uri
    )


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


    current_result = calculate_career_fit(
        user_skills,
        essential_skills,
        optional_skills
    )


    simulated_skills = list(
        user_skills
    )

    if new_skill not in simulated_skills:
        simulated_skills.append(
            new_skill
        )


    new_result = calculate_career_fit(
        simulated_skills,
        essential_skills,
        optional_skills
    )


    improvement = (
        new_result[
            "career_fit_score"
        ]
        -
        current_result[
            "career_fit_score"
        ]
    )


    return {
        "occupation":
            occupation[
                "preferredLabel"
            ],

        "new_skill":
            new_skill,

        "current_score":
            current_result[
                "career_fit_score"
            ],

        "new_score":
            new_result[
                "career_fit_score"
            ],

        "improvement":
            round(
                improvement,
                2
            ),

        "current_confidence":
            current_result[
                "confidence"
            ],

        "new_confidence":
            new_result[
                "confidence"
            ]
    }


def rank_skill_impacts(
    user_skills,
    occupation_keyword,
    limit=5
):
    """
    Rank missing skills according to how much
    they improve the career fit score.
    """

    occupations = search_occupations(
        occupation_keyword,
        limit=1
    )

    if occupations.empty:
        return {
            "error": "Occupation not found"
        }


    occupation = occupations.iloc[0]

    occupation_uri = occupation[
        "conceptUri"
    ]


    skills_df = get_occupation_skills(
        occupation_uri
    )


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


    current_result = calculate_career_fit(
        user_skills,
        essential_skills,
        optional_skills
    )


    current_score = current_result[
        "career_fit_score"
    ]


    # Use missing essential skills first because
    # they normally have the biggest impact.
    candidate_skills = list(
        dict.fromkeys(
            current_result[
                "key_gaps"
            ]
        )
    )


    impacts = []


    for skill in candidate_skills:

        simulated_skills = (
            list(user_skills)
            + [skill]
        )


        new_result = calculate_career_fit(
            simulated_skills,
            essential_skills,
            optional_skills
        )


        new_score = new_result[
            "career_fit_score"
        ]


        improvement = (
            new_score
            - current_score
        )


        impacts.append({
            "skill":
                skill,

            "current_score":
                current_score,

            "new_score":
                new_score,

            "improvement":
                round(
                    improvement,
                    2
                ),

            "new_confidence":
                new_result[
                    "confidence"
                ]
        })


    impacts = sorted(
        impacts,
        key=lambda item:
            item["improvement"],
        reverse=True
    )


    return {
        "occupation":
            occupation[
                "preferredLabel"
            ],

        "current_score":
            current_score,

        "current_confidence":
            current_result[
                "confidence"
            ],

        "best_skills_to_learn":
            impacts[:limit]
    }


if __name__ == "__main__":

    user_skills = [
        "Python",
        "SQL",
        "Statistics",
        "Data Analysis"
    ]


    print("\n")
    print("=" * 70)
    print(
        "SKILLGAP AI - SKILL IMPACT SIMULATOR"
    )
    print("=" * 70)


    result = rank_skill_impacts(
        user_skills,
        "database designer",
        limit=5
    )


    if "error" in result:

        print(
            "\nError:",
            result["error"]
        )

    else:

        print(
            "\nOccupation:"
        )

        print(
            result[
                "occupation"
            ]
        )


        print(
            "\nCurrent Career Fit Score:"
        )

        print(
            result[
                "current_score"
            ],
            "/100"
        )


        print(
            "\nCurrent Confidence:"
        )

        print(
            result[
                "current_confidence"
            ]
        )


        print(
            "\nBest Skills To Learn Next:"
        )


        skills = result[
            "best_skills_to_learn"
        ]


        if not skills:

            print(
                "No major missing skills found."
            )

        else:

            for index, item in enumerate(
                skills,
                start=1
            ):

                print(
                    f"\n{index}. "
                    f"{item['skill']}"
                )

                print(
                    "   New Score:",
                    item[
                        "new_score"
                    ],
                    "/100"
                )

                print(
                    "   Improvement:",
                    "+",
                    item[
                        "improvement"
                    ]
                )

                print(
                    "   New Confidence:",
                    item[
                        "new_confidence"
                    ]
                )


    print("\n")
    print("=" * 70)