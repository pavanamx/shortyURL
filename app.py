from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'urls.db')
# Create database
def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT UNIQUE,
        long_url TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Generate random short code
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form["url"]

        code = generate_code()

        conn = sqlite3.connect("urls.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO urls(short_code, long_url) VALUES (?, ?)",
            (code, long_url)
        )

        conn.commit()
        conn.close()

        short_url = request.host_url + code

        return render_template(
            "index.html",
            short_url=short_url,
            long_url=long_url
        )

    return render_template("index.html")

@app.route("/<code>")
def redirect_url(code):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT long_url FROM urls WHERE short_code=?",
        (code,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "URL Not Found"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)