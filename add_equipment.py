import pymysql
from pymysql.cursors import DictCursor
import random

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


def get_world_db():
    """Create connection to world database"""
    config = DB_CONFIG.copy()
    config['db'] = 'mangos0'
    return pymysql.connect(**config)


def add_equipment():
    # First, get Arthas's GUID
    with get_character_db() as char_db:
        with char_db.cursor() as cursor:
            cursor.execute("SELECT guid FROM characters WHERE name = 'Arthas'")
            character = cursor.fetchone()
            if not character:
                print("Character 'Arthas' not found!")
                return

            char_guid = character['guid']
            print(f"Found Arthas with GUID: {char_guid}")

            # Basic paladin equipment item IDs
            equipment = [
                (0, 0, 16866),  # Head - Helm of Might
                (0, 1, 16868),  # Neck - Medallion of Might
                (0, 2, 16867),  # Shoulders - Pauldrons of Might
                (0, 14, 16865),  # Back - Cloak of Might
                (0, 4, 16865),  # Chest - Breastplate of Might
                (0, 3, 16861),  # Shirt - Simple Linen Shirt
                (0, 18, 19032),  # Tabard - Stormwind Tabard
                (0, 8, 16863),  # Wrist - Bracers of Might
                (0, 9, 16863),  # Hands - Gauntlets of Might
                (0, 5, 16864),  # Waist - Belt of Might
                (0, 6, 16867),  # Legs - Legplates of Might
                (0, 7, 16862),  # Feet - Sabatons of Might
                (0, 15, 13262),  # Main Hand - Ashkandi, Greatsword of the Brotherhood
                # Off Hand - Thunderfury, Blessed Blade of the Windseeker
                (0, 16, 19019),
                (0, 17, 19019)  # Ranged - Libram of Might
            ]

            # Clear existing equipment
            cursor.execute(
                "DELETE FROM character_inventory WHERE guid = %s AND bag = 0", (char_guid,))

            # Get the current max item ID
            cursor.execute("SELECT MAX(item) FROM character_inventory")
            result = cursor.fetchone()
            next_item_id = (result['MAX(item)'] or 0) + 1

            # Add new equipment
            for bag, slot, item_template in equipment:
                cursor.execute("""
                    INSERT INTO character_inventory 
                    (guid, bag, slot, item_template, item) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (char_guid, bag, slot, item_template, next_item_id))
                next_item_id += 1

            char_db.commit()
            print(f"Added {len(equipment)} items to Arthas's inventory!")


if __name__ == "__main__":
    add_equipment()
