from pathlib import Path
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ESCO_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "esco"
)


OCCUPATIONS_FILE = ESCO_DIR / "occupations_en.csv"
SKILLS_FILE = ESCO_DIR / "skills_en.csv"
RELATIONS_FILE = ESCO_DIR / "occupationSkillRelations_en.csv"


# --------------------------------------------------
# LOAD ESCO DATA
# --------------------------------------------------

print("Loading ESCO datasets...")


occupations = pd.read_csv(
    OCCUPATIONS_FILE,
    low_memory=False
)

skills = pd.read_csv(
    SKILLS_FILE,
    low_memory=False
)

relations = pd.read_csv(
    RELATIONS_FILE,
    low_memory=False
)


# --------------------------------------------------
# BASIC INFORMATION
# --------------------------------------------------

print("\nESCO DATA LOADED SUCCESSFULLY")


print("\nOccupations shape:")
print(occupations.shape)


print("\nSkills shape:")
print(skills.shape)


print("\nOccupation-Skill Relations shape:")
print(relations.shape)


print("\nOccupations columns:")
print(
    occupations.columns.tolist()
)


print("\nSkills columns:")
print(
    skills.columns.tolist()
)


print("\nRelations columns:")
print(
    relations.columns.tolist()
)


# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

print("\nSample occupations:")
print(
    occupations.head(3)
)


print("\nSample skills:")
print(
    skills.head(3)
)


print("\nSample occupation-skill relations:")
print(
    relations.head(3)
)