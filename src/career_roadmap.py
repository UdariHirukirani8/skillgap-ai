from skill_impact import rank_skill_impacts


def build_career_roadmap(
    user_skills,
    occupation,
    limit=6
):
    impact_result = rank_skill_impacts(
        user_skills,
        occupation,
        limit=limit
    )

    if "error" in impact_result:
        return impact_result

    skills = impact_result.get(
        "best_skills_to_learn",
        []
    )

    if not skills:
        return {
            "occupation": occupation,
            "current_score": impact_result.get(
                "current_score",
                0
            ),
            "current_confidence": impact_result.get(
                "current_confidence",
                "Unknown"
            ),
            "roadmap": {
                "30_days": [],
                "60_days": [],
                "90_days": []
            },
            "message": (
                "No major missing skills were identified."
            )
        }

    skill_names = [
        item["skill"]
        for item in skills
    ]

    # ----------------------------------------
    # 30 DAY PLAN
    # ----------------------------------------

    first_skill = (
        skill_names[0]
        if len(skill_names) >= 1
        else None
    )

    second_skill = (
        skill_names[1]
        if len(skill_names) >= 2
        else None
    )

    thirty_day_tasks = []

    if first_skill:
        thirty_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Learn the fundamentals of "
                    f"{first_skill}"
                ),
                "skill": first_skill
            }
        )

        thirty_day_tasks.append(
            {
                "type": "practice",
                "title": (
                    f"Complete practical exercises "
                    f"using {first_skill}"
                ),
                "skill": first_skill
            }
        )

    if second_skill:
        thirty_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Begin learning "
                    f"{second_skill}"
                ),
                "skill": second_skill
            }
        )

    thirty_day_tasks.append(
        {
            "type": "portfolio",
            "title": (
                "Document your learning progress "
                "and create one small portfolio artifact"
            ),
            "skill": None
        }
    )

    # ----------------------------------------
    # 60 DAY PLAN
    # ----------------------------------------

    third_skill = (
        skill_names[2]
        if len(skill_names) >= 3
        else None
    )

    fourth_skill = (
        skill_names[3]
        if len(skill_names) >= 4
        else None
    )

    sixty_day_tasks = []

    if first_skill:
        sixty_day_tasks.append(
            {
                "type": "project",
                "title": (
                    f"Build a small project that "
                    f"demonstrates {first_skill}"
                ),
                "skill": first_skill
            }
        )

    if third_skill:
        sixty_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Learn and practice "
                    f"{third_skill}"
                ),
                "skill": third_skill
            }
        )

    if fourth_skill:
        sixty_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Develop working knowledge of "
                    f"{fourth_skill}"
                ),
                "skill": fourth_skill
            }
        )

    sixty_day_tasks.append(
        {
            "type": "portfolio",
            "title": (
                "Add at least one stronger project "
                "to your portfolio with clear documentation"
            ),
            "skill": None
        }
    )

    # ----------------------------------------
    # 90 DAY PLAN
    # ----------------------------------------

    fifth_skill = (
        skill_names[4]
        if len(skill_names) >= 5
        else None
    )

    sixth_skill = (
        skill_names[5]
        if len(skill_names) >= 6
        else None
    )

    ninety_day_tasks = []

    if fifth_skill:
        ninety_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Learn the core concepts of "
                    f"{fifth_skill}"
                ),
                "skill": fifth_skill
            }
        )

    if sixth_skill:
        ninety_day_tasks.append(
            {
                "type": "learn",
                "title": (
                    f"Gain practical exposure to "
                    f"{sixth_skill}"
                ),
                "skill": sixth_skill
            }
        )

    ninety_day_tasks.append(
        {
            "type": "project",
            "title": (
                f"Build a portfolio project aligned with "
                f"the {occupation} career path"
            ),
            "skill": None
        }
    )

    ninety_day_tasks.append(
        {
            "type": "career",
            "title": (
                "Update your CV, portfolio, and GitHub "
                "to show evidence of your new skills"
            ),
            "skill": None
        }
    )

    ninety_day_tasks.append(
        {
            "type": "career",
            "title": (
                "Start reviewing real job descriptions "
                "and compare them with your updated skill profile"
            ),
            "skill": None
        }
    )

    return {
        "occupation":
            impact_result[
                "occupation"
            ],

        "current_score":
            impact_result[
                "current_score"
            ],

        "current_confidence":
            impact_result[
                "current_confidence"
            ],

        "priority_skills":
            skills,

        "roadmap": {
            "30_days":
                thirty_day_tasks,

            "60_days":
                sixty_day_tasks,

            "90_days":
                ninety_day_tasks
        }
    }


if __name__ == "__main__":

    user_skills = [
        "Python",
        "SQL",
        "Statistics",
        "Data Analysis"
    ]

    result = build_career_roadmap(
        user_skills,
        "database designer"
    )

    print("\n")
    print("=" * 70)
    print(
        "SKILLGAP AI - 30/60/90 DAY CAREER ROADMAP"
    )
    print("=" * 70)

    if "error" in result:

        print(
            "Error:",
            result["error"]
        )

    else:

        print(
            "\nCareer:",
            result["occupation"]
        )

        print(
            "Current Score:",
            result["current_score"],
            "/100"
        )

        print(
            "Confidence:",
            result[
                "current_confidence"
            ]
        )

        print("\n30 DAYS")

        for item in result[
            "roadmap"
        ]["30_days"]:

            print(
                "-",
                item["title"]
            )

        print("\n60 DAYS")

        for item in result[
            "roadmap"
        ]["60_days"]:

            print(
                "-",
                item["title"]
            )

        print("\n90 DAYS")

        for item in result[
            "roadmap"
        ]["90_days"]:

            print(
                "-",
                item["title"]
            )

        print("\n")
        print("=" * 70)