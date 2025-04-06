import os
import sqlite3
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, "db", "updated-db")
IMAGE_DB_PATH = os.path.join(CURRENT_DIR, "db", "images.db")
def initialize_database():
    """Initialize SQLite database with proper permissions"""
    try:
        # Ensure directory exists
        db_dir = os.path.dirname(IMAGE_DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        
        # Set directory permissions (777 for development, adjust for production)
        os.chmod(db_dir, 0o777)
        
        # If database exists, set proper permissions
        if os.path.exists(IMAGE_DB_PATH):
            os.chmod(IMAGE_DB_PATH, 0o666)
        else:
            # Create new database file with proper permissions
            open(IMAGE_DB_PATH, 'a').close()
            os.chmod(IMAGE_DB_PATH, 0o666)
        
        # Create database connection
        conn = sqlite3.connect(IMAGE_DB_PATH)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_name TEXT,
                page_num INTEGER,
                image BLOB,
                pdf_link TEXT
            )
        """)
        conn.commit()
        return conn, cursor
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()
        raise
initialize_database()