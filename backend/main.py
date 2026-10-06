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

if str(SRC_PATH) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_PATH)
    )


# ==================================================
# PROJECT IMPORTS
# ==================================================

from skill_matcher import (
    calculate_skill_match,
    normalize_skill
)

from career_discovery import discover_careers
from skill_impact import rank_skill_impacts
from career_roadmap import build_career_roadmap
from career_compare import compare_careers

from career_plan import (
    save_career_plan,
    get_saved_plans,
    get_saved_plan,
    update_task_progress,
    calculate_plan_progress,
    delete_career_plan
)


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="SkillGap AI API",
    description=(
        "AI-powered career intelligence platform for "
        "job matching, career discovery, skill-gap analysis, "
        "skill impact simulation, personalized career roadmaps, "
        "career comparison, and saved career plans."
    ),
    version="2.4.0"
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
# LOAD JOB DATASET
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


class CareerRoadmapRequest(BaseModel):
    skills: list[str]
    occupation: str
    limit: int = 6


class CareerCompareRequest(BaseModel):
    skills: list[str]
    occupations: list[str]


class SaveCareerPlanRequest(BaseModel):
    skills: list[str]
    occupation: str


class UpdateProgressRequest(BaseModel):
    stage: str
    task_index: int
    completed: bool


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message":
            "SkillGap AI API is running",

        "version":
            "2.4.0"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status":
            "healthy",

        "jobs_loaded":
            len(df)
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

    jobs = df[
        df["category"]
        == "INFORMATION-TECHNOLOGY"
    ].copy()


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

        top_jobs = (
            positive_results[:5]
        )

    else:

        top_jobs = (
            results[:5]
        )


    # ------------------------------------------
    # LEARN NEXT
    # ------------------------------------------

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
            "skill":
                skill,

            "frequency":
                frequency
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
# SKILL IMPACT
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


    return rank_skill_impacts(
        request.skills,
        request.occupation,
        limit=limit
    )


# ==================================================
# CAREER ROADMAP
# ==================================================

@app.post("/career-roadmap")
def career_roadmap_analysis(
    request: CareerRoadmapRequest
):

    limit = max(
        1,
        min(
            request.limit,
            10
        )
    )


    return build_career_roadmap(
        request.skills,
        request.occupation,
        limit=limit
    )


# ==================================================
# CAREER COMPARISON
# ==================================================

@app.post("/compare-careers")
def compare_career_options(
    request: CareerCompareRequest
):

    if len(
        request.occupations
    ) < 2:

        return {
            "error":
                "Please provide at least two careers to compare."
        }


    if len(
        request.occupations
    ) > 5:

        return {
            "error":
                "You can compare a maximum of five careers at once."
        }


    return compare_careers(
        request.skills,
        request.occupations
    )


# ==================================================
# SAVE CAREER PLAN
# ==================================================

@app.post("/career-plans")
def create_career_plan(
    request: SaveCareerPlanRequest
):

    return save_career_plan(
        request.skills,
        request.occupation
    )


# ==================================================
# GET ALL SAVED CAREER PLANS
# ==================================================

@app.get("/career-plans")
def list_career_plans():

    plans = get_saved_plans()

    results = []


    for plan in plans:

        progress_summary = (
            calculate_plan_progress(
                plan
            )
        )


        results.append({
            **plan,

            "progress_summary":
                progress_summary
        })


    return {
        "total_plans":
            len(results),

        "plans":
            results
    }


# ==================================================
# GET ONE SAVED CAREER PLAN
# ==================================================

@app.get("/career-plans/{plan_id}")
def get_career_plan(
    plan_id: int
):

    plan = get_saved_plan(
        plan_id
    )


    if "error" in plan:

        return plan


    plan[
        "progress_summary"
    ] = (
        calculate_plan_progress(
            plan
        )
    )


    return plan


# ==================================================
# UPDATE ROADMAP PROGRESS
# ==================================================

@app.patch(
    "/career-plans/{plan_id}/progress"
)
def update_career_plan_progress(
    plan_id: int,
    request: UpdateProgressRequest
):

    plan = update_task_progress(
        plan_id,
        request.stage,
        request.task_index,
        request.completed
    )


    if "error" in plan:

        return plan


    plan[
        "progress_summary"
    ] = (
        calculate_plan_progress(
            plan
        )
    )


    return plan


# ==================================================
# DELETE SAVED CAREER PLAN
# ==================================================

@app.delete("/career-plans/{plan_id}")
def remove_career_plan(
    plan_id: int
):

    return delete_career_plan(
        plan_id
    )