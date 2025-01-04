import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mypassword",
        database="blood_bank",
        auth_plugin="mysql_native_password"
    )