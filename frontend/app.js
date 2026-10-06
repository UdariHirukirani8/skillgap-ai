let currentMode = "career";
let selectedCareers = [];

const API_BASE =
    "http://127.0.0.1:8000";


// ======================================================
// MODE
// ======================================================

function switchMode(mode) {

    currentMode = mode;

    const careerButton =
        document.getElementById(
            "careerModeBtn"
        );

    const jobButton =
        document.getElementById(
            "jobModeBtn"
        );

    const targetRoleGroup =
        document.getElementById(
            "targetRoleGroup"
        );

    const analyzeButton =
        document.getElementById(
            "analyzeButton"
        );

    const description =
        document.getElementById(
            "modeDescription"
        );


    if (mode === "career") {

        careerButton.classList.add("active");
        jobButton.classList.remove("active");

        targetRoleGroup.classList.add("hidden");

        analyzeButton.textContent =
            "Discover My Careers";

        description.textContent =
            "We'll compare your skills with ESCO occupations and discover suitable career paths.";

    } else {

        jobButton.classList.add("active");
        careerButton.classList.remove("active");

        targetRoleGroup.classList.remove("hidden");

        analyzeButton.textContent =
            "Find Matching Jobs";

        description.textContent =
            "Enter a target role and we'll analyze your job match and missing skills.";
    }

    clearCareerSelection();
    clearResults();
}


// ======================================================
// SKILLS
// ======================================================

function getSkills() {

    return document
        .getElementById("skills")
        .value
        .split(",")
        .map(
            skill => skill.trim()
        )
        .filter(
            skill => skill.length > 0
        );
}


// ======================================================
// ANALYZE
// ======================================================

async function analyzeSkills() {

    const skills = getSkills();

    if (skills.length === 0) {

        showError(
            "Please enter at least one skill."
        );

        return;
    }

    hideError();
    clearCareerSelection();
    clearResults();
    showLoading();

    try {

        if (currentMode === "career") {

            await discoverCareers(
                skills
            );

        } else {

            await matchJobs(
                skills
            );
        }

    } catch (error) {

        console.error(error);

        showError(
            "Unable to connect to SkillGap AI API."
        );

    } finally {

        hideLoading();
    }
}


// ======================================================
// DISCOVER CAREERS
// ======================================================

async function discoverCareers(skills) {

    const response =
        await fetch(
            `${API_BASE}/discover-careers`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills,
                    limit: 10
                })
            }
        );

    const data =
        await response.json();

    renderCareerResults(
        data
    );
}


// ======================================================
// RENDER CAREERS
// ======================================================

function renderCareerResults(data) {

    const section =
        document.getElementById(
            "careerResultsSection"
        );

    const container =
        document.getElementById(
            "careerResults"
        );

    const count =
        document.getElementById(
            "careerCount"
        );

    container.innerHTML = "";

    count.textContent =
        `${data.total_results} careers found`;


    (
        data.career_matches || []
    )
    .forEach(
        (career, index) => {

            const card =
                document.createElement(
                    "article"
                );

            card.className =
                "career-card";

            const safeOccupation =
                escapeHTML(
                    career.occupation
                );

            const matchedSkills = [
                ...(
                    career
                    .matched_essential_skills
                    || []
                ),

                ...(
                    career
                    .matched_optional_skills
                    || []
                )
            ];

            card.innerHTML = `

                <div class="card-top">

                    <div>

                        <span class="eyebrow">
                            MATCH #${index + 1}
                        </span>

                        <h3>
                            ${safeOccupation}
                        </h3>

                        <span
                            class="confidence ${
                                String(
                                    career.confidence
                                ).toLowerCase()
                            }"
                        >
                            ${escapeHTML(
                                career.confidence
                            )}
                            Confidence
                        </span>

                    </div>

                    <div class="fit-score">
                        ${career.career_fit_score}/100
                    </div>

                </div>


                <p class="description">
                    ${escapeHTML(
                        shortenText(
                            career.description,
                            220
                        )
                    )}
                </p>


                <div class="progress-row">

                    <div class="progress-label">

                        <span>
                            Essential skill coverage
                        </span>

                        <span>
                            ${career.essential_coverage}%
                        </span>

                    </div>

                    <div class="progress-track">

                        <div
                            class="progress-fill"
                            style="
                                width:
                                ${Math.min(
                                    career.essential_coverage,
                                    100
                                )}%;
                            "
                        ></div>

                    </div>

                </div>


                <div class="card-section">

                    <h4>
                        Matched Skills
                    </h4>

                    <div class="tag-list">

                        ${renderTags(
                            matchedSkills,
                            "match",
                            "No direct matches"
                        )}

                    </div>

                </div>


                <div class="card-section">

                    <h4>
                        Key Skill Gaps
                    </h4>

                    <div class="tag-list">

                        ${renderTags(
                            career.key_gaps,
                            "gap",
                            "No major gaps"
                        )}

                    </div>

                </div>


                <div class="explanation">

                    <strong>
                        Why recommended
                    </strong>

                    <br>

                    ${escapeHTML(
                        career.explanation
                    )}

                </div>


                <button
                    class="save-plan-button"
                    data-occupation="${safeOccupation}"
                    onclick="saveCareerPlanFromButton(this)"
                >
                    Save Career Plan
                </button>


                <button
                    class="compare-career-button"
                    data-occupation="${safeOccupation}"
                    onclick="toggleCareerComparison(this)"
                >
                    + Add to Compare
                </button>


                <button
                    class="impact-button"
                    data-occupation="${safeOccupation}"
                    data-index="${index}"
                    onclick="showSkillImpactFromButton(this)"
                >
                    See Skill Impact
                </button>


                <div
                    id="impact-${index}"
                    class="impact-panel hidden"
                ></div>


                <button
                    class="roadmap-button"
                    data-occupation="${safeOccupation}"
                    data-index="${index}"
                    onclick="showRoadmapFromButton(this)"
                >
                    Build My 90-Day Roadmap
                </button>


                <div
                    id="roadmap-${index}"
                    class="roadmap-panel hidden"
                ></div>
            `;

            container.appendChild(
                card
            );
        }
    );

    section.classList.remove(
        "hidden"
    );
}


// ======================================================
// SAVE PLAN
// ======================================================

async function saveCareerPlanFromButton(
    button
) {

    const occupation =
        button.dataset.occupation;

    const skills =
        getSkills();


    if (skills.length === 0) {

        showError(
            "Enter your skills before saving a career plan."
        );

        return;
    }


    const originalText =
        button.textContent;

    button.disabled = true;

    button.textContent =
        "Saving Plan...";


    try {

        const response =
            await fetch(
                `${API_BASE}/career-plans`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        skills,
                        occupation
                    })
                }
            );


        const data =
            await response.json();


        if (data.error) {

            throw new Error(
                data.error
            );
        }


        button.textContent =
            "✓ Career Plan Saved";

        button.classList.add(
            "saved"
        );


    } catch (error) {

        console.error(error);

        button.textContent =
            "Save Failed";

    } finally {

        button.disabled =
            false;

        setTimeout(
            () => {

                if (
                    !button.classList.contains(
                        "saved"
                    )
                ) {
                    button.textContent =
                        originalText;
                }

            },
            2000
        );
    }
}


// ======================================================
// DASHBOARD
// ======================================================

async function loadCareerDashboard() {

    clearCareerSelection();
    clearResults();
    hideError();

    const section =
        document.getElementById(
            "dashboardSection"
        );

    const plansContainer =
        document.getElementById(
            "dashboardPlans"
        );

    const summary =
        document.getElementById(
            "dashboardSummary"
        );


    section.classList.remove(
        "hidden"
    );

    plansContainer.innerHTML = `
        <div class="dashboard-loading">
            <div class="spinner"></div>
            <span>
                Loading saved career plans...
            </span>
        </div>
    `;


    try {

        const response =
            await fetch(
                `${API_BASE}/career-plans`
            );


        const data =
            await response.json();


        renderDashboard(
            data
        );


    } catch (error) {

        console.error(error);

        plansContainer.innerHTML = `
            <div class="error-box">
                Unable to load career dashboard.
            </div>
        `;
    }
}


function renderDashboard(data) {

    const plans =
        data.plans || [];

    const container =
        document.getElementById(
            "dashboardPlans"
        );

    const summary =
        document.getElementById(
            "dashboardSummary"
        );


    if (plans.length === 0) {

        summary.innerHTML = "";

        container.innerHTML = `
            <div class="empty-dashboard">

                <h3>
                    No saved career plans yet
                </h3>

                <p>
                    Discover careers and save one
                    to start tracking your progress.
                </p>

            </div>
        `;

        return;
    }


    const averageProgress =
        plans.reduce(
            (total, plan) =>
                total +
                (
                    plan
                    .progress_summary
                    ?.progress_percentage
                    || 0
                ),
            0
        )
        /
        plans.length;


    summary.innerHTML = `

        <div class="summary-card">

            <span>
                Saved Plans
            </span>

            <strong>
                ${plans.length}
            </strong>

        </div>


        <div class="summary-card">

            <span>
                Average Progress
            </span>

            <strong>
                ${averageProgress.toFixed(1)}%
            </strong>

        </div>


        <div class="summary-card">

            <span>
                Active Target
            </span>

            <strong>
                ${escapeHTML(
                    plans[0].occupation
                )}
            </strong>

        </div>
    `;


    container.innerHTML =
        "";


    plans.forEach(
        plan => {

            const card =
                document.createElement(
                    "article"
                );

            card.className =
                "dashboard-plan-card";


            const progress =
                plan.progress_summary
                || {
                    progress_percentage: 0,
                    completed_tasks: 0,
                    total_tasks: 0
                };


            card.innerHTML = `

                <div class="dashboard-plan-header">

                    <div>

                        <span class="eyebrow">
                            SAVED CAREER PLAN
                        </span>

                        <h3>
                            ${escapeHTML(
                                plan.occupation
                            )}
                        </h3>

                        <span
                            class="confidence ${
                                String(
                                    plan.confidence
                                ).toLowerCase()
                            }"
                        >
                            ${escapeHTML(
                                plan.confidence
                            )}
                            Confidence
                        </span>

                    </div>


                    <button
                        class="delete-plan-button"
                        onclick="deleteSavedPlan(
                            ${plan.id}
                        )"
                    >
                        Delete
                    </button>

                </div>


                <div class="dashboard-score-grid">

                    <div>

                        <span>
                            Current Fit
                        </span>

                        <strong>
                            ${plan.current_score}/100
                        </strong>

                    </div>


                    <div>

                        <span>
                            Projected Fit
                        </span>

                        <strong class="green-value">
                            ${plan.projected_score}/100
                        </strong>

                    </div>


                    <div>

                        <span>
                            Best Next Skill
                        </span>

                        <strong>
                            ${escapeHTML(
                                plan.best_next_skill
                                || "None"
                            )}
                        </strong>

                    </div>

                </div>


                <div class="dashboard-progress-area">

                    <div class="dashboard-progress-label">

                        <span>
                            Roadmap Progress
                        </span>

                        <strong>
                            ${progress.progress_percentage}%
                        </strong>

                    </div>


                    <div class="dashboard-progress-track">

                        <div
                            class="dashboard-progress-fill"
                            style="
                                width:
                                ${Math.min(
                                    progress.progress_percentage,
                                    100
                                )}%;
                            "
                        ></div>

                    </div>


                    <small>

                        ${progress.completed_tasks}
                        of
                        ${progress.total_tasks}
                        tasks completed

                    </small>

                </div>


                <div class="dashboard-priority">

                    <h4>
                        Priority Skills
                    </h4>

                    <div class="tag-list">

                        ${renderTags(
                            (
                                plan.skill_priorities
                                || []
                            )
                            .map(
                                item => item.skill
                            ),
                            "match",
                            "No priority skills"
                        )}

                    </div>

                </div>


                <div class="dashboard-roadmap">

                    ${renderDashboardStage(
                        plan,
                        "30_days",
                        "30 Days"
                    )}

                    ${renderDashboardStage(
                        plan,
                        "60_days",
                        "60 Days"
                    )}

                    ${renderDashboardStage(
                        plan,
                        "90_days",
                        "90 Days"
                    )}

                </div>
            `;


            container.appendChild(
                card
            );
        }
    );
}


// ======================================================
// DASHBOARD ROADMAP
// ======================================================

function renderDashboardStage(
    plan,
    stageKey,
    title
) {

    const tasks =
        plan.progress?.[
            stageKey
        ]
        || [];


    const tasksHtml =
        tasks
        .map(
            (
                task,
                index
            ) => `

                <label class="dashboard-task">

                    <input
                        type="checkbox"

                        ${
                            task.completed
                            ? "checked"
                            : ""
                        }

                        onchange="
                            updatePlanTask(
                                ${plan.id},
                                '${stageKey}',
                                ${index},
                                this.checked
                            )
                        "
                    >

                    <span
                        class="${
                            task.completed
                            ? "completed-task"
                            : ""
                        }"
                    >
                        ${escapeHTML(
                            task.title
                        )}
                    </span>

                </label>
            `
        )
        .join("");


    return `

        <div class="dashboard-stage">

            <div class="dashboard-stage-title">
                ${title}
            </div>

            <div class="dashboard-task-list">

                ${
                    tasksHtml
                    ||
                    "<p>No tasks</p>"
                }

            </div>

        </div>
    `;
}


// ======================================================
// UPDATE PROGRESS
// ======================================================

async function updatePlanTask(
    planId,
    stage,
    taskIndex,
    completed
) {

    try {

        const response =
            await fetch(
                `${API_BASE}/career-plans/${planId}/progress`,
                {
                    method:
                        "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            stage,
                            task_index:
                                taskIndex,
                            completed
                        })
                }
            );


        const data =
            await response.json();


        if (data.error) {

            throw new Error(
                data.error
            );
        }


        await loadCareerDashboard();


    } catch (error) {

        console.error(error);

        showError(
            "Unable to update progress."
        );
    }
}


// ======================================================
// DELETE PLAN
// ======================================================

async function deleteSavedPlan(
    planId
) {

    const confirmed =
        window.confirm(
            "Delete this saved career plan?"
        );


    if (!confirmed) {
        return;
    }


    try {

        await fetch(
            `${API_BASE}/career-plans/${planId}`,
            {
                method:
                    "DELETE"
            }
        );


        await loadCareerDashboard();


    } catch (error) {

        console.error(error);

        showError(
            "Unable to delete career plan."
        );
    }
}


// ======================================================
// CAREER COMPARISON
// ======================================================

function toggleCareerComparison(
    button
) {

    const occupation =
        button.dataset.occupation;


    if (
        selectedCareers.includes(
            occupation
        )
    ) {

        selectedCareers =
            selectedCareers.filter(
                item =>
                    item !== occupation
            );


        button.classList.remove(
            "selected"
        );


        button.textContent =
            "+ Add to Compare";

    } else {

        if (
            selectedCareers.length >= 3
        ) {

            showError(
                "You can compare a maximum of 3 careers."
            );

            return;
        }


        selectedCareers.push(
            occupation
        );


        button.classList.add(
            "selected"
        );


        button.textContent =
            "✓ Selected for Compare";
    }


    updateCompareBar();
}


function updateCompareBar() {

    const bar =
        document.getElementById(
            "compareBar"
        );

    const count =
        document.getElementById(
            "compareCount"
        );

    const button =
        document.getElementById(
            "compareSelectedButton"
        );


    count.textContent =
        `${selectedCareers.length} career(s) selected`;


    button.disabled =
        selectedCareers.length < 2;


    bar.classList.toggle(
        "hidden",
        selectedCareers.length === 0
    );
}


function clearCareerSelection() {

    selectedCareers = [];


    document
        .querySelectorAll(
            ".compare-career-button"
        )
        .forEach(
            button => {

                button.classList.remove(
                    "selected"
                );

                button.textContent =
                    "+ Add to Compare";
            }
        );


    updateCompareBar();
}


async function compareSelectedCareers() {

    if (
        selectedCareers.length < 2
    ) {

        return;
    }


    const response =
        await fetch(
            `${API_BASE}/compare-careers`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills:
                        getSkills(),

                    occupations:
                        selectedCareers
                })
            }
        );


    const data =
        await response.json();


    renderCareerComparison(
        data
    );
}


function renderCareerComparison(data) {

    const section =
        document.getElementById(
            "comparisonSection"
        );

    const recommendation =
        document.getElementById(
            "comparisonRecommendation"
        );

    const container =
        document.getElementById(
            "comparisonResults"
        );


    recommendation.innerHTML = `

        <span class="eyebrow">
            BEST OVERALL MATCH
        </span>

        <h3>
            ${escapeHTML(
                data.recommended_career
            )}
        </h3>

        <p>
            ${escapeHTML(
                data.recommendation_reason
            )}
        </p>
    `;


    container.innerHTML =
        "";


    (
        data.comparisons || []
    )
    .forEach(
        career => {

            const card =
                document.createElement(
                    "article"
                );


            card.className =
                "comparison-card";


            if (
                career.occupation
                ===
                data.recommended_career
            ) {

                card.classList.add(
                    "winner"
                );
            }


            card.innerHTML = `

                <div class="comparison-rank">
                    #${career.rank}
                </div>

                <h3>
                    ${escapeHTML(
                        career.occupation
                    )}
                </h3>

                <p class="comparison-description">
                    ${escapeHTML(
                        shortenText(
                            career.description,
                            150
                        )
                    )}
                </p>

                <div class="comparison-score">

                    <span>
                        Current Fit
                    </span>

                    <strong>
                        ${career.career_fit_score}/100
                    </strong>

                </div>

                <div class="comparison-metric">

                    <span>
                        Confidence
                    </span>

                    <strong>
                        ${escapeHTML(
                            career.confidence
                        )}
                    </strong>

                </div>

                <div class="comparison-metric">

                    <span>
                        Essential Coverage
                    </span>

                    <strong>
                        ${career.essential_coverage}%
                    </strong>

                </div>

                <div class="comparison-metric">

                    <span>
                        Best Next Skill
                    </span>

                    <strong>
                        ${escapeHTML(
                            career.best_next_skill
                            || "None"
                        )}
                    </strong>

                </div>

                <div class="projected-score-box">

                    <span>
                        Projected Score
                    </span>

                    <strong>
                        ${career.projected_score}/100
                    </strong>

                </div>
            `;


            container.appendChild(
                card
            );
        }
    );


    section.classList.remove(
        "hidden"
    );


    section.scrollIntoView({
        behavior:
            "smooth"
    });
}


// ======================================================
// SKILL IMPACT
// ======================================================

function showSkillImpactFromButton(
    button
) {

    showSkillImpact(
        button.dataset.occupation,
        button.dataset.index,
        button
    );
}


async function showSkillImpact(
    occupation,
    index,
    button
) {

    const panel =
        document.getElementById(
            `impact-${index}`
        );


    if (
        panel.dataset.loaded === "true"
        &&
        !panel.classList.contains(
            "hidden"
        )
    ) {

        panel.classList.add(
            "hidden"
        );

        button.textContent =
            "See Skill Impact";

        return;
    }


    panel.classList.remove(
        "hidden"
    );


    panel.innerHTML = `
        <div class="impact-loading">
            <div class="mini-spinner"></div>
            Calculating skill impact...
        </div>
    `;


    const response =
        await fetch(
            `${API_BASE}/skill-impact`,
            {
                method:
                    "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        skills:
                            getSkills(),

                        occupation,

                        limit:
                            5
                    })
            }
        );


    const data =
        await response.json();


    let html = `

        <div class="impact-header">

            <div>

                <span class="eyebrow">
                    SKILL IMPACT SIMULATOR
                </span>

                <h4>
                    What should you learn next?
                </h4>

            </div>

            <div class="current-impact-score">

                <span>
                    Current Fit
                </span>

                <strong>
                    ${data.current_score}/100
                </strong>

            </div>

        </div>

        <div class="impact-list">
    `;


    (
        data.best_skills_to_learn
        || []
    )
    .forEach(
        (item, i) => {

            html += `

                <div class="impact-item">

                    <div class="impact-rank">
                        ${i + 1}
                    </div>

                    <div class="impact-skill-info">

                        <strong>
                            ${escapeHTML(
                                item.skill
                            )}
                        </strong>

                        <div class="impact-score-change">
                            ${item.current_score}
                            →
                            ${item.new_score}
                        </div>

                    </div>

                    <div class="impact-gain">
                        +${item.improvement}
                    </div>

                </div>
            `;
        }
    );


    html += `
        </div>
    `;


    panel.innerHTML =
        html;


    panel.dataset.loaded =
        "true";


    button.textContent =
        "Hide Skill Impact";
}


// ======================================================
// ROADMAP
// ======================================================

function showRoadmapFromButton(
    button
) {

    showCareerRoadmap(
        button.dataset.occupation,
        button.dataset.index,
        button
    );
}


async function showCareerRoadmap(
    occupation,
    index,
    button
) {

    const panel =
        document.getElementById(
            `roadmap-${index}`
        );


    if (
        panel.dataset.loaded === "true"
        &&
        !panel.classList.contains(
            "hidden"
        )
    ) {

        panel.classList.add(
            "hidden"
        );

        button.textContent =
            "Build My 90-Day Roadmap";

        return;
    }


    panel.classList.remove(
        "hidden"
    );


    const response =
        await fetch(
            `${API_BASE}/career-roadmap`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills:
                        getSkills(),

                    occupation,

                    limit:
                        6
                })
            }
        );


    const data =
        await response.json();


    panel.innerHTML = `

        <div class="roadmap-header">

            <span class="eyebrow">
                PERSONALIZED ROADMAP
            </span>

            <h4>
                30 / 60 / 90 Day Plan
            </h4>

        </div>

        ${renderRoadmapStage(
            "30 Days",
            data.roadmap?.["30_days"]
            || []
        )}

        ${renderRoadmapStage(
            "60 Days",
            data.roadmap?.["60_days"]
            || []
        )}

        ${renderRoadmapStage(
            "90 Days",
            data.roadmap?.["90_days"]
            || []
        )}
    `;


    panel.dataset.loaded =
        "true";


    button.textContent =
        "Hide 90-Day Roadmap";
}


function renderRoadmapStage(
    title,
    tasks
) {

    return `

        <div class="roadmap-stage">

            <div class="roadmap-stage-badge">
                ${title}
            </div>

            <div class="roadmap-stage-content">

                <ul>

                    ${tasks
                        .map(
                            task => `
                                <li>
                                    <span class="roadmap-task-dot"></span>

                                    <div>
                                        ${escapeHTML(
                                            task.title
                                        )}
                                    </div>
                                </li>
                            `
                        )
                        .join("")
                    }

                </ul>

            </div>

        </div>
    `;
}


// ======================================================
// JOBS
// ======================================================

async function matchJobs(skills) {

    const targetRole =
        document
        .getElementById(
            "targetRole"
        )
        .value
        .trim();


    const response =
        await fetch(
            `${API_BASE}/recommend`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills,
                    target_role:
                        targetRole
                })
            }
        );


    const data =
        await response.json();


    renderJobResults(
        data
    );
}


function renderJobResults(data) {

    const section =
        document.getElementById(
            "jobResultsSection"
        );

    const jobsContainer =
        document.getElementById(
            "jobResults"
        );

    const learningContainer =
        document.getElementById(
            "learningSkills"
        );


    jobsContainer.innerHTML =
        "";


    learningContainer.innerHTML =
        "";


    (
        data.top_jobs || []
    )
    .forEach(
        (job, index) => {

            const card =
                document.createElement(
                    "article"
                );

            card.className =
                "job-card";

            card.innerHTML = `

                <span class="eyebrow">
                    JOB MATCH #${index + 1}
                </span>

                <h3>
                    ${escapeHTML(
                        job.job_title
                    )}
                </h3>

                <div class="job-score">
                    ${job.match_score}%
                </div>

                <div class="card-section">

                    <h4>
                        Matched Skills
                    </h4>

                    <div class="tag-list">

                        ${renderTags(
                            job.matched_skills,
                            "match",
                            "No direct matches"
                        )}

                    </div>

                </div>
            `;

            jobsContainer.appendChild(
                card
            );
        }
    );


    (
        data.learn_next || []
    )
    .forEach(
        item => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "learning-card";

            card.innerHTML = `

                <strong>
                    ${escapeHTML(
                        item.skill
                    )}
                </strong>

                <span>
                    Required by
                    ${item.frequency}
                    top job(s)
                </span>
            `;

            learningContainer.appendChild(
                card
            );
        }
    );


    section.classList.remove(
        "hidden"
    );
}


// ======================================================
// HELPERS
// ======================================================

function renderTags(
    skills,
    className,
    emptyText
) {

    if (
        !skills ||
        skills.length === 0
    ) {

        return `
            <span class="tag">
                ${escapeHTML(
                    emptyText
                )}
            </span>
        `;
    }


    return skills
        .slice(
            0,
            8
        )
        .map(
            skill => `
                <span
                    class="tag ${className}"
                >
                    ${escapeHTML(
                        skill
                    )}
                </span>
            `
        )
        .join("");
}


function shortenText(
    text,
    maxLength
) {

    if (!text) {
        return "No description available.";
    }

    return (
        text.length <= maxLength
        ? text
        : text.slice(
            0,
            maxLength
        ) + "..."
    );
}


function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showLoading() {

    document
        .getElementById(
            "loading"
        )
        .classList
        .remove(
            "hidden"
        );
}


function hideLoading() {

    document
        .getElementById(
            "loading"
        )
        .classList
        .add(
            "hidden"
        );
}


function showError(message) {

    const box =
        document.getElementById(
            "errorBox"
        );

    box.textContent =
        message;

    box.classList.remove(
        "hidden"
    );
}


function hideError() {

    document
        .getElementById(
            "errorBox"
        )
        .classList
        .add(
            "hidden"
        );
}


function clearResults() {

    [
        "careerResultsSection",
        "comparisonSection",
        "jobResultsSection",
        "dashboardSection"
    ]
    .forEach(
        id => {

            document
                .getElementById(id)
                .classList
                .add(
                    "hidden"
                );
        }
    );
}