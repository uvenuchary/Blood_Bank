from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os
from database import connect_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        units = request.form['units']
        contact = request.form['contact']
        
        conn=connect_db()
        cur=conn.cursor()
        cur.execute("INSERT INTO donors (name, blood_type, Units, contact,status) VALUES (%s, %s, %s, %s,%s)", (name, blood_group, units, contact, 'Pending'))
        conn.commit()
        flash('Blood request submitted successfully!', 'success')
        return redirect(url_for('request_list'))
    return render_template('request_blood.html')

@app.route('/request_list')
def request_list():
    conn=connect_db()
    cur=conn.cursor()
    cur.execute("SELECT * FROM donors")
    requests = cur.fetchall()
    cur.close()
    return render_template('request_list.html', requests=requests)

@app.route('/update_status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    status = request.form['status']
    
    conn=connect_db()
    cur=conn.cursor()
    cur.execute("UPDATE donors SET status=%s WHERE id=%s", (status, request_id))
    cur.close()
    flash('Request status updated successfully!', 'success')
    return redirect(url_for('request_list'))

@app.route('/rewards_and_payments')
def rewards_and_payments():
    conn=connect_db()
    cur=conn.cursor()
    cur.execute("SELECT * FROM rewards")
    rewards = cur.fetchall()
    cur.close()
    return render_template('rewards_and_payments.html', rewards=rewards)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6000, debug=True)
