from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from mysql.connector import Error
from functools import wraps
from datetime import datetime, timedelta
import uuid 
import os
from config import Config
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "GSaB_bSREZ6vfZg1-58S62IhSL69fX1xum-pHrjIVZ4"
)

# Clean up old temporary cart items - run periodically
def cleanup_temporary_carts():
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            # Delete cart items older than 24 hours
            # This assumes the Temp_Cart table has a created_at column
            expiration = datetime.now() - timedelta(hours=24)
            cursor.execute("DELETE FROM Temp_Cart WHERE created_at < %s AND session_id NOT LIKE 'user_%'", 
                         (expiration,))
            conn.commit()
            deleted_count = cursor.rowcount
            print(f"Cleaned up {deleted_count} expired cart items")
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error cleaning up carts: {e}")

@app.before_request
def ensure_cart_token():
    # Check if we need to generate a new cart token
    if 'cart_token' not in session:
        # For anonymous users, generate a temporary cart token
        # This will be lost when the browser session ends
        session['cart_token'] = str(uuid.uuid4())
        session['is_temporary'] = True
    
    # For logged in users, maintain their cart_token
    if 'logged_in' in session and session.get('is_temporary'):
        # If user just logged in and had a temporary cart, convert it
        # Get the temporary cart items and associate them with the user
        old_token = session['cart_token']
        
        # Check if user_id exists in session
        if 'user_id' in session:
            new_token = f"user_{session['user_id']}"
            
            try:
                # Transfer cart items to the user's permanent cart
                conn = connect_to_database()
                if conn:
                    cursor = conn.cursor()
                    # First, check if there are items in the temporary cart
                    cursor.execute("SELECT COUNT(*) FROM Temp_Cart WHERE session_id = %s", (old_token,))
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        # Update the session_id to the user's permanent ID
                        cursor.execute("UPDATE Temp_Cart SET session_id = %s WHERE session_id = %s", 
                                      (new_token, old_token))
                        conn.commit()
                    cursor.close()
                    conn.close()
            except Exception as e:
                print(f"Error transferring cart: {e}")
            
            # Update session with permanent cart token
            session['cart_token'] = new_token
            session.pop('is_temporary', None)

# Enhanced security decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'student':
            flash('Access denied: Student privileges required', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'admin':
            flash('Access denied: Administrator privileges required', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Connection function that selects the appropriate database user based on role
def connect_to_database(role=None):
    try:
        # Determine if we're using Aiven
        is_aiven = Config.SSL_ENABLED
        
        # Set up connection parameters
        conn_params = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'database': Config.MYSQL_DB
        }
        
        # For admin on Aiven, use the main Aiven credentials to avoid access issues
        if role == 'admin' and is_aiven:
            print("Using main Aiven credentials for admin connection")
            conn_params['user'] = Config.MYSQL_USER  # use avnadmin
            conn_params['password'] = Config.MYSQL_PASSWORD  # use Aiven password
        elif role == 'student':
            conn_params['user'] = Config.STUDENT_USER
            conn_params['password'] = Config.STUDENT_PASSWORD
        elif role == 'admin':
            conn_params['user'] = Config.ADMIN_USER
            conn_params['password'] = Config.ADMIN_PASSWORD
        else:
            # Default application user
            conn_params['user'] = Config.MYSQL_USER
            conn_params['password'] = Config.MYSQL_PASSWORD
        
        # Add SSL for Aiven
        if is_aiven:
            print(f"Connecting to Aiven MySQL at {Config.MYSQL_HOST} as {conn_params['user']}")
            conn_params.update({
                'ssl_disabled': False,
                'ssl_verify_cert': False
            })
        
        connection = mysql.connector.connect(**conn_params)
        
        if connection.is_connected():
            print(f"Successfully connected to database as {conn_params['user']}")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        if role == 'admin' and 'Access denied' in str(e):
            print("Access denied with admin credentials, retrying with default credentials")
            try:
                # Try with default credentials as fallback
                conn_params['user'] = Config.MYSQL_USER
                conn_params['password'] = Config.MYSQL_PASSWORD
                connection = mysql.connector.connect(**conn_params)
                if connection.is_connected():
                    print(f"Connected with fallback credentials")
                return connection
            except Error as fallback_error:
                print(f"Fallback connection failed: {fallback_error}")
        return None

@app.route('/')
def index():
    return redirect(url_for('courses'))

@app.route('/courses', methods=['GET', 'POST'])
# @login_required
def courses():
    courses_by_school = {}
    sections_by_course = {}
    instructor_names = {}

    # Get the user's cart items
    cart_items = []
    if 'cart_token' in session:
        try:
            cart_conn = connect_to_database()
            if cart_conn:
                cart_cursor = cart_conn.cursor()
                cart_cursor.execute("SELECT sectionID FROM Temp_Cart WHERE session_id = %s", 
                                   (session['cart_token'],))
                cart_items = [str(row[0]) for row in cart_cursor.fetchall()]
                cart_cursor.close()
                cart_conn.close()
        except Error as e:
            print(f"Error fetching cart items: {e}")

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
        search_query = request.args.get('search', '').strip()
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
                course_id = course_row[0]
                course_name = course_row[1]
                course_credits = course_row[3]
                course_status = course_row[5]
                
                # Apply search filter if present
                if search_query and search_query.lower() not in course_id.lower() and search_query.lower() not in course_name.lower():
                    return False
                
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

                # Fetch instructor names and section times for each section
                for section in sections:
                    section_id = section[0]
                    instructor_id = section[2]

                    # Fetch instructor name
                    if instructor_id not in instructor_names:
                        cursor.execute("SELECT instructorname FROM instructor WHERE instructorID = %s", (instructor_id,))
                        instructor_name = cursor.fetchone()
                        if instructor_name:
                            instructor_names[instructor_id] = instructor_name[0]
                    
                    # Fetch section times and days
                    cursor.execute("""
                        SELECT st.startTime, st.endTime, sd.day 
                        FROM sectiontime st 
                        JOIN sectionday sd ON st.sectionID = sd.sectionID 
                        WHERE st.sectionID = %s
                    """, (section_id,))
                    times = cursor.fetchall()
                    
                    # Add times to the section tuple
                    section_list = list(section)
                    section_list.append(times)
                    sections_by_course[course_id][sections_by_course[course_id].index(section)] = tuple(section_list)

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
        selected_credits=selected_credits,
        cart_items=cart_items,
        is_home=True,  # Flag to indicate this is now the home page
        is_admin=session.get('role') == 'admin'  # Flag to indicate if the user is an admin
    )

@app.route('/cart')
def cart():
    sections = []
    cart_token = session.get('cart_token')

    if not cart_token:
        flash("No items in cart.", "warning")
        return render_template('cart.html', sections=sections, is_admin=session.get('role') == 'admin')

    try:
        # Use default database connection for all users
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Retrieve sections with instructor, course, time, location and ratings
            cursor.execute("""
                SELECT 
                    s.sectionID,
                    s.courseID,
                    i.instructorName,
                    s.termID,
                    s.address,
                    s.sectionType,
                    s.sectionNo,
                    c.courseName,
                    c.credit,
                    c.courseStatus,
                    GROUP_CONCAT(
                        CONCAT(sd.day, ': ',
                               TIME_FORMAT(st.startTime, '%h:%i %p'),
                               ' - ',
                               TIME_FORMAT(st.endTime, '%h:%i %p')
                        ) SEPARATOR '<br>'
                    ) as schedule_time,
                    (SELECT ir.instructorRating 
                     FROM instructorrating ir 
                     WHERE ir.courseID = s.courseID AND ir.instructorID = s.instructorID) as instructor_rating
                FROM section s
                JOIN Temp_Cart tc ON s.sectionID = tc.sectionID
                JOIN course c ON s.courseID = c.courseID
                JOIN instructor i ON s.instructorID = i.instructorID
                LEFT JOIN sectionday sd ON s.sectionID = sd.sectionID
                LEFT JOIN sectiontime st ON s.sectionID = st.sectionID
                WHERE tc.session_id = %s
                GROUP BY s.sectionID
            """, (cart_token,))
            sections = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return render_template('cart.html', sections=sections, is_admin=session.get('role') == 'admin')

@app.route('/get-cart-courses')
def get_cart_courses():
    cart_token = session.get('cart_token')
    
    # If user is not logged in and being redirected to login page,
    # return a different status code that won't trigger error messages
    if 'logged_in' not in session and request.referrer and 'login' in request.referrer:
        return jsonify({'success': True, 'courses': [], 'redirected': True})
    
    if not cart_token:
        return jsonify({'success': False, 'message': 'No cart found'})
    
    courses = []
    try:
        # Use default database connection for all users
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Retrieve sections with necessary data
            cursor.execute("""
                SELECT 
                    s.sectionID,
                    s.courseID as code,
                    c.courseName as name,
                    s.sectionNo as section,
                    GROUP_CONCAT(
                        CONCAT(sd.day, ' ',
                               TIME_FORMAT(st.startTime, '%H:%i'),
                               '-',
                               TIME_FORMAT(st.endTime, '%H:%i')
                        ) SEPARATOR ', '
                    ) as schedule,
                    MIN(TIME_FORMAT(st.startTime, '%H:%i')) as start_time,
                    MAX(TIME_FORMAT(st.endTime, '%H:%i')) as end_time,
                    MIN(sd.day) as day
                FROM section s
                JOIN Temp_Cart tc ON s.sectionID = tc.sectionID
                JOIN course c ON s.courseID = c.courseID
                LEFT JOIN sectionday sd ON s.sectionID = sd.sectionID
                LEFT JOIN sectiontime st ON s.sectionID = st.sectionID
                WHERE tc.session_id = %s
                GROUP BY s.sectionID
            """, (cart_token,))
            
            courses = cursor.fetchall()
            
            # Convert to list of dicts and ensure sectionID is always a string
            formatted_courses = []
            for course in courses:
                course_dict = dict(course)
                # Ensure sectionID is a string
                course_dict['sectionID'] = str(course_dict['sectionID'])
                formatted_courses.append(course_dict)
                
            courses = formatted_courses
            
            print(f"Returning {len(courses)} cart courses")
    except Error as e:
        print(f"Error fetching cart courses: {e}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return jsonify({'success': True, 'courses': courses})

# ensure every visitor has a cart token
@app.route('/add_to_cart/', methods=['POST'])
def add_to_cart():
    section_id = request.form.get('section_id')
    cart_token = session['cart_token']
    
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Check if the section is already in the cart
        cursor.execute("SELECT COUNT(*) FROM Temp_Cart WHERE session_id = %s AND sectionID = %s", 
                      (cart_token, section_id))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Already in cart
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Already in cart', 'already_in_cart': True})
            else:
                flash("This section is already in your cart.", "info")
                return redirect(url_for('courses'))
        
        # Not in cart, proceed with insert
        cursor.execute("""
            INSERT INTO Temp_Cart (session_id, sectionID)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE 
              created_at = CURRENT_TIMESTAMP
        """, (cart_token, section_id))

        conn.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Section added to cart!'})
        else:
            flash("Section added to cart!", "success")

    except Error as e:
        print("MYSQL ERROR:", e)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Could not add to cart.'})
        else:
            flash("Could not add to cart.", "danger")

    finally:
        cursor.close()
        conn.close()
    
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(url_for('cart'))
    else:
        return jsonify({'success': True, 'message': 'Section added to cart!'})


# --- Remove Course from Cart ---
@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    section_id = request.form.get('section_id')
    cart_token = session.get('cart_token')  # Assuming the session token is stored in the session

    if not cart_token:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Session token not found'})
        flash("Session token not found.", "warning")
        return redirect(url_for('cart'))

    success = False
    message = ""
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            # Delete the section from Temp_Cart where session_id and section_id match
            cursor.execute("""
                DELETE FROM Temp_Cart
                WHERE session_id = %s AND sectionID = %s
            """, (cart_token, section_id))
            connection.commit()
            success = True
            message = "Section removed from cart."
            if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                flash(message, "success")
    except Error as e:
        message = f"Database error: {e}"
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash(message, "danger")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
        
    # Handle regular form posts
    return redirect(url_for('cart'))

@app.route('/schedule')
def view_schedule():
    # 1) Grab the cart_token from the session
    cart_token = session.get('cart_token')
    
    if not cart_token:
        flash("No cart found.", "warning")
        return redirect(url_for('courses'))

    # 2) Fetch all sections in the cart, with their course info
    cart_items = []
    try:
        # Use default database connection for all users
        connection = connect_to_database()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
              t.sectionID      AS section_id,
              s.courseID      AS course_id,
              s.sectionNo AS section_number,
              c.courseName    AS course_name
            FROM Temp_Cart t
            JOIN section      s ON t.sectionID = s.sectionID
            JOIN course       c ON s.courseID = c.courseID
            WHERE t.session_id = %s
        """, (cart_token,))

        for row in cursor.fetchall():
            cart_items.append({
                'id':   row['section_id'],
                'code': row['course_id'],
                'name': row['course_name'],
                'sect': row['section_number']
            })
        print(cart_items)

    except Error as e:
        app.logger.error(f"DB error fetching cart items: {e}")
        flash("Could not load your cart.", "danger")
        return redirect(url_for('courses'))
    finally:
        cursor.close()
        connection.close()

    # 3) Build the calendar grid
    hours = list(range(8, 25))   # e.g. 8AM–5PM
    schedule_map = {}

    try:
        # Use default database connection for all users
        connection = connect_to_database()
        cursor = connection.cursor()
        for item in cart_items:
            # call your stored proc; passing the section_id
            cursor.callproc('getSectionSchedule', [item['id']])
            for result in cursor.stored_results():
                for day, start_time, end_time in result.fetchall():
                    print(day, start_time, end_time)
                    start_hour = int(start_time.split(':')[0])
                    
                    # Format times to remove seconds (HH:MM)
                    formatted_start = ':'.join(str(start_time).split(':')[:2]) 
                    formatted_end = ':'.join(str(end_time).split(':')[:2])
                    
                    schedule_map[(day, start_hour)] = {
                        'code':  item['code'],
                        'name':  item['name'],
                        'sect':  item['sect'],
                        'start': formatted_start,
                        'end':   formatted_end
                    }

    except Error as e:
        app.logger.error(f"DB error building schedule: {e}")
        flash("Could not load your schedule.", "danger")
    finally:
        cursor.close()
        connection.close()

    # 4) Render the grid
    return render_template(
        'schedule.html',
        hours=hours,
        schedule=schedule_map,
        is_admin=session.get('role') == 'admin'
    )



@app.route('/login', methods=['GET', 'POST'])
def login():
    majors = ["Computer Science", "Biology", "Chemistry", "Physics", "Mathematics", "Engineering", "Business", "Economics", "Psychology", "Sociology"]
    schools = ["College of Arts and Science", "Stern School of Business", "Tandon School of Engineering", "Tisch School of the Arts"]

    # Remember the referrer for redirection after login
    if request.method == 'GET' and request.referrer and 'login' not in request.referrer:
        session['login_referrer'] = request.referrer

    if request.method == 'POST':
        # User login logic
        username = request.form['username']
        password = request.form['password']
        
        # Connect using default application credentials
        conn = connect_to_database()
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('login.html', majors=majors, schools=schools)
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if it's a student - first get student info
            cursor.execute('SELECT * FROM student WHERE StudentID = %s', (username,))
            account = cursor.fetchone()
            
            # Debug the account data
            print("Account from DB:", account)
            
            if account:
                # Get the password from login table
                cursor.execute('SELECT password_hash FROM login WHERE StudentID = %s', (username,))
                password_data = cursor.fetchone()
                
                # Check if password matches
                if password_data and check_password_hash(password_data['password_hash'], password):
                    # Set session variables for student
                    session['logged_in'] = True
                    # Use consistent session variable names
                    session['user_id'] = account['StudentID']  # Used in profile.html
                    session['name'] = account['name']
                    session['email'] = account['email']
                    session['level'] = account['currentLevel']
                    session['role'] = 'student'
                    
                    # Debug session data
                    print("Session after login:", session)
                    
                    # The before_request handler will transfer any temporary cart items
                    # to the permanent user cart on the next request
                    
                    flash('Login successful', 'success')
                    
                    # Redirect to next page, referrer, or default to view_schedule
                    next_page = request.args.get('next')
                    referrer = session.pop('login_referrer', None)
                    
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    elif referrer:
                        return redirect(referrer)
                    else:
                        return redirect(url_for('view_schedule'))
            
            # If not a student, check if it's an admin (username: admin)
            if username == 'admin':
                # Simplified admin login check - just compare with configured admin password
                if password == Config.ADMIN_PASSWORD:
                    # Set session variables for admin
                    session['logged_in'] = True
                    session['user_id'] = 'admin'
                    session['name'] = 'Administrator'
                    session['role'] = 'admin'
                    
                    flash('Administrator login successful', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    print(f"Admin login failed - incorrect password")
            
            # If none of the above, credentials are invalid
            flash('Invalid credentials', 'danger')
            
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login error. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    # Check if the register tab should be active
    register_active = request.args.get('register') == 'true'
    return render_template('login.html', majors=majors, schools=schools, register_active=register_active)

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        school = request.form['school']
        major = request.form['major']
        level = request.form['level']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('login', register='true'))
        
        # Connect to the database
        conn = connect_to_database()
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('login', register='true'))
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if student_id already exists
            cursor.execute('SELECT * FROM student WHERE StudentID = %s', (student_id,))
            account = cursor.fetchone()
            
            if account:
                flash('Student ID already exists!', 'danger')
                return redirect(url_for('login', register='true'))
            
            # Check if email already exists
            cursor.execute('SELECT * FROM student WHERE email = %s', (email,))
            account = cursor.fetchone()
            
            if account:
                flash('Email already exists!', 'danger')
                return redirect(url_for('login', register='true'))
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert new student (without password in student table)
            cursor.execute(
                'INSERT INTO student (StudentID, schoolname, majorName, name, currentLevel, email) VALUES (%s, %s, %s, %s, %s, %s)',
                (student_id, school, major, name, level, email)
            )
            
            # Insert password into login table
            cursor.execute(
                'INSERT INTO login (StudentID, password_hash) VALUES (%s, %s)',
                (student_id, hashed_password)
            )
            
            conn.commit()
            
            flash('Registration successful! You can now login.', 'success')
            
            return redirect(url_for('login'))
        except Error as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('login', register='true'))
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('login', register='true'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'logged_in' not in session:
        flash('Please log in to access your profile', 'warning')
        return redirect(url_for('courses'))
    
    user_info = None
    enrolled_courses = []
    student_id = session.get('user_id')
    
    if not student_id:
        return redirect(url_for('login'))
    
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get student information
            cursor.execute("SELECT * FROM student WHERE StudentID = %s", (student_id,))
            user_info = cursor.fetchone()
            
            if user_info:
                # Get department information for the student's major
                if user_info.get('majorName'):
                    cursor.execute("""
                        SELECT majorName 
                        FROM student 
                        WHERE studentID = %s
                    """, (user_info['majorName'],))
                    dept_result = cursor.fetchone()
                    if dept_result:
                        user_info['departmentName'] = dept_result['departmentName']
            
                # Get user's enrolled courses
                # cursor.execute("""
                #     SELECT 
                #         c.courseID, 
                #         c.courseName, 
                #         c.credit, 
                #         s.sectionNo, 
                #         i.instructorName,
                #         e.enrollStatus,
                #         GROUP_CONCAT(DISTINCT CONCAT(sd.day, ' ', 
                #                     TIME_FORMAT(st.startTime, '%h:%i %p'), '-', 
                #                     TIME_FORMAT(st.endTime, '%h:%i %p'))) as schedule
                #     FROM enrollment e
                #     JOIN section s ON e.sectionID = s.sectionID
                #     JOIN course c ON s.courseID = c.courseID
                #     JOIN instructor i ON s.instructorID = i.instructorID
                #     LEFT JOIN sectionday sd ON s.sectionID = sd.sectionID
                #     LEFT JOIN sectiontime st ON s.sectionID = st.sectionID
                #     WHERE e.studentID = %s
                #     GROUP BY c.courseID, s.sectionID
                # """, (student_id,))
                # enrolled_courses = cursor.fetchall()
                
                # Handle profile updates
                if request.method == 'POST':
                    # Get form data
                    email = request.form.get('email')
                    date_of_birth = request.form.get('date_of_birth')
                    school = request.form.get('school')
                    major = request.form.get('major')
                    current_password = request.form.get('current_password')
                    new_password = request.form.get('new_password')
                    confirm_password = request.form.get('confirm_password')
                    
                    updates_made = False
                    
                    # Update email if provided and changed
                    if email and email != user_info['email']:
                        print(f"Updating email from {user_info['email']} to {email}")
                        cursor.execute("UPDATE student SET email = %s WHERE StudentID = %s", 
                                      (email, student_id))
                        updates_made = True
                    
                    # Update school if provided and changed
                    if school and school != user_info['schoolname']:
                        print(f"Updating school from {user_info['schoolname']} to {school}")
                        cursor.execute("UPDATE student SET schoolname = %s WHERE StudentID = %s",
                                      (school, student_id))
                        updates_made = True
                        
                    # Update major if provided and changed
                    if major and major != user_info['majorName']:
                        print(f"Updating major from {user_info['majorName']} to {major}")
                        cursor.execute("UPDATE student SET majorName = %s WHERE StudentID = %s",
                                      (major, student_id))
                        updates_made = True
                    
                    # Update date of birth if provided and changed
                    if date_of_birth:
                        # Convert string date to proper date object if needed
                        try:
                            from datetime import datetime
                            formatted_dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                            
                            # Check if it's different from current value
                            current_dob = user_info.get('dateOfBirth')
                            if not current_dob or formatted_dob != current_dob:
                                cursor.execute("UPDATE student SET dateOfBirth = %s WHERE StudentID = %s", 
                                             (formatted_dob, student_id))
                                updates_made = True
                        except Exception as e:
                            print(f"Error updating date of birth: {e}")
                    
                    # Update password if provided
                    if current_password and new_password and confirm_password:
                        # Verify current password
                        cursor.execute("SELECT password_hash FROM login WHERE StudentID = %s", 
                                      (student_id,))
                        password_data = cursor.fetchone()
                        
                        if password_data and check_password_hash(password_data['password_hash'], current_password):
                            if new_password == confirm_password:
                                if len(new_password) >= 8:
                                    # Update password
                                    password_hash = generate_password_hash(new_password)
                                    cursor.execute("UPDATE login SET password_hash = %s WHERE StudentID = %s", 
                                                 (password_hash, student_id))
                                    updates_made = True
                                else:
                                    flash('New password must be at least 8 characters long.', 'danger')
                            else:
                                flash('New passwords do not match.', 'danger')
                        else:
                            flash('Current password is incorrect.', 'danger')
                    
                    # Commit changes if any were made
                    if updates_made:
                        conn.commit()
                        flash('Profile updated successfully!', 'success')
                        
                        # Refresh user data after updates
                        cursor.execute("SELECT * FROM student WHERE StudentID = %s", (student_id,))
                        user_info = cursor.fetchone()
                        
                        # Get department information again
                        # if user_info.get('majorName'):
                        #     cursor.execute("SELECT departmentName FROM major WHERE majorName = %s", 
                        #                  (user_info['majorName'],))
                        #     dept_result = cursor.fetchone()
                        #     if dept_result:
                        #         user_info['departmentName'] = dept_result['departmentName']
                
    except Exception as e:
        print(f"Error in profile: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return render_template('profile.html', user=user_info, enrolled_courses=enrolled_courses, is_admin=session.get('role') == 'admin')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = {
        'total_students': 0,
        'total_courses': 0,
        'total_sections': 0,
        'total_enrollments': 0,
    }
    
    recent_activities = []
    
    try:
        # Connect using admin role credentials
        conn = connect_to_database(role='admin')
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get database statistics
            cursor.execute("SELECT COUNT(*) as count FROM student")
            stats['total_students'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM course")
            stats['total_courses'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM section")
            stats['total_sections'] = cursor.fetchone()['count']
            
            # cursor.execute("SELECT COUNT(*) as count FROM enrollment")
            # stats['total_enrollments'] = cursor.fetchone()['count']
            
            # Get recent enrollments with corrected JOIN using StudentID
            # cursor.execute("""
            #     SELECT e.enrollDate, s.name as student_name, c.courseID, c.courseName
            #     FROM enrollment e
            #     JOIN student s ON e.studentID = s.StudentID
            #     JOIN section sec ON e.sectionID = sec.sectionID
            #     JOIN course c ON sec.courseID = c.courseID
            #     ORDER BY e.enrollDate DESC
            #     LIMIT 10
            # """)
            # recent_activities = cursor.fetchall()
            
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error fetching admin data: {e}")
        flash("Error retrieving system information", "danger")
    
    return render_template(
        'admin_dashboard.html',
        stats=stats,
        recent_activities=recent_activities
    )

@app.route('/admin/users')
@admin_required
def admin_users():
    # Very visible start marker
    print("\n" + "*" * 50)
    print("ADMIN_USERS ROUTE IS BEING EXECUTED")
    print("*" * 50 + "\n")
    
    students = []
    
    try:
        # Connect using admin role credentials
        print("Attempting to connect to database with admin role...")
        conn = connect_to_database(role='admin')
        if conn:
            print("Successfully connected to database")
            cursor = conn.cursor(dictionary=True)
            
            # Get all students with correctly mapped field names
            print("Executing SQL query to fetch students...")
            sql_query = """
                SELECT 
                    StudentID, 
                    name, 
                    email, 
                    schoolname,
                    majorName
                FROM student 
            """
            print(f"SQL Query: {sql_query}")
            cursor.execute(sql_query)
            students = cursor.fetchall()
            
            # Debug prints
            print(f"Number of students found: {len(students)}")
            if students:
                print(f"First student data: {students[0]}")
            else:
                print("No students found in the database")
                
                # Try a simpler query to debug
                print("Trying a simple COUNT query...")
                cursor.execute("SELECT COUNT(*) as count FROM student")
                student_count = cursor.fetchone()['count']
                print(f"Simple count query returned: {student_count} students")
                
                if student_count > 0:
                    print("Students exist, but the detailed query might have issues.")
                    cursor.execute("SELECT * FROM student LIMIT 1")
                    first_student = cursor.fetchone()
                    print(f"Raw student data: {first_student}")
            
            cursor.close()
            conn.close()
        else:
            print("Failed to connect to database")
    except Exception as e:
        import traceback
        print(f"Error fetching users data: {e}")
        print("Exception traceback:")
        print(traceback.format_exc())
        flash("Error retrieving user information", "danger")
    
    # Debug: Check what we're sending to the template
    print(f"Rendering template with {len(students)} students")
    
    # Very visible end marker
    print("\n" + "*" * 50)
    print("END OF ADMIN_USERS ROUTE")
    print("*" * 50 + "\n")
    
    return render_template(
        'admin_users.html',
        students=students
    )

@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = []
    
    try:
        # Connect using admin role credentials
        conn = connect_to_database(role='admin')
        if conn:
            cursor = conn.cursor()
            
            # Get all courses
            cursor.execute("""
                SELECT c.courseID, c.courseName, c.departmentName, c.credit, 
                       c.description, c.courseStatus
                FROM course c
                ORDER BY c.departmentName, c.courseID
            """)
            courses = cursor.fetchall()
            
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error fetching courses data: {e}")
        flash("Error retrieving course information", "danger")
    
    return render_template(
        'admin_courses.html',
        courses=courses
    )

@app.route('/admin/add-course', methods=['POST'])
@admin_required
def admin_add_course():
    if request.method == 'POST':
        # Get form data
        course_id = request.form['courseID']
        course_name = request.form['courseName']
        department_name = request.form['departmentName']
        credits = request.form['credits']
        description = request.form['description']
        course_status = request.form['courseStatus']
        
        # Connect to database
        conn = connect_to_database(role='admin')
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('admin_courses'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if course ID already exists
            cursor.execute('SELECT * FROM course WHERE courseID = %s', (course_id,))
            existing_course = cursor.fetchone()
            
            if existing_course:
                flash('A course with this ID already exists!', 'danger')
                return redirect(url_for('admin_courses'))
            
            # Check if department exists
            cursor.execute('SELECT * FROM department WHERE DepartmentName = %s', (department_name,))
            department = cursor.fetchone()
            
            if not department:
                flash('The specified department does not exist!', 'danger')
                return redirect(url_for('admin_courses'))
            
            # Insert new course
            cursor.execute(
                'INSERT INTO course (courseID, courseName, departmentName, credit, description, courseStatus) VALUES (%s, %s, %s, %s, %s, %s)',
                (course_id, course_name, department_name, credits, description, course_status)
            )
            
            conn.commit()
            
            flash('Course added successfully!', 'success')
            
        except Exception as e:
            conn.rollback()
            print(f"Error adding course: {e}")
            flash('An error occurred while adding the course. Please try again.', 'danger')
            
        finally:
            cursor.close()
            conn.close()
        
    return redirect(url_for('admin_courses'))

# Add new student route for admin
@app.route('/admin/add-student', methods=['POST'])
@admin_required
def admin_add_student():
    if request.method == 'POST':
        # Get form data
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        level = request.form['level']
        school = request.form['school']
        major = request.form['major']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin_users'))
        
        # Connect to database
        conn = connect_to_database(role='admin')
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('admin_users'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if student_id already exists
            cursor.execute('SELECT * FROM student WHERE StudentID = %s', (student_id,))
            account = cursor.fetchone()
            
            if account:
                flash('Student ID already exists!', 'danger')
                return redirect(url_for('admin_users'))
            
            # Check if email already exists
            cursor.execute('SELECT * FROM student WHERE email = %s', (email,))
            account = cursor.fetchone()
            
            if account:
                flash('Email already exists!', 'danger')
                return redirect(url_for('admin_users'))
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert new student
            cursor.execute(
                'INSERT INTO student (StudentID, schoolname, majorName, name, currentLevel, email) VALUES (%s, %s, %s, %s, %s, %s)',
                (student_id, school, major, name, level, email)
            )
            
            # Insert password into login table
            cursor.execute(
                'INSERT INTO login (StudentID, password_hash) VALUES (%s, %s)',
                (student_id, hashed_password)
            )
            
            conn.commit()
            
            flash('Student added successfully!', 'success')
            
        except Exception as e:
            import traceback
            print(f"Error adding student: {e}")
            print(traceback.format_exc())
            flash('An error occurred while adding the student. Please try again.', 'danger')
            
        finally:
            cursor.close()
            conn.close()
        
    return redirect(url_for('admin_users'))

# Edit student route for admin
@app.route('/admin/edit-student/<student_id>', methods=['POST'])
@admin_required
def admin_edit_student(student_id):
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        school = request.form['school']
        major = request.form['major']
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Connect to database
        conn = connect_to_database(role='admin')
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('admin_users'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if student exists
            cursor.execute('SELECT * FROM student WHERE StudentID = %s', (student_id,))
            student = cursor.fetchone()
            
            if not student:
                flash('Student not found!', 'danger')
                return redirect(url_for('admin_users'))
            
            # Check if email already exists but belongs to a different student
            cursor.execute('SELECT * FROM student WHERE email = %s AND StudentID != %s', (email, student_id))
            account = cursor.fetchone()
            
            if account:
                flash('Email already used by another student!', 'danger')
                return redirect(url_for('admin_users'))
            
            # Update student information
            cursor.execute(
                'UPDATE student SET name = %s, email = %s, schoolname = %s, majorName = %s WHERE StudentID = %s',
                (name, email, school, major, student_id)
            )
            
            # Update password if a new one was provided
            if new_password:
                if new_password != confirm_password:
                    flash('New passwords do not match!', 'danger')
                    return redirect(url_for('admin_users'))
                
                # Hash the new password
                hashed_password = generate_password_hash(new_password)
                
                # Update password in login table
                cursor.execute(
                    'UPDATE login SET password_hash = %s WHERE StudentID = %s',
                    (hashed_password, student_id)
                )
            
            conn.commit()
            
            flash('Student updated successfully!', 'success')
            
        except Exception as e:
            import traceback
            print(f"Error updating student: {e}")
            print(traceback.format_exc())
            flash('An error occurred while updating the student. Please try again.', 'danger')
            
        finally:
            cursor.close()
            conn.close()
        
    return redirect(url_for('admin_users'))

# Delete student route for admin
@app.route('/admin/delete-student/<student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    if request.method == 'POST':
        # Connect to database
        conn = connect_to_database(role='admin')
        if not conn:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('admin_users'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if student exists
            cursor.execute('SELECT * FROM student WHERE StudentID = %s', (student_id,))
            student = cursor.fetchone()
            
            if not student:
                flash('Student not found!', 'danger')
                return redirect(url_for('admin_users'))
            
            # Delete login information first (to handle foreign key constraint)
            cursor.execute('DELETE FROM login WHERE StudentID = %s', (student_id,))
            
            # Then delete the student
            cursor.execute('DELETE FROM student WHERE StudentID = %s', (student_id,))
            
            conn.commit()
            
            flash('Student deleted successfully!', 'success')
            
        except Exception as e:
            import traceback
            print(f"Error deleting student: {e}")
            print(traceback.format_exc())
            flash('An error occurred while deleting the student. Please try again.', 'danger')
            
        finally:
            cursor.close()
            conn.close()
        
    return redirect(url_for('admin_users'))

# Error handlers
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run cleanup on startup
    cleanup_temporary_carts()
    
    # Start the app
    app.run(debug=True)