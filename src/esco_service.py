from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ESCO_DIR = PROJECT_ROOT / "data" / "raw" / "esco"


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


def search_occupations(keyword, limit=10):
    keyword = keyword.strip().lower()

    matches = occupations[
        occupations["preferredLabel"]
        .str.lower()
        .str.contains(keyword, na=False)
    ]

    return matches[
        [
            "conceptUri",
            "preferredLabel",
            "description"
        ]
    ].head(limit)


def get_occupation_skills(occupation_uri):
    occupation_relations = relations[
        relations["occupationUri"] == occupation_uri
    ].copy()

    merged = occupation_relations.merge(
        skills,
        left_on="skillUri",
        right_on="conceptUri",
        how="left"
    )

    columns = [
        "relationType",
        "preferredLabel",
        "description"
    ]

    available_columns = [
        col
        for col in columns
        if col in merged.columns
    ]

    return merged[available_columns]


if __name__ == "__main__":
    print("\nSearch results for 'teacher':\n")

    results = search_occupations("teacher", 5)

    print(results)

    if not results.empty:
        occupation_uri = results.iloc[0]["conceptUri"]

        print("\nSkills for:")
        print(results.iloc[0]["preferredLabel"])

        occupation_skills = get_occupation_skills(
            occupation_uri
        )

        print(occupation_skills.head(20))