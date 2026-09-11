document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const adminActivitiesList = document.getElementById("admin-activities-list");
  const newActivityForm = document.getElementById("new-activity-form");

  function showMessage(text, type = "success") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchAdminActivities() {
    try {
      const response = await fetch("/admin/activities");
      const adminActivities = await response.json();
      const pendingActivities = adminActivities.pending || {};

      if (Object.keys(pendingActivities).length === 0) {
        adminActivitiesList.innerHTML = "<p>No pending activities.</p>";
        return;
      }

      adminActivitiesList.innerHTML = Object.entries(pendingActivities)
        .map(
          ([name, details]) => `
            <div class="admin-activity-card">
              <h4>${name}</h4>
              <p>${details.description}</p>
              <p><strong>Schedule:</strong> ${details.schedule}</p>
              <p><strong>Capacity:</strong> ${details.max_participants}</p>
              <div class="admin-actions">
                <button class="approve-btn" data-activity="${name}">Approve</button>
                <button class="reject-btn" data-activity="${name}">Reject</button>
              </div>
            </div>
          `
        )
        .join("");

      document.querySelectorAll(".approve-btn").forEach((button) => {
        button.addEventListener("click", async () => {
          const activity = button.getAttribute("data-activity");
          const response = await fetch(
            `/admin/activities/${encodeURIComponent(activity)}/approve`,
            { method: "POST" }
          );
          const result = await response.json();
          if (response.ok) {
            showMessage(result.message, "success");
            fetchActivities();
            fetchAdminActivities();
          } else {
            showMessage(result.detail || "Could not approve activity.", "error");
          }
        });
      });

      document.querySelectorAll(".reject-btn").forEach((button) => {
        button.addEventListener("click", async () => {
          const activity = button.getAttribute("data-activity");
          const reason = window.prompt(
            `Why should ${activity} be rejected?`,
            "Needs additional review."
          );
          if (reason === null) return;

          const response = await fetch(
            `/admin/activities/${encodeURIComponent(activity)}/reject`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ reason }),
            }
          );
          const result = await response.json();
          if (response.ok) {
            showMessage(result.message, "success");
            fetchActivities();
            fetchAdminActivities();
          } else {
            showMessage(result.detail || "Could not reject activity.", "error");
          }
        });
      });
    } catch (error) {
      adminActivitiesList.innerHTML =
        "<p>Failed to load approval queue.</p>";
      console.error("Error fetching admin activities:", error);
    }
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      activitiesList.innerHTML = "";

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  newActivityForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      name: document.getElementById("new-activity-name").value,
      description: document.getElementById("new-activity-description").value,
      schedule: document.getElementById("new-activity-schedule").value,
      max_participants: Number(document.getElementById("new-activity-capacity").value),
    };

    try {
      const response = await fetch("/admin/activities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "info");
        newActivityForm.reset();
        fetchAdminActivities();
      } else {
        showMessage(result.detail || "Activity could not be submitted.", "error");
      }
    } catch (error) {
      showMessage("Failed to submit activity for approval.", "error");
      console.error("Error submitting activity:", error);
    }
  });

  fetchActivities();
  fetchAdminActivities();
});
