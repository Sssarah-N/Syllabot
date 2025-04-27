@echo off
echo Connecting to Aiven MySQL to check users...
"C:\xampp\mysql\bin\mysql" --host=mysql-syllabot-syllabot.l.aivencloud.com --port=25840 --user=avnadmin --password=AVNS_18iQd0hdK7JR4o1_RAo --ssl -e "SELECT User, Host FROM mysql.user;"
echo Done. 