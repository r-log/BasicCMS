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


def get_realm_db():
    """Create connection to realm database"""
    config = DB_CONFIG.copy()
    config['db'] = 'realmd'
    return pymysql.connect(**config)


def get_character_db():
    """Create connection to character database"""
    config = DB_CONFIG.copy()
    config['db'] = 'character0'
    return pymysql.connect(**config)


# First, get the administrator's account ID
with get_realm_db() as realm_conn:
    with realm_conn.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM account WHERE username = 'ADMINISTRATOR'")
        account = cursor.fetchone()
        if not account:
            print("Administrator account not found!")
            exit(1)
        account_id = account['id']
        print(f"Found administrator account ID: {account_id}")

# Now insert a character
with get_character_db() as char_conn:
    with char_conn.cursor() as cursor:
        # Check if character name exists
        char_name = "Arthas"
        cursor.execute(
            "SELECT guid FROM characters WHERE name = %s", (char_name,))
        if cursor.fetchone():
            print(f"Character {char_name} already exists!")
            exit(1)

        # Insert character data
        sql = """
        INSERT INTO characters (
            account, name, race, class, gender, level, money, 
            position_x, position_y, position_z, map, orientation,
            health, playerBytes, playerBytes2
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        """
        values = (
            account_id,  # account
            char_name,   # name
            1,          # race (1 = Human)
            2,          # class (2 = Paladin)
            0,          # gender (0 = Male)
            80,         # level
            100000,     # money (10 gold)
            -8949.95,   # position_x (Stormwind)
            -132.493,   # position_y
            83.5312,    # position_z
            0,          # map (0 = Eastern Kingdoms)
            0,          # orientation
            100,        # health
            33554432,   # playerBytes
            0          # playerBytes2
        )

        cursor.execute(sql, values)
        char_conn.commit()

        print(
            f"Successfully created character {char_name} for administrator account!")
