
import discord
from discord import app_commands
import random
import json
from dataclasses import dataclass
from typing import List, Dict
import os
from datetime import datetime

# Data structures
@dataclass
class Character:
    name: str
    nen_type: str
    hp: int
    max_hp: int
    inventory: Dict[str, List[str]]
    coins: int

@dataclass
class Area:
    name: str
    enemies: List[str]
    items: List[str]
    difficulty: int

# Initialize bot
class RPGBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.characters = {}
        self.weather = ["Sunny", "Rainy", "Stormy", "Foggy", "Clear"]
        self.current_weather = "Sunny"
        
        # Load game data
        self.areas = {
            "Forest": Area("Forest", ["Wolf", "Bandit", "Dark Spirit"], ["Health Potion", "Wood Sword", "Leather Armor"], 1),
            "Cave": Area("Cave", ["Goblin", "Troll", "Dragon"], ["Magic Stone", "Steel Sword", "Iron Shield"], 2),
            "Castle": Area("Castle", ["Knight", "Wizard", "Dark Lord"], ["Royal Sword", "Magic Staff", "Golden Armor"], 3)
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
    user_id = str(interaction.user.id)
    client.characters[user_id] = Character(
        name=name,
        nen_type=nen_type,
        hp=100,
        max_hp=100,
        inventory={"items": [], "consumables": []},
        coins=100
    )
    await interaction.response.send_message(f"Character created: {name} ({nen_type})")

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

@client.tree.command(name="explore", description="Explore an area")
async def explore(interaction: discord.Interaction, area: str):
    user_id = str(interaction.user.id)
    if user_id not in client.characters:
        await interaction.response.send_message("Create a character first!")
        return
    
    if area not in client.areas:
        await interaction.response.send_message("Invalid area!")
        return
    
    selected_area = client.areas[area]
    # Random encounter
    if random.random() < 0.7:  # 70% chance of encounter
        enemy = random.choice(selected_area.enemies)
        item = random.choice(selected_area.items) if random.random() < 0.5 else None
        coins = random.randint(10, 50) * selected_area.difficulty
        
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

client.run('YOUR_BOT_TOKEN')
