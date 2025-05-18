import sqlite3

DB_NAME = "game_database.db"

def connect():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = connect()
    cursor = conn.cursor()

    # Table for character profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        character_name TEXT,
        nickname TEXT,
        hp INTEGER,
        level INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        weapon TEXT,
        active_location TEXT,
        gp INTEGER DEFAULT 0
    )
    """)

    # Add nickname column if it doesn't exist
    cursor.execute("""
    SELECT name FROM pragma_table_info('profiles') WHERE name='nickname'
    """)
    if not cursor.fetchone():
        cursor.execute("""
        ALTER TABLE profiles ADD COLUMN nickname TEXT
        """)

    # Add gp column if it doesn't exist
    cursor.execute("""
    SELECT name FROM pragma_table_info('profiles') WHERE name='gp'
    """)
    if not cursor.fetchone():
        cursor.execute("""
        ALTER TABLE profiles ADD COLUMN gp INTEGER DEFAULT 0
        """)

    # Table for character inventories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        item_name TEXT,
        description TEXT,
        value INTEGER,
        hp_effect INTEGER,
        FOREIGN KEY (character_id) REFERENCES profiles(character_id)
    )
    """)

    # Table for enemies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enemies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        level_min INTEGER,
        level_max INTEGER,
        location TEXT
    )
    """)

    # Table for loot items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loot_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        value INTEGER,
        hp_effect INTEGER,
        drop_rate REAL,
        location TEXT
    )
    """)

    # Table for enemies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enemies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        level_min INTEGER,
        level_max INTEGER,
        location TEXT
    )
    """)

    # Table for loot items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loot_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        value INTEGER,
        hp_effect INTEGER,
        drop_rate REAL, 
        location TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_enemy(name, description, level_min, level_max, location):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO enemies (name, description, level_min, level_max, location)
    VALUES (?, ?, ?, ?, ?)
    """, (name, description, level_min, level_max, location))
    conn.commit()
    conn.close()

def add_loot_item(name, description, value, hp_effect, drop_rate, location):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO loot_items (name, description, value, hp_effect, drop_rate, location)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, description, value, hp_effect, drop_rate, location))
    conn.commit()
    conn.close()

def set_active_location(user_id, character_name, location):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE profiles
    SET active_location = ?
    WHERE user_id = ? AND character_name = ?
    """, (location, user_id, character_name))
    conn.commit()
    conn.close()

def get_active_location(user_id, character_name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT active_location FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (user_id, character_name))
    location = cursor.fetchone()
    conn.close()
    return location[0] if location else None

def add_item_to_inventory(character_id, item_name, description, value, hp_effect):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
    VALUES (?, ?, ?, ?, ?)
    """, (character_id, item_name, description, value, hp_effect))
    conn.commit()
    conn.close()

def get_item_from_inventory(character_id, item_name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, item_name, description, value, hp_effect FROM inventory
    WHERE character_id = ? AND item_name = ?
    """, (character_id, item_name))
    item = cursor.fetchone()
    conn.close()
    return item

def update_character_hp(character_id, hp_increase):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE profiles
    SET hp = hp + ?
    WHERE character_id = ?
    """, (hp_increase, character_id))
    conn.commit()
    conn.close()

def remove_item_from_inventory(item_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM inventory
    WHERE id = ?
    """, (item_id,))
    conn.commit()
    conn.close()

def update_character_xp(character_name: str, xp_gain: int):
    conn = connect()
    cursor = conn.cursor()

    # Get current XP, level and HP
    cursor.execute("""
    SELECT level, xp, hp FROM profiles 
    WHERE character_name = ?
    """, (character_name,))
    current_level, current_xp, current_hp = cursor.fetchone()

    # Calculate XP needed for next level (increases exponentially)
    xp_for_next_level = 100 * (current_level + 1) * 1.5

    # Add new XP
    new_xp = current_xp + xp_gain
    new_level = current_level
    new_hp = current_hp

    # Check if leveled up
    while new_xp >= xp_for_next_level and new_level < 20:
        new_level += 1
        new_xp -= xp_for_next_level
        xp_for_next_level = 100 * (new_level + 1) * 1.5
        new_hp = min(100 + (new_level * 10), new_hp + 10)  # Increase max HP by 10 per level

    # Update character
    cursor.execute("""
    UPDATE profiles 
    SET level = ?, xp = ?, hp = ?
    WHERE character_name = ?
    """, (new_level, new_xp, new_hp, character_name))

    conn.commit()
    conn.close()
    return new_level > current_level