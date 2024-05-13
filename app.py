from flask import Flask, render_template, request, jsonify
import requests
import sqlite3


app = Flask(__name__)
# BYTT PATH PÅ DATABASEN    
con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INTEGER PRIMARY KEY, 
                restaurant_name TEXT,
                owner_id INTEGER,
                restaurant_image BLOB,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            );""")
con.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS meals (
                meal_id INTEGER PRIMARY KEY, 
                restaurant_id INTEGER,
                meal_name TEXT,
                meal_price INTEGER,
                meal_desc TEXT,
                meal_image BLOB,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
            );""")
con.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                username TEXT,
                password TEXT 
            );""")

con.commit()


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



if __name__ == "__main__":
    app.run(debug=True, port=5020)
