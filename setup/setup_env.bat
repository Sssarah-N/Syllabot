@echo off
REM Setup environment variables for the Syllabot database connection

REM Choose which database to use (local or aiven)
set DB_TYPE=local

REM Set the DB_TYPE for the Config class
setx DB_TYPE %DB_TYPE%

IF "%DB_TYPE%"=="local" (
  REM Local database configuration
  set MYSQL_HOST=127.0.0.1
  set MYSQL_PORT=3306
  set MYSQL_USER=root
  set MYSQL_PASSWORD=
  set MYSQL_DB=syllabot
  echo Using LOCAL database configuration
) ELSE (
  REM Aiven database configuration
  set MYSQL_HOST=mysql-syllabot-syllabot.l.aivencloud.com
  set MYSQL_PORT=25840
  set MYSQL_USER=avnadmin
  set MYSQL_PASSWORD=AVNS_18iQd0hdK7JR4o1_RAo
  set MYSQL_DB=defaultdb
  echo Using AIVEN database configuration
)

echo Environment variables set successfully!
echo.
echo Current configuration:
echo DB_TYPE: %DB_TYPE%
echo MYSQL_HOST: %MYSQL_HOST%
echo MYSQL_PORT: %MYSQL_PORT%
echo MYSQL_USER: %MYSQL_USER%
echo MYSQL_DB: %MYSQL_DB%
echo MYSQL_PASSWORD: [HIDDEN]
echo.
echo To switch between database types, edit this file and change DB_TYPE to "local" or "aiven"
echo.
echo To run the application with these settings:
echo    python app.py 