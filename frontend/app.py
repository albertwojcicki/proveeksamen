from flask import Flask, render_template, request, session, redirect
import sqlite3
import requests


app = Flask(__name__)
navn = "Gjøvik restauranter"
app.secret_key = 'your_secret_key'




@app.route("/")
def index():
    return render_template("index.html")


# Assuming you have a form in your template named "login_form"
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Send the credentials to backend for authentication
        response = requests.post("http://127.0.0.1:5020/login", json={"username": username, "password": password})
        if response.status_code == 200:
            session['username'] = username  # Store the username in session
            return redirect(f"/admin/{username}")  # Redirect to admin page with username
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html", error=None)

@app.route("/admin/<username>")
def admin(username):
    if 'username' in session and session['username'] == username:
        return render_template("admin.html", username=username)
    else:
        return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
