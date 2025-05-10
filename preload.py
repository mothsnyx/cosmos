from database import add_enemy, add_loot_item

# Preload enemies
def preload_enemies():
    # High School Enemies
    add_enemy("Possessed Lockers", "Animated by a mischievous spirit; they trap students inside.", 0, 5, "High School")
    add_enemy("Drama Club Phantoms", "Former students who haunt the auditorium with psychic screeches.", 0, 5, "High School")
    add_enemy("Library Ghoul", "A hunched figure that smells like old paper.", 0, 5, "High School")
    add_enemy("Social Feeders", "Teens who need attention literally to survive; violent when ignored.", 0, 5, "High School")

    # City Enemies
    add_enemy("Street Delinquents", "Gangs of troublemakers prowling the streets.", 5, 10, "City")
    add_enemy("Blackmarket Enforcers", "Shady underworld figures; ex-adventurers turned mercenaries.", 5, 10, "City")
    add_enemy("Lawmen (Corrupt)", "City guards abusing their powers to control areas.", 5, 10, "City")
    add_enemy("The Eyeless", "Urban homeless who’ve had their eyes removed and still ‘see.’", 5, 10, "City")

    # More enemies for other locations...

# Preload loot items
def preload_loot_items():
    # High School Loot
    add_loot_item("Pencil Case", "A regular pencil case.", 2, 0, 0.25, "High School")
    add_loot_item("Minor Healing Potion", "+10 HP", 5, 10, 0.15, "High School")
    add_loot_item("Energy Drink", "+5 HP", 7, 5, 0.2, "High School")
    add_loot_item("Hall Monitor’s Whistle", "A whistle that once belonged to a hall monitor.", 7, 0, 0.1, "High School")
    add_loot_item("Lucky Eraser", "A supposedly lucky eraser.", 4, 0, 0.2, "High School")
    add_loot_item("Notebook", "A notebook with blank pages.", 5, 0, 0.2, "High School")

    # City Loot
    add_loot_item("Lighter", "A small, refillable lighter.", 7, 0, 0.25, "City")
    add_loot_item("Phone Charger", "A basic phone charger.", 15, 0, 0.15, "City")
    add_loot_item("Wallet", "A lost wallet with some cash.", 50, 0, 0.1, "City")
    add_loot_item("First Aid Kit", "A basic medical kit.", 30, 20, 0.2, "City")
    
    # Sewers Loot
    add_loot_item("Rusty Key", "An old key, might be useful.", 25, 0, 0.2, "Sewers")
    add_loot_item("Strange Crystal", "A glowing crystal formation.", 100, 0, 0.05, "Sewers")
    add_loot_item("Toxic Waste", "Dangerous but valuable.", 75, -10, 0.15, "Sewers")
    
    # Forest Loot
    add_loot_item("Herbs", "Medicinal herbs.", 20, 15, 0.3, "Forest")
    add_loot_item("Beast Fang", "A sharp fang from a creature.", 45, 0, 0.2, "Forest")
    add_loot_item("Spirit Essence", "Glowing ethereal substance.", 90, 0, 0.1, "Forest")
    
    # Abandoned Facility Loot
    add_loot_item("Research Data", "Valuable experiment data.", 150, 0, 0.1, "Abandoned Facility")
    add_loot_item("Prototype Device", "Strange technological device.", 200, 0, 0.05, "Abandoned Facility")
    add_loot_item("Healing Nanites", "Advanced medical technology.", 100, 50, 0.15, "Abandoned Facility")

# Run preloading
if __name__ == "__main__":
    preload_enemies()
    preload_loot_items()