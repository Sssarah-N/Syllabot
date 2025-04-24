from flask import Flask, render_template, request
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

if __name__ == '__main__':
    app.run(debug=True)
