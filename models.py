from config import get_db_connection

def create_tables():
    """Creates necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Friends table (for friend requests & friendships)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status TEXT CHECK( status IN ('pending', 'accepted', 'rejected') ) DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
    ''')

    # Messages table (for real-time chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# ---------------------- Helper Functions ----------------------

def add_user(name, email, password):
    """Adds a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        conn.close()

def send_friend_request(user_id, friend_id):
    """Sends a friend request from user_id to friend_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'pending')", (user_id, friend_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error sending friend request: {e}")
        return False
    finally:
        conn.close()

def send_message(sender_id, receiver_id, message):
    """Stores a message between users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)", 
                       (sender_id, receiver_id, message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
    finally:
        conn.close()

# ---------------------- Initialize Database ----------------------
if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")
