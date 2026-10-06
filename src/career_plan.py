import json
import sqlite3
from pathlib import Path
from datetime import datetime

from career_roadmap import build_career_roadmap
from skill_impact import rank_skill_impacts


# ==================================================
# DATABASE PATH
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "skillgap.db"
)

DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


# ==================================================
# CREATE TABLE
# ==================================================

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS career_plans (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            occupation TEXT NOT NULL,

            user_skills TEXT NOT NULL,

            current_score REAL NOT NULL,

            confidence TEXT,

            best_next_skill TEXT,

            projected_score REAL,

            skill_priorities TEXT,

            roadmap TEXT,

            progress TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# ==================================================
# BUILD PLAN
# ==================================================

def build_saved_career_plan(
    user_skills,
    occupation
):

    roadmap_result = (
        build_career_roadmap(
            user_skills,
            occupation,
            limit=6
        )
    )


    if "error" in roadmap_result:

        return roadmap_result


    impact_result = (
        rank_skill_impacts(
            user_skills,
            occupation,
            limit=6
        )
    )


    if "error" in impact_result:

        return impact_result


    priority_skills = (
        impact_result.get(
            "best_skills_to_learn",
            []
        )
    )


    best_next_skill = None

    projected_score = (
        roadmap_result.get(
            "current_score",
            0
        )
    )


    if priority_skills:

        best_next_skill = (
            priority_skills[0]
            .get(
                "skill"
            )
        )

        projected_score = (
            priority_skills[0]
            .get(
                "new_score",
                projected_score
            )
        )


    roadmap = (
        roadmap_result.get(
            "roadmap",
            {}
        )
    )


    # ------------------------------------------
    # INITIAL PROGRESS STATE
    # ------------------------------------------

    progress = {
        "30_days": [],
        "60_days": [],
        "90_days": []
    }


    for stage in progress.keys():

        tasks = roadmap.get(
            stage,
            []
        )

        for index, task in enumerate(
            tasks
        ):

            progress[
                stage
            ].append({
                "task_index":
                    index,

                "title":
                    task.get(
                        "title",
                        ""
                    ),

                "completed":
                    False
            })


    return {
        "occupation":
            roadmap_result[
                "occupation"
            ],

        "user_skills":
            user_skills,

        "current_score":
            roadmap_result[
                "current_score"
            ],

        "confidence":
            roadmap_result[
                "current_confidence"
            ],

        "best_next_skill":
            best_next_skill,

        "projected_score":
            projected_score,

        "skill_priorities":
            priority_skills,

        "roadmap":
            roadmap,

        "progress":
            progress
    }


# ==================================================
# SAVE PLAN
# ==================================================

def save_career_plan(
    user_skills,
    occupation
):

    create_tables()


    plan = build_saved_career_plan(
        user_skills,
        occupation
    )


    if "error" in plan:

        return plan


    now = datetime.now().isoformat()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO career_plans (

            occupation,

            user_skills,

            current_score,

            confidence,

            best_next_skill,

            projected_score,

            skill_priorities,

            roadmap,

            progress,

            created_at,

            updated_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (

            plan[
                "occupation"
            ],

            json.dumps(
                plan[
                    "user_skills"
                ]
            ),

            plan[
                "current_score"
            ],

            plan[
                "confidence"
            ],

            plan[
                "best_next_skill"
            ],

            plan[
                "projected_score"
            ],

            json.dumps(
                plan[
                    "skill_priorities"
                ]
            ),

            json.dumps(
                plan[
                    "roadmap"
                ]
            ),

            json.dumps(
                plan[
                    "progress"
                ]
            ),

            now,

            now
        )
    )


    plan_id = (
        cursor.lastrowid
    )


    connection.commit()

    connection.close()


    plan["id"] = (
        plan_id
    )

    plan["created_at"] = (
        now
    )


    return plan


# ==================================================
# CONVERT DATABASE ROW
# ==================================================

def row_to_plan(
    row
):

    return {
        "id":
            row[
                "id"
            ],

        "occupation":
            row[
                "occupation"
            ],

        "user_skills":
            json.loads(
                row[
                    "user_skills"
                ]
            ),

        "current_score":
            row[
                "current_score"
            ],

        "confidence":
            row[
                "confidence"
            ],

        "best_next_skill":
            row[
                "best_next_skill"
            ],

        "projected_score":
            row[
                "projected_score"
            ],

        "skill_priorities":
            json.loads(
                row[
                    "skill_priorities"
                ]
            ),

        "roadmap":
            json.loads(
                row[
                    "roadmap"
                ]
            ),

        "progress":
            json.loads(
                row[
                    "progress"
                ]
            ),

        "created_at":
            row[
                "created_at"
            ],

        "updated_at":
            row[
                "updated_at"
            ]
    }


# ==================================================
# GET ALL SAVED PLANS
# ==================================================

def get_saved_plans():

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM career_plans
        ORDER BY updated_at DESC
        """
    )


    rows = cursor.fetchall()

    connection.close()


    return [
        row_to_plan(
            row
        )
        for row in rows
    ]


# ==================================================
# GET ONE PLAN
# ==================================================

def get_saved_plan(
    plan_id
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM career_plans
        WHERE id = ?
        """,
        (
            plan_id,
        )
    )


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return {
            "error":
                "Career plan not found."
        }


    return row_to_plan(
        row
    )


# ==================================================
# UPDATE TASK PROGRESS
# ==================================================

def update_task_progress(
    plan_id,
    stage,
    task_index,
    completed
):

    plan = get_saved_plan(
        plan_id
    )


    if "error" in plan:

        return plan


    valid_stages = {
        "30_days",
        "60_days",
        "90_days"
    }


    if stage not in valid_stages:

        return {
            "error":
                "Invalid roadmap stage."
        }


    stage_tasks = (
        plan[
            "progress"
        ].get(
            stage,
            []
        )
    )


    if (
        task_index < 0
        or
        task_index >= len(
            stage_tasks
        )
    ):

        return {
            "error":
                "Invalid task index."
        }


    stage_tasks[
        task_index
    ][
        "completed"
    ] = bool(
        completed
    )


    now = datetime.now().isoformat()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE career_plans

        SET progress = ?,
            updated_at = ?

        WHERE id = ?
        """,

        (
            json.dumps(
                plan[
                    "progress"
                ]
            ),

            now,

            plan_id
        )
    )


    connection.commit()

    connection.close()


    return get_saved_plan(
        plan_id
    )


# ==================================================
# CALCULATE PROGRESS %
# ==================================================

def calculate_plan_progress(
    plan
):

    total_tasks = 0

    completed_tasks = 0


    for stage_tasks in (
        plan[
            "progress"
        ].values()
    ):

        for task in stage_tasks:

            total_tasks += 1

            if task.get(
                "completed",
                False
            ):

                completed_tasks += 1


    if total_tasks == 0:

        percentage = 0

    else:

        percentage = (
            completed_tasks
            /
            total_tasks
        ) * 100


    return {
        "completed_tasks":
            completed_tasks,

        "total_tasks":
            total_tasks,

        "progress_percentage":
            round(
                percentage,
                2
            )
    }


# ==================================================
# DELETE PLAN
# ==================================================

def delete_career_plan(
    plan_id
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM career_plans
        WHERE id = ?
        """,
        (
            plan_id,
        )
    )


    deleted = (
        cursor.rowcount
    )


    connection.commit()

    connection.close()


    if deleted == 0:

        return {
            "error":
                "Career plan not found."
        }


    return {
        "message":
            "Career plan deleted successfully.",

        "id":
            plan_id
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    test_skills = [
        "Python",
        "SQL",
        "Statistics",
        "Data Analysis",
        "Communication",
        "Problem Solving"
    ]


    print("\n")
    print("=" * 70)

    print(
        "SKILLGAP AI - SAVED CAREER PLAN"
    )

    print("=" * 70)


    saved_plan = save_career_plan(
        test_skills,
        "database designer"
    )


    if "error" in saved_plan:

        print(
            saved_plan[
                "error"
            ]
        )

    else:

        print(
            "\nSaved Plan ID:",
            saved_plan[
                "id"
            ]
        )


        print(
            "Career:",
            saved_plan[
                "occupation"
            ]
        )


        print(
            "Current Score:",
            saved_plan[
                "current_score"
            ]
        )


        print(
            "Best Next Skill:",
            saved_plan[
                "best_next_skill"
            ]
        )


        print(
            "Projected Score:",
            saved_plan[
                "projected_score"
            ]
        )


        progress = (
            calculate_plan_progress(
                saved_plan
            )
        )


        print(
            "\nProgress:",
            progress
        )


        print(
            "\nTotal Saved Plans:",
            len(
                get_saved_plans()
            )
        )


    print("\n")
    print("=" * 70)