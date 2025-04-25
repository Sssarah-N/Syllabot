from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import mysql.connector
from mysql.connector import Error
from functools import wraps
from datetime import datetime
import uuid 
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "GSaB_bSREZ6vfZg1-58S62IhSL69fX1xum-pHrjIVZ4"
)

@app.before_request
def ensure_cart_token():
    if 'cart_token' not in session:
        # generate a new cart identifier
        session['cart_token'] = str(uuid.uuid4())

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='syllabot'
        )
        if connection.is_connected():
            print("Connected to the database")
        else:
            print("Failed to connect to the database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    schools = []
    try:
        connection = connect_to_database()
        print("Connection successful")
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT schoolName FROM school")
            schools = [row[0] for row in cursor.fetchall()]
            print("Fetched schools:", schools)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return render_template('index.html', schools=schools)


@app.route('/courses', methods=['GET', 'POST'])
# @login_required
def courses():
    courses_by_school = {}
    sections_by_course = {}
    instructor_names = {}

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Fetch all schools
        cursor.execute("SELECT schoolName FROM school")
        all_schools = [r[0] for r in cursor.fetchall()]

        # Read filters
        selected_schools = request.args.getlist('school')
        selected_statuses = request.args.getlist('status')
        selected_credits = request.args.getlist('credits')
        credit = [float(c) for c in selected_credits]

        # Decide which schools to show
        schools_to_show = selected_schools or all_schools

        # Fetch courses and sections for each school
        for school in schools_to_show:
            cursor.callproc('getCoursesBySchool', [school])
            raw_courses = []
            for result in cursor.stored_results():
                raw_courses.extend(result.fetchall())

            def keep(course_row):
                course_credits = course_row[3]
                course_status = course_row[4]
                
                if selected_statuses and course_status not in selected_statuses:
                    return False
                if credit and course_credits not in credit:
                    return False
                return True

            courses_by_school[school] = [r for r in raw_courses if keep(r)]

            # Fetch sections for each course
            for course in courses_by_school[school]:
                course_id = course[0]
                cursor.callproc('getSection', [course_id])
                sections = []
                for result in cursor.stored_results():
                    sections.extend(result.fetchall())
                sections_by_course[course_id] = sections

                # Fetch instructor names for each section
                for section in sections:
                    instructor_id = section[2]  # Assuming instructorID is at index 2
                    if instructor_id not in instructor_names:
                        cursor.execute("SELECT instructorname FROM instructor WHERE instructorID = %s", (instructor_id,))
                        instructor_name = cursor.fetchone()
                        if instructor_name:
                            instructor_names[instructor_id] = instructor_name[0]

    except Error as e:
        print("DB Error:", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template(
        'courses.html',
        courses_by_school=courses_by_school,
        sections_by_course=sections_by_course,
        instructor_names=instructor_names,
        all_schools=all_schools,
        selected_schools=selected_schools,
        selected_statuses=selected_statuses,
        selected_credits=selected_credits
    )

@app.route('/cart')
#@login_required
def cart():
    sections = []
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM section")
            sections = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return render_template('cart.html', sections=sections)



# ensure every visitor has a cart token
@app.route('/add-to-cart/', methods=['POST'])
def add_to_cart():
    section_id = request.form.get('section_id')
    print(section_id)
    #if not section_id:
    #    flash("No section selected.", "warning")
    #    return redirect(url_for('course_detail'))

    cart_token = session['cart_token']

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Temp_Cart (session_id, section_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
              created_at = CURRENT_TIMESTAMP
        """, (cart_token, section_id))

        conn.commit()
        flash("Section added to cart!", "success")

    except Error as e:
        flash(f"Database error: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cart'))


# --- Remove Course from Cart ---
@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    course_id = int(request.form['course_id'])
    cart = session.get('cart', [])
    cart = [i for i in cart if i['id'] != course_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/schedule')
#@login_required
def view_schedule():
    # 1) Get cart from session
    cart_items = session.get('cart', [])  # list of dicts with keys: id, code, name, ...

    # 2) Define hours to display (e.g., 8 AM to 5 PM)
    hours = list(range(8, 18))  # 8,9,...,17

    # 3) Build a schedule map: {(day, hour): {code, name, start, end}}
    schedule_map = {}
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        for item in cart_items:
            # Call stored proc to get schedule slots for this course
            cursor.callproc('getCourseSchedule', [item['id']])
            for result in cursor.stored_results():
                for row in result.fetchall():
                    # Assume row = (day_char, "HH:MM", "HH:MM")
                    day, start, end = row
                    start_hour = int(start.split(':')[0])
                    # Use the first matching hour slot
                    schedule_map[(day, start_hour)] = {
                        'code':  item['code'],
                        'name':  item['name'],
                        'start': start,
                        'end':   end
                    }
    except Error as e:
        print("DB Error:", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    # 4) Render the schedule grid
    return render_template(
        'schedule.html',
        hours=hours,
        schedule=schedule_map
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[0], password):
                session['logged_in'] = True
                return redirect(url_for('courses'))
            else:
                error = 'Invalid credentials. Please try again.'
        
        except Error as e:
            print(f"Error during login: {e}")
            error = 'An error occurred. Please try again later.'
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('login.html', error=error)

from werkzeug.security import generate_password_hash

def create_user(username, password):
    password_hash = generate_password_hash(password)
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
    except Error as e:
        print(f"Error creating user: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        else:
            # Call the create_user function to add the new user
            try:
                create_user(username, password)
                return redirect(url_for('login'))
            except Error as e:
                error = 'An error occurred during registration. Please try again.'
    
    return render_template('register.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)