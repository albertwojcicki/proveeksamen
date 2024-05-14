from flask import Flask, render_template, request, session, redirect, json, url_for
import sqlite3
import requests


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
navn = "Gjøvik restauranter"
app.secret_key = 'your_secret_key'
appHasRunBefore:bool = False

   
@app.before_request
def check_login():
    global appHasRunBefore
    if not appHasRunBefore:
        session["username"] = "None"
        appHasRunBefore = True
    if session.get("username") != "None":
        print("logget inn", session.get("username"))
   

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
    if session.get("username") == "None":
       return redirect("/login")
    if request.method == "POST":
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
        response = requests.post("http://127.0.0.1:5020/login", json={"username": username, "password": password})
        if response.status_code == 200:
            session['username'] = username  
            return redirect(f"/admin/{username}")
        else:
            return render_template("login.html", error="Invalid credentials")
    if session.get("username") != "None":
        username = session.get("username")
        return redirect(f"/admin/{username}")

    return render_template("login.html", error=None)


@app.route("/admin/<username>")
def admin(username):
    if session.get("username") == "None":
       return redirect("/login")
    if 'username' in session and session['username'] == username:
        user_id = requests.get("http://127.0.0.1:5020/get_user_id", json={"username":username}).json()["user_id"]
        return render_template("admin.html", username=username, user_id = user_id)
    else:
        return redirect("/login")
    
@app.route("/upload_form/<user_id>")
def upload_form(user_id):
    if session.get("username") == "None":
       return redirect("/login")
    return render_template("upload_form.html", user_id = user_id)

@app.route("/add_meals/<user_id>", methods=["POST", "GET"])
def add_meals(user_id):
    if session.get("username") == "None":
       return redirect("/login")
    if request.method == "POST":
        meal_name = request.form.get("meal_name")
        meal_price = request.form.get("meal_price")
        meal_description = request.form.get("meal_description")
        meal_image = request.files["meal_image"]
        meal_data = {
            "user_id": user_id,
            "meal_name": meal_name,
            "meal_price": meal_price,
            "meal_description": meal_description
        }
        print(meal_image)
        files = {"meal_image": meal_image}
        response = requests.post("http://127.0.0.1:5020/add_meals", data=meal_data, files=files)
        
        # Handle the response as needed
        if response.status_code == 200:
            return redirect(url_for("index"))
        else:
            return "Error adding meal"

    return render_template("admin.html")

@app.route("/edit_meals/<meal_id>", methods=["POST", "GET"])
def edit_meals(meal_id):
    if session.get("username") == "None":
       return redirect("/login")
    get_data = requests.get("http://127.0.0.1:5020/get_data_edit", json={"meal_id": meal_id}).json()
    print(get_data)
    return render_template("edit_page.html", meal_data = get_data, meal_id = meal_id)

@app.route("/update_meal/<meal_id>", methods = ["POST", "GET"])
def update_meal(meal_id):
    if session.get("username") == "None":
       return redirect("/login")
    meal_name = request.form.get("meal_name")
    meal_price = request.form.get("meal_price")
    meal_description = request.form.get("meal_description")
    meal_data = {
        "meal_name": meal_name,
        "meal_price": meal_price,
        "meal_description": meal_description,
        "meal_id": meal_id
            }
    
    json_data = json.dumps(meal_data)
    print(json_data)
    response = requests.post("http://127.0.0.1:5020/update_meal/" + meal_id, json=json_data)
    
    return redirect(url_for("index"))
    
   

@app.route("/delete_meal/<meal_id>/<user_id>", methods=["POST"])
def delete_meal(meal_id, user_id):
    if session.get("username") == "None":
       return redirect("/login")
    response = requests.delete(f"http://127.0.0.1:5020/delete_meal/{meal_id}")
    return redirect(url_for('edit_meal', user_id = user_id))

@app.route("/edit_meal/<user_id>")
def edit_meal(user_id):
    if session.get("username") == "None":
       return redirect("/login")
    mealToEdit = requests.post("http://127.0.0.1:5020/edit_meal", json={"user_id": user_id}).json()
    print(mealToEdit)

    return render_template("edit_meal.html", mealToEdit = mealToEdit, user_id = user_id)

if __name__ == "__main__":
    app.run(debug=True)
