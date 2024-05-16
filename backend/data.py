import sqlite3
con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INTEGER PRIMARY KEY, 
                restaurant_name TEXT,
                owner_id INTEGER,
                restaurant_image BLOB,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
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

cur.execute("""CREATE TABLE IF NOT EXISTS customers (
                user_id INTEGER PRIMARY KEY, 
                email TEXT,
                password TEXT 
            );""")
con.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS basket (
                user_id INTEGER, 
                meal_id INTEGER,
                meal_name TEXT, 
                number_of_meals INTEGER,
                bought INTEGER DEFAULT 0,
                meal_price INTEGER,
            purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES customers(user_id)
            );""")
con.commit()
cur.execute("INSERT INTO users (username, password) VALUES ('Albert', 'passord')")
cur.execute("INSERT INTO users (username, password) VALUES ('Kjell', 'passord')")
cur.execute("INSERT INTO users (username, password) VALUES ('Sivert', 'passord')")
con.commit()

cur.execute("INSERT INTO restaurants (restaurant_name, owner_id, restaurant_image) VALUES ('San Marino', 1, 'sanmarino.jpg')")
cur.execute("INSERT INTO restaurants (restaurant_name, owner_id, restaurant_image) VALUES ('McDonalds', 2, 'mcdonalds.jpg')")
cur.execute("INSERT INTO restaurants (restaurant_name, owner_id, restaurant_image) VALUES ('Burger King', 3, 'burgerking.jpg')")
con.commit()
