from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "1234"
DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods= ["GET", "POST"])
def login():
    if request.method == "POST":
        username =request.form["username"]
        password =request.form["password"]

        conn =get_db_connection()
        #VULNERABLE to SQL INJECTION
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        user = conn.execute(query).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search_query = request.args.get("search", "")
    search_query_replace = search_query.replace("'", "''")
    conn = get_db_connection()

    #SEARCHBOX is VULNERABLE to XSS REFLECTED AND SQL INJECTION
    if search_query:
        query = f"SELECT * FROM clients WHERE name LIKE '%{search_query_replace}%'"
    else:
        query = "SELECT * FROM clients"

    clients = conn.execute(query).fetchall()

    conn.close()
    return render_template("dashboard.html", clients=clients, search_query=search_query)

@app.route("/add_client", methods=["GET", "POST"])
def add_client():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn = get_db_connection()
        # ADDING a payload in NAME FIELD IS VULNERABLE to XSS STORED
        conn.execute("INSERT INTO clients (name, email) VALUES ('" + name + "', '" + email + "')")
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))
    return render_template("add_client.html")

@app.route("/delete_client/<int:client_id>")
def delete_client(client_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute(f"DELETE FROM clients WHERE id={client_id}")
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    print("Flask started")
    app.run(debug=True)