from flask import Flask, request, jsonify
import sqlite3
import datetime
import bcrypt
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey' 

# ---------------- GET CLIENT IP ----------------
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR']
    return request.remote_addr or "UNKNOWN"

# ---------------- LOGGING ----------------
def log_action(username, role, action):
    now = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    ip = get_client_ip()
    log_line = f"{now} | {role.upper()} |  {username}   |      {action}     | IP: {ip}\n"
    with open("system_logs.txt", "a") as f:
        f.write(log_line)

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            marks INTEGER,
            fee_status TEXT,
            enrollment_year TEXT,
            course TEXT
        )
    ''')

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            salary REAL,
            join_year TEXT
        )
    ''')

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            ip TEXT PRIMARY KEY,
            block_time TEXT
        )
    ''')

    
    def add_user(username, password, role):
        c.execute("SELECT * FROM users WHERE username=? AND role=?", (username, role))
        if not c.fetchone():
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))

    add_user("admin", "admin123", "admin")
    add_user("teacher1", "teacher123", "teacher")
    add_user("student", "student123", "student")
    conn.commit()
    conn.close()

init_db()

# ---------------- IP BLOCKING ----------------
failed_attempts = {}

def is_ip_blocked(ip):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT block_time FROM blocked_ips WHERE ip=?", (ip,))
    row = c.fetchone()
    conn.close()
    if row:
        block_time = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < block_time + datetime.timedelta(hours=24):
            return True
        else:
            unblock_ip(ip)
    return False

def block_ip(ip):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO blocked_ips (ip, block_time) VALUES (?, ?)", (ip, now))
    conn.commit()
    conn.close()

def unblock_ip(ip):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
    conn.commit()
    conn.close()

# ---------------- JWT VALIDATION ----------------
def validate_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split()[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return payload, None, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"error": "Token expired"}), 401
    # except jwt.InvalidTokenError:
    #     return None, jsonify({"error": "Invalid token"}), 401

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    ip = get_client_ip()

    if is_ip_blocked(ip):
        return jsonify({"success": False, "message": "Your IP is blocked for 24 hours due to multiple failed attempts."}), 403

    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "").strip().lower()

    if not username or not password or not role:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=? AND role=?", (username, role))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        token = jwt.encode(
            {"username": username, "role": role, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
            app.config['SECRET_KEY'], algorithm="HS256"
        )
        log_action(username, role, "LOGIN SUCCESS")
        failed_attempts.pop(ip, None)  
        return jsonify({"success": True, "message": "Login successful", "token": token})
    else:
        failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
        if failed_attempts[ip] >= 10:
            block_ip(ip)
            failed_attempts.pop(ip, None)
            log_action(username or "UNKNOWN", role or "UNKNOWN", "IP BLOCKED AFTER 10 FAILED ATTEMPTS")
            return jsonify({"success": False, "message": "Your IP has been blocked for 24 hours."}), 403
        log_action(username or "UNKNOWN", role or "UNKNOWN", "LOGIN FAILED")
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

# ---------------- LOGS VIEW ----------------
@app.route("/logs", methods=["GET"])
def view_logs():
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        with open("system_logs.txt", "r") as f:
            logs = f.readlines()
        return jsonify(logs)
    except FileNotFoundError:
        return jsonify([])

# ---------------- STUDENT ROUTES ----------------
@app.route("/students", methods=["GET"])
def get_students():
    payload, error, status = validate_token()
    if error:
        return error, status

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = [{"id": r[0], "name": r[1], "marks": r[2], "fee_status": r[3],
                 "enrollment_year": r[4], "course": r[5]} for r in c.fetchall()]
    conn.close()
    return jsonify(students)

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if row:
        student = {
            "id": row[0], "name": row[1], "marks": row[2],
            "fee_status": row[3], "enrollment_year": row[4], "course": row[5]
        }
        return jsonify(student), 200
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route("/students", methods=["POST"])
def add_student():
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO students (name, marks, fee_status, enrollment_year, course) VALUES (?, ?, ?, ?, ?)",
              (data["name"], data["marks"], data["fee_status"], data["enrollment_year"], data["course"]))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], "ADDED STUDENT")
    return jsonify({"message": "Student added"}), 201

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE students SET name=?, marks=?, fee_status=?, enrollment_year=?, course=? WHERE id=?",
              (data["name"], data["marks"], data["fee_status"], data["enrollment_year"], data["course"], id))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], f"UPDATED STUDENT {id}")
    return jsonify({"message": "Student updated"})

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], f"DELETED STUDENT {id}")
    return jsonify({"message": "Student deleted"})

# ---------------- TEACHER ROUTES ----------------
@app.route("/teachers", methods=["GET"])
def get_teachers():
    payload, error, status = validate_token()
    if error:
        return error, status

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM teachers")
    teachers = [{"id": r[0], "name": r[1], "subject": r[2], "salary": r[3], "join_year": r[4]} for r in c.fetchall()]
    conn.close()
    return jsonify(teachers)

@app.route("/teachers/<int:id>", methods=["GET"])
def get_teacher(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM teachers WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if row:
        teacher = {
            "id": row[0], "name": row[1], "subject": row[2],
            "salary": row[3], "join_year": row[4]
        }
        return jsonify(teacher), 200
    else:
        return jsonify({"error": "Teacher not found"}), 404

@app.route("/teachers", methods=["POST"])
def add_teacher():
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO teachers (name, subject, salary, join_year) VALUES (?, ?, ?, ?)",
              (data["name"], data["subject"], data["salary"], data["join_year"]))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], "ADDED TEACHER")
    return jsonify({"message": "Teacher added"}), 201

@app.route("/teachers/<int:id>", methods=["PUT"])
def update_teacher(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE teachers SET name=?, subject=?, salary=?, join_year=? WHERE id=?",
              (data["name"], data["subject"], data["salary"], data["join_year"], id))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], f"UPDATED TEACHER {id}")
    return jsonify({"message": "Teacher updated"})

@app.route("/teachers/<int:id>", methods=["DELETE"])
def delete_teacher(id):
    payload, error, status = validate_token()
    if error:
        return error, status

    if payload['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM teachers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_action(payload['username'], payload['role'], f"DELETED TEACHER {id}")
    return jsonify({"message": "Teacher deleted"})

if __name__ == "__main__":
    app.run(debug=True)
