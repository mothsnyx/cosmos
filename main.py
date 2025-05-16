import discord
from discord import app_commands
import random
import json
import logging
from dataclasses import dataclass
from typing import List, Dict
import os
from datetime import datetime
from dotenv import load_dotenv
from database import setup_database, connect, update_character_xp
from dotenv import load_dotenv

load_dotenv()
setup_database()  # Initialize database tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data structures
@dataclass
class Character:
    name: str
    hp: int
    max_hp: int
    inventory: Dict[str, List[str]]
    coins: int
    level: int = 0
    exp: int = 0
    owner_id: str = ""

@dataclass
class Area:
    name: str
    enemies: List[str]
    items: List[str]
    min_level: int
    max_level: int
    exp_reward: int

# Initialize bot
class RPGBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.weather = ["Sunny", "Rainy", "Stormy", "Foggy", "Clear"]
        self.current_weather = "Sunny"

        # Load game data with difficulty levels
        self.areas = {
            "High School": Area("High School (Easy)", ["Possessed Locker", "Drama Club Phantom", "Library Ghoul", "Social Feeder", "Janitor"], 
                              ["Training Manual", "School Uniform", "Basic Nen Tools"], 0, 5, 5),
            "Park": Area("Park (Easy)", ["Vineleech", "Hollow Deer", "Soot Crow", "Smiling Bench Guy", "Playground Ghost"],
                          ["Bike Lock", "Bench", "Picnic Basket"], 0, 5, 5),
            "Beach": Area("Beach (Medium)", ["Drifter", "Crabswarm", "Broken Ray", "Tidewolf", "Gullmock"],
                          ["Sea Glass", "Shell", "Driftwood", "Beach Ball", "Towel"], 5, 10, 15),
            "City": Area("City (Medium)", ["Street Delinquent", "Blackmarket Enforcer", "Lawmen (Corrupt)", "Eyeless", "Weeper", "Hunter"], 
                          ["Street Weapon", "Combat Gear", "City Maps"], 5, 10, 20),
            "Sewers": Area("Sewers (Hard)", ["Drowned", "Molemen", "Sewer Rat", "Sludge Beast", "Pipeborn"], 
                          ["Toxic Shield", "Sewer Map", "Rare Artifact"], 10, 15, 30),
            "Forest": Area("Forest (Hard)", ["Beast", "Dark Hunter", "Ancient Spirit"], 
                          ["Beast Core", "Spirit Essence", "Forest Relic"], 10, 15, 30),
            "Destroyed Research Site": Area("Destroyed Research Site (Extreme)", ["Murmur", "Revenant", "Gnawer", "Screamer"],
                          ["Research Data", "Prototype Device", "Healing Nanites"], 15, 20, 50),
            "Abandoned Facility": Area("Abandoned Facility (Extreme)", ["Failed Experiment", "Mad Scientist", "Ultimate Weapon"], 
                          ["Experimental Gear", "Research Data", "Ultimate Tech"], 15, 20, 50),
            "Ash Lake": Area("Ash Lake (Nightmare)", ["Ash Beast", "Ash Hunter", "Ash Guardian"],
                          ["Ash Core", "Ash Essence", "Ash Relic"], 20, 20, 100)
        }

        self.shop_items = {
            "Minor Healing Potion": {"price": 20, "hp_effect": 10, "description": "Restores 10 HP"},
            "Moderate Healing Potion": {"price": 80, "hp_effect": 50, "description": "Restores 50 HP"},
            "Big Healing Potion": {"price": 160, "hp_effect": 100, "description": "Restores 100 HP"}
        }

client = RPGBot()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Commands
@client.tree.command(name="create_character", description="Create your character")
async def create_character(interaction: discord.Interaction, name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists
    cursor.execute("SELECT character_name FROM profiles WHERE character_name = ?", (name,))
    if cursor.fetchone():
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ A character with this name already exists!")
        conn.close()
        return

    # Create character
    cursor.execute("""
    INSERT INTO profiles (user_id, character_name, hp, level)
    VALUES (?, ?, ?, ?)
    """, (interaction.user.id, name, 100, 0))
    conn.commit()
    conn.close()

    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ Character created: **{name}**!")

@client.tree.command(name="delete_character", description="Delete one of your characters")
async def delete_character(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles 
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found or doesn't belong to you!")
        conn.close()
        return

    # Delete character's inventory
    cursor.execute("DELETE FROM inventory WHERE character_id = ?", (character[0],))

    # Delete character profile
    cursor.execute("DELETE FROM profiles WHERE character_id = ?", (character[0],))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ Character deleted: **{character_name}**!")

@client.tree.command(name="list_characters", description="List all your characters")
async def list_characters(interaction: discord.Interaction):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT character_name, hp, level FROM profiles
    WHERE user_id = ?
    """, (interaction.user.id,))
    characters = cursor.fetchall()
    conn.close()

    if not characters:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ You don't have any characters yet!")
        return

    embed = discord.Embed(title="Your Characters", color=discord.Color.blue())
    for char in characters:
        max_hp = 100 + (char[2] * 10)  # Base HP + (level * 10)
        embed.add_field(name=char[0], 
                       value=f"Level: {char[2]}\nHP: {char[1]}/{max_hp}",
                       inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="profile", description="Show a character's profile")
async def profile(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT p.character_name, p.hp, p.level, p.active_location, p.character_id, p.xp
    FROM profiles p
    WHERE p.user_id = ? AND p.character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found! Use `/create_character` to make one.")
        conn.close()
        return

    # Calculate XP needed for next level
    xp_for_next_level = 100 * (character[2] + 1) * 1.5

    # Get GP
    cursor.execute("SELECT gp FROM profiles WHERE character_name = ?", (character[0],))
    gp = cursor.fetchone()[0]

    max_hp = 100 + (character[2] * 10)  # Base HP + (level * 10)
    embed = discord.Embed(title=f"{character[0]}'s Profile", color=discord.Color.blue())
    embed.add_field(name="HP", value=f"{character[1]}/{max_hp}")
    embed.add_field(name="Level", value=str(character[2]))
    embed.add_field(name="XP Progress", value=f"{character[5]}/{int(xp_for_next_level)}")
    embed.add_field(name="GP", value=str(gp))
    embed.add_field(name="Location", value=character[3] or "Not in any location")

    # Get inventory items
    cursor.execute("""
    SELECT item_name, description, value, hp_effect 
    FROM inventory 
    WHERE character_id = ?
    """, (character[4],))
    items = cursor.fetchall()

    if items:
        # Count duplicate items
        item_counts = {}
        for item in items:
            item_key = (item[0], item[2], item[3])  # name, value, hp_effect
            item_counts[item_key] = item_counts.get(item_key, 0) + 1

        inventory_text = ""
        for item_key, count in item_counts.items():
            name, value, hp_effect = item_key
            inventory_text += f"• {name} (Value: {value} GP"
            if hp_effect != 0:
                inventory_text += f", HP: {hp_effect}"
            if count > 1:
                inventory_text += f") [x{count}]\n"
            else:
                inventory_text += ")\n"
        embed.add_field(name="Inventory", value=inventory_text, inline=False)
    else:
        embed.add_field(name="Inventory", value="Empty", inline=False)

    await interaction.response.send_message(embed=embed)
    conn.close()

@client.tree.command(name="explore", description="Explore an area with a specific character")
@app_commands.choices(area=[
    app_commands.Choice(name="High School (Easy) - Level 0-5", value="High School"),
    app_commands.Choice(name="Park (Easy) - Level 5-10", value="Park"),
    app_commands.Choice(name="Beach (Medium) - Level 5-10", value="Beach"),
    app_commands.Choice(name="City (Medium) - Level 5-10", value="City"),
    app_commands.Choice(name="Sewers (Hard) - Level 10-15", value="Sewers"),
    app_commands.Choice(name="Forest (Hard) - Level 10-15", value="Forest"),
    app_commands.Choice(name="Destroyed Research Site (Extreme) - Level 15-20", value="Destroyed Research Site"),
    app_commands.Choice(name="Abandoned Facility (Extreme) - Level 15-20", value="Abandoned Facility"),
    app_commands.Choice(name="Ash Lake (Nightmare) - Level 20", value="Ash Lake")
])
async def explore(interaction: discord.Interaction, character_name: str, area: str):
    conn = connect()
    cursor = conn.cursor()

    # Get character info
    cursor.execute("""
    SELECT character_name, level FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ You don't have a character! Use `/create_character` to make one.")
        conn.close()
        return

    if area not in client.areas:
        available_areas = ", ".join(client.areas.keys())
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ Invalid area! Available areas: {available_areas}")
        conn.close()
        return

    selected_area = client.areas[area]
    char_level = character[1]

    # Location descriptions
    location_descriptions = {
        "High School": "A normal-looking High School with noisy classrooms, messy lockers and weird rumors in the halls. It's eerily silent at night.",
        "Park": "A run-down park with broken swings, old trails, and overgrown paths. It feels frozen in time.",
        "Beach": "A quiet, foggy shore with broken docks and scattered trash. The waves carry whispers.",
        "City": "Busy streets, dark alleys and strange people. The deeper you go, the more dangerous it gets.",
        "Sewers": "Dark, damp tunnels under the city. It smells bad and worse things live down here.",
        "Forest": "A thick forest just outside town. It's quiet, too quiet. You always feel like something's watching.",
        "Destroyed Research Site": "Smashed equipment, scorched walls, and sparking wires still flicker beneath the roots. Whatever happened here was violent.",
        "Abandoned Facility": "An old lab that's falling apart. It's locked up, full of weird tech... and maybe something still inside.",
        "Ash Lake": "A vast, quiet lake blanketed in ash. The sky above is pale and empty and the water below feels bottomless. Time seems to pause here."
    }

    if char_level < selected_area.min_level:
        await interaction.response.send_message(
            f"<a:warning:1372876834135609404> ┃ Your level ({char_level}) is too low for {area}! You need to be at least level {selected_area.min_level}."
        )
        conn.close()
        return

    # Update character's location
    cursor.execute("""
    UPDATE profiles 
    SET active_location = ?
    WHERE user_id = ? AND character_name = ?
    """, (area, interaction.user.id, character_name))
    conn.commit()
    conn.close()

    embed = discord.Embed(title=f"{character_name} entered {area}", description=location_descriptions[area], color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="leave", description="Leave your current location with a specific character")
async def leave(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT character_name, active_location FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    if not character[1]:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ {character_name} is not in any location!")
        conn.close()
        return

    location = character[1]
    cursor.execute("""
    UPDATE profiles 
    SET active_location = NULL
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    conn.commit()
    conn.close()

    await interaction.response.send_message(f"{character_name} left {location}.")

@client.tree.command(name="shop", description="View available items in the shop")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(title="Shop", description="Available items:", color=discord.Color.gold())
    for item, details in client.shop_items.items():
        embed.add_field(name=item, value=f"Price: {details['price']} GP\n{details['description']}", inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="buy", description="Buy an item from the shop")
async def buy(interaction: discord.Interaction, character_name: str, item: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    if item not in client.shop_items:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Item not available!")
        conn.close()
        return

    item_details = client.shop_items[item]

    # Check if player has enough GP
    cursor.execute("SELECT gp FROM profiles WHERE character_id = ?", (character[0],))
    current_gp = cursor.fetchone()[0]

    if current_gp < item_details['price']:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ Not enough GP! You need {item_details['price']} GP, but you only have {current_gp} GP.")
        conn.close()
        return

    # Subtract GP and add item to inventory
    cursor.execute("UPDATE profiles SET gp = gp - ? WHERE character_id = ?", 
                  (item_details['price'], character[0]))

    cursor.execute("""
    INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
    VALUES (?, ?, ?, ?, ?)
    """, (character[0], item, item_details['description'], item_details['price'], item_details.get('hp_effect', 0)))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"Bought {item} for {item_details['price']} GP!")

@client.tree.command(name="loot", description="Search for loot in your current area")
async def loot(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Get character location and info
    cursor.execute("""
    SELECT active_location FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character or not character[0]:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ {character_name} is not in any location!")
        conn.close()
        return

    current_location = character[0]

    # Random chance (20%) to encounter enemy
    if random.random() < 0.2:
        cursor.execute("""
        SELECT name, description FROM enemies
        WHERE location = ?
        ORDER BY RANDOM() LIMIT 1
        """, (current_location,))
        enemy = cursor.fetchone()

        if enemy:
            embed = discord.Embed(
                title="Enemy Encounter", 
                description=f"While searching for loot, {character_name} encountered a {enemy[0]}!\n{enemy[1]}", 
                color=discord.Color.red()
            )
            view = EncounterView(character_name, enemy[0], enemy[1], current_location)
            await interaction.response.send_message(embed=embed, view=view)
            conn.close()
            return

    await interaction.response.send_message(f"{character_name} found nothing of value...")

    conn.close()

# Encounter system variables
active_encounters = {}

class EncounterView(discord.ui.View):
    def __init__(self, character_name: str, enemy_name: str, enemy_description: str, location: str):
        super().__init__()
        self.character_name = character_name
        self.enemy_name = enemy_name
        self.enemy_description = enemy_description
        self.location = location
        self.combat_round = 1

        # Get character level and calculate enemy HP
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT level, hp FROM profiles WHERE character_name = ?", (character_name,))
        char_data = cursor.fetchone()
        self.char_level = char_data[0]
        self.char_hp = char_data[1]
        conn.close()

        # Enemy HP scales with location (reduced for lower levels)
        location_hp = {
            "High School": (15, 30),
            "Park": (25, 35),
            "Beach": (30, 50),
            "City": (35, 60),
            "Sewers": (60, 100),
            "Forest": (60, 100),
            "Destroyed Research Site": (110, 150),
            "Abandoned Facility": (100, 130),
            "Ash Lake": (150, 200)
        }
        min_hp, max_hp = location_hp.get(location, (30, 50))
        self.enemy_hp = random.randint(min_hp, max_hp)
        self.max_enemy_hp = self.enemy_hp

    async def calculate_damage(self, location: str, is_second_roll: bool = False) -> int:
        # Adjusted damage ranges (player deals more damage, enemies deal less)
        damage_ranges = {
            "High School": (5, 15),  # Easier starting area
            "Park": (5, 15),         # Similar to high school
            "Beach": (10, 25),        # Moderate challenge
            "City": (10, 25),         # Moderate challenge
            "Sewers": (15, 35),      # Harder but not unfair
            "Forest": (15, 35),      # Similar to sewers
            "Destroyed Research Site": (30, 50),
            "Abandoned Facility": (25, 45),  # Tough but manageable
            "Ash Lake": (40, 70)
        }
        min_dmg, max_dmg = damage_ranges.get(location, (5, 15))

        # Player deals more damage, enemies deal less
        if is_second_roll:  # Enemy damage
            damage = random.randint(min_dmg // 2, max_dmg // 2)
        else:  # Player damage
            damage = random.randint(min_dmg * 2, max_dmg * 2)

        return damage

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.character_name in active_encounters:
            del active_encounters[self.character_name]
        await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ {self.character_name} fled safely from the {self.enemy_name}.")
        self.stop()

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = connect()
        cursor = conn.cursor()

        # Get character's location and current HP
        cursor.execute("""
        SELECT active_location, hp FROM profiles
        WHERE character_name = ?
        """, (self.character_name,))
        char_data = cursor.fetchone()
        location, self.char_hp = char_data

        # Combat roll with full range
        player_roll = random.randint(1, 20)
        enemy_roll = random.randint(1, 20)

        embed = discord.Embed(title="Combat Roll", color=discord.Color.blue())
        embed.add_field(name=f"{self.character_name}'s Roll", value=str(player_roll), inline=True)
        embed.add_field(name=f"{self.enemy_name}'s Roll", value=str(enemy_roll), inline=True)

        if player_roll == enemy_roll:
            embed.description = f"Both {self.character_name} and {self.enemy_name} matched each other's moves! Combat continues!"
            max_hp = 100 + (self.char_level * 10)  # Base HP + (level * 10)
            embed.add_field(name="Your HP", value=f"{self.char_hp}/{max_hp}", inline=True)
            embed.add_field(name="Enemy HP", value=f"{self.enemy_hp}/{self.max_enemy_hp}", inline=True)
            embed.add_field(name="Combat Continues!", value="Choose your next action!", inline=False)
            await interaction.response.send_message(embed=embed, view=self)
            conn.close()
            return
        # Calculate damage based on roll difference
        if player_roll > enemy_roll:
            # Calculate damage with level scaling (10% increase per level)
            base_damage = player_roll - enemy_roll
            level_multiplier = 1 + (self.char_level * 0.1)  # Each level adds 10% damage
            damage_to_enemy = int(base_damage * level_multiplier)
            self.enemy_hp -= damage_to_enemy
            embed.description = f"Victory! You won the roll and dealt {damage_to_enemy} damage to the {self.enemy_name}!"
            embed.add_field(name="Damage Dealt", value=f"You dealt {damage_to_enemy} damage (Level bonus: {int((level_multiplier-1)*100)}%)")
            embed.add_field(name="Enemy HP", value=f"{self.enemy_hp}/{self.max_enemy_hp}", inline=True)

            if self.enemy_hp <= 0:
                # Get location XP values
                location_xp = {
                    "High School": 50,
                    "Park": 50,
                    "Beach": 65,
                    "City": 65,
                    "Sewers": 80,
                    "Forest": 80,
                    "Destroyed Research Site": 150,
                    "Abandoned Facility": 100,
                    "Ash Lake": 200
                }
                xp_gain = location_xp.get(self.location, 50)
                leveled_up = update_character_xp(self.character_name, xp_gain)

                # Check for loot
                cursor.execute("""
                    SELECT name, description, value, hp_effect FROM loot_items
                    WHERE location = ?
                    ORDER BY RANDOM() LIMIT 1
                    """, (self.location,))
                loot = cursor.fetchone()

                # Create victory embed
                victory_embed = discord.Embed(
                    title="🏆 Combat Victory!",
                    description=f"{self.character_name} defeated the {self.enemy_name}!",
                    color=discord.Color.green()
                )

                victory_embed.add_field(name="💫 Experience Gained", value=f"+{xp_gain} XP", inline=False)

                if leveled_up:
                    victory_embed.add_field(
                        name="🎉 LEVEL UP!",
                        value="You've grown stronger!",
                        inline=False
                    )

                # Add loot if found
                if loot and random.random() < 0.7:  # 70% chance to get loot
                    cursor.execute("""
                    INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
                    SELECT character_id, ?, ?, ?, ?
                    FROM profiles
                    WHERE character_name = ?
                    """, (loot[0], loot[1], loot[2], loot[3], self.character_name))
                    conn.commit()

                    loot_text = f"**{loot[0]}**\n"
                    loot_text += f"Value: {loot[2]} GP"
                    if loot[3] != 0:
                        loot_text += f"\nHP Effect: {loot[3]}"
                    victory_embed.add_field(
                        name="🎁 Loot Acquired!",
                        value=loot_text,
                        inline=False
                    )

                conn.close()
                await interaction.response.send_message(embed=victory_embed)
                return self.stop()
            else:
                await interaction.response.send_message(embed=embed, view=self)
        else:
            # Calculate and apply damage (with fixed multiplier)
            damage = enemy_roll - player_roll  # Direct damage without multiplier
            new_hp = max(0, self.char_hp - damage)
            cursor.execute("""
            UPDATE profiles
            SET hp = ?
            WHERE character_name = ?
            """, (new_hp, self.character_name))
            conn.commit()

            embed.description = f"You lost the first roll and took {damage} damage! Choose to flee or fight again!"
            max_hp = 100 + (self.char_level * 10)  # Base HP + (level * 10)
            embed.add_field(name="Your HP", value=f"{new_hp}/{max_hp}", inline=True)
            embed.add_field(name="Enemy HP", value=f"{self.enemy_hp}/{self.max_enemy_hp}", inline=True)

            if new_hp <= 0:
                embed.description = f"💀 {self.character_name} was killed by the {self.enemy_name}!"
                await interaction.response.send_message(embed=embed)
                return self.stop()
            else:
                embed.add_field(name="Combat Continues!", value="Choose your next action!", inline=False)
                if new_hp <= 10:
                    embed.add_field(name="⚠️ WARNING", value=f"{self.character_name} is critically wounded!", inline=False)
                await interaction.response.send_message(embed=embed, view=self)
            conn.close()

class SecondChanceView(discord.ui.View):
    def __init__(self, character_name: str, enemy_name: str, location: str):
        super().__init__()
        self.character_name = character_name
        self.enemy_name = enemy_name
        self.location = location

    async def calculate_damage(self, location: str, is_second_roll: bool = False) -> int:
        damage_ranges = {
            "High School": (2, 20),
            "Park": (2, 20),
            "Beach": (10, 30),
            "City": (10, 30),
            "Sewers": (30, 50),
            "Forest": (15, 30),
            "Destroyed Research Site": (40, 70),
            "Abandoned Facility": (45, 65),
            "Ash Lake": (50, 80)
        }
        min_dmg, max_dmg = damage_ranges.get(location, (2, 20))
        damage = random.randint(min_dmg, max_dmg)
        if is_second_roll:
            damage *= 2
        return damage

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{self.character_name} fled safely from the {self.enemy_name}.")
        self.stop()

    @discord.ui.button(label="Fight Again", style=discord.ButtonStyle.danger)
    async def fight_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = connect()
        cursor = conn.cursor()

        # Get character's current HP
        cursor.execute("""
        SELECT hp FROM profiles
        WHERE character_name = ?
        """, (self.character_name,))
        current_hp = cursor.fetchone()[0]

        player_roll = random.randint(1, 10)
        enemy_roll = random.randint(1, 10)

        embed = discord.Embed(title="Second Combat Roll", color=discord.Color.blue())
        embed.add_field(name=f"{self.character_name}'s Roll", value=str(player_roll), inline=True)
        embed.add_field(name=f"{self.enemy_name}'s Roll", value=str(enemy_roll), inline=True)

        if player_roll > enemy_roll:
            embed.description = f"After a tough battle, {self.character_name} managed to defeat the {self.enemy_name}!"
        else:
            # Calculate double damage on second loss
            damage = await self.calculate_damage(self.location, is_second_roll=True)
            new_hp = max(0, current_hp - damage)

            cursor.execute("""
            UPDATE profiles
            SET hp = ?
            WHERE character_name = ?
            """, (new_hp, self.character_name))
            conn.commit()

            embed.description = f"🪦 {self.character_name} was defeated by the {self.enemy_name} after taking {damage} damage!"
            embed.add_field(name="HP Remaining", value=f"{new_hp}/100", inline=False)

            if new_hp == 0:
                embed.add_field(name="💀 DEATH", value=f"{self.character_name} has fallen in battle!", inline=False)
            elif new_hp <= 10:
                embed.add_field(name="⚠️ WARNING", value=f"{self.character_name} is critically wounded!", inline=False)

            await interaction.response.send_message(embed=embed)
            conn.close()
            self.stop()

@client.tree.command(name="sell_item", description="Sell an item from your inventory")
async def sell_item(interaction: discord.Interaction, character_name: str, item_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    # Get item from inventory
    cursor.execute("""
    SELECT id, value FROM inventory
    WHERE character_id = ? AND item_name = ?
    LIMIT 1
    """, (character[0], item_name))
    item = cursor.fetchone()

    if not item:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ {character_name} doesn't have a {item_name}!")
        conn.close()
        return

    # Add full value as GP
    sell_value = item[1]
    cursor.execute("UPDATE profiles SET gp = gp + ? WHERE character_id = ?", 
                  (sell_value, character[0]))

    # Remove the item
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item[0],))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"Sold {item_name} for {sell_value} GP!")



@client.tree.command(name="weather", description="Check the current weather")
async def weather(interaction: discord.Interaction):
    if random.random() < 0.3:  # 30% chance to change weather
        client.current_weather = random.choice(client.weather)
    await interaction.response.send_message(f"Current weather: {client.current_weather}")

# Register all commands at startup
@client.event
async def setup_hook():
    try:
        await client.tree.sync()
        print("Commands synced successfully")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.tree.command(name="remove_item", description="Remove an item from your character's inventory")
async def remove_item(interaction: discord.Interaction, character_name: str, item_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    # Check if item exists in inventory
    cursor.execute("""
    SELECT id FROM inventory
    WHERE character_id = ? AND item_name = ?
    LIMIT 1
    """, (character[0], item_name))
    item = cursor.fetchone()

    if not item:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ {character_name} doesn't have a {item_name}!")
        conn.close()
        return

    # Remove the item
    cursor.execute("""
    DELETE FROM inventory
    WHERE id = ?
    """, (item[0],))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ Removed {item_name} from {character_name}'s inventory.")

@client.tree.command(name="heal", description="Use a healing item from your inventory")
async def heal(interaction: discord.Interaction, character_name: str, item_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id, hp FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    character_id, current_hp = character

    # Get the item with hp_effect > 0
    cursor.execute("""
    SELECT id, item_name, hp_effect FROM inventory
    WHERE character_id = ? AND item_name = ? AND hp_effect > 0
    LIMIT 1
    """, (character_id, item_name))
    item = cursor.fetchone()

    if not item:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ No healing item named '{item_name}' found in inventory!")
        conn.close()
        return

    item_id, item_name, hp_effect = item
    # Get character level for max HP calculation
    cursor.execute("SELECT level FROM profiles WHERE character_id = ?", (character_id,))
    char_level = cursor.fetchone()[0]
    max_hp = 100 + (char_level * 10)  # Base HP + (level * 10)
    new_hp = min(max_hp, current_hp + hp_effect)  # Cap HP at max_hp

    # Update character's HP
    cursor.execute("""
    UPDATE profiles
    SET hp = ?
    WHERE character_id = ?
    """, (new_hp, character_id))

    # Remove the used item from inventory
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()

    embed = discord.Embed(title="Item Used", color=discord.Color.green())
    embed.add_field(name="Item", value=item_name)
    embed.add_field(name="Healing", value=f"+{hp_effect} HP")
    embed.add_field(name="New HP", value=f"{new_hp}/100", inline=False)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="fight", description="Fight a specific enemy with your character")
async def fight(interaction: discord.Interaction, character_name: str, enemy_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT active_location FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    if not character[0]:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ {character_name} is not in any location!")
        conn.close()
        return

    # Get enemy from current location
    cursor.execute("""
    SELECT name, description FROM enemies
    WHERE location = ? AND name LIKE ?
    """, (character[0], f"%{enemy_name}%"))
    enemy = cursor.fetchone()
    conn.close()

    if not enemy:
        await interaction.response.send_message(f"<a:warning:1372876834135609404> ┃ No enemy named '{enemy_name}' found in {character[0]}!")
        return

    embed = discord.Embed(
        title="Enemy Encounter", 
        description=f"{character_name} challenged {enemy[0]}!\n{enemy[1]}", 
        color=discord.Color.red()
    )
    view = EncounterView(character_name, enemy[0], enemy[1], character[0])
    await interaction.response.send_message(embed=embed, view=view)



@client.tree.command(name="add_hp", description="Add HP to your character (maximum 100)")
async def add_hp(interaction: discord.Interaction, character_name: str, amount: int):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id, hp FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    character_id, current_hp = character
    cursor.execute("SELECT level FROM profiles WHERE character_id = ?", (character_id,))
    char_level = cursor.fetchone()[0]
    max_hp = 100 + (char_level * 10)  # Base HP + (level * 10)
    new_hp = min(max_hp, current_hp + amount)  # Cap HP at max_hp

    # Update character's HP
    cursor.execute("""
    UPDATE profiles
    SET hp = ?
    WHERE character_id = ?
    """, (new_hp, character_id))

    conn.commit()
    conn.close()

    embed = discord.Embed(title="HP Added", color=discord.Color.green())
    embed.add_field(name="Added", value=f"+{amount} HP")
    embed.add_field(name="New HP", value=f"{new_hp}/100")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="roll", description="Rolls dice in NdX format (e.g. 2d6 for two 6-sided dice)")
async def roll(interaction: discord.Interaction, dice: str = "1d20"):
    try:
        num, sides = map(int, dice.lower().split("d"))
        if num <= 0 or sides <= 0 or num > 100:  # Added upper limit for safety
            await interaction.response.send_message("Please enter a valid dice format (e.g., 1d20). Maximum 100 dice.")
            return

        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls)
        roll_results = ", ".join(map(str, rolls))
        
        message = f"<a:DiceRoll:1372965997841223700> ┃ You rolled **{roll_results}**!"
        if len(rolls) > 1:
            message += f"\n⤷ Total: **{total}**"
            
        await interaction.response.send_message(message)

    except ValueError:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Invalid format! Use NdX (e.g., 1d20, 2d6).")


@client.tree.command(name="commands", description="List all available commands")
async def commands(interaction: discord.Interaction):
    embed = discord.Embed(title="<:AdminIcon:1372980092027928726> ┃ Available Commands", color=0x8c52ff)

    embed.add_field(name="‎", value="", inline=False)
    
    # Character Management
    embed.add_field(name="<a:Animated_Arrow_Purple:1372976728435331163> Character Commands", value="""
`/create_character` - Create a new character
`/delete_character` - Delete one of your characters
`/list_characters` - List all your characters
`/profile` - Show detailed character information
`/set_level` - Manually set character level

""", inline=False)


    embed.add_field(name="‎", value="", inline=False)

    # Combat & Exploration
    embed.add_field(name="<a:Animated_Arrow_Purple:1372976728435331163> Combat & Exploration", value="""
`/weather` - Check current weather
`/explore` - Enter a location to explore
`/leave` - Leave current location
`/fight` - Fight a specific enemy
`/loot` - Search for loot in current area
`/roll` - Roll dice (e.g. 2d6 for two 6-sided dice)

""", inline=False)

    embed.add_field(name="‎", value="", inline=False)

    # Inventory & Items
    embed.add_field(name="<a:Animated_Arrow_Purple:1372976728435331163> Inventory & Items", value="""
`/shop` - View items available in shop
`/buy` - Purchase an item from shop
`/sell_item` - Sell an item from inventory
`/remove_item` - Remove an item from inventory
`/heal` - Use a healing item
`/add_hp` - Add HP to your character

""", inline=False)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="set_level", description="Manually set your character's level")
async def set_level(interaction: discord.Interaction, character_name: str, level: int):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:warning:1372876834135609404> ┃ Character not found!")
        conn.close()
        return

    # Update character's level
    cursor.execute("""
    UPDATE profiles
    SET level = ?
    WHERE character_id = ?
    """, (level, character[0]))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"{character_name}'s level has been set to {level}.")

try:
    client.run(os.getenv('DISCORD_TOKEN'))
except KeyboardInterrupt:
    # Graceful shutdown
    logger.info("Bot is shutting down...")
finally:
    # Cleanup
    if not client.is_closed():
        client.close()