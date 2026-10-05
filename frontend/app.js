let currentMode = "career";


// ======================================================
// SWITCH MODE
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

    clearResults();
}


// ======================================================
// GET USER SKILLS
// ======================================================

function getSkills() {

    const skillsText =
        document.getElementById(
            "skills"
        ).value;

    return skillsText
        .split(",")
        .map(
            skill =>
                skill.trim()
        )
        .filter(
            skill =>
                skill.length > 0
        );
}


// ======================================================
// MAIN ANALYZE BUTTON
// ======================================================

async function analyzeSkills() {

    const skills =
        getSkills();

    if (skills.length === 0) {

        showError(
            "Please enter at least one skill."
        );

        return;
    }

    hideError();
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
            "Unable to connect to SkillGap AI API. Make sure the FastAPI backend is running."
        );

    } finally {

        hideLoading();
    }
}


// ======================================================
// CAREER DISCOVERY API
// ======================================================

async function discoverCareers(
    skills
) {

    const response =
        await fetch(
            "http://127.0.0.1:8000/discover-careers",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills: skills,
                    limit: 10
                })
            }
        );

    if (!response.ok) {

        throw new Error(
            "Career discovery request failed."
        );
    }

    const data =
        await response.json();

    renderCareerResults(
        data
    );
}


// ======================================================
// JOB MATCH API
// ======================================================

async function matchJobs(
    skills
) {

    const targetRole =
        document.getElementById(
            "targetRole"
        )
        .value
        .trim();

    const response =
        await fetch(
            "http://127.0.0.1:8000/recommend",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    skills: skills,
                    target_role:
                        targetRole
                })
            }
        );

    if (!response.ok) {

        throw new Error(
            "Job recommendation request failed."
        );
    }

    const data =
        await response.json();

    renderJobResults(
        data
    );
}


// ======================================================
// RENDER CAREER RESULTS
// ======================================================

function renderCareerResults(
    data
) {

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

    if (
        !data.career_matches ||
        data.career_matches.length === 0
    ) {

        container.innerHTML = `
            <div class="career-card">
                No suitable careers were found.
            </div>
        `;

        section.classList.remove(
            "hidden"
        );

        return;
    }

    data.career_matches.forEach(
        (career, index) => {

            const card =
                document.createElement(
                    "article"
                );

            card.className =
                "career-card";

            const confidenceClass =
                String(
                    career.confidence
                )
                .toLowerCase();

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

            const safeOccupation =
                escapeHTML(
                    career.occupation
                );

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
                            class="confidence ${confidenceClass}"
                        >
                            ${escapeHTML(
                                career.confidence
                            )}
                            Confidence
                        </span>

                    </div>

                    <div class="fit-score">
                        ${
                            career
                            .career_fit_score
                        }/100
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
                            ${
                                career
                                .essential_coverage
                            }%
                        </span>

                    </div>

                    <div class="progress-track">

                        <div
                            class="progress-fill"
                            style="
                                width:
                                ${
                                    Math.min(
                                        career
                                        .essential_coverage,
                                        100
                                    )
                                }%;
                            "
                        ></div>

                    </div>

                </div>


                <div class="card-section">

                    <h4>
                        Matched Skills
                    </h4>

                    <div class="tag-list">
                        ${
                            renderTags(
                                matchedSkills,
                                "match",
                                "No direct skill matches."
                            )
                        }
                    </div>

                </div>


                <div class="card-section">

                    <h4>
                        Key Skill Gaps
                    </h4>

                    <div class="tag-list">
                        ${
                            renderTags(
                                career.key_gaps,
                                "gap",
                                "No major gaps identified."
                            )
                        }
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
// SKILL IMPACT
// ======================================================

function showSkillImpactFromButton(
    button
) {

    const occupation =
        button.dataset.occupation;

    const index =
        button.dataset.index;

    showSkillImpact(
        occupation,
        index,
        button
    );
}


async function showSkillImpact(
    occupation,
    index,
    button
) {

    const skills =
        getSkills();

    const panel =
        document.getElementById(
            `impact-${index}`
        );

    if (!panel) {
        return;
    }

    if (
        !panel.classList.contains(
            "hidden"
        )
        &&
        panel.dataset.loaded === "true"
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

            <span>
                Calculating highest-impact skills...
            </span>
        </div>
    `;

    button.disabled = true;
    button.textContent =
        "Calculating...";

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/skill-impact",
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
                                skills,

                            occupation:
                                occupation,

                            limit:
                                5
                        })
                }
            );

        if (!response.ok) {

            throw new Error(
                "Skill impact request failed."
            );
        }

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


            <p class="impact-intro">

                These skills are ranked by how much
                they could improve your fit for

                <strong>
                    ${escapeHTML(
                        data.occupation
                    )}
                </strong>.

            </p>
        `;

        if (
            !data.best_skills_to_learn ||
            data.best_skills_to_learn.length === 0
        ) {

            html += `
                <div class="impact-empty">
                    No major skill improvements were identified.
                </div>
            `;

        } else {

            html += `
                <div class="impact-list">
            `;

            data.best_skills_to_learn.forEach(
                (item, skillIndex) => {

                    html += `

                        <div class="impact-item">

                            <div class="impact-rank">
                                ${skillIndex + 1}
                            </div>

                            <div class="impact-skill-info">

                                <strong>
                                    ${escapeHTML(
                                        item.skill
                                    )}
                                </strong>

                                <div class="impact-score-change">

                                    <span>
                                        ${item.current_score}
                                    </span>

                                    <span>→</span>

                                    <span>
                                        ${item.new_score}
                                    </span>

                                </div>

                                <small>
                                    New confidence:
                                    ${escapeHTML(
                                        item.new_confidence
                                    )}
                                </small>

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
        }

        panel.innerHTML =
            html;

        panel.dataset.loaded =
            "true";

        button.textContent =
            "Hide Skill Impact";

    } catch (error) {

        console.error(error);

        panel.innerHTML = `
            <p class="impact-error">
                Unable to calculate skill impact.
            </p>
        `;

        button.textContent =
            "Try Skill Impact Again";

    } finally {

        button.disabled =
            false;
    }
}


// ======================================================
// CAREER ROADMAP
// ======================================================

function showRoadmapFromButton(
    button
) {

    const occupation =
        button.dataset.occupation;

    const index =
        button.dataset.index;

    showCareerRoadmap(
        occupation,
        index,
        button
    );
}


async function showCareerRoadmap(
    occupation,
    index,
    button
) {

    const skills =
        getSkills();

    const panel =
        document.getElementById(
            `roadmap-${index}`
        );

    if (!panel) {
        return;
    }

    if (
        !panel.classList.contains(
            "hidden"
        )
        &&
        panel.dataset.loaded === "true"
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

    panel.innerHTML = `
        <div class="roadmap-loading">
            <div class="mini-spinner"></div>

            <span>
                Building your 90-day roadmap...
            </span>
        </div>
    `;

    button.disabled = true;
    button.textContent =
        "Building Roadmap...";

    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/career-roadmap",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            skills:
                                skills,

                            occupation:
                                occupation,

                            limit:
                                6
                        })
                }
            );

        if (!response.ok) {

            throw new Error(
                "Career roadmap request failed."
            );
        }

        const data =
            await response.json();

        const roadmap =
            data.roadmap || {};

        let html = `

            <div class="roadmap-header">

                <div>

                    <span class="eyebrow">
                        PERSONALIZED ROADMAP
                    </span>

                    <h4>
                        30 / 60 / 90 Day Plan
                    </h4>

                </div>

                <div class="roadmap-score">

                    <span>
                        Current Fit
                    </span>

                    <strong>
                        ${data.current_score}/100
                    </strong>

                </div>

            </div>


            <p class="roadmap-intro">

                A practical learning roadmap for

                <strong>
                    ${escapeHTML(
                        data.occupation
                    )}
                </strong>.

            </p>


            <div class="roadmap-timeline">

                ${renderRoadmapStage(
                    "30 Days",
                    "Foundation",
                    roadmap["30_days"] || []
                )}

                ${renderRoadmapStage(
                    "60 Days",
                    "Build & Practice",
                    roadmap["60_days"] || []
                )}

                ${renderRoadmapStage(
                    "90 Days",
                    "Portfolio & Career",
                    roadmap["90_days"] || []
                )}

            </div>
        `;

        panel.innerHTML =
            html;

        panel.dataset.loaded =
            "true";

        button.textContent =
            "Hide 90-Day Roadmap";

    } catch (error) {

        console.error(error);

        panel.innerHTML = `
            <p class="roadmap-error">
                Unable to build the roadmap.
            </p>
        `;

        button.textContent =
            "Try Roadmap Again";

    } finally {

        button.disabled =
            false;
    }
}


// ======================================================
// ROADMAP STAGE RENDERER
// ======================================================

function renderRoadmapStage(
    period,
    subtitle,
    tasks
) {

    let tasksHtml = "";

    if (
        !tasks ||
        tasks.length === 0
    ) {

        tasksHtml = `
            <li>
                No tasks generated for this stage.
            </li>
        `;

    } else {

        tasksHtml =
            tasks
            .map(
                task => `
                    <li>

                        <span class="roadmap-task-dot"></span>

                        <div>

                            <strong>
                                ${escapeHTML(
                                    task.title
                                )}
                            </strong>

                            ${
                                task.skill
                                ? `
                                    <small>
                                        Focus skill:
                                        ${escapeHTML(
                                            task.skill
                                        )}
                                    </small>
                                `
                                : ""
                            }

                        </div>

                    </li>
                `
            )
            .join("");
    }

    return `

        <div class="roadmap-stage">

            <div class="roadmap-stage-badge">
                ${period}
            </div>

            <div class="roadmap-stage-content">

                <h5>
                    ${subtitle}
                </h5>

                <ul>
                    ${tasksHtml}
                </ul>

            </div>

        </div>
    `;
}


// ======================================================
// RENDER JOB RESULTS
// ======================================================

function renderJobResults(
    data
) {

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

    if (
        !data.top_jobs ||
        data.top_jobs.length === 0
    ) {

        jobsContainer.innerHTML = `
            <div class="job-card">
                No job matches found.
            </div>
        `;

    } else {

        data.top_jobs.forEach(
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

                            ${
                                renderTags(
                                    job.matched_skills,
                                    "match",
                                    "No direct matches"
                                )
                            }

                        </div>

                    </div>


                    <div class="card-section">

                        <h4>
                            Missing Skills
                        </h4>

                        <div class="tag-list">

                            ${
                                renderTags(
                                    job.missing_skills,
                                    "gap",
                                    "No major gaps"
                                )
                            }

                        </div>

                    </div>
                `;

                jobsContainer.appendChild(
                    card
                );
            }
        );
    }

    if (
        data.learn_next &&
        data.learn_next.length > 0
    ) {

        data.learn_next.forEach(
            (item, index) => {

                const card =
                    document.createElement(
                        "div"
                    );

                card.className =
                    "learning-card";

                card.innerHTML = `

                    <strong>
                        ${index + 1}.
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
    }

    section.classList.remove(
        "hidden"
    );
}


// ======================================================
// TAG RENDERER
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


// ======================================================
// SHORTEN TEXT
// ======================================================

function shortenText(
    text,
    maxLength
) {

    if (!text) {

        return (
            "No description available."
        );
    }

    if (
        text.length <= maxLength
    ) {

        return text;
    }

    return (
        text.slice(
            0,
            maxLength
        )
        +
        "..."
    );
}


// ======================================================
// ESCAPE HTML
// ======================================================

function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }

    return String(
        value
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


// ======================================================
// LOADING
// ======================================================

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


// ======================================================
// ERRORS
// ======================================================

function showError(
    message
) {

    const errorBox =
        document.getElementById(
            "errorBox"
        );

    errorBox.textContent =
        message;

    errorBox.classList.remove(
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


// ======================================================
// CLEAR RESULTS
// ======================================================

function clearResults() {

    document
        .getElementById(
            "careerResultsSection"
        )
        .classList
        .add(
            "hidden"
        );

    document
        .getElementById(
            "jobResultsSection"
        )
        .classList
        .add(
            "hidden"
        );
}