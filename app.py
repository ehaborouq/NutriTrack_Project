import flask

app = flask.Flask("NutriTrack")

def get_html(page_name):
    html_file = open("templates/" + page_name + ".html")
    content = html_file.read()
    html_file.close()
    return content

@app.route("/")
def home():
    return get_html("index")