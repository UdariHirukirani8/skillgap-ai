async function getRecommendations() {

    const skillsText =
        document.getElementById("skills").value;

    const targetRole =
        document.getElementById("targetRole").value;

    const skills =
        skillsText
            .split(",")
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0);

    if (skills.length === 0) {
        alert("Please enter at least one skill.");
        return;
    }

    document
        .getElementById("loading")
        .classList.remove("hidden");

    document
        .getElementById("results")
        .classList.add("hidden");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/recommend",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    skills: skills,
                    target_role: targetRole
                })
            }
        );

        const data = await response.json();

        displayJobs(data.top_jobs);
        displayLearningSkills(data.learn_next);

        document
            .getElementById("results")
            .classList.remove("hidden");

    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to SkillGap AI API."
        );

    } finally {

        document
            .getElementById("loading")
            .classList.add("hidden");
    }
}


function displayJobs(jobs) {

    const container =
        document.getElementById("jobResults");

    container.innerHTML = "";

    jobs.forEach((job, index) => {

        const card =
            document.createElement("div");

        card.className = "job-card";

        card.innerHTML = `
            <h3>
                ${index + 1}. ${job.job_title}
            </h3>

            <div class="score">
                Match: ${job.match_score}%
            </div>

            <h4>Matched Skills</h4>

            <div>
                ${
                    job.matched_skills
                        .map(
                            skill =>
                            `<span class="skill-tag">
                                ${skill}
                            </span>`
                        )
                        .join("")
                }
            </div>

            <h4>Missing Skills</h4>

            <div>
                ${
                    job.missing_skills
                        .map(
                            skill =>
                            `<span class="skill-tag">
                                ${skill}
                            </span>`
                        )
                        .join("")
                }
            </div>
        `;

        container.appendChild(card);
    });
}


function displayLearningSkills(skills) {

    const container =
        document.getElementById(
            "learningSkills"
        );

    container.innerHTML = "";

    skills.forEach((item, index) => {

        const card =
            document.createElement("div");

        card.className =
            "learning-card";

        card.innerHTML = `
            <strong>
                ${index + 1}. ${item.skill}
            </strong>

            <br>

            Required by
            ${item.frequency}
            top job(s)
        `;

        container.appendChild(card);
    });
}