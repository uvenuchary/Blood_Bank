from flask import Flask, render_template, request, redirect, flash, url_for, session
from database import connect_db

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use a strong secret key for production

@app.route('/')
def home():
    if 'username' in session:  # Check if user is logged in
        return render_template('index.html')
    return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # For simplicity, we're using hardcoded values. Replace this with your database validation logic.
        if username == 'admin' and password == 'password':  # Replace with proper validation
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return render_template('login.html', username=username)  # Pass the username back
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the user from session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/stock')
def view_stock():
    if 'username' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blood_stock")
    stock = cursor.fetchall()
    conn.close()
    return render_template('stock.html', stock=stock)

@app.route('/donor/admin', methods=['GET', 'POST'])
def add_donor():
    if 'username' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))
    if 'username' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()

    cursor.execute("SELECT * FROM recipients")
    recipients = cursor.fetchall()

    conn.close()
    return render_template('admin.html', donors=donors, recipients=recipients)
@app.route('/update_status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    status = request.form['status']
    
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE donors SET status=%s WHERE id=%s", (status, request_id))
    conn.commit()
    cur.close()
    flash('Request status updated successfully!', 'success')
    return redirect(url_for('add_donor'))  # Make sure this is the correct URL to redirect to



@app.route('/recipient/request', methods=['GET', 'POST'])
def request_blood():
    if 'username' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        blood_type = request.form['blood_type']
        contact = request.form['contact']

        conn = connect_db()
        cursor = conn.cursor()

        # Check if blood is available
        cursor.execute("SELECT units_available FROM blood_stock WHERE blood_type=%s", (blood_type,))
        stock = cursor.fetchone()

        if stock and stock[0] > 0:
            # Deduct blood stock and record the recipient
            cursor.execute("UPDATE blood_stock SET units_available = units_available - 1 WHERE blood_type=%s", (blood_type,))
            cursor.execute(
                "INSERT INTO recipients (name, blood_type, contact) VALUES (%s, %s, %s)",
                (name, blood_type, contact)
            )
            conn.commit()
            flash("Blood request processed successfully!", "success")
        else:
            flash("Requested blood type is out of stock.", "danger")

        conn.close()
        return redirect(url_for('home'))

    return render_template('request_blood.html')
'''
@app.route('/admin')
def admin():
    return render_template('login.html')
    if 'username' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors")
    donors = cursor.fetchall()

    cursor.execute("SELECT * FROM recipients")
    recipients = cursor.fetchall()

    conn.close()
    return render_template('admin.html', donors=donors, recipients=recipients)

    '''
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)