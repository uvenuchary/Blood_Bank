import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import hashlib
import random
from twilio.rest import Client
from config import Config
from database import connect_db

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
app.secret_key = os.urandom(24)

# Twilio configuration
TWILIO_ACCOUNT_SID = "AC1a62abd1762aae85d4e7b8e162b7e07b"
TWILIO_AUTH_TOKEN = "2babaeba0b58e42b620cd7cb14526f9a"
TWILIO_PHONE_NUMBER = "+12697784409"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Donor Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO donors_logindetails(name, email, password) VALUES(%s, %s, %s)', (name, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        # Replace with database validation
        if username == 'uvenuchary@gmail.com' and password == 'password':
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return render_template('login.html', username=username)

    return render_template('login.html')

# SMS Verification Route
@app.route('/send_code', methods=['POST'])
def send_code():
    phone_number = request.form.get('phone_number')
    verification_code = random.randint(100000, 999999)
    session['verification_code'] = str(verification_code)
    session['phone_number'] = phone_number

    try:
        client.messages.create(
            body=f"VSB OTP is: {verification_code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return render_template('verify_code.html', phone_number=phone_number)
    except Exception as e:
        return f"Error: {e}"

@app.route('/verify_code', methods=['POST'])
def verify_code():
    user_code = request.form.get('verification_code')
    if user_code == session.get('verification_code'):
        session['verified'] = True
        flash("Phone number verified successfully!", "success")
        return redirect(url_for('request_form'))
    else:
        flash("Verification failed. Please try again.", "danger")
        return render_template('verify_code.html', phone_number=session.get('phone_number'))

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        session['verified'] = False
        return redirect(url_for('send_code', phone_number=phone_number))

    return render_template('verify.html')

@app.route('/request_form', methods=['GET', 'POST'])
def request_form():
    if not session.get('verified'):
        flash("Please verify your phone number first.", "danger")
        return redirect(url_for('donate'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_type = request.form['blood_type']
        contact = request.form['contact']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO recipients (name, age, blood_type, contact) VALUES (%s, %s, %s, %s)',
            (name, age, blood_type, contact)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Request submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('request_form.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=7000, debug=True)
