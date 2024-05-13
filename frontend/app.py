from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)
navn = "Gjøvik restauranter"


brukere = ["Per","Ola", "Abdi", "Sander", "Michel"]


con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

cur.execute(""" CREATE TABLE
            IF NOT EXISTS
            brukere(ID integer PRIMARY KEY, 
            fornavn text,
            etternavn text,
            telefon integer,
            bilde blob);""")




if __name__ == "__main__":
    app.run(debug=True)
