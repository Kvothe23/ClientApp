from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import bleach

app = Flask(__name__)
app.secret_key = "1234"
DATABASE = "database.db"

#SECURITY HEADERS IMPLEMENTATION
@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="strict-origin"
    return response

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def sanitize_data(input_data):
    return bleach.clean(input_data)

@app.route("/", methods= ["GET", "POST"])
def login():
    if request.method == "POST":

        #SANITIZED DATA
        username = sanitize_data(request.form["username"])
        password =sanitize_data(request.form["password"])

        conn =get_db_connection()
        #SECURE AGAINST SQL INJECTION -> prepared statements
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = conn.execute(query, (username, password)).fetchone()
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
    sanitize_query = sanitize_data(search_query)
    conn = get_db_connection()

    #SECURE PREPARED STATEMENT AND SANITIZED DATA
    if search_query:
        query = "SELECT * FROM clients WHERE name LIKE ?"
        clients = conn.execute(query, (f"%{sanitize_query}%",)).fetchall()
    else:
        query = "SELECT * FROM clients"

    clients = conn.execute(query).fetchall()

    conn.close()
    return render_template("dashboard.html", clients=clients, search_query=sanitize_query)

@app.route("/add_client", methods=["GET", "POST"])
def add_client():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        #SANITIZED DATA
        name = sanitize_data(request.form["name"])
        email = sanitize_data(request.form["email"])

        conn = get_db_connection()
        # SECURE PREPARED STATEMENT
        conn.execute("INSERT INTO clients (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))
    return render_template("add_client.html")

@app.route("/delete_client/<int:client_id>")
def delete_client(client_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    #PREPARED STATEMENT
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
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