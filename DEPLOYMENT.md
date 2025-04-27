# Syllabot - Database Project Details

## 1. Database Design

### a) E-R Diagram

```sql
-- Main Tables
CREATE TABLE school (
  schoolName VARCHAR(100) NOT NULL,
  schoolAddress TEXT DEFAULT NULL,
  PRIMARY KEY (schoolName)
);

CREATE TABLE department (
  DepartmentName VARCHAR(100) NOT NULL,
  schoolName VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (DepartmentName),
  FOREIGN KEY (schoolName) REFERENCES school (schoolName)
);

CREATE TABLE major (
  majorName VARCHAR(100) NOT NULL,
  departmentName VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (majorName),
  FOREIGN KEY (departmentName) REFERENCES department (DepartmentName)
);

CREATE TABLE location (
  address VARCHAR(200) NOT NULL,
  schoolName VARCHAR(100) NOT NULL,
  PRIMARY KEY (address, schoolName),
  FOREIGN KEY (schoolName) REFERENCES school (schoolName)
);

CREATE TABLE instructor (
  instructorID INT(11) NOT NULL,
  instructorName VARCHAR(100) DEFAULT NULL,
  departmentName VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (instructorID),
  FOREIGN KEY (departmentName) REFERENCES department (DepartmentName)
);

CREATE TABLE instructorrating (
  ratingID INT(11) NOT NULL,
  instructorRating INT(11) DEFAULT NULL,
  instructorID INT(11) DEFAULT NULL,
  PRIMARY KEY (ratingID),
  FOREIGN KEY (instructorID) REFERENCES instructor (instructorID)
);

CREATE TABLE course (
  courseID VARCHAR(50) DEFAULT NULL,
  courseName VARCHAR(255) DEFAULT NULL,
  departmentName VARCHAR(100) DEFAULT NULL,
  credit FLOAT DEFAULT NULL,
  description TEXT DEFAULT NULL,
  courseStatus VARCHAR(50) DEFAULT NULL
);

CREATE TABLE term (
  termID VARCHAR(8) NOT NULL,
  startDate DATE DEFAULT NULL,
  endDate DATE DEFAULT NULL,
  PRIMARY KEY (termID)
);

CREATE TABLE section (
  sectionID INT(11) NOT NULL,
  courseID VARCHAR(20) DEFAULT NULL,
  instructorID INT(11) DEFAULT NULL,
  termID VARCHAR(8) DEFAULT NULL,
  address VARCHAR(200) DEFAULT NULL,
  sectionType VARCHAR(20) DEFAULT NULL,
  sectionNo VARCHAR(10) DEFAULT NULL,
  PRIMARY KEY (sectionID),
  FOREIGN KEY (courseID) REFERENCES course (courseID),
  FOREIGN KEY (instructorID) REFERENCES instructor (instructorID),
  FOREIGN KEY (termID) REFERENCES term (termID),
  FOREIGN KEY (address) REFERENCES location (address)
);

CREATE TABLE sectionday (
  sectionID INT(11) NOT NULL,
  day VARCHAR(3) NOT NULL,
  PRIMARY KEY (sectionID, day),
  FOREIGN KEY (sectionID) REFERENCES section (sectionID)
);

CREATE TABLE sectiontime (
  startTime TIME NOT NULL,
  endTime TIME NOT NULL,
  sectionID INT(11) NOT NULL,
  PRIMARY KEY (startTime, endTime, sectionID),
  FOREIGN KEY (sectionID) REFERENCES section (sectionID)
);

CREATE TABLE student (
  StudentID VARCHAR(10) NOT NULL,
  schoolname VARCHAR(100) DEFAULT NULL,
  majorName VARCHAR(100) DEFAULT NULL,
  name VARCHAR(100) DEFAULT NULL,
  currentLevel VARCHAR(20) DEFAULT NULL,
  email VARCHAR(50) DEFAULT NULL,
  dateOfBirth DATE DEFAULT NULL,
  PRIMARY KEY (StudentID),
  FOREIGN KEY (schoolname) REFERENCES school (schoolName),
  FOREIGN KEY (majorName) REFERENCES major (majorName)
);

CREATE TABLE login (
  StudentID VARCHAR(10) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  PRIMARY KEY (StudentID, password_hash),
  FOREIGN KEY (StudentID) REFERENCES student (StudentID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE enrollment (
  studentID VARCHAR(10) NOT NULL,
  sectionID INT(11) NOT NULL,
  enrollStatus TINYINT(1) DEFAULT NULL,
  PRIMARY KEY (studentID, sectionID),
  FOREIGN KEY (studentID) REFERENCES student (StudentID),
  FOREIGN KEY (sectionID) REFERENCES section (sectionID)
);

CREATE TABLE temp_cart (
  session_id VARCHAR(36) NOT NULL,
  sectionID INT(11) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (session_id, sectionID),
  FOREIGN KEY (sectionID) REFERENCES section (sectionID)
);
```

## 2. Database Programming

### a) Database Hosting

Our database is hosted on Aiven's MySQL cloud service, a managed database-as-a-service platform. We chose Aiven for its:

- Free tier for development and testing
- High availability and reliability
- Built-in security features
- Automated backups
- Easy SSL/TLS configuration

The database is accessible through the Aiven console and can be connected to via standard MySQL clients using SSL encryption.

### b) Application Hosting Environment

The Syllabot application is hosted on a standard web server with the following requirements:

- Python 3.8 or higher
- Flask web framework
- MySQL client libraries
- WSGI server (for production deployment)

The application can be deployed in various environments:

1. **Development**: Local XAMPP/WAMP/MAMP server
2. **Testing**: Heroku or similar PaaS
3. **Production**: AWS, Azure, or GCP with proper load balancing

### c) Deployment Instructions

#### Prerequisites
- Python 3.8+
- pip (Python package manager)
- MySQL client tools
- Git

#### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd syllabot
```

#### Step 2: Set Up Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Database Connection
```bash
# Copy the example configuration file
cp config.py.example config.py

# Edit config.py with your database credentials
# For Aiven:
# MYSQL_HOST = "mysql-syllabot-syllabot.l.aivencloud.com"
# MYSQL_USER = "avnadmin" (or your custom username)
# MYSQL_PASSWORD = "your-password"
# MYSQL_DB = "defaultdb"
# MYSQL_PORT = 3306
# SSL_ENABLED = True
```

#### Step 5: Set Up the Database
```bash
# Option 1: Import from SQL dump
mysql -h <your-host> -P <port> -u <username> -p <database> < syllabot_test.sql

# Option 2: For Aiven with SSL
mysql --ssl-mode=REQUIRED -h <your-host> -P <port> -u <username> -p <database> < syllabot_test.sql
```

#### Step 6: Apply Database Security Settings
```bash
python apply_aiven_security.py
```

#### Step 7: Run the Application
```bash
# Development
python app.py

# Production with WSGI (e.g., Gunicorn)
gunicorn app:app
```

#### Step 8: Access the Application
Open your browser and navigate to:
- Development: http://localhost:5000
- Production: Your configured domain

### d) Advanced SQL Commands

The application utilizes several advanced SQL features:

1. **Stored Procedures**: 
   - `GetCoursesBySchool`: Retrieves all courses from a specific school
   - `GetInstructorAverageRating`: Calculates the average rating for an instructor
   - `getSectionSchedule`: Retrieves the schedule for a specific section with days and times

```sql
-- Example usage in app.py:
cursor.execute("CALL GetCoursesBySchool(%s)", (school_name,))
```

2. **User-Defined Functions**:
   - `find_course_sections`: Returns the number of sections for a course

```sql
-- Example usage in app.py:
cursor.execute("SELECT find_course_sections(%s)", (course_id,))
```

3. **Triggers**:
   - Time conflict detection for course registration

These advanced SQL features provide significant benefits:
- Improved performance by moving complex operations to the database layer
- Better data integrity through server-side validation
- Simplified application code by encapsulating logic in the database
- Consistent business rules enforcement across different applications

## 3. Database Security at the Database Level

### a) Security Target Users

The database security is primarily set for both developers and end users:

- **Developer security**: Controls what database operations developers can perform during development and maintenance
- **End user security**: Restricts what database operations the application can perform on behalf of different types of users

### b) Database-Level Access Control

We implemented a robust security model at the database level following the principle of least privilege through multiple user roles:

1. **Developer Role** (`syllabot_dev`):
   - Has full access to all database objects for development and maintenance
   - Used only in development environments

2. **Application Role** (`syllabot_app`):
   - Has minimum privileges needed for the application to function
   - Used as the default connection for general operations

3. **Student Role** (`student_role`):
   - Limited to specific operations needed for students
   - Can read course, section, and instructor data
   - Can manage their own cart and enrollments
   - Can only view/update their own profile

4. **Read-only Role** (`syllabot_readonly`):
   - Can only read data, with no ability to modify
   - Used for reporting and monitoring

### c) SQL Privilege Commands

```sql
-- Developer role (full access for development)
CREATE USER IF NOT EXISTS 'syllabot_dev'@'%' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON defaultdb.* TO 'syllabot_dev'@'%';

-- Application role (limited to needed operations)
CREATE USER IF NOT EXISTS 'syllabot_app'@'%' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON defaultdb.* TO 'syllabot_app'@'%';

-- Read-only role (for reporting, analysis)
CREATE USER IF NOT EXISTS 'syllabot_readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON defaultdb.* TO 'syllabot_readonly'@'%';

-- Student role (limited to student-specific operations)
CREATE USER IF NOT EXISTS 'student_role'@'%' IDENTIFIED BY 'student_password';

-- Students can view courses and sections
GRANT SELECT ON defaultdb.course TO 'student_role'@'%';
GRANT SELECT ON defaultdb.section TO 'student_role'@'%';
GRANT SELECT ON defaultdb.sectionday TO 'student_role'@'%';
GRANT SELECT ON defaultdb.sectiontime TO 'student_role'@'%';
GRANT SELECT ON defaultdb.instructor TO 'student_role'@'%';
GRANT SELECT ON defaultdb.instructorrating TO 'student_role'@'%';

-- Students can manage their cart and enrollments
GRANT SELECT, INSERT, DELETE ON defaultdb.Temp_Cart TO 'student_role'@'%';
GRANT SELECT, INSERT ON defaultdb.enrollment TO 'student_role'@'%';

-- Students can view/update their own profile
GRANT SELECT, UPDATE ON defaultdb.student TO 'student_role'@'%';

-- Apply the changes
FLUSH PRIVILEGES;
```

## 4. Database Security at the Application Level

### a) Implementation of Application-Level Security

The application implements several layers of security on top of the database-level security:

1. **Authentication**:
   - Password hashing using Werkzeug's `generate_password_hash` function
   - Session management for maintaining user state
   - Login validation with appropriate error handling
   - CSRF protection for form submissions

2. **Role-Based Access Control**:
   - Custom decorators for protecting routes:
     - `@login_required`: Ensures user is logged in
     - `@student_required`: Ensures user has student role
     - `@admin_required`: Ensures user has admin role

3. **Database Connection Management**:
   - The application selects the appropriate database user based on the current user's role
   - For student operations, it connects using `student_role` credentials
   - For admin operations, it uses `admin_role` credentials
   - This ensures that database access follows the principle of least privilege

4. **Data Validation and Sanitization**:
   - Input validation for all user-submitted data
   - Parameterized queries to prevent SQL injection
   - Escaping of output to prevent XSS attacks

5. **Error Handling**:
   - Custom error pages for 403 (Forbidden), 404 (Not Found), and 500 (Server Error)
   - Prevention of information leakage through generic error messages

### b) Code Snippets

1. **Role-Based Access Control Decorators**:

```python
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
```

2. **Role-Based Database Connection**:

```python
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
        
        # Select appropriate user based on role
        if role == 'admin' and is_aiven:
            conn_params['user'] = Config.MYSQL_USER
            conn_params['password'] = Config.MYSQL_PASSWORD
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
        return None
```

3. **Password Hashing and Validation**:

```python
# Registration: Hashing password
hashed_password = generate_password_hash(password)
cursor.execute(
    'INSERT INTO login (StudentID, password_hash) VALUES (%s, %s)',
    (student_id, hashed_password)
)

# Login: Validating password
cursor.execute('SELECT password_hash FROM login WHERE StudentID = %s', (username,))
password_data = cursor.fetchone()
if password_data and check_password_hash(password_data['password_hash'], password):
    # Authentication successful
```

4. **Parameterized Queries to Prevent SQL Injection**:

```python
# Safe query using parameterization
cursor.execute(
    "SELECT * FROM student WHERE StudentID = %s AND schoolname = %s",
    (student_id, school_name)
)

# Cart management with proper parameter handling
cursor.execute(
    "INSERT INTO Temp_Cart (session_id, sectionID, created_at) VALUES (%s, %s, NOW())",
    (session['cart_token'], section_id)
)
```