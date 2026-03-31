from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_hotel'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Kirankumar07",
        database="hotel_reservation"
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_data = request.form
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Guests WHERE email=%s", (form_data['email'],))
        if cursor.fetchone():
            flash("Email already registered. Please login.", "error")
            return redirect('/register')
            
        cursor.execute("""
            INSERT INTO Guests (name, email, phone, address, id_proof, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            form_data['name'], form_data['email'], form_data['phone'], 
            form_data.get('address', ''), form_data.get('id_proof', ''), 
            form_data['password']
        ))
        db.commit()
        cursor.close()
        db.close()
        flash("Registration successful! Please login.", "success")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Guests WHERE email=%s AND password=%s", (email, password))
        guest = cursor.fetchone()
        cursor.close()
        db.close()
        
        if guest:
            session['guest_id'] = guest['guest_id']
            session['guest_name'] = guest['name']
            return redirect('/')
        else:
            flash("Invalid email or password", "error")
            return redirect('/login')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    if 'guest_id' not in session:
        return redirect('/login')
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms WHERE status='Available'")
    rooms = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.booking_id, r.room_type, b.check_in, b.check_out, r.price
        FROM Bookings b
        JOIN Rooms r ON b.room_id = r.room_id
        WHERE b.guest_id=%s
    """, (session['guest_id'],))
    my_bookings = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('index.html', rooms=rooms, my_bookings=my_bookings, name=session.get('guest_name'))

@app.route('/book_room/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    if 'guest_id' not in session:
        return redirect('/login')
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        special_request = request.form.get('special_request', '')
        
        cursor.execute("""
            INSERT INTO Bookings (guest_id, room_id, check_in, check_out, special_request)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['guest_id'], room_id, check_in, check_out, special_request))
        db.commit()
        booking_id = cursor.lastrowid
        
        cursor.execute("UPDATE Rooms SET status='Booked' WHERE room_id=%s", (room_id,))
        db.commit()
        
        cursor.close()
        db.close()
        return redirect(f'/payment/{booking_id}')
        
    cursor.execute("SELECT * FROM Rooms WHERE room_id=%s", (room_id,))
    room = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('book_room.html', room=room)

@app.route('/payment/<int:booking_id>')
def payment(booking_id):
    if 'guest_id' not in session: return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.booking_id, r.price, g.name 
        FROM Bookings b 
        JOIN Rooms r ON b.room_id = r.room_id 
        JOIN Guests g ON b.guest_id = g.guest_id 
        WHERE b.booking_id=%s AND b.guest_id=%s
    """, (booking_id, session['guest_id']))
    booking = cursor.fetchone()
    cursor.close()
    db.close()
    if not booking:
        return redirect('/')
    return render_template('payment.html', booking=booking)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'guest_id' not in session: return redirect('/login')
    booking_id = request.form['booking_id']
    method = request.form['method']
    transaction_id = request.form.get('transaction_id', 'N/A')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT r.price FROM Bookings b JOIN Rooms r ON b.room_id = r.room_id WHERE b.booking_id=%s", (booking_id,))
    amount = cursor.fetchone()['price']

    cursor.execute("""
        INSERT INTO Payments (booking_id, amount, payment_date, method, transaction_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (booking_id, amount, date.today(), method, transaction_id))
    db.commit()
    cursor.close()
    db.close()

    return render_template('success.html', booking_id=booking_id, amount=amount, method=method)

@app.route('/bookings')
def view_bookings():
    if 'guest_id' not in session: return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.booking_id, g.name, r.room_type, b.check_in, b.check_out, b.special_request, r.price
        FROM Bookings b
        JOIN Guests g ON b.guest_id = g.guest_id
        JOIN Rooms r ON b.room_id = r.room_id
        WHERE b.guest_id=%s
    """, (session['guest_id'],))
    bookings = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)