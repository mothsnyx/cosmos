from database import add_enemy, add_loot_item

# Preload enemies
def preload_enemies():
    
    # High School Enemies
    add_enemy("Possessed Locker", "Animated by a mischievous spirit; they trap students inside.", 0, 5, "High School")
    add_enemy("Drama Club Phantom", "Former students who haunt the auditorium with psychic screeches.", 0, 5, "High School")
    add_enemy("Library Ghoul", "A hunched figure that smells like old paper.", 0, 5, "High School")
    add_enemy("Social Feeder", "Teens who need attention literally to survive; violent when ignored.", 0, 5, "High School")
    add_enemy("Janitor", "Looks like the janitor, but the closer you get, the more distorted he becomes.", 0, 5, "High School")
    add_enemy("Mimic", "A creature that mimics the appearance and abilities of other humans.", 0, 5, "High School")
    add_enemy("Loser", "A pathetic human, who couldn't make his own memories.", 0, 5, "High School")

    # Beach Enemies
    add_enemy("Drifter", "A human who’s been stranded on the beach for so long they've lost their mind.", 5, 10, "Beach")
    add_enemy("Crabswarm", "A swarm of small crabs acting as one.", 5, 10, "Beach")
    add_enemy("Broken Ray", "It limps through shallow water, its skin peeled back.", 5, 10, "Beach")
    add_enemy("Tidewolf", "A hairless dog-like thing that drips saltwater constantly.", 5, 10, "Beach")
    add_enemy("Gullmock", "Mimics human voices in distress to lure prey.", 5, 10, "Beach")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 5, 10, "Beach")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 5, 10, "Beach")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 5, 10, "Beach")

    # Park Enemies
    add_enemy("Vineleech", "A plant-like serpent that drops from trees.", 5, 10, "Park")
    add_enemy("Hollow Deer", "Its body is intact but hollow inside, no organs, no eyes.", 5, 10, "Park")
    add_enemy("Soot Crow", "A large crow that trails smoke and stares too long.", 5, 10, "Park")
    add_enemy("Smiling Bench Guy", "He always sits in the same spot, too friendly.", 5, 10, "Park")
    add_enemy("Playground Ghost", "Swings alone, vanishes when approached.", 5, 10, "Park")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 5, 10, "Park")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 5, 10, "Park")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 5, 10, "Park")
    add_enemy("Undead Dog", "Prowls the streets in packs of two or more.", 5, 10, "Park")

    # City Enemies
    add_enemy("Street Delinquent", "Gangs of troublemakers prowling the streets.", 5, 10, "City")
    add_enemy("Blackmarket Enforcer", "Shady underworld figures; ex-adventurers turned mercenaries.", 5, 10, "City")
    add_enemy("Lawmen (Corrupt)", "City guards abusing their powers to control areas.", 5, 10, "City")
    add_enemy("Eyeless", "Urban homeless who’ve had their eyes removed and still ‘see.’", 5, 10, "City")
    add_enemy("Weeper", "A crying figure in alleys, screams when approached.", 5, 10, "City")
    add_enemy("Hunter", "A hooded man who lurks around the corner and pounces on unsuspecting victims.", 5, 10, "City")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 5, 10, "City")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 5, 10, "City")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 5, 10, "City")
    add_enemy("Undead Dog", "Prowls the streets in packs of two or more.", 5, 10, "City")
    

    # Sewers Enemies
    add_enemy("Drowned", "Bloated bodies that rise from the water, still twitching and gurgling.", 10, 15, "Sewers")
    add_enemy("Molemen", "People who’ve lived underground so long their skin is pale, their eyes gone.", 10, 15, "Sewers")
    add_enemy("Sewer Rat", "Giant rats that have adapted to the dark, filthy environment.", 10, 15, "Sewers")
    add_enemy("Sludge Beast", "A monstrous creature made of toxic waste.", 10, 15, "Sewers")
    add_enemy("Pipeborn", "Crawling humanoid creatures that emerge from boken pipes, made of limbs and wires.", 10, 15, "Sewers")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 10, 15, "Sewers")
    add_enemy("Giant Mosquito", "A giant mosquito that feeds on blood and flesh.", 10, 15, "Sewers")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 10, 15, "Sewers")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 10, 15, "Sewers")
    add_enemy("Egg Carrier", "It crawls on all-fours and is infected with a parasite that's causing large eggs to grow on its back.", 10, 15, "Sewers")

    # Forest Enemies
    add_enemy("Rootbound", "Humans slowly turning into trees; can’t speak, just creak and groan", 10, 15, "Forest")
    add_enemy("Hollow Man", "A man with a gaping hole where his head should be.", 10, 15, "Forest")
    add_enemy("Stray Campers", "Once normal people now feral, wearing tree branches and moss.", 10, 15, "Forest")
    add_enemy("Skin-Crows", "Flocks of crows with torn, human-like faces.", 10, 15, "Forest")
    add_enemy("Fingers", "Mostly humanoid, although faceless, mutants who possess a massive maw extending up their torso, neck and head." , 10, 15, "Forest")
    add_enemy("Laughing Girl", "Always just out of sight. Never stops laughing. If you laugh too, she’ll come closer.", 10, 15, "Forest")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 10, 15, "Forest")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 10, 15, "Forest")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 10, 15, "Forest")

    # Destroyed Research Site Enemies
    add_enemy("Murmur", "A shadow beast that speaks in cursed tongues, its words twisting into physical projectiles.", 15, 20, "Destroyed Research Site")
    add_enemy("Revenant", "A frenzy demon that fuels nearby creatures with violent energy, driving them into a mindless rage.", 15, 20, "Destroyed Research Site")
    add_enemy("Giant Mosquito", "A giant mosquito that feeds on blood and flesh.", 15, 20, "Destroyed Research Site")
    add_enemy("Gnawer", "A creature that feeds on flesh and metal, its teeth sharp and jagged.", 15, 20, "Destroyed Research Site")
    add_enemy("Screamer", "A demon that feeds on fear, its screams echoing through the ruins.", 15, 20, "Destroyed Research Site")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 15, 20, "Destroyed Research Site")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 15, 20, "Destroyed Research Site")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 15, 20, "Destroyed Research Site")

    # Facility Enemies
    add_enemy("Mad Scientist", "A former scientist who lost their mind in the facility.", 15, 20, "Abandoned Facility")
    add_enemy("Dr. Latch", "Insists he’s your doctor. Keeps trying to administer “calmants.” Has a clipboard made of skin.", 15, 20, "Abandoned Facility")
    add_enemy("Experiment 001", "A failed experiment that has gained sentience.", 15, 20, "Abandoned Facility")
    add_enemy("Others", "Indistinct silhouettes that mirror your movement with a delay... then change patterns.", 15, 20, "Abandoned Facility")
    add_enemy("Static Walker", "Moves with jerky, glitchy motion like a broken video.", 15, 20, "Abandoned Facility")
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 15, 20, "Facility")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 15, 20, "Facility")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 15, 20, "Facility")

    # Ash Lake Enemies
    add_enemy("Brute", "A powerful, muscle-bound human often used as a bodyguard or frontline fighter. Hits hard, shrugs off pain, and relies on raw strength over skill.", 20, 20, "Ash Lake")
    add_enemy("Assassin Meta-Human", "Fast, agile and lethal. Strikes from the shadows with precision. Fragile if caught, but difficult to land a hit on. Equipped with specialized assassin abilities.", 20, 20, "Ash Lake")
    add_enemy("Super Soldier", "Enhanced through cybernetics or experimental drugs. Smarter, faster, and tougher than any normal human.", 20, 20, "Ash Lake")
    add_enemy("Man-Eater Shell", "Large clam shell creatures that walk about on five thin legs; their mouths are full of human skulls.", 20, 20, "Ash Lake")
    add_enemy("Basilisk", "A creature known for their ability to run upon water.", 20, 20, "Ash Lake")
    add_enemy("Hydra", "A multi-headed sea creature that can  shoot projectiles of both water and magic.", 20, 20, "Ash Lake")


# Preload loot items
def preload_loot_items():
    # High School Loot
    add_loot_item("Pencil Case", "A regular pencil case.", 2, 0, 0.25, "High School")
    add_loot_item("Minor Healing Potion", "+10 HP", 5, 10, 0.15, "High School")
    add_loot_item("Energy Drink", "+5 HP", 7, 5, 0.2, "High School")
    add_loot_item("Hall Monitor’s Whistle", "A whistle that once belonged to a hall monitor.", 7, 0, 0.1, "High School")
    add_loot_item("Lucky Eraser", "A supposedly lucky eraser.", 4, 0, 0.2, "High School")
    add_loot_item("Notebook", "A notebook with blank pages.", 5, 0, 0.2, "High School")
    add_loot_item("Old Textbook", "A dusty old textbook.", 10, 0, 0.1, "High School")
    add_loot_item("School ID", "A school ID card.", 10, 0, 0.1, "High School")
    add_loot_item("School Lunch", "A lunchbox with some food inside.", 10, 5, 0.1, "High School")
    add_loot_item("School Uniform", "A worn-out school uniform.", 15, 0, 0.1, "High School")
    add_loot_item("Training Manual", "A manual for basic combat techniques.", 20, 0, 0.1, "High School")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "High School")

    
    # Beach Loot
    add_loot_item("Sea Glass", "A piece of colored glass from the sea.", 10, 0, 0.2, "Beach")
    add_loot_item("Shell", "A small seashell.", 5, 0, 0.25, "Beach")
    add_loot_item("Driftwood", "A piece of driftwood.", 2, 0, 0.2, "Beach")
    add_loot_item("Beach Ball", "A deflated beach ball.", 3, 0, 0.2, "Beach")
    add_loot_item("Towel", "A worn-out beach towel.", 5, 0, 0.15, "Beach")
    add_loot_item("Fishing Net", "A small fishing net.", 10, 0, 0.2, "Beach")
    add_loot_item("Fishing Rod", "A broken fishing rod.", 15, 0, 0.2, "Beach")
    add_loot_item("Beach Chair", "A broken beach chair.", 10, 0, 0.2, "Beach")
    add_loot_item("Beach Umbrella", "A broken beach umbrella.", 10, 0, 0.2, "Beach")
    add_loot_item("Bucket", "A small bucket.", 10, 0, 0.2, "Beach")
    add_loot_item("Crab", "A dead crab.", 5, 0, 0.3, "Beach")
    add_loot_item("Luxury Watch", "A fancy watch.", 150, 0, 0.02, "Beach")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Beach")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Beach")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Beach")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Beach")


    # Park Loot
    add_loot_item("Bike Lock", "A rusty bike lock.", 5, 0, 0.2, "Park")
    add_loot_item("Rusted Key", "An old key.", 4, 0, 0.2, "Park")
    add_loot_item("Broken Swing", "A broken swing.", 3, 0, 0.2, "Park")
    add_loot_item("Soccer Ball", "A deflated soccer ball.", 3, 0, 0.2, "Park")
    add_loot_item("Earbud", "A singular broken earbud.", 2, 0, 0.2, "Park")
    add_loot_item("Picnic Basket", "An empty picnic basket.", 7, 0, 0.2, "Park")
    add_loot_item("Pigeon", "A dead pigeon.", 5, 0, 0.3, "Park")
    add_loot_item("Sandwich", "A surprisingly good sandwich.", 10, 15, 0.15, "Park")
    add_loot_item("Frisbee", "A broken frisbee.", 5, 0, 0.2, "Park")
    add_loot_item("Luxury Watch", "A fancy watch.", 150, 0, 0.02, "Park")
    add_loot_item("Broken Phone", "A broken phone.", 10, 0, 0.15, "Park")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Park")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Park")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Park")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Park")

    
    # City Loot
    add_loot_item("Lighter", "A small, refillable lighter.", 7, 0, 0.25, "City")
    add_loot_item("Cigarette", "A single cigarette.", 5, 0, 0.2, "City")
    add_loot_item("Phone Charger", "A basic phone charger.", 15, 0, 0.15, "City")
    add_loot_item("Wallet", "A lost wallet with some cash.", 50, 0, 0.1, "City")
    add_loot_item("First Aid Kit", "A basic medical kit.", 30, 20, 0.2, "City")
    add_loot_item("Used Condoms", "A tied, used condom.", 1, 0, 0.03, "City")
    add_loot_item("Condom", "A pack of condoms.", 5, 0, 0.05, "City")
    add_loot_item("Alcohol", "A bottle of alcohol.", 20, 0, 0.1, "City")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "City")
    add_loot_item("Drugs", "A small bag of drugs.", 50, 0, 0.08, "City")
    add_loot_item("Syringe", "A used syringe.", 2, 0, 0.2, "City")
    add_loot_item("Luxury Watch", "A fancy watch.", 150, 0, 0.02, "City")
    add_loot_item("Broken Phone", "A broken phone.", 10, 0, 0.15, "City")
    add_loot_item("Medkit", "A basic medical kit.", 20, 20, 0.2, "City")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "City")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "City")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "City")
    
    
    # Sewers Loot
    add_loot_item("Rusty Key", "An old key, might be useful.", 25, 0, 0.2, "Sewers")
    add_loot_item("Strange Crystal", "A glowing crystal formation.", 100, 0, 0.05, "Sewers")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Sewers")
    add_loot_item("Syringe", "A used syringe.", 2, 0, 0.2, "Sewers")
    add_loot_item("Alcohol", "A bottle of alcohol.", 15, 0, 0.1, "Sewers")
    add_loot_item("Statue", "A small statue of a person.", 10, 0, 0.1, "Sewers")
    add_loot_item("Paper Boat", "A small paper boat.", 1, 0, 0.2, "Sewers")
    add_loot_item("Red Balloon", "A red balloon.", 5, 0, 0.2, "Sewers")
    add_loot_item("Toolkit", "A small toolkit.", 15, 0, 0.15, "Sewers")
    add_loot_item("Luxury Watch", "A fancy watch.", 150, 0, 0.02, "Sewers")
    add_loot_item("Broken Phone", "A broken phone.", 10, 0, 0.15, "Sewers")
    add_loot_item("Medkit", "A basic medical kit.", 20, 20, 0.2, "Sewers")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Sewers")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Sewers")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Sewers")
    
    # Forest Loot
    add_loot_item("Herbs", "Medicinal herbs.", 20, 15, 0.3, "Forest")
    add_loot_item("Beast Fang", "A sharp fang from a creature.", 45, 0, 0.2, "Forest")
    add_loot_item("Spirit Essence", "Glowing ethereal substance.", 90, 0, 0.1, "Forest")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Forest")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Forest")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Forest")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Forest")

    # Destroyed Research Site Loot
    add_loot_item("Lab Coat", "A worn lab coat.", 15, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Safety Goggles", "Protective safety goggles.", 10, 0, 0.2, "Destroyed Research Site")
    add_loot_item("Safety Gloves", "Protective safety gloves.", 10, 0, 0.2, "Destroyed Research Site")
    add_loot_item("Safety Vest", "Protective safety vest.", 15, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Safety Boots", "Protective safety boots.", 15, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Safety Helmet", "Protective safety helmet.", 15, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Safety Mask", "Protective safety mask.", 15, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Blindfold", "Lets one see a realm in a twisted version of their own.", 200, 0, 0.01, "Destroyed Research Site")
    add_loot_item("Research Data", "Valuable experiment data.", 150, 0, 0.15, "Destroyed Research Site")
    add_loot_item("Prototype Device", "Strange technological device.", 200, 0, 0.05, "Destroyed Research Site")
    add_loot_item("Healing Nanites", "Advanced medical technology.", 100, 50, 0.15, "Destroyed Research Site")
    add_loot_item("Carver Knife", "Lets you revive an ally at the cost of half your HP.", 100, 0, 0.05, "Destroyed Research Site")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Destroyed Research Site")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Destroyed Research Site")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Destroyed Research Site")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Destroyed Research Site")
    
    # Abandoned Facility Loot
    add_loot_item("Lab Coat", "A worn lab coat.", 15, 0, 0.15, "Abandoned Facility")
    add_loot_item("Research Data", "Valuable experiment data.", 150, 0, 0.1, "Abandoned Facility")
    add_loot_item("Prototype Device", "Strange technological device.", 200, 0, 0.05, "Abandoned Facility")
    add_loot_item("Healing Nanites", "Advanced medical technology.", 100, 50, 0.15, "Abandoned Facility")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Abandoned Facility")
    add_loot_item("Performance-Enhancing Drug", "A drug or substance that temporarily enhances physical capabilities, similar to steroids or stimulants.", 100, 0, 0.03, "Abandoned Facility")
    add_loot_item("HP-Boosting Drug", "A performance-enhancing drug that raises your HP.", 100, 50, 0.03, "Abandoned Facility")

    # Ash Lake Loot
    add_loot_item("Lil Liz", "A little version of pookie.", 10000, 0, 0.001, "Ash Lake")
    add_loot_item("Skull", "A skull.", 40, 0, 0.3, "Ash Lake")
    add_loot_item("Solaire's Armor", "A suit of armor.", 600, 0, 0.1, "Ash Lake")
    add_loot_item("Broken Kunai", "A broken kunai.", 20, 0, 0.1, "Ash Lake")
    add_loot_item("String of Golden Threads", "A string of golden threads.", 20, 0, 0.1, "Ash Lake")
    add_loot_item("Owl Mask", "A broken owl mask.", 70, 0, 0.1, "Ash Lake")
    add_loot_item("Beast Claws", "A pair of beast claws.", 100, 0, 0.1, "Ash Lake")
    add_loot_item("Broken Glasses", "A pair of broken glasses.", 4, 0, 0.2, "Ash Lake")
    add_loot_item("Used Bandages", "A pair of used bandages.", 2, 0, 0.2, "Ash Lake")
    add_loot_item("Rusty Sword", "A rusty sword.", 10, 0, 0.3, "Ash Lake")
    add_loot_item("Broken Bow", "A broken bow.", 10, 0, 0.3, "Ash Lake")
    add_loot_item("Empty Vials", "A set of empty vials.", 5, 0, 0.3, "Ash Lake")
    add_loot_item("Rune", "Teleports from A to B", 50, 0, 0.03, "Ash Lake")
    add_loot_item("Soul Gem", "A mystical gem that binds a person’s soul to itself, allowing the soul to pass into the gem upon death.", 400, 0, 0.01, "Ash Lake")

# Run preloading
if __name__ == "__main__":
    preload_enemies()
    preload_loot_items()