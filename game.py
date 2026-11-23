# Game Name: You Got Isekai'd
# Programmer: 
# Date: 11/23/2026
# Purpose: Create a game for Introduction to programming assignment.  

#Global Vars
osType = ""

# Important libraries.  All builtins
# Has to handl differences in Windows vs Linux/Mac which uses different builtins
import os
import sys
import ctypes
import random
import time
from datetime import datetime

# win32 and Linux/MAC use different library for catching keyboard
# scancodes this loads the library based on the OS
try:
    if sys.platform == "win32":  #Windows
        import msvcrt
        osType = "windows"
        # Using the ctypes include we need to make it so ansi commands can be read by the command/powershell console
        con = ctypes.windll.kernel32   # Creates the console object
        con.SetConsoleMode(con.GetStdHandle(-11), 7) # Sets the console mode
        os.system("mode con: cols=80 lines=40") # Sets our play area and removes scroll bars
    else:                 #Mac/Linx
        import tty
        import termios
        import select
        osType = "lm"
except:
    print("There were problems")

# Gets the keyboard inputs.  Different for Windows and Linuxs systems
def getInput():
    if(osType == "windows"):       
        return msvcrt.getch().decode("utf-8", errors="ignore")
    elif(osType == "lm"):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Create a simple timer mechanism so that the monsters
# Doesnt't immediately attack the play as soon as they enter the room
def timerReady(sTime, sec = 3):
    return (time.time() - sTime) >= sec

def addHallofFame(hero):
    try: 
        file = open("halloffame.txt", "a")
        file.write(hero.name + " " + datetime.now().strftime("%m/%d/%Y") + "\n")
        file.close()        
    except Exception as e:
        print(e)
        

def readHallofFame():
    scores = ""
    try: 
        file = open("halloffame.txt", "r")
        scores = file.read()
        file.close()
        return scores
    except Exception as e:
        print(e)
    finally:
        return scores

def drawScores(x, y, scores):
    draw_at(x, y, "Hall Of Fame")
    
    # Split the single string into a list of individual lines
    lines = scores.splitlines()
    
    # Draw each line at the same x, moving down 1 row (y) each time
    for index, line in enumerate(lines):
        draw_at(x, y + 1 + index, line)

# functions
# Draw ANSI charactesrs where we need them
def draw_at(x, y, char):
    sys.stdout.write(f"\033[{y+1};{x+1}H{char}")
    sys.stdout.flush()

def cheatCode(key, history):
    code = ["w", "w", "s", "s" , "a", "d", "a", "d", " "]
    history.append(key)

    if len(history) > len(code):
        history.pop(0)

    if history == code:
        history.clear()
        return True

    return False

# Function to draw the room
def drawRoom(dungeon, rooms, x, y, size):
    wall = "\u2591"
    h = 18
    w = 29
    nDoor = False
    sDoor = False
    eDoor = False
    wDoor = False

    # Draw the outside walls of the room
    for j in range(1,h):
        draw_at(1, j, wall)
        draw_at(w, j, wall)

    for i in range(1,w):
        draw_at(i, 1, wall)
        draw_at(i, h-1, wall)
    
    # Determine what door ways are available based on adjacent rooms
    if(x - 1 >= 0):
        if (dungeon.room(x - 1,y) != 0):
            wDoor = True
    if(x + 1 < size):       
        if (dungeon.room(x + 1,y) != 0):
            eDoor = True
    if(y - 1 >= 0):
        if(dungeon.room(x, y - 1) != 0):
            nDoor = True
    if(y + 1 < size):
        if(dungeon.room(x, y + 1) != 0):
            sDoor = True

    # Adds the door way lables for available rooms
    if(nDoor == True):    
        draw_at(15,1, "N")  
    if(sDoor == True):
        draw_at(15,h-1, "S")    
    if(wDoor == True):
        draw_at(1, 9, "W")
    if(eDoor == True):
        draw_at(w, 9, "E")

    # Returns True of False for door availablility
    return nDoor, sDoor, eDoor, wDoor

# Function to Draw the map array on the screen
def drawMap(dungeon, dx = 40, dy = 20):
    for x in range(dungeon.size):
        for y in range(dungeon.size):
            if(dungeon.rooms[x][y] != 0):
                draw_at(dx + x, dy + y, "\u2261")


# Function to trade the inventory on the screen
def drawInventory(inv, dx = 60, dy = 20):
    draw_at(dx,dy, "Inventory")
    for i in inv.gear:
        dy = dy + 1
        draw_at(dx, dy, i.name)

#classes
# The Player Class.  Tracks the Players collected gear.  
class player:
    def __init__(self, name, x=0, y=0, char="\u263b"):
        self.name = name
        self.x = x
        self.y = y
        self.char = char

        # Track what gear the player has acquired
        self.gear = []

# Item class.  Create a basic item class so that the items can be created and rendered
# In there assigned Rooms. 
class item:
    def __init__(self, name, icon = "", room="", x=0, y=0, color = "\033[97m"):
        self.name = name
        self.icon = icon
        self.room = room
        self.x = x
        self.y = y
        self.color = color

    def renderItem(self):
        return f"{self.color}{self.icon}\033[0m"

# Returns True of False if the Hero has the items.
def hasItem(hero, item):
    for obj in hero.gear:
        if obj.name == item:
            return True
    return False

# The end monsters. As a Render function and a function that allows the monster
# Chase the hero. 
class monster:
    def __init__(self, name="Monster", x=15, y=9, char="M", color="\033[91m"):
        self.name = name
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.alive = True

    def render(self):
        return f"{self.color}{self.char}\033[0m"

    def chase(self, target):
        # Move 1 step toward the hero (either horizontally or vertically)
        if abs(target.x - self.x) > abs(target.y - self.y):
            if target.x > self.x:
                self.x = min(28, self.x + 1)
            elif target.x < self.x:
                self.x = max(2, self.x - 1)
        else:
            if target.y > self.y:
                self.y = min(16, self.y + 1)
            elif target.y < self.y:
                self.y = max(2, self.y - 1)

# Builds the dungeon floor plan.  Randomly designates Treasure Rooms
# For the Items.  Then it using a simple walking algorith to create
# the paths between  the treasure rooms
class dungeon:
      
    def room(self, x, y):
        return self.rooms[x][y]

    def __init__(self, size = 10):
        self.rooms = []
        self.tRooms = []
        self.size = size

        #  Builtd out the room Array.  Defaults all values to NO room
        for x in range(0, self.size):
            row = []
            for y in range(0, self.size):
                row.append(0)
            self.rooms.append(row)

        # Sets the starting room to the very top left corner and the boss room
        # sets the boss room to the bottom right corner
        self.rooms[0][0] = "S"     #Start room
        self.rooms[self.size - 1][self.size - 1] = "B"   #Boss room



        # Randomly designate the Treasure Rooms
        count = 0
        mDistance = 3
        while (count < 8):
            for x in range(1, self.size - 1):
                for y in range(1, self.size -1):
                    if(random.randint(1, 1000) > 999):
                        too_close = False
                        for tx, ty in self.tRooms:
                            distance = abs(x - tx) + abs(y - ty)
                            if distance < mDistance:
                                too_close = True

                        if too_close == False and count < 8:
                            self.rooms[x][y] = "T"
                            self.tRooms.append((x, y))
                            count = count + 1
       
        self.tRooms.append((self.size - 1, self.size -1))    

        # Create the paths between the start room to the Treasure
        # Rooms. Changes the 0s to 1 designating a room.
        # Uses a simple walking algorithm
        cx = 0
        cy = 0
        for x,y in self.tRooms:
            while((cx, cy) != (x,y)):
                if(cx != x) and (cy != y):
                    if(random.randint(1,2) == 1):
                        if(x > cx):
                            cx = cx + 1
                        else:
                            cx = cx - 1
                    else:
                        if(y > cy):
                            cy = cy + 1
                        else:
                            cy = cy - 1
                elif(cx != x):
                    if(x > cx):
                        cx = cx + 1
                    else:
                        cx = cx - 1
                elif(cy != y):
                    if(y > cy):
                        cy = cy + 1
                    else:
                        cy = cy - 1

                if (self.rooms[cx][cy] == 0):
                    self.rooms[cx][cy] = 1

# Main loop
def main():
    dungeonSize = 10
    dung = dungeon(dungeonSize)
    room = []
    kInput = ""
    rNames = ["sword", "shield", "helm", "mail", "boot", "glove", "map", "compass"]
    currentRoom = "start"
    roomx = 0
    roomy = 0
    bTimer = None
    bMove = False
    exitGame = False
    scores = readHallofFame()
    keyHistory = []


    print("\033[?25l\033[2J\033[H", end="", flush=True)
    story = "There you was minding your own business doom scrolling on your cellphone \n"
    story = story + "when you stepped off a curb right in front of a bus WHAMMO!! \n\n"
    story = story + "You woke up in a room a disembodied voice told you what happend \n"
    story = story + "and that you are now in a dungeon.  You must collect the items \n"
    story = story + "Sword, Shield, Helm, Chain Mail, Boots and Gloves.  Then slay \n"
    story = story + "the beast and collect the skeleton key to escape the dungeon. \n"
    story = story + "There are a few other items in the dungeon that may help you.\n\n"
    story = story + "YOU HAVE BEEN ISEKAI'D!! \n\n"
    
    print(story)

    

    pName = input ("What is your name hero: ")
    hero = player(pName, x=5,y=5)
    
    
    # Build out our Room DICTIONARY.  This is needed so that can lookup to see to
    # See if our Room X and Room Y coordinates match a room that should have a treasure
    # And the final Boss room
    try:
        for r in dung.tRooms:
            if(len(rNames) > 0):
                nRoom = {"xy": r, "name": rNames.pop()}
                room.append(nRoom)                
    except Exception as e:
        print(e)
  
    nRoom = {"xy": (dungeonSize - 1, dungeonSize - 1), "name": "Boss"}
    room.append(nRoom)

    # The items we need to defeat the Monster
    world_items = [
    item("Iron Sword", "\u2020", "sword", 10, 6, "\033[96m"),  
    item("Oak Shield", "\u25ca", "shield", 14, 8, "\033[94m"),  
    item("Steel Helm", "\u2229", "helm", 4, 3, "\033[93m"),  
    item("Plate Mail", "\u256c", "mail", 8, 3, "\033[97m"),  
    item("Leather Boots", "\u255d", "boot", 3, 11, "\033[33m"),  
    item("Gauntlets", "\u2663", "glove", 18, 4, "\033[32m"),  
    item("Dungeon Map", "\u25a6", "map", 12, 7, "\033[93m"),  
    item("Compass", "\u263c", "compass", 15, 6, "\033[96m"),  
    item("Skeleton Key", "\u2640", "Boss", 15, 6, "\033[96m")]

    # Clear the screen and draw the initial Room and character
    # Placement
    print("\033[?25l\033[2J\033[H", end="", flush=True)
    draw_at(hero.x, hero.y, hero.char)
    n,s,e,w = drawRoom(dung, room, roomx, roomy, dungeonSize)
    drawInventory(hero, 44, 1)
    drawScores(60, 1, scores)
    draw_at(1, 30, "Use W, A, S, D, to Move...Q to to Quit")
    boss = monster()

    # Main Loops Starts here
    while not(exitGame == True):

        # Gets our input  W, A, S D to move charater up down left and Right
        # q Quits
        kInput = getInput()
        if kInput.lower() == "w":
            if(hero.x == 15 and hero.y == 2 and n == True):
                 roomy = roomy - 1
                 hero.y = 16
            hero.y = max(2, hero.y - 1)
        elif kInput.lower() == "s":
            if(hero.x == 15 and hero.y == 16 and s == True):
                 roomy = roomy + 1
                 hero.y = 2
            hero.y = min(16, hero.y + 1)
        elif kInput.lower() == "a":
            if(hero.x == 2 and hero.y == 9 and w == True):
                 roomx = roomx - 1
                 hero.x = 28
            hero.x = max(2, hero.x - 1)
        elif kInput.lower() == "d":
            if(hero.x == 28 and hero.y == 9 and e == True):
                 roomx = roomx + 1
                 hero.x = 2
            hero.x = min(28, hero.x + 1)
        elif kInput.lower() == "q":
            exitGame = True

        # A cheat code that gives you everything but the key
        if(cheatCode(kInput, keyHistory) == True):
            for obj in world_items[:]:
                if(obj.name != "Skeleton Key"):
                    hero.gear.append(obj)
                    
        # Identifies the room we are currently in.  
        currentRoom = ""
        for r in room:
            if r["xy"] == (roomx,roomy):
                currentRoom = r["name"]
        
        # Draws the HUD   
        print("\033[2J\033[H", end="", flush=True)
        draw_at(hero.x,hero.y, hero.char)
        #draw_at(40,40, str(hero.x) + " " + str(hero.y))
        n,s,e,w = drawRoom(dung, room, roomx, roomy, dungeonSize)
        drawInventory(hero, 44, 1)
        drawScores(60, 1, scores)
        draw_at(1, 30, "Use W, A, S, D, to Move...Q to to Quit")
        # If the player picks up the map draw it on the screen        
        for obj in hero.gear:
            if obj.name == "Dungeon Map":
                drawMap(dung, 31, 1)             

        # If its a treasure room displays the treasure inside.
        for obj in world_items[:]:  # [:] lets us safely remove items while looping

            #Draw the treasures on the screen when they are available. 
            if(currentRoom != "Boss"): 
                if(currentRoom == obj.room):
                    draw_at(obj.x, obj.y, obj.renderItem())

                if(obj.room == currentRoom and obj.x == hero.x and obj.y == hero.y):
                    hero.gear.append(obj)
                    world_items.remove(obj)  # Removes item from the floor

            # Waits until you slay the boss before making the key available
            if(currentRoom == "Boss" and boss.alive == False): 
                if(currentRoom == obj.room):
                    draw_at(obj.x, obj.y, obj.renderItem())

                if(obj.room == currentRoom and obj.x == hero.x and obj.y == hero.y):
                    hero.gear.append(obj)
                    world_items.remove(obj)  # Removes item from the floor


        # Win Condition has been met.  You've collected the key.  Records the completion date in the hall of fame
        if(hasItem(hero, "Skeleton Key") == True):
                print("\033[?25l\033[2J\033[H", end="", flush=True)
                draw_at(1,10, "You have successfully slain the the beast and collected the Skeleton Key.")
                draw_at(1,11, "You escaped the dungeon...but your isekai advantures are just beginning")
                draw_at(1,15, "Press any key to end the game")
                addHallofFame(hero)
                scores = readHallofFame()
                drawScores(1,18, scores)
                kInput = getInput()
                exitGame = True
            
        # The boss fight
        if(currentRoom == "Boss" and boss.alive):

            #Uses a wake up time for the boss that starts as soon as you enter the boss room
            if bTimer is None:                
                bTimer = time.time()

            if timerReady(bTimer, 3):
                if(bMove == True):                    
                    boss.chase(hero)
                    bMove = False
                else:
                    bMove = True
            
            draw_at(boss.x, boss.y, boss.render())        

            # When the Hero and boss are on the same X, Y location they fight.
            # The outcome is determined by what gear the player has picked up
            if(boss.x == hero.x and boss.y == hero.y):
                armor = ["Oak Shield", "Steel Helm", "Plate Mail", "Leather Boots", "Gauntlets"]

                hasArmor = True
                for p in armor:
                    if not hasItem(hero, p):
                        hasArmor = False

                hasSword = hasItem(hero, "Iron Sword")

                # Outcomes   HasArmor/Sword Player is victories  Else if the player has the armor but not the sword the player doesn't get killed but he can't kill the
                # monster.   If the player doesn't have all of the armor pieces he is killed. 
                if(hasArmor == True and hasSword == True):
                    boss.alive = False
                    draw_at(1, 20, "With your armor, sword and shield you launch yourself at the monster.\n It was a fight of the ages but you eventually slay the beast")
                elif(hasArmor == True and hasSword == False):
                    draw_at(1, 20, "You are a tank with that armor...but without the sword the monsters is impervious to your slap fighting!!")
                else:
                    draw_at(1, 20, "You forgot something...The monster beat you mercilessly. Your isekai adventure was only just beginning.")
                    draw.at(1, 25, "Print space to exit")
                    while(getInput == " "):
                        exitGame=True


## Start the Main Loop Running            
if __name__ == "__main__":
    main()
            



        
    
    
