from flask import Flask, render_template, request, session, redirect
import sqlite3
import requests


app = Flask(__name__)
navn = "Gjøvik restauranter"
app.secret_key = 'your_secret_key'




@app.route("/")
def index():
    response = requests.get("http://127.0.0.1:5020/get_restaurants")
    if response.status_code == 200:
        restaurants = response.json()
       
        return render_template("index.html", restaurants=restaurants)
    else:
        return "Error fetching restaurants from the backend"
    
@app.route("/restaurants/<restaurant_id>", methods=["GET", "POST"])
def restaurants(restaurant_id):
    if request.method == "POST":
        # Make a POST request to the backend to get restaurant data
        response = requests.post("http://127.0.0.1:5020/get_restaurant_data", json={"restaurant_id": restaurant_id})
        if response.status_code == 200:
            restaurant_data = response.json()
            return render_template("restaurants.html", restaurant_data=restaurant_data)
        else:
            return "Error fetching restaurant data from the backend"
    else:
        return "Method not allowed", 405

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
        user_id = requests.get("http://127.0.0.1:5020/get_user_id", json={"username":username}).json()["user_id"]
        return render_template("admin.html", username=username, user_id = user_id)
    else:
        return redirect("/login")


@app.route("/add_meals/<user_id>", methods=["POST", "GET"])
def add_meals(user_id):
    if request.method == "POST":
        meal_name = request.form.get("meal_name")
        meal_price = request.form.get("meal_price")
        meal_description = request.form.get("meal_description")
        requests.post("http://127.0.0.1:5020/add_meals", json={"user_id": user_id,"meal_name": meal_name, "meal_price": meal_price, "meal_description": meal_description})
        
        return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
