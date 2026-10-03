import ast
from collections import Counter

import pandas as pd

from skill_matcher import (
    calculate_skill_match,
    normalize_skill
)


# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

file_path = "data/raw/train-00000-of-00001.parquet"

df = pd.read_parquet(file_path)


# --------------------------------------------------
# 2. USER INPUT
# --------------------------------------------------

skills_input = input(
    "Enter your skills separated by commas: "
)

user_skills = [
    skill.strip()
    for skill in skills_input.split(",")
    if skill.strip()
]


target_role = input(
    "Enter your target job role: "
).strip().lower()


# --------------------------------------------------
# 3. FILTER IT JOBS
# --------------------------------------------------

jobs = df[
    df["category"] == "INFORMATION-TECHNOLOGY"
].copy()


# --------------------------------------------------
# 4. FILTER BY TARGET ROLE
# --------------------------------------------------

if target_role:
    filtered_jobs = jobs[
        jobs["job_title"]
        .str.lower()
        .str.contains(
            target_role,
            na=False
        )
    ]

    if not filtered_jobs.empty:
        jobs = filtered_jobs

    else:
        print(
            "\nNo exact title matches found."
        )

        print(
            "Showing best matches from all "
            "Information Technology jobs.\n"
        )


# --------------------------------------------------
# 5. CALCULATE JOB MATCH SCORES
# --------------------------------------------------

results = []


for _, job in jobs.iterrows():

    required_skills = job[
        "job_skill_set"
    ]

    if isinstance(required_skills, str):
        try:
            required_skills = ast.literal_eval(
                required_skills
            )

        except (ValueError, SyntaxError):
            continue


    if not isinstance(
        required_skills,
        (list, tuple, set)
    ):
        continue


    result = calculate_skill_match(
        user_skills,
        required_skills
    )


    results.append({
        "job_title":
            job["job_title"],

        "match_score":
            result["match_score"],

        "matched_skills":
            result["matched_skills"],

        "missing_skills":
            result["missing_skills"]
    })


# --------------------------------------------------
# 6. CREATE RECOMMENDATION TABLE
# --------------------------------------------------

recommendations = pd.DataFrame(
    results
)


if recommendations.empty:
    print(
        "\nNo jobs could be analyzed."
    )

    raise SystemExit


recommendations = recommendations.sort_values(
    by="match_score",
    ascending=False
)


# Remove zero-score jobs
positive_matches = recommendations[
    recommendations["match_score"] > 0
]


# --------------------------------------------------
# 7. SELECT TOP 5 JOBS
# --------------------------------------------------

if not positive_matches.empty:

    top_matches = positive_matches.head(5)

else:

    print(
        "\nNo jobs had a direct skill match."
    )

    print(
        "Showing the closest available "
        "jobs instead.\n"
    )

    top_matches = recommendations.head(5)


# --------------------------------------------------
# 8. DISPLAY TOP JOB MATCHES
# --------------------------------------------------

print("\n")
print("=" * 70)

print("SKILLGAP AI - TOP JOB MATCHES")

print("=" * 70)


for number, (_, row) in enumerate(
    top_matches.iterrows(),
    start=1
):

    print(
        f"\n#{number} JOB TITLE:"
    )

    print(
        row["job_title"]
    )


    print(
        "\nMATCH SCORE:"
    )

    print(
        f'{row["match_score"]}%'
    )


    print(
        "\nMATCHED SKILLS:"
    )

    if row["matched_skills"]:
        for skill in row[
            "matched_skills"
        ]:

            print(
                f"  + {skill}"
            )

    else:
        print(
            "  No direct skill matches"
        )


    print(
        "\nMISSING SKILLS:"
    )

    if row["missing_skills"]:
        for skill in row[
            "missing_skills"
        ]:

            print(
                f"  - {skill}"
            )

    else:
        print(
            "  No missing skills"
        )


    print(
        "\n" + "-" * 70
    )


# --------------------------------------------------
# 9. RECOMMEND SKILLS TO LEARN NEXT
# --------------------------------------------------

missing_skill_counter = Counter()


for _, row in top_matches.iterrows():

    for skill in row[
        "missing_skills"
    ]:

        normalized_skill = normalize_skill(
            skill
        )

        missing_skill_counter[
            normalized_skill
        ] += 1


top_learning_skills = (
    missing_skill_counter
    .most_common(5)
)


print("\n")

print("=" * 70)

print(
    "TOP SKILLS YOU SHOULD LEARN NEXT"
)

print("=" * 70)


if top_learning_skills:

    for position, (
        skill,
        frequency
    ) in enumerate(
        top_learning_skills,
        start=1
    ):

        print(
            f"{position}. "
            f"{skill.title()} "
            f"(required by "
            f"{frequency} top jobs)"
        )

else:

    print(
        "You already match the "
        "main skills for these jobs."
    )


print("\n")

print(
    "Analysis complete."
)