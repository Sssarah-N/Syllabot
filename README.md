# Syllabot - Course Registration System

Syllabot is a web application that allows students to view course offerings, build schedules, and manage their academic catalog.

## Features

- Browse courses by school, department, and credits
- Add/remove courses from a shopping cart
- View schedule with calendar visualization
- User authentication (login/registration)
- User profiles
- Multi-user support with centralized database
- Google OAuth login integration

## Technical Requirements

- Python 3.8+
- Flask web framework
- MySQL database (local or cloud-hosted)
- Web browser

## Setup & Installation

### 1. Clone the repository

```
git clone <repository-url>
cd syllabot
```

### 2. Set up a virtual environment (recommended)

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install required dependencies

```
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Local Database (Development)

1. Create a MySQL database named `syllabot`
2. Import the SQL schema from `syllabot_test.sql` file:
   ```
   mysql -u root -p syllabot < syllabot_test.sql
   ```

#### Option B: Shared/Public Database (Multi-user Support)

For multi-user support, we use a cloud-hosted MySQL database with Aiven:

1. Create an account on [Aiven](https://aiven.io/)
2. Set up a new MySQL service
3. Use the connection details in your configuration

### 5. Configuration

Copy the example configuration file and modify it with your database credentials:

```
cp config.py.example config.py
```

Then edit `config.py` with your database connection details:

```python
class Config:
    # Database Configuration
    MYSQL_HOST = "your-database-host"  # e.g., localhost or mysql-syllabot-syllabot.l.aivencloud.com
    MYSQL_USER = "your-username"
    MYSQL_PASSWORD = "your-password"
    MYSQL_DB = "defaultdb"  # or your custom database name
    MYSQL_PORT = 3306  # default MySQL port (may be different for cloud providers)
    
    # SSL Configuration for Aiven
    SSL_ENABLED = True  # Set to False for local MySQL
```

### 6. Run the Database Setup Scripts (if using Aiven)

If you're using Aiven, run the scripts in this order to properly set up the database:

```
python scripts/fix_section_tables.py
```

This script fixes the sectionday and sectiontime tables and ensures the stored procedures are correctly configured.

### 7. Run the application

```
python app.py
```

Access the application at http://localhost:5000

## Troubleshooting

### Common Issues

1. **Missing Flask Module**: Make sure you've activated your virtual environment before running the app.

2. **Database Connection Issues**: Verify your database credentials in `config.py` and ensure the database server is running.

3. **Table Not Found Errors**: If you encounter table not found errors, run the appropriate setup scripts in the `scripts/` directory.

## Multi-User Support

This application supports concurrent usage by multiple users through:

1. **Centralized Database:** The app can connect to a shared MySQL database hosted on a public server.
2. **Session Management:** Each user gets a unique session for their shopping cart and login status.
3. **Scalable Architecture:** The database schema is designed for multi-user environments.

## Project Structure

- `app.py`: Main application file with routes and logic
- `config.py`: Configuration settings
- `static/`: CSS, JavaScript, and image files
- `templates/`: HTML templates for the web pages
- `scripts/`: Utility scripts for database setup and maintenance

## Tables and Data Structure

Key tables in the database:

- `course`: Contains course information (ID, name, credits, etc.)
- `section`: Contains section information for each course
- `sectionday`: Contains the days on which each section meets
- `sectiontime`: Contains the time periods for each section
- `Temp_Cart`: Temporary storage for user shopping carts
- `student`: Student information for registered users
- `instructor`: Information about course instructors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Google OAuth Setup

To enable Google login, you need to set up a Google OAuth application:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Go to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Add "http://localhost:5000/login/google/authorized" to the Authorized redirect URIs
7. Copy the Client ID and Client Secret
8. Update the following values in app.py:
   ```python
   app.config["GOOGLE_OAUTH_CLIENT_ID"] = "YOUR_GOOGLE_CLIENT_ID"
   app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "YOUR_GOOGLE_CLIENT_SECRET"
   ``` 