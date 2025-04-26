from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
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
                        FROM sectionTime st 
                        JOIN sectionDay sd ON st.sectionID = sd.sectionID 
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
        is_home=True  # Flag to indicate this is now the home page
    )

@app.route('/cart')
def cart():
    sections = []
    cart_token = session.get('cart_token')

    if not cart_token:
        flash("No items in cart.", "warning")
        return render_template('cart.html', sections=sections)

    try:
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
    
    return render_template('cart.html', sections=sections)



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
        flash("Session token not found.", "warning")
        return redirect(url_for('cart'))

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
            flash("Section removed from cart.", "success")
    except Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('cart'))

from flask import session, flash, render_template, redirect, url_for
from mysql.connector import Error

@app.route('/schedule')
def view_schedule():
    # 1) Grab the cart_token from the session
    cart_token = session.get('cart_token')
    print(cart_token)
    if not cart_token:
        flash("No cart found.", "warning")
        print("No cart found.")
        return redirect(url_for('courses'))

    # 2) Fetch all sections in the cart, with their course info
    cart_items = []
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
              t.sectionID      AS section_id,
              s.courseID      AS course_id,
              s.sectionNo AS section_number,
              c.courseName    AS course_name
            FROM Temp_Cart t
            JOIN Section      s ON t.sectionID = s.sectionID
            JOIN Course       c ON s.courseID = c.courseID
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
        conn.close()

    # 3) Build the calendar grid
    hours = list(range(8, 25))   # e.g. 8AM–5PM
    schedule_map = {}

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        for item in cart_items:
            # call your stored proc; passing the section_id
            cursor.callproc('getSectionSchedule', [item['id']])
            for result in cursor.stored_results():
                for day, start_time, end_time in result.fetchall():
                    print(day, start_time, end_time)
                    start_hour = int(start_time.split(':')[0])
                    schedule_map[(day, start_hour)] = {
                        'code':  item['code'],
                        'name':  item['name'],
                        'sect':  item['sect'],
                        'start': start_time,
                        'end':   end_time
                    }

    except Error as e:
        app.logger.error(f"DB error building schedule: {e}")
        flash("Could not load your schedule.", "danger")
    finally:
        cursor.close()
        conn.close()

    # 4) Render the grid
    return render_template(
        'schedule.html',
        hours=hours,
        schedule=schedule_map
    )



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # If user is already logged in, redirect to courses
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('courses'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            error = 'Username and password are required'
        else:
            try:
                conn = connect_to_database()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    # Query student info along with login credentials
                    cursor.execute("""
                        SELECT s.StudentID, s.name, s.schoolname, s.majorName, s.currentLevel, 
                               s.email, l.password_hash 
                        FROM student s
                        JOIN login l ON s.StudentID = l.StudentID
                        WHERE s.StudentID = %s
                    """, (username,))
                    user = cursor.fetchone()
                    
                    if user and check_password_hash(user['password_hash'], password):
                        # Set session variables
                        session['logged_in'] = True
                        session['user_id'] = user['StudentID']
                        session['user_name'] = user['name']
                        session['school'] = user['schoolname']
                        session['major'] = user['majorName']
                        session['level'] = user['currentLevel']
                        session['email'] = user['email']
                        
                        # Redirect to the next page or requested URL
                        next_page = request.args.get('next')
                        if not next_page or not next_page.startswith('/'):
                            next_page = url_for('courses')
                        
                        flash('Login successful! Welcome, ' + user['name'], 'success')
                        return redirect(next_page)
                    else:
                        error = 'Invalid credentials. Please try again.'
                else:
                    error = 'Database connection error. Please try again later.'
            
            except Error as e:
                print(f"Error during login: {e}")
                error = 'An error occurred. Please try again later.'
            
            finally:
                if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        email = request.form.get('email')
        school = request.form.get('school')
        major = request.form.get('major')
        level = request.form.get('level')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not student_id or not name or not email or not school or not major or not level or not password:
            error = 'All fields are required'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long'
        else:
            try:
                conn = connect_to_database()
                if conn:
                    cursor = conn.cursor()
                    
                    # Check if student ID already exists
                    cursor.execute("SELECT StudentID FROM student WHERE StudentID = %s", (student_id,))
                    if cursor.fetchone():
                        error = 'Student ID already exists'
                    else:
                        # Insert new student
                        cursor.execute("""
                            INSERT INTO student (StudentID, schoolname, majorName, name, currentLevel, email)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (student_id, school, major, name, level, email))
                        
                        # Create login credentials
                        password_hash = generate_password_hash(password)
                        cursor.execute("""
                            INSERT INTO login (StudentID, password_hash)
                            VALUES (%s, %s)
                        """, (student_id, password_hash))
                        
                        conn.commit()
                        success = 'Registration successful! You can now login.'
            except Error as e:
                print(f"Error during registration: {e}")
                error = 'An error occurred during registration. Please try again.'
            finally:
                if conn and conn.is_connected():
                    cursor.close()
                    conn.close()
    
    # Get schools and majors for the dropdown
    schools = []
    majors = []
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT schoolName FROM school")
            schools = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT majorName FROM major")
            majors = [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching schools and majors: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return render_template('register.html', error=error, success=success, schools=schools, majors=majors)

@app.route('/profile', methods=['GET', 'POST'])
@login_required  # This ensures only logged-in users can access this page
def profile():
    # Get user info from the database for the most up-to-date data
    user_info = None
    enrolled_courses = []
    
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Get student information
            cursor.execute("""
                SELECT s.*, m.departmentName 
                FROM student s
                LEFT JOIN major m ON s.majorName = m.majorName
                WHERE s.StudentID = %s
            """, (session['user_id'],))
            user_info = cursor.fetchone()
            
            # Get user's enrolled courses and sections
            cursor.execute("""
                SELECT 
                    c.courseID, 
                    c.courseName, 
                    c.credit, 
                    s.sectionNo, 
                    i.instructorName,
                    e.enrollStatus,
                    GROUP_CONCAT(DISTINCT CONCAT(sd.day, ' ', 
                                TIME_FORMAT(st.startTime, '%h:%i %p'), '-', 
                                TIME_FORMAT(st.endTime, '%h:%i %p'))) as schedule
                FROM enrollment e
                JOIN section s ON e.sectionID = s.sectionID
                JOIN course c ON s.courseID = c.courseID
                JOIN instructor i ON s.instructorID = i.instructorID
                LEFT JOIN sectionday sd ON s.sectionID = sd.sectionID
                LEFT JOIN sectiontime st ON s.sectionID = st.sectionID
                WHERE e.studentID = %s
                GROUP BY c.courseID, s.sectionID
            """, (session['user_id'],))
            enrolled_courses = cursor.fetchall()
            
            # Handle profile updates
            if request.method == 'POST':
                # Get form data
                email = request.form.get('email')
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                # Update email if provided
                if email and email != user_info['email']:
                    cursor.execute("""
                        UPDATE student SET email = %s WHERE StudentID = %s
                    """, (email, session['user_id']))
                    conn.commit()
                    flash('Email updated successfully!', 'success')
                
                # Update password if provided
                if current_password and new_password and confirm_password:
                    # Verify current password
                    cursor.execute("""
                        SELECT password_hash FROM login WHERE StudentID = %s
                    """, (session['user_id'],))
                    password_data = cursor.fetchone()
                    
                    if password_data and check_password_hash(password_data['password_hash'], current_password):
                        if new_password == confirm_password:
                            if len(new_password) >= 8:
                                # Update password
                                password_hash = generate_password_hash(new_password)
                                cursor.execute("""
                                    UPDATE login SET password_hash = %s WHERE StudentID = %s
                                """, (password_hash, session['user_id']))
                                conn.commit()
                                flash('Password updated successfully!', 'success')
                            else:
                                flash('New password must be at least 8 characters long.', 'danger')
                        else:
                            flash('New passwords do not match.', 'danger')
                    else:
                        flash('Current password is incorrect.', 'danger')
                
                # Refresh user data after updates
                cursor.execute("""
                    SELECT s.*, m.departmentName 
                    FROM student s
                    LEFT JOIN major m ON s.majorName = m.majorName
                    WHERE s.StudentID = %s
                """, (session['user_id'],))
                user_info = cursor.fetchone()
    
    except Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while retrieving your profile.', 'danger')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return render_template('profile.html', user=user_info, enrolled_courses=enrolled_courses)

if __name__ == '__main__':
    app.run(debug=True)