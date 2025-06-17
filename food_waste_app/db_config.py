import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="xxxxx",
        database="food_waste_db"
    )

#test