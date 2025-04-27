-- Check if security users exist
SELECT User, Host FROM mysql.user 
WHERE User IN ('syllabot_dev', 'syllabot_app', 'student_role', 'syllabot_readonly');

-- Check privileges
SHOW GRANTS FOR 'student_role'@'%'; 