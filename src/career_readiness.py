from esco_service import (
    search_occupations,
    get_occupation_skills
)

from skill_matcher import skills_are_similar


# --------------------------------------------------
# MATCH A USER AGAINST A LIST OF SKILLS
# --------------------------------------------------

def compare_skills(user_skills, required_skills):

    matched = []
    missing = []

    for required_skill in required_skills:

        found = False

        for user_skill in user_skills:

            if skills_are_similar(
                user_skill,
                required_skill
            ):
                matched.append(required_skill)
                found = True
                break

        if not found:
            missing.append(required_skill)

    return matched, missing


# --------------------------------------------------
# CALCULATE CAREER READINESS
# --------------------------------------------------

def calculate_career_readiness(
    user_skills,
    occupation_keyword
):

    # Search occupation
    occupation_results = search_occupations(
        occupation_keyword,
        limit=1
    )

    if occupation_results.empty:

        return {
            "error":
                "Occupation not found"
        }


    occupation = (
        occupation_results.iloc[0]
    )

    occupation_uri = (
        occupation["conceptUri"]
    )


    # Get occupation skills
    skills_df = get_occupation_skills(
        occupation_uri
    )


    # --------------------------------------------------
    # ESSENTIAL SKILLS
    # --------------------------------------------------

    essential_skills = (
        skills_df[
            skills_df["relationType"]
            == "essential"
        ]["preferredLabel"]
        .dropna()
        .tolist()
    )


    # --------------------------------------------------
    # OPTIONAL SKILLS
    # --------------------------------------------------

    optional_skills = (
        skills_df[
            skills_df["relationType"]
            == "optional"
        ]["preferredLabel"]
        .dropna()
        .tolist()
    )


    # --------------------------------------------------
    # MATCH SKILLS
    # --------------------------------------------------

    matched_essential, missing_essential = (
        compare_skills(
            user_skills,
            essential_skills
        )
    )


    matched_optional, missing_optional = (
        compare_skills(
            user_skills,
            optional_skills
        )
    )


    # --------------------------------------------------
    # ESSENTIAL COVERAGE
    # --------------------------------------------------

    if essential_skills:

        essential_score = (
            len(matched_essential)
            / len(essential_skills)
        ) * 100

    else:

        essential_score = 0


    # --------------------------------------------------
    # OPTIONAL COVERAGE
    # --------------------------------------------------

    if optional_skills:

        optional_score = (
            len(matched_optional)
            / len(optional_skills)
        ) * 100

    else:

        optional_score = 0


    # --------------------------------------------------
    # FINAL CAREER READINESS SCORE
    #
    # Essential skills = 80%
    # Optional skills  = 20%
    # --------------------------------------------------

    readiness_score = (
        essential_score * 0.80
        +
        optional_score * 0.20
    )


    return {

        "occupation":
            occupation[
                "preferredLabel"
            ],

        "description":
            occupation[
                "description"
            ],

        "career_readiness_score":
            round(
                readiness_score,
                2
            ),

        "essential_skill_coverage":
            round(
                essential_score,
                2
            ),

        "optional_skill_coverage":
            round(
                optional_score,
                2
            ),

        "matched_essential_skills":
            matched_essential,

        "missing_essential_skills":
            missing_essential,

        "matched_optional_skills":
            matched_optional,

        "missing_optional_skills":
            missing_optional
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    user_skills = [
        "communication",
        "lesson planning",
        "presentation",
        "teamwork",
        "student assessment",
        "mathematics"
    ]


    result = calculate_career_readiness(
        user_skills,
        "teacher"
    )


    print("\n")
    print("=" * 70)

    print(
        "SKILLGAP AI - CAREER READINESS"
    )

    print("=" * 70)


    if "error" in result:

        print(
            result["error"]
        )

    else:

        print(
            "\nOccupation:"
        )

        print(
            result["occupation"]
        )


        print(
            "\nCareer Readiness Score:"
        )

        print(
            result[
                "career_readiness_score"
            ],
            "%"
        )


        print(
            "\nEssential Skill Coverage:"
        )

        print(
            result[
                "essential_skill_coverage"
            ],
            "%"
        )


        print(
            "\nOptional Skill Coverage:"
        )

        print(
            result[
                "optional_skill_coverage"
            ],
            "%"
        )


        print(
            "\nMatched Essential Skills:"
        )

        for skill in result[
            "matched_essential_skills"
        ]:

            print(
                "+",
                skill
            )


        print(
            "\nMissing Essential Skills:"
        )

        for skill in result[
            "missing_essential_skills"
        ][:15]:

            print(
                "-",
                skill
            )