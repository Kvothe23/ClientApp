import sqlite3

conn = sqlite3.connect("database.db")
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')
conn.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
)
''')
conn.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin', 'admin')")
conn.execute("INSERT INTO users (username, password, role) VALUES ('user', 'password', 'user')")

conn.commit()
conn.close()
print("Database started")