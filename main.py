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

        # Location images
        self.location_images = {
            "High School": "https://img.freepik.com/premium-photo/horror-creepy-classroom-background-happy-halloween-ai-generated_768733-45236.jpg",  # Creepy school hallway
            "Park": "https://images.stockcake.com/public/7/e/8/7e8e8ce1-f6df-4aaf-be35-5613a00e83b6_large/misty-playground-night-stockcake.jpg",        # Abandoned park
            "Beach": "https://www.shutterstock.com/shutterstock/videos/27109123/thumb/1.jpg?ip=x480",       # Foggy beach
            "City": "https://media.istockphoto.com/id/655391120/photo/dark-gritty-alleyway.jpg?s=612x612&w=0&k=20&c=1MJph3u_Mzj0-UKn-lfsbuuH0VCtQJC97fr_TkC7NGI=",        # Dark city street
            "Sewers": "https://i.pinimg.com/736x/17/81/13/178113127a3288af5a3accdff0520354.jpg",      # Dark sewer tunnel
            "Forest": "https://t3.ftcdn.net/jpg/01/88/23/12/360_F_188231209_KPPc1OfDIq7OfOOL8jSq5HHlQscmPhca.jpg",      # Dark forest
            "Destroyed Research Site": "https://img.freepik.com/premium-photo/discover-secrets-abandoned-lab-uncover-truth-experiments-that-took-place-within-these-walls_36682-13730.jpg",  # Ruined lab
            "Abandoned Facility": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/f700b7b2-208d-46fc-986e-38d7dc1ad83a/daju7x4-b64e64ef-e67e-4b84-913e-b18a7266835d.jpg/v1/fill/w_900,h_461,q_75,strp/abandoned_lab_by_milkmom_daju7x4-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NDYxIiwicGF0aCI6IlwvZlwvZjcwMGI3YjItMjA4ZC00NmZjLTk4NmUtMzhkN2RjMWFkODNhXC9kYWp1N3g0LWI2NGU2NGVmLWU2N2UtNGI4NC05MTNlLWIxOGE3MjY2ODM1ZC5qcGciLCJ3aWR0aCI6Ijw9OTAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.KSsjBXNkh5d7pT5Ob7ybfUdBE8ajJrh4K51Zwq2Oyzs",      # Abandoned facility
            "Ash Lake": "https://darksouls.wiki.fextralife.com/file/Dark-Souls/20111108220734.jpg"     # Misty lake
        }

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
            "<:wizard_potion:1372986090046357657> Minor Healing Potion": {"price": 20, "hp_effect": 10, "description": "-# Restores 10 HP"},
            "<:wizard_potion2:1372986129250255048> Moderate Healing Potion": {"price": 80, "hp_effect": 50, "description": "-# Restores 50 HP"},
            "<:wizard_potion3:1372986138465407046> Big Healing Potion": {"price": 160, "hp_effect": 100, "description": "-# Restores 100 HP"}
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ A character with this name already exists!")
        conn.close()
        return

    # Create character
    cursor.execute("""
    INSERT INTO profiles (user_id, character_name, hp, level, gp)
    VALUES (?, ?, ?, ?, ?)
    """, (interaction.user.id, name, 100, 0, 200))
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found or doesn't belong to you!")
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
    SELECT character_name, hp, level, nickname FROM profiles
    WHERE user_id = ?
    ORDER BY level DESC
    """, (interaction.user.id,))
    characters = cursor.fetchall()
    conn.close()

    if not characters:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ You don't have any characters yet!")
        return

    embed = discord.Embed(title="<a:Purplestar:1373007899240173710> ┃ Your Characters", color=0x8c52ff)

    # Group characters by level range
    level_ranges = [(0, 5), (6, 10), (11, 15), (16, 20)]

    for min_level, max_level in level_ranges:
        range_chars = [char for char in characters if min_level <= char[2] <= max_level]
        if range_chars:
            embed.add_field(name=f"── ✦ Level {min_level}-{max_level}", value="", inline=False)
            embed.add_field(name="‎", value="", inline=False)
            for char in range_chars:
                max_hp = 100 + (char[2] * 10)  # Base HP + (level * 10)
                display_name = char[0]
                if char[3]:  # If nickname exists
                    display_name = f"{char[0]} ({char[3]})"
                embed.add_field(name=display_name, 
                              value=f"Level: {char[2]}\nHP: {char[1]}/{max_hp}",
                              inline=True)
            embed.add_field(name="‎", value="", inline=False)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="profile", description="Show a character's profile")
async def profile(interaction: discord.Interaction, character_name: str):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT p.character_name, p.hp, p.level, p.active_location, p.character_id, p.xp, p.nickname
    FROM profiles p
    WHERE p.user_id = ? AND p.character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found! Use `/create_character` to make one.")
        conn.close()
        return

    # Calculate XP needed for next level
    xp_for_next_level = 100 * (character[2] + 1) * 1.5

    # Get GP
    cursor.execute("SELECT gp FROM profiles WHERE character_name = ?", (character[0],))
    gp = cursor.fetchone()[0]

    max_hp = 100 + (character[2] * 10)  # Base HP + (level * 10)
    title = f"<a:Purplestar:1373007899240173710> ┃ {character[0]}'s Profile"
    if character[6]:
         title = f"<a:Purplestar:1373007899240173710> ┃ {character[0]} ({character[6]})'s Profile"
    embed = discord.Embed(title=title, color=0x8c52ff)

    # Character Stats Section
    embed.add_field(name="── ✦ Character Stats", value="", inline=False)
    embed.add_field(name="‎", value="", inline=False)
    embed.add_field(name="<:61152memberglow:1373020726294085743> HP", value=f"{character[1]}/{max_hp}", inline=True)
    embed.add_field(name="‎", value="", inline=False)
    embed.add_field(name="<:37208ownerglow:1373020739090911386> Level", value=str(character[2]), inline=True)
    embed.add_field(name="‎", value="", inline=False)
    embed.add_field(name="<:93739moderatorglow:1373020791997993190> XP Progress", value=f"{character[5]}/{int(xp_for_next_level)}", inline=True)
    embed.add_field(name="‎", value="", inline=False)
    embed.add_field(name="<:74658vipglow:1373020781163843604> GP", value=str(gp), inline=True)
    embed.add_field(name="‎", value="", inline=False)
    embed.add_field(name="<:34647adminglow:1373020846209372250> Location", value=character[3] or "Not in any location", inline=True)
    embed.add_field(name="‎", value="", inline=False)

    # Get inventory items
    cursor.execute("""
    SELECT item_name, description, value, hp_effect 
    FROM inventory 
    WHERE character_id = ?
    """, (character[4],))
    items = cursor.fetchall()

    if items:
        # Separate items into categories
        consumables = []
        sellable_items = []

        # Count duplicate items
        item_counts = {}
        for item in items:
            item_key = (item[0], item[2], item[3])  # name, value, hp_effect
            item_counts[item_key] = item_counts.get(item_key, 0) + 1

        # Sort items into categories
        for item_key, count in item_counts.items():
            name, value, hp_effect = item_key
            item_text = f"• {name} (*{value} GP*"
            if hp_effect != 0:
                item_text += f", *HP: {hp_effect}*"
            if count > 1:
                item_text += f") **[x{count}]**"
            else:
                item_text += ")"

            if hp_effect > 0:
                consumables.append(item_text)
            else:
                sellable_items.append(item_text)

        # Add Consumables Section
        if consumables:
            embed.add_field(name="── ✦ Consumables", value="\n".join(consumables), inline=False)

        # Add Sellable Items Section
        if sellable_items:
            embed.add_field(name="── ✦ Sellable Items", value="\n".join(sellable_items), inline=False)

    else:
        embed.add_field(name="── ✦ Inventory", value="Empty", inline=False)

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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ You don't have a character! Use `/create_character` to make one.")
        conn.close()
        return

    if area not in client.areas:
        available_areas = ", ".join(client.areas.keys())
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ Invalid area! Available areas: {available_areas}")
        conn.close()
        return

    selected_area = client.areas[area]
    char_level = character[1]

    # Location descriptions
    location_descriptions = {
        "High School": "By day, it’s a prestigious High School filled with light and order, but when night falls, the halls twist into something dark and unrecognizable.",
        "Park": "During the day, the park is full of life and laughter. But at night the lights flicker weakly, the playground lies broken and still.",
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
            f"<a:tickred:1373240267880267836> ┃ Your level ({char_level}) is too low for {area}! You need to be at least level {selected_area.min_level}."
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

    embed = discord.Embed(title=f"<a:Purplestar:1373007899240173710> ┃ {character_name} entered the {area}.", description=location_descriptions[area], color=0x8c52ff)
    embed.set_image(url=client.location_images[area])
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
        conn.close()
        return

    if not character[1]:
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ {character_name} is not in any location!")
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

    await interaction.response.send_message(f"<a:Purplestar:1373007899240173710> ┃ {character_name} left the {location}.")

@client.tree.command(name="shop", description="View available items in the shop")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(title="<:AdminIcon:1372980092027928726> ┃ Shop", description="Available items:", color=0x8c52ff)
    embed.add_field(name="‎", value="", inline=False)  # Add initial spacing
    for item, details in client.shop_items.items():
        embed.add_field(name=item, value=f"- Price: {details['price']} GP\n{details['description']}", inline=False)
        embed.add_field(name="‎", value="", inline=False)  # Add spacing between items
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.choices(item=[
    app_commands.Choice(name="Minor Healing Potion", value="<:wizard_potion:1372986090046357657> Minor Healing Potion"),
    app_commands.Choice(name="Moderate Healing Potion", value="<:wizard_potion2:1372986129250255048> Moderate Healing Potion"),
    app_commands.Choice(name="Big Healing Potion", value="<:wizard_potion3:1372986138465407046> Big Healing Potion")
])
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
        conn.close()
        return

    if item not in client.shop_items:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Item not available!")
        conn.close()
        return

    item_details = client.shop_items[item]

    # Check if player has enough GP
    cursor.execute("SELECT gp FROM profiles WHERE character_id = ?", (character[0],))
    current_gp = cursor.fetchone()[0]

    if current_gp < item_details['price']:
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ Not enough GP! You need {item_details['price']} GP, but you only have {current_gp} GP.")
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
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ {character_name} is not in any location!")
        conn.close()
        return

    current_location = character[0]

    # 70% chance to find loot when no enemy
    if random.random() >= 0.2:  # No enemy encounter
        cursor.execute("""
        SELECT name, description, value, hp_effect FROM loot_items
        WHERE location = ?
        ORDER BY RANDOM() LIMIT 1
        """, (current_location,))
        loot = cursor.fetchone()

        if loot and random.random() < 0.8:  # 70% chance to get the loot
            # Add item to inventory
            cursor.execute("""
            INSERT INTO inventory (character_id, item_name, description, value, hp_effect)
            SELECT character_id, ?, ?, ?, ?
            FROM profiles
            WHERE character_name = ?
            """, (loot[0], loot[1], loot[2], loot[3], character_name))
            conn.commit()

            # Give XP based on location
            location_xp = {
                "High School": 10,
                "Park": 10,
                "Beach": 15,
                "City": 15,
                "Sewers": 20,
                "Forest": 20,
                "Destroyed Research Site": 30,
                "Abandoned Facility": 25,
                "Ash Lake": 40
            }
            xp_gain = location_xp.get(current_location, 10)
            leveled_up = update_character_xp(character_name, xp_gain)

            embed = discord.Embed(title="<a:Purplestar:1373007899240173710> ┃ Loot Found!", color=0x8c52ff)
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="✦ Item Found", value=loot[0], inline=True)
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="✦ Value", value=f"{loot[2]} GP", inline=True)
            if loot[3] != 0:
                embed.add_field(name="‎", value="", inline=False)
                embed.add_field(name="✦ HP Effect", value=str(loot[3]), inline=True)
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="✦ Experience Gained", value=f"+{xp_gain} XP", inline=False)
            if leveled_up:
                embed.add_field(name="‎", value="", inline=False)
                embed.add_field(name="<:levelup:1372873464406347846> ┃ LEVEL UP!", value="-# You've grown stronger!", inline=False)
            await interaction.response.send_message(embed=embed)
            conn.close()
            return

        await interaction.response.send_message(f"<a:purple:1373242196592951406> . . . {character_name} found nothing of value . . .")
        conn.close()
        return

    # Enemy encounter (20% chance)
    cursor.execute("""
    SELECT name, description FROM enemies
    WHERE location = ?
    ORDER BY RANDOM() LIMIT 1
    """, (current_location,))
    enemy = cursor.fetchone()

    if enemy:
        embed = discord.Embed(
            title="<a:warning:1372876834135609404> ┃ Enemy Encounter", 
            description=f"While searching for loot, {character_name} encountered a {enemy[0]}!\n-# {enemy[1]}", 
            color=0xa60306
        )
        view = EncounterView(character_name, enemy[0], enemy[1], current_location)
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(f"{character_name} found nothing of value...")

    conn.close()

# Encounter system```python
# Adding commands for changing character names and nicknames, updating database schema, and modifying profile/list_characters displays.
# GLobal variables
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

        embed = discord.Embed(title="<a:DiceRoll:1372965997841223700> ┃ Combat Roll", color=0x8c52ff)
        embed.add_field(name="‎", value="", inline=False)
        embed.add_field(name=f"✦ {self.character_name}'s Roll", value=str(player_roll), inline=True)
        embed.add_field(name="‎", value="", inline=False)
        embed.add_field(name=f"✦ {self.enemy_name}'s Roll", value=str(enemy_roll), inline=True)
        embed.add_field(name="‎", value="", inline=False)

        if player_roll == enemy_roll:
            embed.description = f"Both {self.character_name} and {self.enemy_name} matched each other's moves!"
            max_hp = 100 + (self.char_level * 10)  # Base HP + (level * 10)
            embed.add_field(name=f"{self.character_name}'s HP", value=f"{self.char_hp}/{max_hp}", inline=True)
            embed.add_field(name=f"{self.enemy_name}'s HP", value=f"{self.enemy_hp}/{self.max_enemy_hp}", inline=True)
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="Combat Continues!", value="-# Choose your next action!", inline=False)
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
            embed.description = f"You **won** the roll and dealt {damage_to_enemy} damage to the {self.enemy_name}!"
            embed.add_field(name="Damage Dealt", value=f"You dealt {damage_to_enemy} damage *(Level bonus: {int((level_multiplier-1)*100)}%)*")
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
                    title="<a:PurpleCrown:1373243160855052449> ┃ Combat Victory!",
                    description=f"{self.character_name} defeated the {self.enemy_name}!",
                    color=0x8c52ff
                )

                embed.add_field(name="‎", value="", inline=False)
                victory_embed.add_field(name="‎", value="", inline=False)
                victory_embed.add_field(name="<:xp:1372873431040659546> Experience Gained", value=f"+{xp_gain} XP", inline=False)
                victory_embed.add_field(name="‎", value="", inline=False)

                if leveled_up:
                    embed.add_field(name="‎", value="", inline=False)
                    victory_embed.add_field(name="‎", value="", inline=False)
                    victory_embed.add_field(
                        name="<:levelup:1372873464406347846> ┃ LEVEL UP!",
                        value="-# You've grown stronger!",
                        inline=False
                    )
                    victory_embed.add_field(name="‎", value="", inline=False)

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
                    embed.add_field(name="‎", value="", inline=False)
                    victory_embed.add_field(
                        name="<a:Purplestar:1373007899240173710> Loot Acquired!",
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

            embed.description = f"You **lost** the roll and took {damage} damage!"
            max_hp = 100 + (self.char_level * 10)  # Base HP + (level * 10)
            embed.add_field(name=f"{self.character_name}'s HP", value=f"{new_hp}/{max_hp}", inline=True)
            embed.add_field(name=f"{self.enemy_name}'s HP", value=f"{self.enemy_hp}/{self.max_enemy_hp}", inline=True)

            if new_hp <= 0:
                embed.add_field(name="‎", value="", inline=False)
                embed.description = f"<a:skull_animated:1373222285422493798> {self.character_name} was killed by the {self.enemy_name}!"
                await interaction.response.send_message(embed=embed)
                return self.stop()
            else:
                embed.add_field(name="‎", value="", inline=False)
                embed.add_field(name="Combat Continues!", value="-# Choose your next action!", inline=False)
                if new_hp <= 10:
                    embed.add_field(name="‎", value="", inline=False)
                    embed.add_field(name="<a:warning:1372876834135609404> WARNING!", value=f"{self.character_name} is **critically wounded**!", inline=False)
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
            embed.add_field(name="‎", value="", inline=False)
            embed.description = f"<a:shooting_stars:1373223111758971142> After a tough battle, {self.character_name} managed to defeat the {self.enemy_name}!"
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

            embed.add_field(name="‎", value="", inline=False)
            embed.description = f"{self.character_name} was defeated by the {self.enemy_name} after taking {damage} damage!"
            embed.add_field(name="HP Remaining", value=f"{new_hp}/100", inline=False)

            if new_hp == 0:
                embed.add_field(name="<a:skull_animated:1373222285422493798> DEATH", value=f"{self.character_name} has fallen in battle!", inline=False)
            elif new_hp <= 10:
                embed.add_field(name="<a:warning:1372876834135609404> WARNING", value=f"{self.character_name} is **critically wounded**!", inline=False)

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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
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
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ {character_name} doesn't have a {item_name}!")
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

    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ Sold {item_name} for {sell_value} GP!")



@client.tree.command(name="weather", description="Check the current weather")
async def weather(interaction: discord.Interaction):
    # Always pick a random weather if not set
    if not hasattr(client, 'current_weather'):
        client.current_weather = random.choice(client.weather)
    elif random.random() < 0.3:  # 30% chance to change weather
        client.current_weather = random.choice(client.weather)
    await interaction.response.send_message(f"<a:Purplestar:1373007899240173710> ┃ Current weather: **{client.current_weather}**")

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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
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
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ {character_name} doesn't have a {item_name}!")
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
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
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ No healing item named '{item_name}' found in inventory!")
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
        conn.close()
        return

    if not character[0]:
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ {character_name} is not in any location!")
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
        await interaction.response.send_message(f"<a:tickred:1373240267880267836> ┃ No enemy named '{enemy_name}' found in {character[0]}!")
        return

    embed = discord.Embed(
        title="<a:Purplestar:1373007899240173710> ┃ Enemy Encounter", 
        description=f"{character_name} challenged {enemy[0]}!\n-# {enemy[1]}", 
        color=0x8c52ff
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
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

    embed = discord.Embed(title="<a:Purplestar:1373007899240173710> ┃ HP Added", color=0x8c52ff)
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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Invalid format! Use NdX (e.g., 1d20, 2d6).")


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
`/rename_character` - Rename your character
`/set_nickname` - Set a nickname for your character
`/choose` - Randomly choose between multiple options

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
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
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

    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ {character_name}'s level has been set to {level}.")

@client.tree.command(name="rename_character", description="Rename your character")
async def rename_character(interaction: discord.Interaction, old_name: str, new_name: str):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, old_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
        conn.close()
        return

     # Check if the new name is already taken
    cursor.execute("SELECT character_name FROM profiles WHERE character_name = ?", (new_name,))
    if cursor.fetchone():
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ A character with this name already exists!")
        conn.close()
        return

    # Update character's name
    cursor.execute("""
    UPDATE profiles
    SET character_name = ?
    WHERE character_id = ?
    """, (new_name, character[0]))

    # Update inventory items to the new character name
    cursor.execute("""
    UPDATE inventory
    SET character_id = (SELECT character_id FROM profiles WHERE character_name = ?)
    WHERE character_id = ?
    """, (new_name, character[0]))

    conn.commit()
    conn.close()



@client.tree.command(name="choose", description="Randomly choose between multiple options")
async def choose(interaction: discord.Interaction, options: str):
    # Split options by commas and clean up whitespace
    choices = [opt.strip() for opt in options.split(',') if opt.strip()]
    
    if len(choices) < 2:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Please provide at least 2 options, separated by commas!")
        return
        
    chosen = random.choice(choices)
    await interaction.response.send_message(f"<a:DiceRoll:1372965997841223700> ┃ I choose: **{chosen}**!")


    await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ {old_name}'s name has been changed to {new_name}.")

@client.tree.command(name="set_nickname", description="Set a nickname for your character")
async def set_nickname(interaction: discord.Interaction, character_name: str, nickname: str = None):
    conn = connect()
    cursor = conn.cursor()

    # Check if character exists and belongs to user
    cursor.execute("""
    SELECT character_id FROM profiles
    WHERE user_id = ? AND character_name = ?
    """, (interaction.user.id, character_name))
    character = cursor.fetchone()

    if not character:
        await interaction.response.send_message("<a:tickred:1373240267880267836> ┃ Character not found!")
        conn.close()
        return

    # Update character's nickname
    cursor.execute("""
    UPDATE profiles
    SET nickname = ?
    WHERE character_id = ?
    """, (nickname, character[0]))

    conn.commit()
    conn.close()

    if nickname:
        await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ {character_name}'s nickname has been set to {nickname}.")
    else:
        await interaction.response.send_message(f"<a:verified:1372873503384010826> ┃ {character_name}'s nickname has been removed.")

# Adding database schema changes and commands for renaming characters and setting nicknames.
try:
    client.run(os.getenv('DISCORD_TOKEN'))
except KeyboardInterrupt:
    # Graceful shutdown
    logger.info("Bot is shutting down...")
finally:
    # Cleanup
    if not client.is_closed():
        client.close()