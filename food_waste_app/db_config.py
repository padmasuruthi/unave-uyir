import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="abc@12345",
        database="food_waste_db"
    )
