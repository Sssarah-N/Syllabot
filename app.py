from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

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


@app.route('/courses')
def courses():
    courses_by_school = {}
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # 1) sidebar data
        cursor.execute("SELECT schoolName FROM school")
        all_schools = [r[0] for r in cursor.fetchall()]

        # 2) read filters
        selected_schools  = request.args.getlist('school')
        selected_statuses = request.args.getlist('status')
        selected_credits = request.args.getlist('credits')   # e.g. ["3.0","4.5"]
        credit= [float(c) for c in selected_credits]
        

        # 3) decide which schools to show
        schools_to_show = selected_schools or all_schools

        # 4) for each school: fetch *all* courses, then Python-filter
        for school in schools_to_show:
            cursor.callproc('getCoursesBySchool', [school])

            # collect all rows returned by the proc
            raw = []
            for result in cursor.stored_results():
                raw.extend(result.fetchall())

            print(raw)

            # Python filter function
            def keep(course_row):
                # adjust these indices if your proc returns columns in a different order
                course_status  = course_row[3]    # e.g. “Open” / “Closed” / “Wait List”
                course_credits = course_row[2]    # an integer
                
                if selected_statuses and course_status not in selected_statuses:
                    return False
                if credit and course_credits not in credit:
                    return False
                return True

            # apply the filter in one list comprehension
            courses_by_school[school] = [r for r in raw if keep(r)]
            print(courses_by_school)

    except Error as e:
        print("DB Error:", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template(
        'courses.html',
        courses_by_school=courses_by_school,
        all_schools=all_schools,
        selected_schools=selected_schools,
        selected_statuses=selected_statuses,
        selected_credits=selected_credits
    )

@app.route('/cart')
def cart():
    sections = []
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM sections")
            sections = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return render_template('cart.html', sections = sections)

@app.route('/add-to-cart/<int:course_id>')
def add_to_cart(course_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.callproc('getCourseById', [course_id])
    row = None
    for res in cursor.stored_results():
        row = res.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return redirect(url_for('cart'))

    item = {
        'id':      row[0],
        'code':    row[1],
        'name':    row[2],
        'status':  row[3],
        'credits': float(row[4])
    }

    cart = session.get('cart', [])
    if not any(i['id'] == course_id for i in cart):
        cart.append(item)
        session['cart'] = cart

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

if __name__ == '__main__':
    app.run(debug=True)
