import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
from database import Database  # type: ignore
from table import DuplicateKeyError  # type: ignore

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

db = Database(base_dir=os.path.dirname(os.path.dirname(__file__)))

# Ensure 'users' table exists with primary key
def _ensure_users_table():
    """Create users table if it doesn't exist."""
    try:
        db.get_table("users")
    except FileNotFoundError:
        db.create_table(
            name="users",
            columns=[
                {"name": "id", "type": "int"},
                {"name": "name", "type": "str"},
                {"name": "email", "type": "str"}
            ],
            primary_key="id"
        )

@app.get("/")
def index():
    """Display user registration form and list of registered users."""
    _ensure_users_table()
    
    # Fetch all registered users
    users_table = db.get_table("users")
    registered_users = users_table.select()
    
    tables = db.list_tables()
    return render_template("index.html", tables=tables, registered_users=registered_users)

@app.post("/register")
def register():
    """Handle user registration form submission."""
    _ensure_users_table()
    
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    
    if not name or not email:
        flash("Name and email are required", "error")
        return redirect(url_for("index"))
    
    try:
        users_table = db.get_table("users")
        
        # Generate a simple ID (count + 1)
        user_id = users_table.count() + 1
        
        # Insert the new user
        user = users_table.insert({
            "id": user_id,
            "name": name,
            "email": email
        })
        flash(f"Successfully registered: {name} ({email})", "success")
    except DuplicateKeyError:
        flash(f"User with ID already exists", "error")
    except Exception as e:
        flash(f"Error registering user: {e}", "error")
    
    return redirect(url_for("index"))

@app.post("/create_table")
def create_table():
    name = request.form.get("table_name", "").strip()
    columns_spec = request.form.get("columns", "").strip()
    if not name or not columns_spec:
        flash("Table name and columns are required")
        return redirect(url_for("index"))
    cols = []
    try:
        for part in columns_spec.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                col, typ = part.split(":", 1)
            else:
                # default type
                col, typ = part, "str"
            cols.append({"name": col.strip(), "type": typ.strip()})
        db.create_table(name, cols)
        flash(f"Table '{name}' created")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for("index"))

@app.post("/insert")
def insert():
    table = request.form.get("table", "").strip()
    data = request.form.get("json_data", "").strip()
    try:
        import json
        values = json.loads(data or "{}")
        t = db.get_table(table)
        row = t.insert(values)
        flash(f"Inserted: {row}")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for("index"))

@app.post("/query")
def query():
    sql = request.form.get("sql", "").strip()
    try:
        result = db.execute(sql)
        flash(str(result))
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
