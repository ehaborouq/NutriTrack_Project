document.addEventListener("DOMContentLoaded", () => {
  // --- Elements Selection ---
  const categoryButtons = document.querySelectorAll(".cat-btn");
  const categoryInput = document.querySelector("#category-input");
  const timeInput = document.querySelector("#meal-time");

  // --- Initial Category Setup ---
  // Load the last used category from localStorage or default to "Healthy"
  const lastCategory = localStorage.getItem("lastCategory") || "Healthy";
  updateCategory(lastCategory);

  // --- Category Click Event Listeners ---
  categoryButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedCategory = button.getAttribute("data-value");
      updateCategory(selectedCategory);
      // Save selection to persist across page reloads
      localStorage.setItem("lastCategory", selectedCategory);
    });
  });

  /*
    Updates the UI active state for category buttons and hidden input
   */
  function updateCategory(category) {
    if (!categoryInput) return; // Guard clause
    categoryInput.value = category;

    // Reset all buttons by removing active classes
    categoryButtons.forEach((btn) => {
      btn.classList.remove(
        "healthy-active",
        "fastfood-active",
        "celebration-active",
      );
    });

    // Find and highlight the selected category button
    const activeBtn = Array.from(categoryButtons).find(
      (btn) => btn.getAttribute("data-value") === category,
    );

    if (activeBtn) {
      // Transform category name to matching CSS class (e.g., "Fast Food" -> "fastfood-active")
      const className = `${category.toLowerCase().replace(/\s+/g, "")}-active`;
      activeBtn.classList.add(className);
    }
  }

  // --- Default Meal Time ---
  // Auto-fills the time input with the current system time if it's empty
  if (timeInput && !timeInput.value) {
    const now = new Date();
    timeInput.value = now.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  }
});

/* Handles individual meal deletion with confirmation */

function handleDelete(index) {
  Swal.fire({
    title: "Are you sure?",
    text: "This meal will be removed from your history!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#2d6a4f",
    confirmButtonText: "Yes, delete it!",
    cancelButtonText: "Cancel",
    reverseButtons: true,
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = `/delete-meal/${index}`;
    }
  });
}

// --- Profile Settings Form Submission ---
const settingsForm = document.getElementById("profile-settings-form");
if (settingsForm) {
  settingsForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const newName = document.getElementById("setting-username").value;
    const newGoal = document.getElementById("setting-goal").value;
    const newPersonality = document.getElementById("coach-style").value;

    fetch("/update-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: newName,
        goal: newGoal,
        personality: newPersonality,
      }),
    }).then((response) => {
      if (response.ok) {
        const Toast = Swal.mixin({
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 2000,
        });

        Toast.fire({
          icon: "success",
          title: "Profile updated successfully!",
        }).then(() => {
          // Reload the page to reflect name/goal changes in the UI
          window.location.reload();
        });
      }
    });
  });
}

// --- Quick Coach Personality Change ---
const coachSelect = document.getElementById("coach-style");
if (coachSelect) {
  coachSelect.addEventListener("change", function () {
    const newPersonality = this.value;
    const currentName = document.getElementById("setting-username").value;
    const currentGoal = document.getElementById("setting-goal").value;

    fetch("/update-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: currentName,
        goal: currentGoal,
        personality: newPersonality,
      }),
    }).then((response) => {
      if (response.ok) {
        const Toast = Swal.mixin({
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 2000,
        });
        Toast.fire({
          icon: "success",
          title: `Coach personality updated!`,
        });
      }
    });
  });
}

// --- Bulk Action: Clear All History ---
const clearHistoryBtn = document.getElementById("clear-history-btn");
if (clearHistoryBtn) {
  clearHistoryBtn.addEventListener("click", function () {
    Swal.fire({
      title: "Are you sure?",
      text: "This will clear all your meals, but keep your profile settings.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#2d6a4f",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, clear it!",
    }).then((result) => {
      if (result.isConfirmed) {
        fetch("/clear-history", { method: "POST" }).then(() => {
          Swal.fire(
            "Cleared!",
            "Your history has been deleted.",
            "success",
          ).then(() => window.location.reload());
        });
      }
    });
  });
}

// --- Critical Action: Reset Account ---
const deleteAccountBtn = document.getElementById("reset-account-btn");
if (deleteAccountBtn) {
  deleteAccountBtn.addEventListener("click", function () {
    Swal.fire({
      title: "Delete Account?",
      text: "Everything will be lost forever! You will be redirected to setup.",
      icon: "error",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete everything!",
    }).then((result) => {
      if (result.isConfirmed) {
        fetch("/delete-account", { method: "POST" }).then(() => {
          // Redirect to onboarding page after deletion
          window.location.href = "/setup";
        });
      }
    });
  });
}

/**
 * --- Dark Mode Persistence ---
 * Handles the visual toggle and saves preference to localStorage
 */
function toggleDarkMode() {
  const isDark = document.getElementById("darkModeToggle").checked;
  if (isDark) {
    document.body.classList.add("dark-mode");
    localStorage.setItem("theme", "dark");
  } else {
    document.body.classList.remove("dark-mode");
    localStorage.setItem("theme", "light");
  }
}

// --- Apply Theme on Page Load ---
window.onload = function () {
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
    const toggle = document.getElementById("darkModeToggle");
    if (toggle) {
      toggle.checked = true;
    }
  }
};
