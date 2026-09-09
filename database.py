import mysql.connector
def connectDB():
    return mysql.connector.connect(
        host="localhost",  
        user="root",
        password="",
        database="mygame"
    )