from flask import Flask, render_template, request, redirect, url_for
from analyzer import analyze_text

app = Flask(__name__)

latest_result = None
latest_text = ""

@app.route("/", methods=["GET", "POST"])
def home():

    global latest_result
    global latest_text

    if request.method == "POST":

        latest_text = request.form["text"]

        latest_result = analyze_text(latest_text)

        return redirect(url_for("result"))

    return render_template(
        "index.html",
        result=None,
        user_text=""
    )

@app.route("/result")
def result():

    return render_template(
        "index.html",
        result=latest_result,
        user_text=latest_text
    )

if __name__ == "__main__":
    app.run(debug=True)