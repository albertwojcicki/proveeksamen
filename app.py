from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import sqlite3



app = Flask(__name__)
# BYTT PATH PÅ DATABASEN    
con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()



@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    # Query the database to check if the user exists and the password is correct
    # Replace this with your actual database query
    user = cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    print(user)
    if user:
        return jsonify({"message": "Login successful", "username": username}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@app.route("/get_image/<image_name>", methods = ["GET"])
def get_image(image_name):
    
    return send_from_directory("Q://proveeksamen flask/frontend/static/bilder", image_name)

@app.route("/get_restaurants")
def get_restaurants():
    cur.execute("SELECT * FROM restaurants")
    data = cur.fetchall()

    # Convert fetched data into a list of dictionaries
    restaurants = []
    for row in data:
        restaurant = {
            "restaurant_id": row[0],
            "restaurant_name": row[1],
            "owner_id": row[2],
            "restaurant_image": row[3]
            # Add more fields as needed
        }
        restaurants.append(restaurant)

    # Return the data to the frontend as JSON
    return jsonify(restaurants)

if __name__ == "__main__":
    app.run(debug=True, port=5020)
