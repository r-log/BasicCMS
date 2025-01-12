import pymysql
from pymysql.cursors import DictCursor

# Database configurations
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


def get_character_db():
    """Create connection to character database"""
    config = DB_CONFIG.copy()
    config['db'] = 'character0'
    return pymysql.connect(**config)


# Check all characters in the database
with get_character_db() as char_conn:
    with char_conn.cursor() as cursor:
        # Get all characters with their account info
        cursor.execute("""
            SELECT 
                guid, account, name, race, class, level, gender,
                money, position_x, position_y, position_z, map
            FROM characters
        """)
        characters = cursor.fetchall()

        if not characters:
            print("No characters found in the database!")
        else:
            print("\nCharacters found:")
            print("-" * 50)
            for char in characters:
                print(f"GUID: {char['guid']}")
                print(f"Account ID: {char['account']}")
                print(f"Name: {char['name']}")
                print(
                    f"Level {char['level']} (Race: {char['race']}, Class: {char['class']})")
                print("-" * 50)
