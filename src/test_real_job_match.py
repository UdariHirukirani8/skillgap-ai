import pandas as pd
import ast

from skill_matcher import calculate_skill_match


# Load job dataset
file_path = "data/raw/train-00000-of-00001.parquet"

df = pd.read_parquet(file_path)


# Select one IT job
it_jobs = df[df["category"] == "INFORMATION-TECHNOLOGY"]

job = it_jobs.iloc[0]


# Convert stored skill list into Python list
required_skills = job["job_skill_set"]

if isinstance(required_skills, str):
    required_skills = ast.literal_eval(required_skills)


# Example user skills
user_skills = [
    "Python",
    "SQL",
    "Excel",
    "Git",
    "HTML",
    "CSS"
]


# Calculate match
result = calculate_skill_match(
    user_skills,
    required_skills
)


print("\nJOB TITLE:")
print(job["job_title"])

print("\nREQUIRED SKILLS:")
print(required_skills)

print("\nYOUR SKILLS:")
print(user_skills)

print("\nMATCH SCORE:")
print(result["match_score"], "%")

print("\nMATCHED SKILLS:")
print(result["matched_skills"])

print("\nMISSING SKILLS:")
print(result["missing_skills"])