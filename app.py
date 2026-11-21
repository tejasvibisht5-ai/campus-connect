from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# =====================================================
# APP CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = os.environ.get(
    "CAMPUS_CONNECT_SECRET",
    "campus_connect_secret_key_change_this"
)

DATABASE = os.path.join(BASE_DIR, "campus connect_old.db")


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================================================
# CLUB DETAIL INFORMATION
# =====================================================

CLUB_INFORMATION = {
    "swaragini": {
        "overview": (
            "Swaragini is a music and performing arts community "
            "where students can explore their musical interests, "
            "develop confidence and showcase their talent."
        ),
        "activities": [
            "Singing and instrumental music sessions",
            "Music competitions and performances",
            "Cultural festival participation",
            "Collaborative music practice"
        ],
        "benefits": [
            "Improve musical and creative skills",
            "Build confidence through performances",
            "Collaborate with other talented students",
            "Participate in university cultural events"
        ]
    },

    "uttrayini": {
        "overview": (
            "Uttrayini celebrates culture, creativity and artistic "
            "expression. It provides students with opportunities "
            "to participate in cultural programmes and showcase "
            "their creative abilities."
        ),
        "activities": [
            "Cultural programmes and celebrations",
            "Traditional and contemporary performances",
            "Artistic and creative activities",
            "University cultural festival participation"
        ],
        "benefits": [
            "Explore cultural traditions",
            "Develop communication and teamwork",
            "Express creativity",
            "Build friendships across departments"
        ]
    },

    "coding club": {
        "overview": (
            "The Coding Club brings together students interested "
            "in programming, software development and emerging "
            "technologies. Members can learn, collaborate and "
            "work on practical technology projects."
        ),
        "activities": [
            "Programming and coding practice",
            "Technical workshops",
            "Problem-solving activities",
            "Student project development"
        ],
        "benefits": [
            "Improve programming skills",
            "Develop logical thinking",
            "Gain practical project experience",
            "Collaborate with technology enthusiasts"
        ]
    },

    "sports club": {
        "overview": (
            "The Sports Club encourages students to participate "
            "in physical activities, develop sportsmanship and "
            "represent the university in sporting events."
        ),
        "activities": [
            "Sports practice sessions",
            "Inter-department competitions",
            "Team games and tournaments",
            "University sports events"
        ],
        "benefits": [
            "Develop teamwork and discipline",
            "Improve coordination and sports skills",
            "Build leadership qualities",
            "Participate in university competitions"
        ]
    },

    "dance folks": {
        "overview": (
            "Dance Folks is a creative platform for students who "
            "enjoy dance and performance. Members can explore "
            "different dance styles, practise together and "
            "participate in university events."
        ),
        "activities": [
            "Group dance practice",
            "Dance workshops and rehearsals",
            "Stage performances",
            "Dance competitions and cultural events"
        ],
        "benefits": [
            "Develop dance and performance skills",
            "Improve confidence and coordination",
            "Work with a creative team",
            "Showcase talent at university events"
        ]
    }
}


# =====================================================
# EVENT DETAIL INFORMATION
# =====================================================

EVENT_INFORMATION = {
    "blood donation camp": {
        "overview": (
            "The Blood Donation Camp is an awareness initiative "
            "that encourages students to learn about the importance "
            "of blood donation and community health."
        ),
        "highlights": [
            "Blood donation awareness",
            "Information about community health",
            "Guidance from authorised medical professionals",
            "Student participation and volunteering"
        ],
        "audience": "Students and university community"
    },

    "music and cultural fest": {
        "overview": (
            "The Music and Cultural Fest brings together creativity, "
            "music and celebration. Students can enjoy performances "
            "and experience the cultural spirit of the university."
        ),
        "highlights": [
            "Live music and singing performances",
            "Cultural presentations",
            "Student talent showcases",
            "Entertainment and campus celebrations"
        ],
        "audience": "All interested university students"
    },

    "tech innovation day": {
        "overview": (
            "Tech Innovation Day provides a platform for students "
            "to explore technology, present innovative ideas and "
            "learn about programming and practical projects."
        ),
        "highlights": [
            "Technology demonstrations",
            "Student project showcases",
            "Coding and innovation activities",
            "Technical learning opportunities"
        ],
        "audience": "Technology enthusiasts and students"
    },

    "annual sports meet": {
        "overview": (
            "The Annual Sports Meet brings students together "
            "through sporting activities and friendly competitions. "
            "It celebrates teamwork, discipline and sportsmanship."
        ),
        "highlights": [
            "Sports competitions",
            "Team participation",
            "Athletic activities",
            "Awards and recognition"
        ],
        "audience": "Students interested in sports"
    }
}


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def init_db():

    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            faculty TEXT NOT NULL,
            description TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT NOT NULL UNIQUE COLLATE NOCASE,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            venue TEXT NOT NULL,
            icon TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            student_email TEXT NOT NULL COLLATE NOCASE,
            UNIQUE(event_id, student_email),
            FOREIGN KEY(event_id) REFERENCES events(id),
            FOREIGN KEY(student_email) REFERENCES students(email)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS club_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            club_id INTEGER NOT NULL,
            student_email TEXT NOT NULL COLLATE NOCASE,
            UNIQUE(club_id, student_email),
            FOREIGN KEY(club_id) REFERENCES clubs(id),
            FOREIGN KEY(student_email) REFERENCES students(email)
                ON DELETE CASCADE
        );
    """)

    # Add description column to an older events table.

    event_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(events)"
        ).fetchall()
    ]

    if "description" not in event_columns:
        conn.execute("""
            ALTER TABLE events
            ADD COLUMN description TEXT NOT NULL DEFAULT ''
        """)

    club_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(clubs)"
        ).fetchall()
    ]

    if "faculty_email" not in club_columns:
        conn.execute("ALTER TABLE clubs ADD COLUMN faculty_email TEXT")

    # =================================================
    # DEFAULT CLUBS - FIVE FEATURED CLUBS
    # =================================================

    default_clubs = [
        (
            "Swaragini",
            "Music and Cultural",
            "Faculty Coordinator",
            "A music and cultural club where students explore singing, music and stage performances.",
            "swaragini@gehu.ac.in",
            "9876543210",
            "swaragini123"
        ),
        (
            "Uttrayini",
            "Cultural",
            "Faculty Coordinator",
            "A creative platform celebrating culture, traditions, art and student participation.",
            "uttrayini@gehu.ac.in",
            "9876543211",
            "uttrayini123"
        ),
        (
            "Coding Club",
            "Technology",
            "Faculty Coordinator",
            "Learn programming, solve problems and collaborate on exciting technology projects.",
            "coding@gehu.ac.in",
            "9876543213",
            "coding123"
        ),
        (
            "Sports Club",
            "Sports",
            "Faculty Coordinator",
            "Participate in sporting activities, competitions and university sports events.",
            "sports@gehu.ac.in",
            "9876543214",
            "sports123"
        ),
        (
            "Photography Club",
            "Photography and Arts",
            "Faculty Coordinator",
            "Explore photography, develop creative skills and capture memorable campus moments.",
            "photography@gehu.ac.in",
            "9876543216",
            "photo123"
        ),
        (
            "Theatre Club",
            "Drama and Performing Arts",
            "Faculty Coordinator",
            "Explore acting, drama, storytelling and stage performances with fellow students.",
            "theatre@gehu.ac.in",
            "9876543217",
            "theatre123"
        )
    ]

    for club in default_clubs:

        exists = conn.execute("""
            SELECT id FROM clubs
            WHERE email = ? OR LOWER(name) = LOWER(?)
        """, (
            club[4],
            club[0]
        )).fetchone()

        if not exists:

            conn.execute("""
                INSERT INTO clubs
                (name, category, faculty, description, email, phone, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                club[0],
                club[1],
                club[2],
                club[3],
                club[4],
                club[5],
                generate_password_hash(club[6])
            ))

    # =================================================
    # DEFAULT EVENTS
    # Existing event records are not overwritten.
    # =================================================

    default_events = [
        (
            1,
            "Blood Donation Camp",
            "20 NOV 2026",
            "10:00 AM",
            "University Campus",
            "❤️",
            "A campus blood donation awareness and participation camp."
        ),
        (
            2,
            "Music and Cultural Fest",
            "25 NOV 2026",
            "5:00 PM",
            "Main Auditorium",
            "🎤",
            "Enjoy music, singing and cultural performances."
        ),
        (
            3,
            "Tech Innovation Day",
            "02 DEC 2026",
            "11:00 AM",
            "Computer Lab",
            "💻",
            "Explore technology, coding and innovative student projects."
        ),
        (
            4,
            "Sports Meet",
            "10 DEC 2026",
            "9:00 AM",
            "Sports Complex",
            "🏆",
            "Participate in exciting sports activities and competitions."
        ),
        (
            5,
            "business pitching",
            "15 DEC 2026",
            "11:00 AM",
            "Seminar Hall",
            "💡",
            "Present innovative business ideas, showcase your entrepreneurial skills and pitch your startup concepts to a panel of judges."
        ),
        (
            6,
            "Debate Competition",
            "20 DEC 2026",
            "10:00 AM",
            "Seminar Hall",
            "🎙️",
            "Showcase your communication skills and share your ideas."
        )
    ]
    for event in default_events:

        conn.execute("""
            INSERT OR IGNORE INTO events
            (id, name, date, time, venue, icon, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, event)

        # Only fill an empty description.
        # Existing event descriptions are preserved.

        conn.execute("""
            UPDATE events
            SET description = ?
            WHERE id = ?
            AND (description IS NULL OR description = '')
        """, (
            event[6],
            event[0]
        ))

    conn.commit()
    conn.close()


init_db()


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_club_information(club):

    name = club["name"].lower()

    for key, information in CLUB_INFORMATION.items():
        if key in name:
            return information

    return {
        "overview": club["description"],
        "activities": [
            "Club activities and interactive sessions",
            "Student participation programmes",
            "Skill development activities",
            "University events and initiatives"
        ],
        "benefits": [
            "Develop new skills",
            "Meet students with similar interests",
            "Improve teamwork",
            "Participate in campus activities"
        ]
    }


def get_event_information(event):

    name = event["name"].lower()

    for key, information in EVENT_INFORMATION.items():
        if key in name:
            return information

    return {
        "overview": event["description"],
        "highlights": [
            "Student participation",
            "Interactive activities",
            "Learning and engagement",
            "University community experience"
        ],
        "audience": "University students"
    }
def get_five_clubs():

    conn = get_db()

    clubs = [
        dict(row) for row in conn.execute("""
            SELECT id, name, category, faculty,
                   description, email, phone
            FROM clubs
            WHERE id IN (
                SELECT MIN(id)
                FROM clubs
                WHERE LOWER(TRIM(name)) IN (
                    'swaragini',
                    'uttrayini',
                    'uttaryini',
                    'coding club',
                    'sports club',
                    'photography club',
                    'theatre club'
                )
                GROUP BY LOWER(TRIM(name))
            )
            ORDER BY
                CASE LOWER(TRIM(name))
                    WHEN 'swaragini' THEN 1
                    WHEN 'uttrayini' THEN 2
                    WHEN 'uttaryini' THEN 2
                    WHEN 'coding club' THEN 3
                    WHEN 'sports club' THEN 4
                    WHEN 'photography club' THEN 5
                    WHEN 'theatre club' THEN 6
                END
            LIMIT 6
        """).fetchall()
    ]

    conn.close()

    return clubs
# =====================================================
# PASSWORD VALIDATION
# =====================================================

def is_strong_password(password):
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and any(not char.isalnum() for char in password)
    )


# =====================================================
# LOGIN DECORATORS
# =====================================================

def student_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("student_email"):
            flash("Please log in as a student first.")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


def club_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("club_email"):
            flash("Please log in with your club account first.")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


def faculty_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("faculty_email"):
            flash("Please log in as faculty first.")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():

    conn = get_db()

    events = [
        dict(row) for row in conn.execute(
            "SELECT * FROM events ORDER BY id"
        ).fetchall()
    ]

    conn.close()

    clubs = get_five_clubs()

    return render_template(
        "index.html",
        events=events,
        clubs=clubs
    )


# =====================================================
# EVENTS PAGE
# =====================================================

@app.route("/events")
def events_page():

    conn = get_db()

    events = [
        dict(row) for row in conn.execute(
            "SELECT * FROM events ORDER BY id"
        ).fetchall()
    ]

    conn.close()

    return render_template(
        "events.html",
        events=events
    )


# =====================================================
# EVENT DETAILS PAGE
# =====================================================

@app.route("/event/<int:event_id>")
def event_details(event_id):

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    conn.close()

    if not row:
        flash("Event not found.")
        return redirect(url_for("events_page"))

    event = dict(row)

    if not event.get("description"):
        event["description"] = (
            "Discover this university event and participate "
            "in campus activities."
        )

    information = get_event_information(event)

    event["overview"] = information["overview"]
    event["highlights"] = information["highlights"]
    event["audience"] = information["audience"]

    return render_template(
        "event-details.html",
        event=event
    )


# =====================================================
# CLUBS PAGE - ONLY FIVE CLUBS
# =====================================================

@app.route("/clubs")
def clubs_page():

    clubs = get_five_clubs()

    return render_template(
        "clubs.html",
        clubs=clubs
    )


# =====================================================
# CLUB DETAILS PAGE
# =====================================================

@app.route("/club/<int:club_id>")
def club_details(club_id):

    conn = get_db()

    row = conn.execute("""
        SELECT id, name, category, faculty,
               description, email, phone
        FROM clubs
        WHERE id = ?
    """, (club_id,)).fetchone()

    conn.close()

    if not row:
        flash("Club not found.")
        return redirect(url_for("clubs_page"))

    club = dict(row)

    information = get_club_information(club)

    club["overview"] = information["overview"]
    club["activities"] = information["activities"]
    club["benefits"] = information["benefits"]

    return render_template(
        "club-details.html",
        club=club
    )


# =====================================================
# REGISTER PAGE
# =====================================================

@app.route("/register")
def register():
    return render_template("register.html")


# =====================================================
# LOGIN PAGE
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip().lower()

        if not email or not password:
            return render_template(
                "login.html",
                error="Please enter your email and password."
            )

        conn = get_db()

        if role in ("", "student"):
            student = conn.execute(
                "SELECT * FROM students WHERE email = ?",
                (email,)
            ).fetchone()

            if student and check_password_hash(student["password"], password):
                conn.close()
                session.clear()
                session["student_email"] = student["email"]
                session["user_type"] = "student"
                return redirect(url_for("student_dashboard"))

        if role in ("", "faculty"):
            faculty = conn.execute(
                "SELECT * FROM faculty WHERE email = ?",
                (email,)
            ).fetchone()

            if faculty and check_password_hash(faculty["password"], password):
                conn.close()
                session.clear()
                session["faculty_email"] = faculty["email"]
                session["user_type"] = "faculty"
                return redirect(url_for("faculty_dashboard"))

        if role in ("", "club_admin", "club"):
            club = conn.execute(
                "SELECT * FROM clubs WHERE email = ?",
                (email,)
            ).fetchone()

            if club and check_password_hash(club["password"], password):
                conn.close()
                session.clear()
                session["club_email"] = club["email"]
                session["user_type"] = "club"
                return redirect(url_for("club_dashboard"))

        conn.close()
        return render_template(
            "login.html",
            error="Invalid email, password or selected role."
        )

    return render_template("login.html")


# STUDENT REGISTRATION
# =====================================================

@app.route("/student-register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        student = {
            "name": request.form.get("name", "").strip(),
            "student_id": request.form.get("student_id", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "department": request.form.get("department", "").strip(),
            "year": request.form.get("year", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "password": request.form.get("password", "")
        }

        if not all(student.values()):
            flash("Please fill in all required fields.")
            return render_template("std-register.html")

        if not is_strong_password(student["password"]):
            flash(
                "Password must be at least 8 characters and include uppercase, lowercase, number and special character."
            )
            return render_template("std-register.html")

        conn = get_db()

        existing = conn.execute("""
            SELECT id FROM students
            WHERE email = ? OR student_id = ?
        """, (
            student["email"],
            student["student_id"]
        )).fetchone()

        if existing:
            conn.close()
            flash("Email or Student ID is already registered.")
            return render_template("std-register.html")

        try:

            conn.execute("""
                INSERT INTO students
                (name, student_id, email, department, year, phone, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student["name"],
                student["student_id"],
                student["email"],
                student["department"],
                student["year"],
                student["phone"],
                generate_password_hash(student["password"])
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.rollback()
            conn.close()

            flash("Email or Student ID is already registered.")
            return render_template("std-register.html")

        conn.close()

        flash("Student registration successful. Please log in.")

        return redirect(url_for("student_success"))

    return render_template("std-register.html")


# =====================================================
# STUDENT SUCCESS
# =====================================================

@app.route("/student-success")
def student_success():
    return render_template("student-success.html")


# =====================================================
# CLUB REGISTRATION
# =====================================================

@app.route("/club-register", methods=["GET", "POST"])
def club_register():

    if request.method == "POST":

        club = {
            "name": request.form.get("club_name", "").strip(),
            "category": request.form.get("category", "").strip(),
            "faculty": request.form.get("faculty", "").strip(),
            "description": request.form.get("description", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "phone": request.form.get("phone", "").strip(),
            "password": request.form.get("password", "")
        }

        faculty_email = request.form.get("faculty_email", "").strip().lower()

        if not all(club.values()):
            flash("Please fill in all required fields.")
            return render_template("club-register.html")

        if not is_strong_password(club["password"]):
            flash(
                "Password must be at least 8 characters and include uppercase, lowercase, number and special character."
            )
            return render_template("club-register.html")

        conn = get_db()

        if faculty_email:
            faculty_record = conn.execute(
                "SELECT id FROM faculty WHERE email = ?",
                (faculty_email,)
            ).fetchone()

            if not faculty_record:
                conn.close()
                flash("Please enter the email of a registered faculty member.")
                return render_template("club-register.html")

        try:
            conn.execute("""
                INSERT INTO clubs
                (name, category, faculty, description, email, phone,
                 password, faculty_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                club["name"],
                club["category"],
                club["faculty"],
                club["description"],
                club["email"],
                club["phone"],
                generate_password_hash(club["password"]),
                faculty_email or None
            ))
            conn.commit()

        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            flash("This club email is already registered.")
            return render_template("club-register.html")

        conn.close()
        flash("Club registered successfully. Please log in.")
        return redirect(url_for("club_success"))

    return render_template("club-register.html")


# =====================================================
# FACULTY REGISTRATION
# =====================================================

@app.route("/faculty-register", methods=["GET", "POST"])
def faculty_register():

    if request.method == "POST":

        faculty = {
            "name": request.form.get("name", "").strip(),
            "employee_id": request.form.get("employee_id", "").strip(),
            "department": request.form.get("department", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "phone": request.form.get("phone", "").strip(),
            "password": request.form.get("password", "")
        }

        if not all(faculty.values()):
            flash("Please fill in all required fields.")
            return render_template("faculty-register.html")

        if not is_strong_password(faculty["password"]):
            flash(
                "Password must be at least 8 characters and include uppercase, lowercase, number and special character."
            )
            return render_template("faculty-register.html")

        conn = get_db()

        existing = conn.execute("""
            SELECT id FROM faculty
            WHERE email = ? OR employee_id = ?
        """, (
            faculty["email"],
            faculty["employee_id"]
        )).fetchone()

        if existing:
            conn.close()
            flash("Faculty email or Employee ID is already registered.")
            return render_template("faculty-register.html")

        try:
            conn.execute("""
                INSERT INTO faculty
                (name, employee_id, department, email, phone, password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                faculty["name"],
                faculty["employee_id"],
                faculty["department"],
                faculty["email"],
                faculty["phone"],
                generate_password_hash(faculty["password"])
            ))
            conn.commit()

        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            flash("Faculty email or Employee ID is already registered.")
            return render_template("faculty-register.html")

        conn.close()
        flash("Faculty registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("faculty-register.html")


# CLUB SUCCESS
# =====================================================

@app.route("/club-success")
def club_success():
    return render_template("club-success.html")


# =====================================================
# EVENT REGISTRATION
# =====================================================

@app.route("/register-event/<int:event_id>")
@student_required
def register_event(event_id):

    student_email = session["student_email"]

    conn = get_db()

    event = conn.execute(
        "SELECT id FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    if not event:

        conn.close()

        flash("Event not found.")
        return redirect(url_for("student_dashboard"))

    try:

        conn.execute("""
            INSERT INTO event_registrations
            (event_id, student_email)
            VALUES (?, ?)
        """, (
            event_id,
            student_email
        ))

        conn.commit()

        flash("Successfully registered for the event!")

    except sqlite3.IntegrityError:

        flash("You are already registered for this event.")

    finally:
        conn.close()

    return redirect(url_for("student_dashboard"))


# =====================================================
# JOIN CLUB
# =====================================================

@app.route("/join-club/<int:club_id>")
@student_required
def join_club(club_id):

    student_email = session["student_email"]

    conn = get_db()

    club = conn.execute(
        "SELECT id FROM clubs WHERE id = ?",
        (club_id,)
    ).fetchone()

    if not club:

        conn.close()

        flash("Club not found.")
        return redirect(url_for("clubs_page"))

    try:

        conn.execute("""
            INSERT INTO club_members
            (club_id, student_email)
            VALUES (?, ?)
        """, (
            club_id,
            student_email
        ))

        conn.commit()

        flash("You successfully joined the club!")

    except sqlite3.IntegrityError:

        flash("You are already a member of this club.")

    finally:
        conn.close()

    return redirect(url_for("student_dashboard"))


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@app.route("/student-dashboard")
@student_required
def student_dashboard():

    student_email = session["student_email"]

    conn = get_db()

    student_row = conn.execute("""
        SELECT id, name, student_id, email,
               department, year, phone
        FROM students
        WHERE email = ?
    """, (student_email,)).fetchone()

    if not student_row:

        conn.close()
        session.clear()

        flash("Student account not found.")
        return redirect(url_for("login"))

    student = dict(student_row)

    registered_events = [
        dict(row) for row in conn.execute("""
            SELECT e.*
            FROM events e
            JOIN event_registrations r
                ON e.id = r.event_id
            WHERE r.student_email = ?
            ORDER BY e.id
        """, (student_email,)).fetchall()
    ]

    joined_clubs = [
        dict(row) for row in conn.execute("""
            SELECT c.id, c.name, c.category, c.faculty,
                   c.description, c.email, c.phone
            FROM clubs c
            JOIN club_members m
                ON c.id = m.club_id
            WHERE m.student_email = ?
            ORDER BY c.id
        """, (student_email,)).fetchall()
    ]

    conn.close()

    return render_template(
        "student-dashboard.html",
        student=student,
        registered_events=registered_events,
        joined_clubs=joined_clubs
    )


# =====================================================
# CLUB DASHBOARD
# =====================================================

@app.route("/club-dashboard")
@club_required
def club_dashboard():

    club_email = session["club_email"]

    conn = get_db()

    club_row = conn.execute("""
        SELECT id, name, category, faculty,
               description, email, phone, faculty_email
        FROM clubs
        WHERE email = ?
    """, (club_email,)).fetchone()

    if not club_row:

        conn.close()
        session.clear()

        flash("Club account not found.")
        return redirect(url_for("login"))

    club = dict(club_row)

    joined_students = [
        dict(row) for row in conn.execute("""
            SELECT s.id, s.name, s.student_id, s.email,
                   s.department, s.year, s.phone
            FROM students s
            JOIN club_members m
                ON s.email = m.student_email
            WHERE m.club_id = ?
            ORDER BY s.name
        """, (club["id"],)).fetchall()
    ]

    conn.close()

    return render_template(
        "club-dashboard.html",
        club=club,
        students=joined_students,
        total_students=len(joined_students)
    )


# =====================================================
# =====================================================
# FACULTY DASHBOARD
# =====================================================

@app.route("/faculty-dashboard")
@faculty_required
def faculty_dashboard():

    faculty_email = session["faculty_email"]

    conn = get_db()

    faculty_row = conn.execute("""
        SELECT id, name, employee_id, department, email, phone
        FROM faculty
        WHERE email = ?
    """, (faculty_email,)).fetchone()

    if not faculty_row:
        conn.close()
        session.clear()
        flash("Faculty account not found.")
        return redirect(url_for("login"))

    faculty = dict(faculty_row)

    assigned_clubs = [
        dict(row) for row in conn.execute("""
            SELECT
                c.id, c.name, c.category, c.faculty,
                c.description, c.email, c.phone, c.faculty_email,
                (
                    SELECT COUNT(DISTINCT m.student_email)
                    FROM club_members m
                    WHERE m.club_id = c.id
                ) AS member_count
            FROM clubs c
            WHERE LOWER(c.faculty_email) = LOWER(?)
            ORDER BY c.name
        """, (faculty_email,)).fetchall()
    ]

    students = [
        dict(row) for row in conn.execute("""
            SELECT DISTINCT
                s.id, s.name, s.student_id, s.email,
                s.department, s.year, s.phone,
                c.name AS club_name,
                c.id AS club_id
            FROM students s
            JOIN club_members m
                ON s.email = m.student_email
            JOIN clubs c
                ON c.id = m.club_id
            WHERE LOWER(c.faculty_email) = LOWER(?)
            ORDER BY s.name
        """, (faculty_email,)).fetchall()
    ]

    upcoming_events = [
        dict(row) for row in conn.execute("""
            SELECT * FROM events
            ORDER BY id
        """).fetchall()
    ]

    conn.close()

    return render_template(
        "faculty-dashboard.html",
        faculty=faculty,
        assigned_clubs=assigned_clubs,
        students=students,
        upcoming_events=upcoming_events,
        total_clubs=len(assigned_clubs),
        total_students=len(students)
    )


# STUDENT PROFILE
# =====================================================

@app.route("/profile")
@student_required
def profile():

    student_email = session["student_email"]

    conn = get_db()

    row = conn.execute("""
        SELECT id, name, student_id, email,
               department, year, phone
        FROM students
        WHERE email = ?
    """, (student_email,)).fetchone()

    conn.close()

    if not row:

        session.clear()
        return redirect(url_for("login"))

    student = dict(row)

    return render_template(
        "profile.html",
        profile=student,
        student=student
    )


# =====================================================
# CLUB STUDENTS PAGE
# =====================================================

@app.route("/students")
@club_required
def students_list():

    club_email = session["club_email"]

    conn = get_db()

    club = conn.execute(
        "SELECT id FROM clubs WHERE email = ?",
        (club_email,)
    ).fetchone()

    if not club:

        conn.close()
        session.clear()
        return redirect(url_for("login"))

    students = [
        dict(row) for row in conn.execute("""
            SELECT s.id, s.name, s.student_id, s.email,
                   s.department, s.year, s.phone
            FROM students s
            JOIN club_members m
                ON s.email = m.student_email
            WHERE m.club_id = ?
            ORDER BY s.name
        """, (club["id"],)).fetchall()
    ]

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# =====================================================
# STUDENT PROFILE FOR CLUB
# =====================================================

@app.route("/student-profile/<student_id>")
@club_required
def student_profile(student_id):

    club_email = session["club_email"]

    conn = get_db()

    row = conn.execute("""
        SELECT s.id, s.name, s.student_id, s.email,
               s.department, s.year, s.phone
        FROM students s
        JOIN club_members m
            ON s.email = m.student_email
        JOIN clubs c
            ON c.id = m.club_id
        WHERE s.student_id = ? AND c.email = ?
    """, (
        student_id,
        club_email
    )).fetchone()

    conn.close()

    if not row:

        flash("Student not found in your club.")
        return redirect(url_for("club_dashboard"))

    return render_template(
        "student-profile.html",
        student=dict(row)
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("home"))


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)