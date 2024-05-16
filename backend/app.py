from flask import Flask, render_template, request, jsonify, send_from_directory, json, redirect, session
import json
import requests
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
workingdir = os.getcwd()


app = Flask(__name__)
# BYTT PATH PÅ DATABASEN    
con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()
app.secret_key = 'your_secret_key'


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    print(user)
    if user:
        session['username'] = username
        return jsonify({"message": "Login successful", "username": username}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@app.route("/get_image/<image_name>")
def get_image(image_name):
    return send_from_directory("static/bilder", image_name)

@app.route('/get_image_meal/<image_name>', methods = ["GET"])
def get_image_meal(image_name):
    return send_from_directory('C:\\wamp64\\www\\proveeksamen\\backend\\static\\bilder\\',  image_name)

@app.route('/post_image/<meal_id>/', methods=['POST'])
def upload_image(meal_id):
    new_image_file = request.files['meal_image_edit']
    cur.execute("SELECT meal_image from meals WHERE meal_id = ?", (meal_id,))
    old_image_file = cur.fetchone()[0]
    os.remove('C:\\wamp64\\www\\proveeksamen\\backend\\static\\bilder\\' + old_image_file)
    new_image_file.save('C:\\wamp64\\www\\proveeksamen\\backend\\static\\bilder\\' + new_image_file.filename)
    cur.execute("UPDATE meals SET meal_image = ? WHERE meal_id = ?", (new_image_file.filename, meal_id))
    con.commit()
    return redirect('http://127.0.0.1:5000')

@app.route("/registrer_bruker", methods=["POST", "GET"])
def registrer_bruker():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    cur.execute("INSERT INTO customers (email, password) VALUES (?, ?)", (email, password))
    con.commit()
    return  "succesfully registered user"

@app.route("/delete_basket", methods=["POST", "GET"])
def delete_basket():
    meal_id = request.get_json()["meal_id"]
    cur.execute("DELETE FROM basket WHERE meal_id = ?", (meal_id))
    con.commit()
    return "deleted the basket "

@app.route("/add_to_basket", methods=["POST"])
def add_to_basket():
    data = request.json
    email = data.get('email')
    meal_id = data.get('meal_id')
    quantity = data.get('quantity')
    
    # Fetch user ID from the database
    cur.execute("SELECT user_id FROM customers WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if user:
        user_id = user[0]  # Extract user ID from the tuple
        cur.execute("SELECT meal_name FROM meals WHERE meal_id = ?", (meal_id,))
        meal_name_result = cur.fetchone()  # Use fetchone instead of fetchall
        print(meal_name_result)
        cur.execute("SELECT meal_id, number_of_meals FROM basket WHERE user_id = ? AND meal_id = ?", (user_id, meal_id))
        existing_meal = cur.fetchone()
        if meal_name_result:
            meal_name = meal_name_result[0]  # Extract meal name from the tuple
        else:
            return jsonify({"error": "Meal not found"}), 404
        if existing_meal:
            # If the meal exists, update the quantity
            basket_id, existing_quantity = existing_meal
            new_quantity = existing_quantity + quantity
            cur.execute("UPDATE basket SET number_of_meals = ? WHERE meal_id = ?", (new_quantity, basket_id))
        else:
            # If the meal does not exist, insert a new row
            cur.execute("INSERT INTO basket (user_id, meal_name, meal_id, number_of_meals) VALUES (?, ?, ?, ?)", (user_id, meal_name, meal_id, quantity))

        con.commit()
        return jsonify({"message": "Meal added to basket successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/update_quantity/", methods=["POST"])
def update_quantity():
    data = request.json
    email = data.get('email')
    meal_id = data.get('meal_id')
    new_quantity = data.get('quantity')

    cur.execute("SELECT user_id FROM customers WHERE email = ?", (email,))
    user = cur.fetchone()
    if user:
        user_id = user[0]
        cur.execute("UPDATE basket SET number_of_meals = ? WHERE user_id = ? AND meal_id = ?", (new_quantity, user_id, meal_id))
        con.commit()
        return jsonify({"message": "Quantity updated successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route("/get_handlekurv", methods=["GET"])
def get_handlekurv():
    email = request.json.get('email')
    cur.execute("SELECT user_id FROM customers WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if user:
        user_id = user[0]
        cur.execute("SELECT user_id, meal_id, number_of_meals, bought, purchase_time, meal_name FROM basket WHERE user_id  = ? AND bought = 0  ", (user_id,))
        basket_data = cur.fetchall()
        # cur.execute("SELECT meal_id FROM basket WHERE ")
        return jsonify(basket_data), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/login_bruker", methods=["POST", "GET"])
def login_bruker():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Query the database to check if a user with the provided email and password exists
    cur.execute("SELECT * FROM customers WHERE email = ? AND password = ?", (email, password))
    user = cur.fetchone()

    if user:
        # Successful login
        return jsonify({"message": "Login successful"}), 200
    else:
        # Invalid credentials
        return jsonify({"message": "Invalid email or password"}), 401


@app.route("/add_meals", methods=["POST"])
def add_meals():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        meal_name = request.form.get("meal_name")
        meal_price = request.form.get("meal_price")
        meal_description = request.form.get("meal_description")
        meal_image_name = request.form.get("meal_image")
        meal_image = request.files["meal_image"]
        meal_image.save(workingdir + "\\static\\bilder\\" + meal_image_name)
        print(meal_image_name)
        cur.execute("INSERT INTO meals (meal_name, meal_price, meal_desc, restaurant_id, meal_image) VALUES (?, ?, ?, ?, ?)",
                    (meal_name, meal_price, meal_description, user_id, meal_image_name))
        con.commit()

        return jsonify({"message": "Meal added successfully", "meal_image_path": 'C:\\wamp64\\www\\proveeksamen\\backend\\static\\bilder\\' + meal_image_name})

@app.route("/get_restaurant_data", methods=["GET", "POST"])
def get_restaurant_data():
    if request.method == "POST":
        data = request.json
        restaurant_id = data.get("restaurant_id")
        if restaurant_id:
            cur.execute("SELECT * FROM meals WHERE restaurant_id = ?", (restaurant_id,))
            meals = cur.fetchall()
            meal_list = []
            for meal in meals:
                meal_data = {
                    "meal_id": meal[0],
                    "restaurant_id": meal[1],
                    "meal_name": meal[2],
                    "meal_price": meal[3],
                    "meal_description": meal[4],
                    "meal_image": meal[5]
                }
                meal_list.append(meal_data)
            return jsonify(meal_list)
        else:
            return jsonify({"error": "No restaurant_id provided in the request"})
    else:
        return jsonify({"error": "Method not allowed"}), 405
    

@app.route("/get_restaurants")
def get_restaurants():
    cur.execute("SELECT * FROM restaurants")
    data = cur.fetchall()
    restaurants = []
    for row in data:
        restaurant = {
            "restaurant_id": row[0],
            "restaurant_name": row[1],
            "owner_id": row[2],
            "restaurant_image": row[3]
        }
        restaurants.append(restaurant)
    return jsonify(restaurants)

@app.route("/edit_meal", methods=["POST"])
def edit_meal():
    user_id = request.json["user_id"]
    cur.execute("SELECT * FROM meals WHERE restaurant_id = ?", (user_id,))
    data = cur.fetchall()
    mealsList = []
    for row in data:
        meals = {
            "meal_id": row[0],
            "meal_name": row[2],
            "meal_price": row[3],
            "meal_description": row[4]
        }
        mealsList.append(meals)
    return jsonify(mealsList)

@app.route("/get_data_edit", methods=["GET", "POST"])
def get_data_edit():
    meal_id = request.get_json()["meal_id"]
    cur.execute("SELECT * FROM meals WHERE meal_id = ?", (meal_id,))
    data = cur.fetchall()
    mealsList = []
    for row in data:
        meals = {
            "meal_id": row[0],
            "meal_name": row[2],
            "meal_price": row[3],
            "meal_description": row[4]
        }
        mealsList.append(meals)
    return jsonify(mealsList)

@app.route("/update_meal/<meal_id>", methods=["GET","POST"])
def update_meal(meal_id):
    json_data = json.loads(request.json)
    meal_name = json_data["meal_name"]
    meal_price = json_data["meal_price"]
    meal_description = json_data["meal_description"]
    cur.execute("UPDATE meals SET meal_name = ?, meal_price = ?, meal_desc = ? WHERE meal_id = ?",
                (meal_name, meal_price, meal_description, meal_id))
    con.commit()
    return "status_code", 200

@app.route("/delete_meal/<meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    cur.execute("DELETE FROM meals WHERE meal_id = ?", (meal_id,))
    con.commit()
    return "Meal deleted successfully", 200

@app.route("/get_user_id", methods=["GET"])
def get_user_id():
    username = request.get_json()["username"]
    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = cur.fetchone()
    return {"user_id": user_id[0]}

if __name__ == "__main__":
    app.run(debug=True, port=5020)
