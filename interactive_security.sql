-- Create Developer role
CREATE USER IF NOT EXISTS 'syllabot_dev'@'%' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON defaultdb.* TO 'syllabot_dev'@'%';

-- Create Application role
CREATE USER IF NOT EXISTS 'syllabot_app'@'%' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON defaultdb.* TO 'syllabot_app'@'%';

-- Create Read-only role
CREATE USER IF NOT EXISTS 'syllabot_readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON defaultdb.* TO 'syllabot_readonly'@'%';

-- Create Student role
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

FLUSH PRIVILEGES;

-- Verify the users were created
SELECT 'VERIFICATION: Security users' AS operation;
SELECT User, Host FROM mysql.user 
WHERE User IN ('syllabot_dev', 'syllabot_app', 'student_role', 'syllabot_readonly');

-- Check some privileges
SELECT 'VERIFICATION: Student privileges' AS operation;
SHOW GRANTS FOR 'student_role'@'%'; 