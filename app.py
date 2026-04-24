import flask

app = flask.Flask("NutriTrack")

# Temporary variable to simulate the recording process
is_user_registered = False

def get_html(page_name):
    html_file = open("templates/" + page_name + ".html", encoding="utf-8")
    content = html_file.read()
    html_file.close()
    return content

@app.route("/")
def home():
    if not is_user_registered:
        return flask.redirect("/setup")
    return get_html("index")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    global is_user_registered
    if flask.request.method == "POST":
        is_user_registered = True
        return flask.redirect("/")
    return get_html("setup")

@app.route("/add-meal")
def add_meal():
    return get_html("add_meal")

@app.route("/history")
def history():
    return get_html("history")

@app.route("/settings")
def settings():
    return get_html("settings")