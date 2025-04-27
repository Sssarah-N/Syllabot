#!/bin/bash
# Setup environment variables for the Syllabot remote database connection
# Replace these values with your actual database credentials

# Uncomment and set these variables with your actual remote database information
# export MYSQL_HOST=your-mysql-host.aivencloud.com
# export MYSQL_PORT=12345
# export MYSQL_USER=avnadmin
# export MYSQL_PASSWORD=your-password
# export MYSQL_DB=syllabot

echo "Environment variables set successfully!"
echo
echo "Current configuration:"
echo "MYSQL_HOST: $MYSQL_HOST"
echo "MYSQL_PORT: $MYSQL_PORT"
echo "MYSQL_USER: $MYSQL_USER"
echo "MYSQL_DB: $MYSQL_DB"
echo "MYSQL_PASSWORD: [HIDDEN]"
echo
echo "To activate these settings, run this script using:"
echo "    source setup_env.sh"
echo
echo "To run the application with these settings:"
echo "    python app.py" 