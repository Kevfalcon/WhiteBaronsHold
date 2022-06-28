import random
import csv
import copy
import time

def importlist(list):
    # Import from raw data for usage in the game
    # First convert CSV to usable data
    with open(f'lists/{list}.csv', newline='') as file:
        readin = csv.reader(file, quotechar='|')
        read = []
        for row in readin:
            read.append(row)
        list = {}
        # Cycle through actual data items, creating a dictionary for each. Row 1 is headings and Row 2 is datatype
        for i in range(2, len(read)):
            list[read[i][0]] = {}
            for j in range(0, len(read[i])):
                if read[1][j] == "int":
                    list[read[i][0]][read[0][j]] = int(read[i][j])
                elif read[1][j] == "list":
                    list[read[i][0]][read[0][j]] = read[i][j].split("|")
                else:
                    list[read[i][0]][read[0][j]] = read[i][j]

    return list


monsters = importlist("monsters")
items = importlist("items")
spells = importlist("spells")
classes = importlist("classes")

allies = {}
enemies = {}


def CharacterCreation():
    while True:
        character = {}
        # Name the character
        print("\nFirst, what is your characters name?")
        character["name"] = input()

        # Choose from a class for your character
        print(f"\nWhat sort of adventurer is {character['name']}?")
        for i in classes:
            print(i.title(), ":", classes[i]["description"])
        while True:
            classselection = input()
            if classselection.lower() in classes.keys():
                character["class"] = classselection.lower()
                break

        # Set base stat values, equipment, and spellbook based on class selection
        character["maxhp"] = classes[character["class"]]["basehp"]
        character["currenthp"] = classes[character["class"]]["basehp"]
        character["armourvalue"] = classes[character["class"]]["basearmour"]
        character["strength"] = classes[character["class"]]["basestrength"]
        character["wits"] = classes[character["class"]]["basewits"]
        character["intelligence"] = classes[character["class"]]["baseintelligence"]
        character["righthand"] = classes[character["class"]]["righthand"]
        character["lefthand"] = classes[character["class"]]["lefthand"]
        character["armour"] = classes[character["class"]]["armour"]
        character["backpack"] = classes[character["class"]]["startingitems"]
        character["spellbook"] = classes[character["class"]]["startingspells"]
        character["enemy"] = classes[character["class"]]["enemy"]

        # Confirm character
        print(f"\nSo you want to play {character['name']} the {character['class'].title()}?")
        confirm = input()
        if confirm[0].upper() == "Y":
            break
    # Add character to the allies dictionary
    allies["player"] = character


def skillcheck(bonus):
    # A skill check takes the relevant skill (or a flat number bonus) to test, plus any modifiers
    roll = random.randint(1, 6)
    # A check passes if a d6 roll is less than or equal to the relevant skill plus any bonuses
    if roll <= bonus:
        return 1
    else:
        return 0


def heal(creature, healamount):
    # Healing increases a creature's current HP by a set amount but not in excess of their max HP
    if creature["currenthp"] + healamount > creature["maxhp"]:
        creature["currenthp"] = creature["maxhp"]
    else:
        creature["currenthp"] += healamount


def damage(creature, damage):
    # Use total damage to track the sum of inputs
    totaldamage = 0
    # If the input is a number simply add it to the total damage
    if type(damage) == int:
        totaldamage += damage
    # Else the damage roll should be a series of numbers and XdY rolls split by + or -
    else:
        # Replace - with +- for processing
        # Then split the damage roll into sections
        roll = damage.replace("-", "+-").split("+")
        for i in range(len(roll)):
            # If the section is negative
            if roll[i][0] == "-":
                if roll[i][1:].isdigit():
                    # Subtract flat modifiers to the total damage
                    totaldamage -= int(roll[i][1:])
                elif roll[i][1:].replace("d", "").isdigit() or roll[i][1:].replace("D", "").isdigit():
                    # Roll dice and subtract the results to the total damage
                    rollcalc = roll[i][1:].replace("D", "d").split("d")
                    for j in range(int(rollcalc[0])):
                        totaldamage -= random.randint(1, int(rollcalc[1]))
            # Else if the section is positive
            else:
                if roll[i].isdigit():
                    # Add flat modifiers to the total damage
                    totaldamage += int(roll[i])
                elif roll[i].replace("d", "").isdigit() or roll[i].replace("D", "").isdigit():
                    # Roll dice and add the results to the total damage
                    rollcalc = roll[i].replace("D", "d").split("d")
                    for j in range(int(rollcalc[0])):
                        totaldamage += random.randint(1, int(rollcalc[1]))
    # Subtract the creature's armour value from the total damage
    totaldamage -= creature["armourvalue"]
    # Damage cannot be negative, so set negative total damage to 0
    if totaldamage < 0:
        totaldamage = 0
    # Print message to inform player of the output of the attack
    if totaldamage == 0:
        print("But the damage is absorbed by armour")
    else:
        print(f"Dealing {totaldamage} damage")
    # Remove the damage from the target's current hit points
    creature["currenthp"] -= totaldamage


def monsterattack(monster, target):
    # Check to see if the monster hits with their weapon
    hit = skillcheck(monster[items[monster["weapon"]]["stat"]] + items[monster["weapon"]]["bonus"])
    # If the attack hits calculate and apply damage
    if hit == 1:
        print("It hits")
        damage(target, items[monster["weapon"]]["damage"])
    else:
        print("It misses")


def playerattack():
    # The player can choose to attack with a weapon or shield in one of their hands or make an unarmed strike
    print("Attack with what?")
    weaponoptions = []
    # Checks to see if the player has a valid weapon or shield in their right hand
    if items[allies["player"]["righthand"]]["type"] in ["weapon", "shield"]:
        weaponoptions.append(allies["player"]["righthand"])
    # Checks to see if the player has a valid weapon or shield in their left hand
    if items[allies["player"]["lefthand"]]["type"] in ["weapon", "shield"]:
        weaponoptions.append(allies["player"]["lefthand"])
    weaponoptions.append("unarmed strike")
    # Player is displayed their weapon options to choose from
    print(", ".join(weaponoptions).title())
    while True:
        weaponchoice = input().lower()
        if weaponchoice in weaponoptions:
            # If there is more than one enemy in the battle the player chooses who to attack
            if len(enemies) > 1:
                print("Choose a target")
                print(", ".join(enemies).title())
                while True:
                    targetchoice = input().lower()
                    if targetchoice in enemies:
                        break
            # If there is only one enemy their target is choosen for them
            else:
                targetchoice = list(enemies.keys())[0]
            # Player tests to see if they hit using the relevant stat for the weapon
            hit = skillcheck(allies["player"][items[weaponchoice]["stat"]] + items[weaponchoice]["bonus"])
            # If the attack hits calculate and apply damage
            if hit == 1:
                print("It hits")
                damage(enemies[targetchoice], items[weaponchoice]["damage"])
            else:
                print("It misses")
            break


def examineitem():
    # TBD
    pass


def combatexamine():
    # In combat the examine action is limited to relevant targets
    print("Examine what?")
    # Player selects what they wish to examine
    print("Enemies, Self, Allies, Inventory")
    while True:
        examinetarget = input()
        if examinetarget.upper()[0:3] == "ENE":
            # Examining enemies shows a little about the type of creature plus a rough estimate of how damaged they are
            print("Examine who?")
            print(", ".join(enemies).title())
            while True:
                examinetarget = input().lower()
                if examinetarget in enemies:
                    print(f"A {enemies[examinetarget]['creature']}")
                    print(enemies[examinetarget]["description"])
                    if enemies[examinetarget]["currenthp"] / enemies[examinetarget]["maxhp"] > 0.66:
                        print("They are looking pretty healthy")
                    elif enemies[examinetarget]["currenthp"] / enemies[examinetarget]["maxhp"] > 0.33:
                        print("They have take a bit of a beating")
                    else:
                        print("They are on death's door")
                    break
            break
        elif examinetarget.upper()[0:3] == "SELF":
            # Examining themselves gives the player a rough estimate of how damaged they are
            print(f"You! A heroic {allies[examinetarget]['class']}")
            if allies["player"]["currenthp"] / allies["player"]["maxhp"] > 0.66:
                print("You are feeling healthy")
            elif allies["player"]["currenthp"] / allies["player"]["maxhp"] > 0.33:
                print("You could do with a sit down")
            else:
                print("You feel the shadow of death approaching")
        elif examinetarget.upper()[0:3] == "ALL":
            if len(allies) - 1 == 0:
                print("You have no allies, you are alone in this battle")
            else:
                # Examining allies shows a little about the type of creature plus a rough estimate of how damaged they are
                print("Examine who?")
                print(", ".join(list(allies.keys())[1:]).title())
                while True:
                    examinetarget = input().lower()
                    if examinetarget in allies:
                        print(f"A {allies[examinetarget]['creature']}")
                        print(allies[examinetarget]["description"])
                        if allies[examinetarget]["currenthp"] / allies[examinetarget]["maxhp"] > 0.66:
                            print("They are looking pretty healthy")
                        elif allies[examinetarget]["currenthp"] / allies[examinetarget]["maxhp"] > 0.33:
                            print("They have take a bit of a beating")
                        else:
                            print("They are on death's door")
                        break
            break
        elif examinetarget.upper()[0:3] == "INV":
            # Once implemented the player will be able to see information about your equipment and other items
            print("No time to be looking in your backpack! (Feature to come)")
            break


def combatflee():
    # Attempting to flee requires a wits check
    flee = skillcheck(skillcheck(allies["player"]["wits"]))
    print("You attempt to escape from battle")
    time.sleep(1)
    # Whenever the player attempts to flee a random enemy gets to make an attack for free
    randenemy = random.choice(list(enemies.keys()))
    print(f"{randenemy.title()} takes advantage")
    time.sleep(1)
    monsterattack(enemies[randenemy], allies["player"])
    if flee == 1:
        # If the fleeing check is successful the player escapes the battle
        print("\nYou escape to fight another day!")
        enemies.clear()
        return 3
    else:
        # If the fleeing check fails the player wastes their turn
        print("\nYour enemies cut off your escape, the battle continues!")
        return 0


def combatadmin(combatend=0):
    # Runs after each turn to clean up dead things and check for combat end scenarios

    # If the player has successful fled combat will end
    if combatend == 3:
        return 3

    # If the player is dead combat will end
    if allies["player"]["currenthp"] <= 0:
        print("\nYou have died!")
        return 1

    # Remove dead allies
    for ally in allies:
        if allies[ally]["currenthp"] <= 0:
            print(f"\n{ally.title()} has been tragically slain")
            del allies[ally]

    # Remove dead enemies
    for enemy in list(enemies.keys()):
        if enemies[enemy]["currenthp"] <= 0:
            print(f"\n{enemy.title()} has been defeated")
            del enemies[enemy]

    # If all enemies are dead combat will end
    if len(enemies) == 0:
        print("\nAll enemies are defeated. You are triumphant!")
        return 2

    # Otherwise combat will continue
    else:
        return 0


def battle():
    # Decide who goes first, the player or the enemies, by testing the players Wits
    turnmarker = skillcheck(allies["player"]["wits"])
    combatend = 0
    while combatend == 0:
        if turnmarker == 0:
            # Cycle through the enemies in combat
            for enemy in enemies:
                time.sleep(2)
                print(f"\n{enemy.title()}'s turn")
                if len(allies) > 1:
                    # If the player has any allies the enemy will target at random, but heavily favour attacking the player
                    if random.randint(1, 2) == 1:
                        print(f"{enemy.title()} attacks You")
                        time.sleep(1)
                        monsterattack(enemies[enemy], allies["player"])
                    else:
                        target = random.choice(list(allies.keys()))
                        if target == "player":
                            print(f"{enemy.title()} attacks You")
                        else:
                            print(f"{enemy.title()} attacks {target.title()}")
                        time.sleep(1)
                        monsterattack(enemies[enemy], allies[target])
                else:
                    # Else the player is attacked
                    print(f"{enemy.title()} attacks You")
                    monsterattack(enemies[enemy], allies["player"])
                # After each turn check for combat end
                combatend = combatadmin(combatend)
                # If a combat end condition has been reached then no more turns are taken
                if combatend > 0:
                    break
        else:
            for ally in allies:
                time.sleep(1)
                if ally == "player":
                    # On the players turn let them select which action to take
                    print("\nYour turn")
                    while True:
                        print("Attack, Flee, Examine")
                        action = input().upper()
                        # Examine action does not end the turn, player can examine as much as they wish
                        if action[0:3] == "EXA":
                            combatexamine()
                        elif action[0:3] == "FLE":
                            combatend = combatflee()
                            break
                        elif action[0:3] == "ATT":
                            playerattack()
                            break
                    # After each turn check for combat end
                    combatend = combatadmin(combatend)
                else:
                    print(f"\n{ally.title()}'s turn")
                    target = random.choice(list(enemies.keys()))
                    print(f"{ally.title()} attacks {target.title()}")
                    monsterattack(allies[ally], enemies[target])
                    # After each turn check for combat end
                    combatend = combatadmin(combatend)
                # If a combat end condition has been reached then no more turns are taken
                if combatend > 0:
                    break
        # If combat has not ended, switch from player turn to enemies turn or vice-versa
        turnmarker = (turnmarker + 1) % 2

    # Combat End 1: Player Death. Results in game over
    if combatend == 1:
        pass
    # Combat End 2: All enemies removed from the battle. Victory!
    elif combatend == 2:
        pass
    # Combat End 3: Player successfully fled from battle.
    #       They will move to previous room and the current room state will not change
    elif combatend == 3:
        pass

CharacterCreation()

print("\nYou are about to embark on an epic quest into the Mountain Manor.")
print("The monstrous half-dragon knight known as the White Baron has come to the remote lands of eastern Temeria.")
print("He has claimed an ancient elven ruin, rebuilding it as a fortress from which to rule.")
print(
    "The Baron's kobold minions have raided and ravaged the country for miles around, taking all that stolen wealth "
    "back to their tyrannical master.")
print("Hearing of the people's plight (and also the potential for vast treasures) you have come to challenge the "
      "White Baron in the name of honour, glory, and gold!")
print("Are you ready?")
start = input().upper()
if start[0] == "N":
    print("You realise adventuring is stupidly dangerous and decide to go home")
    exit()


print("\nAs you approach the Mountain Manor you are ambushed by a trio of kobolds!")
time.sleep(2)



enemies["dragonheart"] = copy.deepcopy(monsters["kobold dragonheart"])
enemies["kobold 1"] = copy.deepcopy(monsters["kobold"])
enemies["kobold 2"] = copy.deepcopy(monsters["kobold"])

battle()
