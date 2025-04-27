# Syllabot Deployment Guide

This guide explains how to set up Syllabot with a shared/public database that allows multiple users to access the application simultaneously.

## Prerequisites

- Python 3.8+
- Flask
- MySQL client tools (for database export/import)
- A MySQL database hosting account (we recommend Aiven's free tier)

## Setting Up a Public Database

### Option 1: Aiven Free MySQL (Recommended)

1. Sign up for an Aiven account at [aiven.io](https://aiven.io/free-mysql-database)
2. Create a new MySQL service with the free plan
3. Once created, note the following connection details:
   - Host name
   - Port
   - Database name
   - Username
   - Password
   - SSL Certificate (if required)

### Option 2: Alternative MySQL Providers

Other services you might consider:
- Filess.io (Free tier with 10MB storage)
- db4free.net (Free MySQL hosting)
- Clever Cloud (Free tier with 256MB storage)

## Exporting Your Local Database

1. Export your existing database to a file:
   ```
   python export_db.py
   ```
   This will create `syllabot_export.sql` file with your database schema and data.

2. Import the file to your new cloud database using one of these methods:
   - Using the provider's web interface (if available)
   - Using the MySQL command line client:
     ```
     mysql -h [host] -P [port] -u [username] -p [database] < syllabot_export.sql
     ```
   - Using a database management tool like phpMyAdmin, MySQL Workbench, etc.

## Configuring the Application

1. Set up environment variables for your database connection:

   On Windows:
   ```
   set MYSQL_HOST=your_host
   set MYSQL_USER=your_username
   set MYSQL_PASSWORD=your_password
   set MYSQL_DB=your_database
   set MYSQL_PORT=your_port
   ```

   On Linux/macOS:
   ```
   export MYSQL_HOST=your_host
   export MYSQL_USER=your_username
   export MYSQL_PASSWORD=your_password
   export MYSQL_DB=your_database
   export MYSQL_PORT=your_port
   ```

2. For deployment, you should set these in your hosting provider's environment variable configuration.

## Testing the Connection

1. Run the application:
   ```
   python app.py
   ```

2. Verify the application connects to the remote database by checking the console output.

3. Test that multiple users can access and use the application simultaneously.

## Common Issues

1. **Connection Timeouts**: Make sure your database host allows connections from your application's IP address.

2. **SSL Requirements**: Some providers require SSL for connections. You may need to modify the connection parameters to include SSL certificates.

3. **Connection Limits**: Be aware of the maximum concurrent connections allowed by your database plan (especially on free tiers).

4. **Database Size Limits**: Free plans often have storage limits. Monitor your database size to avoid hitting these limits.

## Production Considerations

For a production environment:
1. Use environment variables to store sensitive connection details
2. Consider using a reverse proxy like Nginx
3. Use a production-grade WSGI server like Gunicorn
4. Implement proper backup strategies
5. Monitor database performance and connection counts 