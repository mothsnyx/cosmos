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
            "High School": Area("High School (Easy)", ["Bully", "Delinquent", "Rival Student"], 
                              ["Training Manual", "School Uniform", "Basic Nen Tools"], 0, 5, 10),
            "City": Area("City (Medium)", ["Thug", "Criminal", "Corrupt Officer"], 
                        ["Street Weapon", "Combat Gear", "City Maps"], 5, 10, 20),
            "Sewers": Area("Sewers (Hard)", ["Mutant", "Underground Boss", "Escaped Experiment"], 
                          ["Toxic Shield", "Sewer Map", "Rare Artifact"], 10, 15, 30),
            "Forest": Area("Forest (Hard)", ["Beast", "Dark Hunter", "Ancient Spirit"], 
                          ["Beast Core", "Spirit Essence", "Forest Relic"], 10, 15, 30),
            "Abandoned Facility": Area("Abandoned Facility (Extreme)", ["Failed Experiment", "Mad Scientist", "Ultimate Weapon"], 
                                    ["Experimental Gear", "Research Data", "Ultimate Tech"], 15, 20, 50)
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
        await interaction.response.send_message("A character with this name already exists!")
        conn.close()
        return

    # Create character
    cursor.execute("""
    INSERT INTO profiles (user_id, character_name, hp, level)
    VALUES (?, ?, ?, ?)
    """, (interaction.user.id, name, 100, 0))
    conn.commit()
    conn.close()

    await interaction.response.send_message(f"Character created: {name} ")

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
        await interaction.response.send_message("Character not found or doesn't belong to you!")
        conn.close()
        return

    # Delete character's inventory
    cursor.execute("DELETE FROM inventory WHERE character_id = ?", (character[0],))

    # Delete character profile
    cursor.execute("DELETE FROM profiles WHERE character_id = ?", (character[0],))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"Character '{character_name}' has been deleted.")

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
        await interaction.response.send_message("You don't have any characters yet!")
        return

    embed = discord.Embed(title="Your Characters", color=discord.Color.blue())
    for char in characters:
        embed.add_field(name=char[0], 
                       value=f"Level: {char[2]}\nHP: {char[1]}/100",
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
        await interaction.response.send_message("Character not found! Use /create_character to make one.")
        conn.close()
        return

    # Calculate XP needed for next level
    xp_for_next_level = 100 * (character[2] + 1) * 1.5

    # Get GP
    cursor.execute("SELECT gp FROM profiles WHERE character_name = ?", (character[0],))
    gp = cursor.fetchone()[0]

    embed = discord.Embed(title=f"{character[0]}'s Profile", color=discord.Color.blue())
    embed.add_field(name="HP", value=f"{character[1]}/100")
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
    app_commands.Choice(name="City (Medium) - Level 5-10", value="City"),
    app_commands.Choice(name="Sewers (Hard) - Level 10-15", value="Sewers"),
    app_commands.Choice(name="Forest (Hard) - Level 10-15", value="Forest"),
    app_commands.Choice(name="Abandoned Facility (Extreme) - Level 15-20", value="Abandoned Facility")
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
        await interaction.response.send_message("You don't have a character! Create one first with /create_character")
        conn.close()
        return

    if area not in client.areas:
        available_areas = ", ".join(client.areas.keys())
        await interaction.response.send_message(f"Invalid area! Available areas: {available_areas}")
        conn.close()
        return

    selected_area = client.areas[area]
    char_level = character[1]

    # Location descriptions
    location_descriptions = {
        "High School": "A normal-looking High School with noisy classrooms, messy lockers and weird rumors in the halls. It's eerily silent at night.",
        "City": "Busy streets, dark alleys and strange people. The deeper you go, the more dangerous it gets.",
        "Sewers": "Dark, damp tunnels under the city. It smells bad and worse things live down here.",
        "Forest": "A thick forest just outside town. It's quiet, too quiet. You always feel like something's watching.",
        "Abandoned Facility": "An old lab that's falling apart. It's locked up, full of weird tech... and maybe something still inside."
    }

    if char_level < selected_area.min_level:
        await interaction.response.send_message(
            f"Your level ({char_level}) is too low for {area}! You need to be at least level {selected_area.min_level}."
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
        await interaction.response.send_message("Character not found!")
        conn.close()
        return

    if not character[1]:
        await interaction.response.send_message(f"{character_name} is not in any location!")
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
        await interaction.response.send_message("Character not found!")
        conn.close()
        return

    if item not in client.shop_items:
        await interaction.response.send_message("Item not available!")
        conn.close()
        return

    item_details = client.shop_items[item]

    # Check if player has enough GP
    cursor.execute("SELECT gp FROM profiles WHERE character_id = ?", (character[0],))
    current_gp = cursor.fetchone()[0]

    if current_gp < item_details['price']:
        await interaction.response.send_message(f"Not enough GP! You need {item_details['price']} GP but only have {current_gp} GP.")
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
        await interaction.response.send_message(f"{character_name} is not in any location!")
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

    # 70% chance to find loot
    if random.random() < 0.7:
        cursor.execute("""
        SELECT name, description, value, hp_effect FROM loot_items
        WHERE location = ?
        ORDER BY RANDOM() LIMIT 1
        """, (current_location,))
        loot = cursor.fetchone()

        if loot:
            # Add item to inventory
            cursor.execute("""
            INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
            SELECT character_id, ?, ?, ?, ?
            FROM profiles
            WHERE user_id = ? AND character_name = ?
            """, (loot[0], loot[1], loot[2], loot[3], interaction.user.id, character_name))

            conn.commit()  # Commit the inventory addition

            embed = discord.Embed(
                title="🎁 Loot Found!",
                description=f"{character_name} found: {loot[0]}\n{loot[1]}",
                color=discord.Color.gold()
            )
            embed.add_field(name="Value", value=f"{loot[2]} GP")
            if loot[3] != 0:
                embed.add_field(name="HP Effect", value=str(loot[3]))

            # Award XP for finding loot (20-40 XP based on location)
            location_xp = {
                "High School": 20,
                "City": 25,
                "Sewers": 30,
                "Forest": 30,
                "Abandoned Facility": 40
            }
            xp_gain = location_xp.get(current_location, 20)
            leveled_up = update_character_xp(character_name, xp_gain)

            if leveled_up:
                embed.add_field(name="Level Up! 🎉", value="You've grown stronger!")
            embed.add_field(name="XP Gained", value=f"+{xp_gain} XP")

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{character_name} found nothing of value...")
    else:
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
        
        # Get character level and calculate enemy HP
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT level, hp FROM profiles WHERE character_name = ?", (character_name,))
        char_data = cursor.fetchone()
        self.char_level = char_data[0]
        self.char_hp = char_data[1]
        conn.close()
        
        # Enemy HP scales with location
        location_hp = {
            "High School": (30, 50),
            "City": (50, 80),
            "Sewers": (80, 120),
            "Forest": (80, 120),
            "Abandoned Facility": (120, 150)
        }
        min_hp, max_hp = location_hp.get(location, (30, 50))
        self.enemy_hp = random.randint(min_hp, max_hp)
        self.max_enemy_hp = self.enemy_hp

    async def calculate_damage(self, location: str, is_second_roll: bool = False) -> int:
        damage_ranges = {
            "High School": (2, 20),
            "City": (10, 30),
            "Sewers": (30, 50),
            "Forest": (15, 30),
            "Abandoned Facility": (45, 65)
        }
        min_dmg, max_dmg = damage_ranges.get(location, (2, 20))
        damage = random.randint(min_dmg, max_dmg)
        if is_second_roll:
            damage *= 2
        return damage

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.character_name in active_encounters:
            del active_encounters[self.character_name]
        await interaction.response.send_message(f"{self.character_name} fled safely from the {self.enemy_name}.")
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

        # First roll with reduced range
        player_roll = random.randint(1, 10)
        enemy_roll = random.randint(1, 10)

        embed = discord.Embed(title="First Combat Roll", color=discord.Color.blue())
        embed.add_field(name=f"{self.character_name}'s Roll", value=str(player_roll), inline=True)
        embed.add_field(name=f"{self.enemy_name}'s Roll", value=str(enemy_roll), inline=True)

        if player_roll == enemy_roll:
            embed.description = f"The {self.enemy_name} changed its mind and fled!"
            await interaction.response.send_message(embed=embed)
            conn.close()
            self.stop()
            return
        # Calculate damage based on roll difference
        if player_roll > enemy_roll:
                damage_to_enemy = (player_roll - enemy_roll) * 10
                self.enemy_hp -= damage_to_enemy
                embed.add_field(name="Damage Dealt", value=f"You dealt {damage_to_enemy} damage!")
                embed.add_field(name="Enemy HP", value=f"{max(0, self.enemy_hp)}/{self.max_enemy_hp}")
                
                if self.enemy_hp <= 0:
                    embed.description = f"🏆 Victory! {self.character_name} killed the {self.enemy_name}!"
                    conn = connect()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT active_location FROM profiles
                        WHERE character_name = ?
                        """, (self.character_name,))
                    location = cursor.fetchone()[0]

            # 70% chance to find loot
                    if random.random() < 0.7:
                        cursor.execute("""
                            SELECT name, description, value, hp_effect FROM loot_items
                            WHERE location = ?
                            ORDER BY RANDOM() LIMIT 1
                            """, (location,))
                        loot = cursor.fetchone()

                        if loot:
                            cursor.execute("""
                                INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
                                SELECT character_id, ?, ?, ?, ?
                                FROM profiles
                                WHERE character_name = ?
                                """, (loot[0], loot[1], loot[2], loot[3], self.character_name))
                            conn.commit()

                            embed.add_field(name="🎁 Loot Reward!", value=f"Found: {loot[0]}\nValue: {loot[2]} GP")
                            if loot[3] != 0:
                                embed.add_field(name="HP Effect", value=str(loot[3]))

            # Award XP for victory (50-100 XP based on location difficulty)
            location_xp = {
                "High School": 50,
                "City": 65,
                "Sewers": 80,
                "Forest": 80,
                "Abandoned Facility": 100
            }
            xp_gain = location_xp.get(location, 50)
            leveled_up = update_character_xp(self.character_name, xp_gain)

            embed.description = f"🏆 Victory! {self.character_name} defeated the {self.enemy_name}!"
            embed.add_field(name="XP Gained", value=f"+{xp_gain} XP")
            if leveled_up:
                embed.add_field(name="Level Up! 🎉", value="You've grown stronger!")

            conn.close()
            await interaction.response.send_message(embed=embed)
            self.stop()
        else:
            # Calculate and apply damage
            damage = (enemy_roll - player_roll) * 8
            new_hp = max(0, self.char_hp - damage)
            cursor.execute("""
            UPDATE profiles
            SET hp = ?
            WHERE character_name = ?
            """, (new_hp, self.character_name))
            conn.commit()

            embed.description = f"You lost the first roll and took {damage} damage! Choose to flee or fight again!"
            embed.add_field(name="HP Remaining", value=f"{new_hp}/100", inline=False)

            if new_hp <= 0:
                embed.description = f"💀 {self.character_name} was killed by the {self.enemy_name}!"
                await interaction.response.send_message(embed=embed)
            elif new_hp <= 10:
                embed.add_field(name="⚠️ WARNING", value=f"{self.character_name} is critically wounded!", inline=False)
                view = SecondChanceView(self.character_name, self.enemy_name, location)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                view = SecondChanceView(self.character_name, self.enemy_name, location)
                await interaction.response.send_message(embed=embed, view=view)
            conn.close()
            self.stop()

class SecondChanceView(discord.ui.View):
    def __init__(self, character_name: str, enemy_name: str, location: str):
        super().__init__()
        self.character_name = character_name
        self.enemy_name = enemy_name
        self.location = location

    async def calculate_damage(self, location: str, is_second_roll: bool = False) -> int:
        damage_ranges = {
            "High School": (2, 20),
            "City": (10, 30),
            "Sewers": (30, 50),
            "Forest": (15, 30),
            "Abandoned Facility": (45, 65)
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
        await interaction.response.send_message("Character not found!")
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
        await interaction.response.send_message(f"{character_name} doesn't have a {item_name}!")
        conn.close()
        return

    # Add half the value as GP (selling gives 50% of buy price)
    sell_value = item[1] // 2
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
        await interaction.response.send_message("Character not found!")
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
        await interaction.response.send_message(f"{character_name} doesn't have a {item_name}!")
        conn.close()
        return

    # Remove the item
    cursor.execute("""
    DELETE FROM inventory
    WHERE id = ?
    """, (item[0],))

    conn.commit()
    conn.close()

    await interaction.response.send_message(f"Removed {item_name} from {character_name}'s inventory.")

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
        await interaction.response.send_message("Character not found!")
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
        await interaction.response.send_message(f"No healing item named '{item_name}' found in inventory!")
        conn.close()
        return

    item_id, item_name, hp_effect = item
    new_hp = min(100, current_hp + hp_effect)  # Cap HP at 100

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

@client.tree.command(name="encounter", description="Start a random enemy encounter")
async def encounter(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT active_location FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("Character not found!")
        conn.close()
        return

    if not character[0]:
        await interaction.response.send_message(f"{character_name} is not in any location!")
        conn.close()
        return

    # Get random enemy from current location
    cursor.execute("""
    SELECT name, description FROM enemies
    WHERE location = ?
    ORDER BY RANDOM() LIMIT 1
    """, (character[0],))
    enemy = cursor.fetchone()
    conn.close()

    if not enemy:
        await interaction.response.send_message("No enemies found in this area.")
        return

    embed = discord.Embed(
        title="Enemy Encounter", 
        description=f"{character_name} encountered a {enemy[0]}!\n{enemy[1]}", 
        color=discord.Color.red()
    )
    view = EncounterView(character_name, enemy[0], enemy[1])
    await interaction.response.send_message(embed=embed, view=view)

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
        await interaction.response.send_message("Character not found!")
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