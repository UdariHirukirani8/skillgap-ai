import ast
import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))


# ==================================================
# PROJECT IMPORTS
# ==================================================

from skill_matcher import (
    calculate_skill_match,
    normalize_skill
)

from career_discovery import discover_careers

from skill_impact import rank_skill_impacts


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="SkillGap AI API",
    description=(
        "AI-powered career intelligence, "
        "job recommendation, skill-gap analysis, "
        "career discovery, and skill impact simulation."
    ),
    version="2.1.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==================================================
# LOAD EXISTING JOB DATASET
# ==================================================

JOB_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "train-00000-of-00001.parquet"
)

df = pd.read_parquet(
    JOB_DATA_PATH
)


# ==================================================
# REQUEST MODELS
# ==================================================

class RecommendationRequest(BaseModel):
    skills: list[str]
    target_role: str = ""


class CareerDiscoveryRequest(BaseModel):
    skills: list[str]
    limit: int = 10


class SkillImpactRequest(BaseModel):
    skills: list[str]
    occupation: str
    limit: int = 5


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "SkillGap AI API is running",
        "version": "2.1.0"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "jobs_loaded": len(df)
    }


# ==================================================
# JOB RECOMMENDATION
# ==================================================

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


    # --------------------------------------------------
    # ORIGINAL JOB DATASET
    # --------------------------------------------------

    jobs = df[
        df["category"]
        == "INFORMATION-TECHNOLOGY"
    ].copy()


    # --------------------------------------------------
    # FILTER TARGET ROLE
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


    # --------------------------------------------------
    # CALCULATE JOB MATCH SCORES
    # --------------------------------------------------

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


        match_result = calculate_skill_match(
            user_skills,
            required_skills
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


    # --------------------------------------------------
    # SORT JOBS
    # --------------------------------------------------

    results = sorted(
        results,
        key=lambda item:
            item["match_score"],
        reverse=True
    )


    positive_results = [
        item
        for item in results
        if item["match_score"] > 0
    ]


    if positive_results:
        top_jobs = positive_results[:5]
    else:
        top_jobs = results[:5]


    # --------------------------------------------------
    # LEARN NEXT
    # --------------------------------------------------

    skill_frequency = {}


    for job in top_jobs:

        for skill in job[
            "missing_skills"
        ]:

            normalized_skill = (
                normalize_skill(
                    skill
                )
            )

            skill_frequency[
                normalized_skill
            ] = (
                skill_frequency.get(
                    normalized_skill,
                    0
                )
                + 1
            )


    learning_skills = sorted(
        skill_frequency.items(),
        key=lambda item:
            item[1],
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


    return {
        "mode":
            "job_recommendation",

        "target_role":
            request.target_role,

        "user_skills":
            user_skills,

        "top_jobs":
            top_jobs,

        "learn_next":
            learn_next
    }


# ==================================================
# UNIVERSAL CAREER DISCOVERY
# ==================================================

@app.post("/discover-careers")
def discover_career_options(
    request: CareerDiscoveryRequest
):

    limit = max(
        1,
        min(
            request.limit,
            25
        )
    )


    career_matches = discover_careers(
        request.skills,
        limit=limit
    )


    return {
        "mode":
            "career_discovery",

        "user_skills":
            request.skills,

        "total_results":
            len(
                career_matches
            ),

        "career_matches":
            career_matches
    }


# ==================================================
# SKILL IMPACT SIMULATOR
# ==================================================

@app.post("/skill-impact")
def skill_impact_analysis(
    request: SkillImpactRequest
):

    limit = max(
        1,
        min(
            request.limit,
            10
        )
    )


    result = rank_skill_impacts(
        request.skills,
        request.occupation,
        limit=limit
    )


    return result