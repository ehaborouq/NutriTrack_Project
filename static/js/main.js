document.addEventListener("DOMContentLoaded", () => {
  const categoryButtons = document.querySelectorAll(".cat-btn");
  const categoryInput = document.querySelector("#category-input");
  const timeInput = document.querySelector("#meal-time");

  const lastCategory = localStorage.getItem("lastCategory") || "Healthy";
  updateCategory(lastCategory);

  categoryButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedCategory = button.getAttribute("data-value");
      updateCategory(selectedCategory);

      localStorage.setItem("lastCategory", selectedCategory);
    });
  });

  function updateCategory(category) {
    categoryInput.value = category;

    categoryButtons.forEach((btn) => {
      btn.classList.remove(
        "healthy-active",
        "fastfood-active",
        "celebration-active",
      );
    });

    const activeBtn = Array.from(categoryButtons).find(
      (btn) => btn.getAttribute("data-value") === category,
    );
    if (activeBtn) {
      let className = "";
      className = `${category.toLowerCase().replace(" ", "")}-active`;
      activeBtn.classList.add(className);
    }
  }

  if (timeInput && !timeInput.value) {
    const now = new Date();
    timeInput.value = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
});

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

const settingsForm = document.getElementById("profile-settings-form");

if (settingsForm) {
  settingsForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const newName = document.getElementById("setting-username").value;
    const newGoal = document.getElementById("setting-goal").value;

    fetch("/update-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName, goal: newGoal }),
    }).then((response) => {
      if (response.ok) {
        window.location.reload();
      }
    });
  });
}

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
          window.location.href = "/setup";
        });
      }
    });
  });
}

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

window.onload = function () {
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
    if (document.getElementById("darkModeToggle")) {
      document.getElementById("darkModeToggle").checked = true;
    }
  }
};
