import sqlite3

def create_database():
    # Create or connect to the database (it will create the file 'orders.db' if it doesn't exist)
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    # Create a table named 'orders' for storing coffee orders
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       coffee_type TEXT,
                       sugar_level TEXT,
                       cup_size TEXT,
                       total_price REAL)''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database and 'orders' table created successfully.")

if __name__ == "__main__":
    create_database()
