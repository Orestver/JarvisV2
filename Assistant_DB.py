import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")


def create_database():
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS commands")
        print("Database created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def create_table():
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database="commands"
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AssistantCom (
                id INT AUTO_INCREMENT PRIMARY KEY,
                command_trigger VARCHAR(255) NOT NULL,
                action VARCHAR(255) NOT NULL,
                description TEXT
            )
        """)
        print("Table created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def insert_command(command_trigger, action, description):
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database="commands"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO AssistantCom (command_trigger, action, description)
            VALUES (%s, %s, %s)
        """, (command_trigger, action, description))
        conn.commit()
        print("Command inserted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def delete_command(command_trigger):
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database="commands"
        )
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM AssistantCom WHERE command_trigger = %s
        """, (command_trigger,))
        conn.commit()
        print(f"Command '{command_trigger}' deleted successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



if __name__ == "__main__":
    create_database()
    create_table()
    insert_command("greeting", "wishME()", "A simple greeting command depends on time.")
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            database="commands"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AssistantCom")
        for row in cursor.fetchall():
            print(row)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
