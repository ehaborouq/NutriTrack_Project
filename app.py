import flask
import json
from meal_manager import MealManager

app = flask.Flask("NutriTrack")
app.secret_key = "nutri_track_secure_key"

def get_html(page_name):
    with open("templates/" + page_name + ".html", encoding="utf-8") as html_file:
        return html_file.read()

def get_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except:
        return []

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def home():
    all_users = get_data()

    current_username = flask.session.get("user_name")

    if not all_users or not current_username:
        return flask.redirect("/setup")
    user_data = next((u for u in all_users if u["name"] == current_username), None)

    if not user_data:
        return flask.redirect("/setup")

    index_page = get_html("index")

    if not user_data.get("meals"):
        back_text = ""
        icon = "🌿"
    else:
        back_text = " back"
        icon = "👋"

    manager = MealManager(daily_limit=user_data["goal"])
    manager.meals_list = user_data["meals"]

    total_consumed = sum(meal['calories'] for meal in user_data['meals'])
    remaining = manager.calculate_remaining_calories()
    advice = manager.get_nutrition_advice()

    consumption_ratio = total_consumed / user_data["goal"]

    status_class = "exceeded" if total_consumed > user_data["goal"] else "normal"

    ui_ratio = consumption_ratio if consumption_ratio <= 1 else 1
    progress_degree = ui_ratio * 360

    page = index_page
    page = page.replace("$$BACK$$", back_text)
    page = page.replace("$$ICON$$", icon)
    page = page.replace("$$NAME$$", user_data["name"])
    page = page.replace("$$TOTAL$$", str(total_consumed))
    page = page.replace("$$GOAL$$", str(user_data["goal"]))
    page = page.replace("$$REMAINING$$", str(remaining))
    page = page.replace("$$ADVICE$$", advice)
    page = page.replace("$$PROGRESS$$", str(progress_degree))
    page = page.replace("$$STATUS_CLASS$$", status_class)

    return page

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        goal = flask.request.form.get("goal")

        all_users = get_data()

        user_exists = False
        for user in all_users:
            if user["name"] == name:
                user["goal"] = int(goal)
                user_exists = True
                break

        if not user_exists:
            new_user = {
                "name": name,
                "goal": int(goal),
                "meals": []
            }
            all_users.append(new_user)

        save_data(all_users)
        flask.session["user_name"] = name
        return flask.redirect("/")

    return get_html("setup")

@app.route("/add-meal", methods=["GET", "POST"])
def add_meal():
    current_username = flask.session.get("user_name")
    if not current_username:
        return flask.redirect("/setup")

    if flask.request.method == "POST":
        new_entry = {
            "name": flask.request.form.get("meal_name"),
            "calories": int(flask.request.form.get("calories")),
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
    all_users = get_data()
    current_username = flask.session.get("user_name")

    if not current_username:
        return flask.redirect("/setup")

    user_data = next((u for u in all_users if u["name"] == current_username), None)
    page = get_html("history")
    meals_html = ""

    if user_data and user_data["meals"]:

        for index, meal in enumerate(user_data["meals"]):

            category = meal.get("category", "Healthy")
            if category == "Healthy":
                border_class = "healthy-border"
                icon_class = "fa-leaf icon-healthy"
            elif category == "Fast Food":
                border_class = "fastfood-border"
                icon_class = "fa-bolt icon-fastfood"
            else:
                border_class = "celebration-border"
                icon_class = "fa-cake-candles icon-celebration"


            meals_html += f'''
            <div class="history-card {border_class}">
                <div class="card-main-info">
                    <div class="card-icon-bg"><i class="fas {icon_class}"></i></div>
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
                    <button class="delete-btn" onclick="handleDelete({index})" style="cursor:pointer; border:none; background:none;">
                        <i class="far fa-trash-can"></i>
                    </button>
                </div>
            </div>
            '''
    else:
        meals_html = '<p style="text-align:center; color:#888;">No meals added yet.</p>'

    return page.replace("$$MEALS_LIST$$", meals_html)


@app.route("/delete-meal/<int:meal_index>")
def delete_meal(meal_index):
    all_users = get_data()
    current_username = flask.session.get("user_name")

    for user in all_users:
        if user["name"] == current_username:
            user["meals"].pop(meal_index)
            break

    save_data(all_users)
    return flask.redirect("/history")


@app.route("/settings")
def settings():
    all_users = get_data()
    current_username = flask.session.get("user_name")

    if not current_username:
        return flask.redirect("/setup")

    user_data = next((u for u in all_users if u["name"] == current_username), None)
    page = get_html("settings")

    if user_data:
        page = page.replace('id="setting-username"', f'id="setting-username" value="{user_data["name"]}"')
        page = page.replace('id="setting-goal"', f'id="setting-goal" value="{user_data["goal"]}"')

    return page


@app.route("/update-profile", methods=["POST"])
def update_profile():
    data = flask.request.json
    new_name = data.get("name")
    new_goal = int(data.get("goal"))

    all_users = get_data()
    current_username = flask.session.get("user_name")

    for user in all_users:
        if user["name"] == current_username:
            user["name"] = new_name
            user["goal"] = new_goal
            break

    save_data(all_users)
    flask.session["user_name"] = new_name

    return flask.jsonify({"status": "success"})


@app.route("/clear-history", methods=["POST"])
def clear_history():
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
    current_username = flask.session.get("user_name")
    all_users = get_data()

    updated_users = [u for u in all_users if u["name"] != current_username]

    save_data(updated_users)
    flask.session.clear()

    return flask.jsonify({"status": "success"})