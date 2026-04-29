import flask
import json
from meal_manager import MealManager

# Initialize the Flask application
app = flask.Flask("NutriTrack")
app.secret_key = "nutri_track_secure_key"

# --- HELPER FUNCTIONS ---

def get_html(page_name):
    """Reads and returns the content of an HTML template file."""
    try:
        with open(f"templates/{page_name}.html", encoding="utf-8") as html_file:
            return html_file.read()
    except FileNotFoundError:
        return "<h1>Template Error: File not found</h1>"

def get_data():
    """Loads user data from the local JSON storage. Returns an empty list if file missing."""
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    """Writes the updated data list to the JSON storage file with clean formatting."""
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def validate_positive_int(value, default=1):
    """Security: Ensures input values are positive integers. Prevents negative calories/goals."""
    try:
        clean_val = int(value)
        return clean_val if 0 < clean_val <= 10000 else default
    except (ValueError, TypeError):
        return default

def is_valid_name(name):
    """Simple check: Name shouldn't be empty or just numbers."""
    if not name or not name.strip():
        return False

    if name.strip().isdigit():
        return False
    return True

# --- ROUTE HANDLERS ---

@app.route("/")
def home():
    """Main Dashboard Route: Orchestrates user stats and nutrition advice."""
    all_users = get_data()
    current_username = flask.session.get("user_name")

    if not all_users or not current_username:
        return flask.redirect("/setup")

    user_data = next((u for u in all_users if u["name"] == current_username), None)
    if not user_data:
        return flask.redirect("/setup")

    manager = MealManager(daily_limit=user_data["goal"])
    manager.meals_list = user_data["meals"]

    total_consumed = sum(meal['calories'] for meal in user_data['meals'])
    remaining = manager.calculate_remaining_calories()
    advice = manager.get_nutrition_advice(personality=user_data.get("personality", "Motivator"))

    icon = "👋" if user_data.get("meals") else "🌿"
    back_text = " back" if user_data.get("meals") else ""

    consumption_ratio = total_consumed / user_data["goal"] if user_data["goal"] > 0 else 0
    status_class = "exceeded" if total_consumed > user_data["goal"] else "normal"
    progress_degree = min(1.0, consumption_ratio) * 360

    page = get_html("index")
    replacements = {
        "$$BACK$$": back_text, "$$ICON$$": icon, "$$NAME$$": user_data["name"],
        "$$TOTAL$$": str(total_consumed), "$$GOAL$$": str(user_data["goal"]),
        "$$REMAINING$$": str(remaining), "$$ADVICE$$": advice,
        "$$PROGRESS$$": str(progress_degree), "$$STATUS_CLASS$$": status_class
    }

    for key, val in replacements.items():
        page = page.replace(key, val)
    return page

@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Onboarding Route: Registers a new user or updates an existing goal."""
    if flask.request.method == "POST":
        name = flask.request.form.get("name", "").strip()
        goal = validate_positive_int(flask.request.form.get("goal"), default=2000)

        if not is_valid_name(name):
            return flask.redirect("/setup")

        all_users = get_data()
        user_exists = False

        for user in all_users:
            if user["name"] == name:
                user["goal"] = goal
                user_exists = True
                break

        if not user_exists:
            all_users.append({
                "name": name, "goal": goal, "personality": "Motivator", "meals": []
            })

        save_data(all_users)
        flask.session["user_name"] = name
        return flask.redirect("/")

    return get_html("setup")

@app.route("/add-meal", methods=["GET", "POST"])
def add_meal():
    """Meal Logging Route: Validates and persists new food entries."""
    current_username = flask.session.get("user_name")
    if not current_username: return flask.redirect("/setup")

    if flask.request.method == "POST":
        meal_name = flask.request.form.get("meal_name", "").strip()
        calories = validate_positive_int(flask.request.form.get("calories"), default=100)

        if not meal_name:
            return flask.redirect("/add-meal")

        new_entry = {
            "name": meal_name,
            "calories": calories,
            "category": flask.request.form.get("category"),
            "time": flask.request.form.get("meal_time")
        }

        all_users = get_data()
        for user in all_users:
            if user["name"] == current_username:
                user["meals"].append(new_entry)
                break

        save_data(all_users)
        return flask.redirect("/")

    return get_html("add_meal")

@app.route("/history")
def history():
    """History View: Renders the chronological list of logged meals."""
    all_users = get_data()
    current_username = flask.session.get("user_name")
    if not current_username: return flask.redirect("/setup")

    user_data = next((u for u in all_users if u["name"] == current_username), None)
    meals_html = ""

    if user_data and user_data["meals"]:
        icons = {
            "Healthy": ("healthy-border", "fa-leaf icon-healthy"),
            "Fast Food": ("fastfood-border", "fa-bolt icon-fastfood"),
            "Celebration": ("celebration-border", "fa-cake-candles icon-celebration")
        }

        for index, meal in enumerate(user_data["meals"]):
            border, icon = icons.get(meal.get("category"), icons["Healthy"])
            meals_html += f'''
            <div class="history-card {border}">
                <div class="card-main-info">
                    <div class="card-icon-bg"><i class="fas {icon}"></i></div>
                    <div class="card-text">
                        <h3>{meal['name']}</h3>
                        <p>{meal['time']}</p>
                    </div>
                </div>
                <div class="card-right-side">
                    <div class="card-stats">
                        <span class="calories-amount">{meal['calories']}</span>
                        <span class="unit">kcal</span>
                    </div>
                    <button class="delete-btn" onclick="handleDelete({index})">
                        <i class="far fa-trash-can"></i>
                    </button>
                </div>
            </div>
            '''
    else:
        meals_html = '<p style="text-align:center; color:#888;">No meals added yet.</p>'

    return get_html("history").replace("$$MEALS_LIST$$", meals_html)

@app.route("/delete-meal/<int:meal_index>")
def delete_meal(meal_index):
    """Deletion Endpoint: Removes a specific meal entry by index."""
    all_users = get_data()
    current_username = flask.session.get("user_name")

    for user in all_users:
        if user["name"] == current_username:
            if 0 <= meal_index < len(user["meals"]):
                user["meals"].pop(meal_index)
            break

    save_data(all_users)
    return flask.redirect("/history")

@app.route("/settings")
def settings():
    """Settings Page: Provides tools for profile updates and account management."""
    all_users = get_data()
    current_username = flask.session.get("user_name")
    if not current_username: return flask.redirect("/setup")

    user_data = next((u for u in all_users if u["name"] == current_username), None)
    page = get_html("settings")

    if user_data:
        page = page.replace('id="setting-username"', f'id="setting-username" value="{user_data["name"]}"')
        page = page.replace('id="setting-goal"', f'id="setting-goal" value="{user_data["goal"]}"')

        current_personality = user_data.get("personality", "Motivator")
        page = page.replace(f'value="{current_personality}"', f'value="{current_personality}" selected')

    return page

@app.route("/update-profile", methods=["POST"])
def update_profile():
    """API Endpoint: JSON-based profile updates for name, goal, and coach style."""
    data = flask.request.json
    all_users = get_data()
    current_username = flask.session.get("user_name")

    new_name = data.get("name", "").strip()
    new_goal = validate_positive_int(data.get("goal"), default=2000)

    if not is_valid_name(new_name):
        return flask.jsonify({"status": "error", "message": "Invalid Name"}), 400

    for user in all_users:
        if user["name"] == current_username:
            user["name"] = new_name
            user["goal"] = new_goal
            user["personality"] = data.get("personality")
            break

    save_data(all_users)
    flask.session["user_name"] = new_name
    return flask.jsonify({"status": "success"})

@app.route("/clear-history", methods=["POST"])
def clear_history():
    """API Endpoint: Wipes all meal records for the current user."""
    current_username = flask.session.get("user_name")
    all_users = get_data()

    for user in all_users:
        if user["name"] == current_username:
            user["meals"] = []
            break

    save_data(all_users)
    return flask.jsonify({"status": "success"})

@app.route("/delete-account", methods=["POST"])
def delete_account():
    """API Endpoint: Permanently deletes the user profile and clears the session."""
    current_username = flask.session.get("user_name")
    all_users = get_data()
    updated_users = [u for u in all_users if u["name"] != current_username]
    save_data(updated_users)
    flask.session.clear()
    return flask.jsonify({"status": "success"})

@app.route("/logout")
def logout():
    """Session Management: Destroys the user session and redirects to setup."""
    flask.session.pop("user_name", None)
    return flask.redirect("/setup")

if __name__ == "__main__":
    app.run(debug=True)