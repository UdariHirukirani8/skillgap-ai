import ast
import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# --------------------------------------------------
# Allow backend to import files from src/
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))


from skill_matcher import (
    calculate_skill_match,
    normalize_skill
)


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="SkillGap AI API",
    description=(
        "AI-powered job skill matching and "
        "career recommendation API."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# LOAD DATASET ONCE
# --------------------------------------------------

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "train-00000-of-00001.parquet"
)

df = pd.read_parquet(DATA_PATH)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class RecommendationRequest(BaseModel):
    skills: list[str]
    target_role: str = ""


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "SkillGap AI API is running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "jobs_loaded": len(df)
    }


# --------------------------------------------------
# RECOMMENDATION ENDPOINT
# --------------------------------------------------

@app.post("/recommend")
def recommend_jobs(
    request: RecommendationRequest
):

    user_skills = request.skills

    target_role = (
        request.target_role
        .strip()
        .lower()
    )


    # ----------------------------------------------
    # FILTER IT JOBS
    # ----------------------------------------------

    jobs = df[
        df["category"]
        == "INFORMATION-TECHNOLOGY"
    ].copy()


    # ----------------------------------------------
    # FILTER BY TARGET ROLE
    # ----------------------------------------------

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


    # ----------------------------------------------
    # SCORE JOBS
    # ----------------------------------------------

    results = []

    for _, job in jobs.iterrows():

        required_skills = job[
            "job_skill_set"
        ]


        if isinstance(
            required_skills,
            str
        ):

            try:
                required_skills = (
                    ast.literal_eval(
                        required_skills
                    )
                )

            except (
                ValueError,
                SyntaxError
            ):
                continue


        if not isinstance(
            required_skills,
            (list, tuple, set)
        ):
            continue


        match_result = (
            calculate_skill_match(
                user_skills,
                required_skills
            )
        )


        results.append({
            "job_title":
                job["job_title"],

            "match_score":
                match_result[
                    "match_score"
                ],

            "matched_skills":
                match_result[
                    "matched_skills"
                ],

            "missing_skills":
                match_result[
                    "missing_skills"
                ]
        })


    # ----------------------------------------------
    # SORT RESULTS
    # ----------------------------------------------

    results = sorted(
        results,
        key=lambda x: x[
            "match_score"
        ],
        reverse=True
    )


    positive_results = [
        result
        for result in results
        if result["match_score"] > 0
    ]


    if positive_results:
        top_jobs = positive_results[:5]
    else:
        top_jobs = results[:5]


    # ----------------------------------------------
    # LEARNING RECOMMENDATIONS
    # ----------------------------------------------

    skill_frequency = {}

    for job in top_jobs:

        for skill in job[
            "missing_skills"
        ]:

            normalized = (
                normalize_skill(skill)
            )

            skill_frequency[
                normalized
            ] = (
                skill_frequency.get(
                    normalized,
                    0
                )
                + 1
            )


    learning_skills = sorted(
        skill_frequency.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]


    learn_next = [
        {
            "skill": skill,
            "frequency": frequency
        }
        for skill, frequency
        in learning_skills
    ]


    # ----------------------------------------------
    # RETURN JSON
    # ----------------------------------------------

    return {
        "target_role":
            request.target_role,

        "user_skills":
            user_skills,

        "top_jobs":
            top_jobs,

        "learn_next":
            learn_next
    }