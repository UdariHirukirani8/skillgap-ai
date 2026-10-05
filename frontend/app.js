let currentMode = "career";


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

        careerButton.classList.add(
            "active"
        );

        jobButton.classList.remove(
            "active"
        );

        targetRoleGroup.classList.add(
            "hidden"
        );

        analyzeButton.textContent =
            "Discover My Careers";

        description.textContent =
            "We'll compare your skills with ESCO occupations and discover suitable career paths.";

    } else {

        jobButton.classList.add(
            "active"
        );

        careerButton.classList.remove(
            "active"
        );

        targetRoleGroup.classList.remove(
            "hidden"
        );

        analyzeButton.textContent =
            "Find Matching Jobs";

        description.textContent =
            "Enter a target role and we'll analyze your job match and missing skills.";
    }


    clearResults();
}


function getSkills() {

    const skillsText =
        document.getElementById(
            "skills"
        ).value;

    return skillsText
        .split(",")
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);
}


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

    showLoading();

    clearResults();


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


async function discoverCareers(skills) {

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


async function matchJobs(skills) {

    const targetRole =
        document.getElementById(
            "targetRole"
        ).value.trim();


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


    container.innerHTML =
        "";

    count.textContent =
        `${data.total_results} careers found`;


    if (
        !data.career_matches ||
        data.career_matches.length === 0
    ) {

        container.innerHTML = `
            <div class="career-card">
                No suitable careers were found for the entered skills.
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


            const matchedSkills =
                [
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
                            ${escapeHTML(
                                career.occupation
                            )}
                        </h3>

                        <span
                            class="confidence ${confidenceClass}"
                        >
                            ${escapeHTML(
                                career.confidence
                            )} Confidence
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
                                "No major skills matched yet."
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
                        ${
                            job.match_score
                        }%
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


                jobsContainer
                    .appendChild(
                        card
                    );
            }
        );
    }


    if (data.learn_next) {

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
                        ${
                            item.frequency
                        }
                        top job(s)
                    </span>
                `;


                learningContainer
                    .appendChild(
                        card
                    );
            }
        );
    }


    section.classList.remove(
        "hidden"
    );
}


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
        .slice(0, 8)
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


function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
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