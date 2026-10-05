from pathlib import Path
import pandas as pd


# ==================================================
# PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ESCO_DIR = PROJECT_ROOT / "data" / "raw" / "esco"


# ==================================================
# LOAD ESCO DATA ONCE
# ==================================================

occupations = pd.read_csv(
    ESCO_DIR / "occupations_en.csv",
    low_memory=False
)

skills = pd.read_csv(
    ESCO_DIR / "skills_en.csv",
    low_memory=False
)

relations = pd.read_csv(
    ESCO_DIR / "occupationSkillRelations_en.csv",
    low_memory=False
)


# ==================================================
# PREPARE SKILL LOOKUP
# ==================================================

skills_lookup = (
    skills[
        [
            "conceptUri",
            "preferredLabel",
            "description"
        ]
    ]
    .rename(
        columns={
            "conceptUri": "skillUri"
        }
    )
)


# ==================================================
# MERGE RELATIONS + SKILLS ONLY ONCE
# ==================================================

occupation_skill_data = relations.merge(
    skills_lookup,
    on="skillUri",
    how="left"
)


# ==================================================
# CREATE FAST CACHE
# ==================================================

OCCUPATION_SKILLS_CACHE = {
    occupation_uri: group[
        [
            "relationType",
            "preferredLabel",
            "description"
        ]
    ].copy()

    for occupation_uri, group
    in occupation_skill_data.groupby(
        "occupationUri"
    )
}


# ==================================================
# SEARCH OCCUPATIONS
# ==================================================

def search_occupations(
    keyword,
    limit=10
):
    keyword = (
        keyword
        .strip()
        .lower()
    )

    matches = occupations[
        occupations[
            "preferredLabel"
        ]
        .str.lower()
        .str.contains(
            keyword,
            na=False
        )
    ]

    return matches[
        [
            "conceptUri",
            "preferredLabel",
            "description"
        ]
    ].head(limit)


# ==================================================
# GET OCCUPATION SKILLS
# ==================================================

def get_occupation_skills(
    occupation_uri
):
    return OCCUPATION_SKILLS_CACHE.get(
        occupation_uri,
        pd.DataFrame(
            columns=[
                "relationType",
                "preferredLabel",
                "description"
            ]
        )
    )


# ==================================================
# QUICK TEST
# ==================================================

if __name__ == "__main__":

    print(
        "ESCO occupations:",
        len(occupations)
    )

    print(
        "Cached occupations:",
        len(
            OCCUPATION_SKILLS_CACHE
        )
    )

    results = search_occupations(
        "teacher",
        5
    )

    print(
        "\nTeacher search:"
    )

    print(results)

    if not results.empty:

        uri = (
            results.iloc[0][
                "conceptUri"
            ]
        )

        print(
            "\nSkills:"
        )

        print(
            get_occupation_skills(
                uri
            ).head(10)
        )