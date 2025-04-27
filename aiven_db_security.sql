-- Aiven MySQL Database Security Setup
--
-- This script establishes database-level security for the Syllabot course registration system.
-- It follows the principle of least privilege, creating specific database users with only
-- the permissions needed for their roles.
--
-- Security Model:
-- 1. Different user roles with specific privileges:
--    - Developer role: Full access for development and maintenance
--    - Application role: General application operations with limited permissions
--    - Student role: Limited access only to needed tables for student operations
--    - Read-only role: For reporting and analysis with no write access
--
-- 2. Permission types are carefully managed:
--    - SELECT: Ability to read data
--    - INSERT: Ability to add new records
--    - UPDATE: Ability to modify existing records
--    - DELETE: Ability to remove records
--
-- 3. This works with application-level security to enforce:
--    - User authentication
--    - Role-based access control
--    - Data access controls based on user identity
--
-- To apply this security model:
-- 1. Run this script on your Aiven MySQL database
-- 2. Configure the application to use the appropriate credentials based on role
-- 3. Update passwords to strong, secure values in production

-- 1. Create different user roles
-- Note: Replace 'password' with secure passwords in production

-- Developer role (full access for development)
CREATE USER IF NOT EXISTS 'syllabot_dev'@'%' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON defaultdb.* TO 'syllabot_dev'@'%';

-- Application role (limited to needed operations)
CREATE USER IF NOT EXISTS 'syllabot_app'@'%' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON defaultdb.* TO 'syllabot_app'@'%';

-- Read-only role (for reporting, analysis)
CREATE USER IF NOT EXISTS 'syllabot_readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON defaultdb.* TO 'syllabot_readonly'@'%';

-- 2. Create specific role for student operations
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