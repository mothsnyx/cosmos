
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
from database import setup_database, connect
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
    nen_type: str
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
            "Health Potion": 50,
            "Strength Potion": 75,
            "Magic Shield": 100
        }

client = RPGBot()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.tree.sync()

# Commands
@client.tree.command(name="create_character", description="Create your character")
async def create_character(interaction: discord.Interaction, name: str, nen_type: str):
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
    INSERT INTO profiles (user_id, character_name, nen_type, hp, level)
    VALUES (?, ?, ?, ?, ?)
    """, (interaction.user.id, name, nen_type, 100, 0))
    conn.commit()
    conn.close()
    
    await interaction.response.send_message(f"Character created: {name} ({nen_type})")

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
    SELECT character_name, nen_type, hp, level FROM profiles
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
                       value=f"Level: {char[3]}\nNen Type: {char[1]}\nHP: {char[2]}/100",
                       inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="profile", description="Show your character profile")
async def profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in client.characters:
        await interaction.response.send_message("You don't have a character yet! Use /create_character to make one.")
        return
    
    char = client.characters[user_id]
    embed = discord.Embed(title=f"{char.name}'s Profile", color=discord.Color.blue())
    embed.add_field(name="Nen Type", value=char.nen_type)
    embed.add_field(name="HP", value=f"{char.hp}/{char.max_hp}")
    embed.add_field(name="Coins", value=str(char.coins))
    embed.add_field(name="Items", value=", ".join(char.inventory["items"]) or "None")
    embed.add_field(name="Consumables", value=", ".join(char.inventory["consumables"]) or "None")
    await interaction.response.send_message(embed=embed)

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
    
    if char_level < selected_area.min_level:
        await interaction.response.send_message(
            f"Your level ({char_level}) is too low for {area}! You need to be level {selected_area.min_level}-{selected_area.max_level}."
        )
        conn.close()
        return
    
    if char_level > selected_area.max_level:
        await interaction.response.send_message(
            f"Your level ({char_level}) is too high for {area}! This area is for levels {selected_area.min_level}-{selected_area.max_level}."
        )
        conn.close()
        return

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
            await interaction.response.send_message("You don't have a character!")
            conn.close()
            return

        if not character[1]:
            await interaction.response.send_message("You're not in any location!")
            conn.close()
            return

        location = character[1]
        cursor.execute("""
        UPDATE profiles 
        SET active_location = NULL
        WHERE user_id = ?
        """, (interaction.user.id,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"{character[0]} left {location}.")

    # Update character's location
    cursor.execute("""
    UPDATE profiles 
    SET active_location = ?
    WHERE user_id = ?
    """, (area, interaction.user.id))
    conn.commit()
    
    await interaction.response.send_message(f"{character[0]} entered {area}.")
    
    # Random encounter
    if random.random() < 0.7:  # 70% chance of encounter
        enemy = random.choice(selected_area.enemies)
        item = random.choice(selected_area.items) if random.random() < 0.5 else None
        coins = random.randint(10, 50)
        exp_gain = selected_area.exp_reward + random.randint(-5, 5)
        
        char.exp += exp_gain
        # Level up check
        while char.exp >= (char.level + 1) * 100:  # Simple level up formula
            char.exp -= (char.level + 1) * 100
            char.level += 1
            char.max_hp += 20
            char.hp = char.max_hp
        
        result = f"You encountered a {enemy}!\n"
        if item:
            client.characters[user_id].inventory["items"].append(item)
            result += f"You found: {item}\n"
        
        client.characters[user_id].coins += coins
        result += f"You earned {coins} coins!"
        
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("You found nothing interesting...")

@client.tree.command(name="shop", description="View available items in the shop")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(title="Shop", description="Available items:", color=discord.Color.gold())
    for item, price in client.shop_items.items():
        embed.add_field(name=item, value=f"{price} coins")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="buy", description="Buy an item from the shop")
async def buy(interaction: discord.Interaction, item: str):
    user_id = str(interaction.user.id)
    if user_id not in client.characters:
        await interaction.response.send_message("Create a character first!")
        return
    
    if item not in client.shop_items:
        await interaction.response.send_message("Item not available!")
        return
    
    char = client.characters[user_id]
    price = client.shop_items[item]
    
    if char.coins < price:
        await interaction.response.send_message("Not enough coins!")
        return
    
    char.coins -= price
    char.inventory["consumables"].append(item)
    await interaction.response.send_message(f"Bought {item} for {price} coins!")

@client.tree.command(name="weather", description="Check the current weather")
async def weather(interaction: discord.Interaction):
    if random.random() < 0.3:  # 30% chance to change weather
        client.current_weather = random.choice(client.weather)
    await interaction.response.send_message(f"Current weather: {client.current_weather}")

client.run(os.getenv('DISCORD_TOKEN'))




