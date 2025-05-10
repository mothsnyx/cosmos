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
    SELECT p.character_name, p.nen_type, p.hp, p.level, p.active_location, p.character_id
    FROM profiles p
    WHERE p.user_id = ? AND p.character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("Character not found! Use /create_character to make one.")
        conn.close()
        return

    embed = discord.Embed(title=f"{character[0]}'s Profile", color=discord.Color.blue())
    embed.add_field(name="Nen Type", value=character[1])
    embed.add_field(name="HP", value=f"{character[2]}/100")
    embed.add_field(name="Level", value=str(character[3]))
    embed.add_field(name="Location", value=character[4] or "Not in any location")

    # Get inventory items
    cursor.execute("""
    SELECT item_name, description, value, hp_effect 
    FROM inventory 
    WHERE character_id = ?
    """, (character[5],))
    items = cursor.fetchall()

    if items:
        inventory_text = ""
        for item in items:
            inventory_text += f"• {item[0]} (Value: {item[2]} GP"
            if item[3] != 0:
                inventory_text += f", HP: {item[3]}"
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
            await interaction.response.send_message(
                f"⚔️ While searching for loot, {character_name} encountered a {enemy[0]}!\n{enemy[1]}\n(Combat system coming soon™)"
            )
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

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{character_name} found nothing of value...")
    else:
        await interaction.response.send_message(f"{character_name} found nothing of value...")

    conn.close()

@client.tree.command(name="weather", description="Check the current weather")
async def weather(interaction: discord.Interaction):
    if random.random() < 0.3:  # 30% chance to change weather
        client.current_weather = random.choice(client.weather)
    await interaction.response.send_message(f"Current weather: {client.current_weather}")

try:
    client.run(os.getenv('DISCORD_TOKEN'))
except KeyboardInterrupt:
    # Graceful shutdown
    logger.info("Bot is shutting down...")
finally:
    # Cleanup
    if not client.is_closed():
        client.close()

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

current_encounter_result = None
failed_attempts = 0

class EncounterView(discord.ui.View):
    def __init__(self, encounter_result):
        super().__init__()
        self.encounter_result = encounter_result

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You fled safely.")
        global current_encounter_result
        global failed_attempts
        current_encounter_result = None
        failed_attempts = 0
        self.stop()

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"You chose to fight the **{self.encounter_result}**! \nUse the command `!fight` to roll a die.")
        global current_encounter_result
        current_encounter_result = self.encounter_result
        self.stop()

class SecondEncounterView(discord.ui.View):
    def __init__(self, encounter_result):
        super().__init__()
        self.encounter_result = encounter_result

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You managed to flee, but suffered injuries in the process.")
        global current_encounter_result
        global failed_attempts
        current_encounter_result = None
        failed_attempts = 0
        self.stop()

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"You chose to continue fighting the **{self.encounter_result}**! \nUse the command `!fight` to roll a die.")
        global current_encounter_result
        current_encounter_result = self.encounter_result
        self.stop()

@bot.command(name="encounter")
async def encounter(ctx):
    """Simulates a Beast Encounter and returns the result."""
    encounter_result = random.choice(ENCOUNTERS)
    if encounter_result == "nothing":
        await ctx.send("You encountered nothing.")
    else:
        embed = discord.Embed(title="Beast Encounter", description=f"You encountered a **{encounter_result}**!", color=0x7d2122)
        view = EncounterView(encounter_result)
        await ctx.send(embed=embed, view=view)

@bot.command(name="fight")
async def fight(ctx, dice: str = "1d20"):
    """Rolls a dice in NdN format."""
    global current_encounter_result
    global failed_attempts
    if not current_encounter_result:
        await ctx.send('There is no active encounter. \nUse the `!encounter` command to start an encounter.')
        return

    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    total = sum(int(num) for num in result.split(', '))
    await ctx.send(f'You rolled **{result}** ')

    if rolls == 1 and limit == 20:
        roll_value = total
        beast_roll_value = random.randint(1, 20)
        survival_threshold = random.randint(10, 20)  # Random threshold to beat

        if roll_value == beast_roll_value:
            await ctx.send(f"The Enemy rolled **{beast_roll_value}** as well.\n\n**The {current_encounter_result} changed its mind and fled!**")
            current_encounter_result = None  # Reset encounter result
            failed_attempts = 0
        elif roll_value > survival_threshold:
            await ctx.send(f"The Enemy rolled **{survival_threshold}** \n\n🏆 ┃ **You defeated the {current_encounter_result}!** \n-# You can scavenge once more today. ")
            current_encounter_result = None  # Reset encounter result
            failed_attempts = 0
        else:
            failed_attempts += 1
            if failed_attempts == 1:
                await ctx.send(f"The Enemy rolled **{survival_threshold}**")
                embed = discord.Embed(title="Beast Encounter", description=f"You've been injured! Do you want to **fight** on or **flee**?\n *Continuing to fight may lead to your muse’s death*.", color=0x7d2122)
                view = SecondEncounterView(current_encounter_result)
                await ctx.send(embed=embed, view=view)
            elif failed_attempts >= 2:
                await ctx.send(f"The Enemy rolled **{survival_threshold}** \n\n🪦 ┃ **Your muse got killed by the {current_encounter_result}**.")
                current_encounter_result = None  # Reset encounter result
                failed_attempts = 0

