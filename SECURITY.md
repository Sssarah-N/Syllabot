# Syllabot Security Implementation

This document outlines the security architecture implemented in the Syllabot course registration system.

## Database Level Security

We've implemented a robust security model at the database level following the principle of least privilege:

### User Roles and Privileges

1. **Developer Role** (`syllabot_dev`)
   - Has full access to all database objects for development and maintenance
   - Should only be used by developers during development and maintenance

2. **Application Role** (`syllabot_app`)
   - Has the minimum privileges needed for the application to function
   - Used as the default connection for general application operations

3. **Student Role** (`student_role`)
   - Limited to specific operations needed for students:
     - Can read course, section, and instructor data
     - Can manage their own cart and enrollments
     - Can only update their own profile information

4. **Read-only Role** (`syllabot_readonly`)
   - Can only read data, with no ability to modify
   - Used for reporting, analysis, and monitoring

### Privilege Management

We carefully manage these types of privileges for different users:
- **SELECT**: Ability to read data
- **INSERT**: Ability to add new records
- **UPDATE**: Ability to modify existing records
- **DELETE**: Ability to remove records

## Application Level Security

The application enforces security through several mechanisms:

### Authentication

- Password hashing for secure credential storage
- Session management for persistent authentication
- Login validation with appropriate error handling

### Role-Based Access Control

The application implements role-based access with custom decorators:
- `@login_required`: Ensures the user is logged in
- `@student_required`: Ensures the user has student role
- `@admin_required`: Ensures the user has admin role

### Secure Database Connections

- The application selects the appropriate database user based on the current user's role
- For student-specific operations, it connects using the `student_role` credentials
- For admin operations, it uses the `admin_role` credentials
- This ensures that database access follows the principle of least privilege

### Error Handling

- Custom error pages for 403 (Forbidden), 404 (Not Found), and 500 (Server Error)
- Preventing information leakage through appropriate error messages

## Implementation 

The security implementation spans multiple components:

1. **Database Setup**: `aiven_db_security.sql`
   - Creates all necessary users and permissions

2. **Connection Management**: `connect_to_database()` function in `app.py`
   - Selects appropriate database credentials based on user role

3. **Access Control Decorators** in `app.py`
   - `@login_required`, `@student_required`, `@admin_required`
   - Protect routes from unauthorized access

4. **Configuration**: `config.py`
   - Stores credential information for different roles

## Production Security Recommendations

For production environments:
1. Use strong, unique passwords for each database user
2. Store sensitive credentials in environment variables, not in code
3. Implement HTTPS to secure data in transit
4. Regularly audit database access
5. Consider implementing additional security measures such as:
   - Rate limiting
   - Two-factor authentication
   - IP restrictions 