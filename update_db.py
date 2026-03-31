import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Kirankumar07",
        database="hotel_reservation"
    )
    cursor = db.cursor()
    # Add password column if it doesn't exist
    cursor.execute("""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'hotel_reservation'
        AND TABLE_NAME = 'Guests'
        AND COLUMN_NAME = 'password'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE Guests ADD COLUMN password VARCHAR(255)")
        print("Column 'password' added successfully.")
    else:
        print("Column 'password' already exists.")
    
    db.commit()
    cursor.close()
    db.close()
except Exception as e:
    print(f"Error: {e}")
