import mysql.connector

# Connect without specifying database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#Kirankumar07"
)

cursor = db.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_reservation")
cursor.execute("USE hotel_reservation")

# Read sql file
with open('tablecreation.txt', 'r') as f:
    sqlCommands = f.read().split(';')

for command in sqlCommands:
    if command.strip():
        try:
            cursor.execute(command)
        except Exception as e:
            print(f"Skipped/Error: {e}")

db.commit()
cursor.close()
db.close()
print("Database setup complete.")
