from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
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


def get_world_db():
    """Create connection to world database"""
    config = DB_CONFIG.copy()
    config['db'] = 'mangos0'
    return pymysql.connect(**config)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, account_data):
        self.id = account_data['id']
        self.username = account_data['username']
        self.email = account_data.get('email', '')
        self.gmlevel = account_data.get('gmlevel', 0)


@login_manager.user_loader
def load_user(user_id):
    with get_realm_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM account WHERE id = %s", (user_id,))
            account = cursor.fetchone()
            if account:
                return User(account)
    return None


def generate_mangos_hash(username, password):
    """Generate a MaNGOS compatible password hash"""
    username = username.upper()
    password = password.upper()
    combined = f"{username}:{password}"
    # Generate SHA1 hash without converting to uppercase
    hash_obj = hashlib.sha1(combined.encode('utf-8'))
    return hash_obj.hexdigest().lower()  # Return lowercase hash to match database


@app.route('/')
def index():
    with get_realm_db() as connection:
        with connection.cursor() as cursor:
            # Get realm list and map the fields correctly
            cursor.execute("""
                SELECT id, name, icon, realmflags, timezone, population 
                FROM realmlist 
                WHERE realmflags != 3
            """)
            realms = cursor.fetchall()
            # Process realm data to match template expectations
            for realm in realms:
                # Map icon to type (0=normal, 1=pvp, 4=normal, 6=rp, 8=rppvp)
                icon_to_type = {
                    0: 'NORMAL',
                    1: 'PVP',
                    4: 'NORMAL',
                    6: 'RP',
                    8: 'RPPVP'
                }
                realm['type'] = icon_to_type.get(
                    realm.get('icon', 0), 'NORMAL')
                # Convert population to text (0=low, 1=medium, 2=high)
                pop_levels = ['Low', 'Medium', 'High']
                pop_index = min(int(realm.get('population', 0)), 2)
                realm['population'] = pop_levels[pop_index]
                # Set status based on realmflags (2=offline, 0=online)
                realm['status'] = realm.get('realmflags', 0) != 2

    return render_template('index.html', realms=realms)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_realm_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM account WHERE UPPER(username) = UPPER(%s)", (username,))
                account = cursor.fetchone()

                if account:
                    password_hash = generate_mangos_hash(username, password)
                    print(f"Login attempt:")
                    print(f"Username (original): {username}")
                    print(f"Username (upper): {username.upper()}")
                    print(f"Password (upper): {password.upper()}")
                    print(
                        f"Combined string: {username.upper()}:{password.upper()}")
                    print(f"Generated hash: {password_hash}")
                    print(f"Stored hash: {account['sha_pass_hash']}")
                    print(
                        f"Match: {account['sha_pass_hash'] == password_hash}")

                    # Compare without converting case
                    if account['sha_pass_hash'] == password_hash:
                        user = User(account)
                        login_user(user)
                        flash('Logged in successfully!', 'success')
                        return redirect(url_for('profile'))
                else:
                    print(f"No account found for username: {username}")

        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')

        with get_realm_db() as connection:
            with connection.cursor() as cursor:
                # Check if username exists
                cursor.execute(
                    "SELECT * FROM account WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists!', 'error')
                    return render_template('register.html')

                # Create new account
                password_hash = generate_mangos_hash(username, password)
                sql = "INSERT INTO account (username, sha_pass_hash, email, gmlevel) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (username, password_hash, email, 0))
                connection.commit()

        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    """Profile page route"""
    characters = []
    print(f"\nDebug - Current user: {current_user.username}")

    # First get the account ID from realmd database
    with get_realm_db() as realm_conn:
        with realm_conn.cursor() as realm_cursor:
            realm_cursor.execute(
                "SELECT id FROM account WHERE username = %s", (current_user.username,))
            account = realm_cursor.fetchone()
            if not account:
                print("Debug - No account found in realmd database")
                flash('Account not found!', 'error')
                return redirect(url_for('index'))
            account_id = account['id']
            print(f"Debug - Found account ID: {account_id}")

    # Then get characters using the account ID
    with get_character_db() as char_conn:
        with char_conn.cursor() as cursor:
            print(f"Debug - Fetching characters for account ID: {account_id}")
            cursor.execute("""
                SELECT 
                    guid, name, race, class, level, gender,
                    money, playerBytes, playerBytes2,
                    position_x, position_y, position_z, map,
                    online, totaltime, leveltime
                FROM characters 
                WHERE account = %s
            """, (account_id,))
            characters = cursor.fetchall()
            print(f"Debug - Found {len(characters)} characters")
            if characters:
                for char in characters:
                    print(
                        f"Debug - Character: {char['name']} (Level {char['level']})")

            # Add realm info
            with get_realm_db() as realm_conn:
                with realm_conn.cursor() as realm_cursor:
                    realm_cursor.execute("SELECT id, name FROM realmlist")
                    realms = {realm['id']: realm['name']
                              for realm in realm_cursor.fetchall()}

            # Add realm names and convert race/class IDs to names
            for char in characters:
                char['realm_name'] = realms.get(
                    1, 'Unknown Realm')  # Default to realm ID 1

                # Convert race ID to name
                races = {
                    1: 'Human', 2: 'Orc', 3: 'Dwarf', 4: 'Night Elf',
                    5: 'Undead', 6: 'Tauren', 7: 'Gnome', 8: 'Troll',
                    10: 'Blood Elf', 11: 'Draenei'
                }
                char['race'] = races.get(
                    char.get('race'), f"Race {char.get('race')}")

                # Convert class ID to name
                classes = {
                    1: 'Warrior', 2: 'Paladin', 3: 'Hunter', 4: 'Rogue',
                    5: 'Priest', 6: 'Death Knight', 7: 'Shaman',
                    8: 'Mage', 9: 'Warlock', 11: 'Druid'
                }
                char['class'] = classes.get(
                    char.get('class'), f"Class {char.get('class')}")

    print(f"Debug - Final characters list length: {len(characters)}")
    return render_template('profile.html', characters=characters)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/api/character/<int:char_id>/equipment')
@login_required
def get_character_equipment(char_id):
    try:
        print(f"\nDebug - Checking inventory for character ID: {char_id}")

        char_db = get_character_db()
        with char_db.cursor() as cursor:
            # First verify the character exists and get their details
            cursor.execute(
                "SELECT name, level, race, class FROM characters WHERE guid = %s", (char_id,))
            character = cursor.fetchone()
            if not character:
                print("Debug - Character not found")
                return jsonify({'error': 'Character not found'}), 404

            print(
                f"Debug - Found character: {character['name']} (Level {character['level']})")

            # Check raw inventory data first
            print("\nDebug - Raw inventory check:")
            cursor.execute("""
                SELECT ci.*, it.name, it.Quality, it.ItemLevel, it.RequiredLevel,
                       it.class as item_class, it.subclass as item_subclass
                FROM character_inventory ci
                LEFT JOIN mangos0.item_template it ON ci.item_template = it.entry
                WHERE ci.guid = %s
                ORDER BY ci.bag, ci.slot
            """, (char_id,))
            raw_items = cursor.fetchall()
            print(f"Debug - Total inventory entries found: {len(raw_items)}")

            if raw_items:
                for item in raw_items:
                    print(f"Debug - Item: bag={item['bag']}, slot={item['slot']}, "
                          f"template={item['item_template']}, "
                          f"name={item.get('name', 'Unknown')}, "
                          f"quality={item.get('Quality', 'Unknown')}, "
                          f"level={item.get('ItemLevel', 'Unknown')}")
            else:
                print("Debug - No inventory entries found")

            # Now get equipped items (bag=0)
            equipped_items = [
                item for item in raw_items if item['bag'] == 0 and 0 <= item['slot'] <= 18]
            print(f"\nDebug - Found {len(equipped_items)} equipped items")

            equipment = []
            for item in equipped_items:
                equipment.append({
                    'slot': item['slot'],
                    'item_id': item['item_template'],
                    'name': item.get('name', 'Unknown Item'),
                    'quality': item.get('Quality', 0),
                    'item_level': item.get('ItemLevel', 0),
                    'required_level': item.get('RequiredLevel', 0),
                    'item_class': item.get('item_class', 0),
                    'item_subclass': item.get('item_subclass', 0)
                })

            return jsonify(equipment)

    except Exception as e:
        print(f"Error checking inventory: {str(e)}")
        return jsonify({'error': 'Failed to fetch equipment data'}), 500


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('profile'))

    with get_realm_db() as connection:
        with connection.cursor() as cursor:
            current_hash = generate_mangos_hash(
                current_user.username, current_password)
            cursor.execute(
                "SELECT * FROM account WHERE username = %s", (current_user.username,))
            account = cursor.fetchone()

            if account['sha_pass_hash'] != current_hash:
                flash('Current password is incorrect!', 'error')
                return redirect(url_for('profile'))

            new_hash = generate_mangos_hash(
                current_user.username, new_password)
            cursor.execute("UPDATE account SET sha_pass_hash = %s WHERE username = %s",
                           (new_hash, current_user.username))
            connection.commit()

    flash('Password updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/change-email', methods=['POST'])
@login_required
def change_email():
    new_email = request.form['new_email']
    password = request.form['password']

    with get_realm_db() as connection:
        with connection.cursor() as cursor:
            password_hash = generate_mangos_hash(
                current_user.username, password)
            cursor.execute(
                "SELECT * FROM account WHERE username = %s", (current_user.username,))
            account = cursor.fetchone()

            if account['sha_pass_hash'] != password_hash:
                flash('Password is incorrect!', 'error')
                return redirect(url_for('profile'))

            cursor.execute("UPDATE account SET email = %s WHERE username = %s",
                           (new_email, current_user.username))
            connection.commit()

    flash('Email updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/debug/character-info')
def debug_character_info():
    """Debug route to check character table structure"""
    info = {}

    with get_character_db() as connection:
        with connection.cursor() as cursor:
            # Get table structure
            cursor.execute("DESCRIBE characters")
            info['character_structure'] = cursor.fetchall()

            # Get a sample character
            cursor.execute("""
                SELECT * FROM characters 
                LIMIT 1
            """)
            info['sample_character'] = cursor.fetchone()

            # Get related tables
            cursor.execute("""
                SHOW TABLES LIKE 'character_%'
            """)
            info['related_tables'] = cursor.fetchall()

            # Check inventory table structure
            cursor.execute("DESCRIBE character_inventory")
            info['inventory_structure'] = cursor.fetchall()

    return jsonify(info)


@app.route('/debug/database-info')
def debug_database_info():
    """Debug route to show all database tables and their structures"""
    info = {
        'realm': {},
        'character': {},
        'world': {}
    }

    # Check realm database
    with get_realm_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            info['realm']['tables'] = [
                list(table.values())[0] for table in tables]

            # Get account table structure
            cursor.execute("DESCRIBE account")
            info['realm']['account_structure'] = cursor.fetchall()

    # Check character database
    with get_character_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            info['character']['tables'] = [
                list(table.values())[0] for table in tables]

            # Get characters table structure
            cursor.execute("DESCRIBE characters")
            info['character']['characters_structure'] = cursor.fetchall()

            # Get character_inventory structure
            cursor.execute("DESCRIBE character_inventory")
            info['character']['inventory_structure'] = cursor.fetchall()

            # Get a sample character
            cursor.execute("""
                SELECT guid, account, name, race, class, level, gender 
                FROM characters 
                LIMIT 1
            """)
            info['character']['sample_character'] = cursor.fetchone()

            # Get sample inventory
            cursor.execute("""
                SELECT * FROM character_inventory 
                LIMIT 1
            """)
            info['character']['sample_inventory'] = cursor.fetchone()

    # Check world database
    with get_world_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            info['world']['tables'] = [
                list(table.values())[0] for table in tables]

            # Get item_template structure
            cursor.execute("DESCRIBE item_template")
            info['world']['item_template_structure'] = cursor.fetchall()

    return jsonify(info)


if __name__ == '__main__':
    # Test database connections
    try:
        with get_realm_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                print("Realm DB tables:", [list(table.values())[
                      0] for table in cursor.fetchall()])

        with get_character_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                print("Character DB tables:", [
                      list(table.values())[0] for table in cursor.fetchall()])

        with get_world_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                print("World DB tables:", [list(table.values())[
                      0] for table in cursor.fetchall()])

    except Exception as e:
        print("Database connection error:", str(e))

    app.run(debug=True)
