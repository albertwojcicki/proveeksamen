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
