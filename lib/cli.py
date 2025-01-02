import sqlite3
from models.player import Player
from models.stock import Stock
import sys
sys.path.insert(0, 'lib')

def main():
    print("Welcome to The Velvet Room!")
    print("""
                   -..:--=::-+                 
           -:.-:-------+*+**#@            
         -...-@@%++=-==+#*##**%           
      @@=..:=%##*+*+:=##*+*%@%#%          
      %%-::*+.--%=-*#%##++*#@#****##%     
       =+--=+:-=+-=+++#*+=*#@@@%**#****#% 
       -..--==+=+**++*+.*=*%@@@@@%***%@@@@
     =:.:--+*+++=+++#*-+*#%@@@@@%%%%@@@@@@
    :.::-+#*+==+++##*#*@%%@@@@@@@@@@@@@@@@
  =..:-=*#%+-=+*##***+*@-:--#@@@@@@@@@@@@@
 -.:--= @@@@@@@@-@===+@%..:+#@@@@@@@@@@@@@
-::-=    @@@@@@#*@*.-@@:::+##*@@@@@@@@@@@@
::-+       @@@@+###:*@@+==*#%*+@@@@@@@@@@@
==         @@@@@%*@*%@@@-+#%@@@#@@@@@@@   
            @@@@%=@*%@@@%@@@@@@@@@@@@     
             @@%%+@%@@@@@@@@@@@@@@@@      
             @@@%+%@@@@@@@@@@@@@@@        
             @@@@*+@@@@@@@@@@@@           
              @@@##@@@@@@@@@@             
                @@@@@@@@@                                     
""")
    
    # Load or create player
    player = initialize_player()

    while True:
        # Display player level at the top
        display_player_level(player)

        print("\nMain Menu:")
        print("1. View Stock")
        print("2. View all arcanas")
        print("3. Summon a Persona")
        print("4. Release a Persona")
        print("5. Fuse Personas")
        print("6. Exit Game")

        choice = input("Choose an option (1-6): ")
        
        if choice == "1":
             view_stock(player)
        elif choice == "2":
            view_all_arcanas()
        elif choice == "3":
            summon_persona(player)
        elif choice == "4":
            release_persona(player)
        elif choice == "5":
            fuse_personas(player)
        elif choice == "6":
            print("Goodbye! We look forward to your next visit.")
            break
        else:
            print("Invalid option. Please try again.")

def display_player_level(player):
    """Display the current player level in the top right corner."""
    level = player.get_player_level()
    print(f"\033[2K\rLevel: {level}", end="")  # Clears the line and prints the level on the same line

def initialize_player():
    """Initialize the player by getting their ID and name."""
    player_name = input("Enter your player name: ")

    # Check if player already exists
    conn = sqlite3.connect("velvetRoom.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, stock_limit FROM players WHERE name = ?", (player_name,))
    player_data = cursor.fetchone()

    if player_data:
        # Player exists, use existing player data
        player_id, stock_limit = player_data
        player = Player(player_id=player_id, stock_limit=stock_limit,)
    else:
        # Player doesn't exist, create a new one
        cursor.execute("INSERT INTO players (name, level, stock_limit) VALUES (?, ?, ?)", 
                       (player_name, 1, 8))  # Default level 1 and stock limit 8
        player_id = cursor.lastrowid
        player = Player(player_id=player_id, name=player_name, stock_limit=8)  # New player with default stock_limit
        conn.commit()

    conn.close()
    return player

def view_stock(player):
    """View the player's stock of personas."""
    stock = Stock(player_id=player.player_id)
    stock_list = stock.list_stock()

    if stock_list:
        print("Your Stock:")
        for persona in stock_list:
            print(f"Name: {persona[0]}, Level: {persona[1]}, Arcana: {persona[2]}")
    # else:
    #     print("Your stock is empty.")
def summon_persona(player):
    """Summon a random persona."""
    print("\nSummoning a persona...")
    player.summon_persona()

def release_persona(self):
    """Release a persona from the player's stock."""
    self.list_stock()  # Display the personas in a numbered list
    selection = input("Enter the number of the persona you want to release: ")

    if selection.isdigit():
        selection = int(selection)
        persona = self.get_persona_by_number(selection)  # Fetch persona by number
        if persona:
            self.remove_persona_from_stock(persona)  # Remove the selected persona from stock
            print(f"You have released {persona.name}!")
        else:
            print("Invalid selection.")
    else:
        print("Please enter a valid number.")

def fuse_personas(player):
    """Fuse two personas in the player's stock."""
    print("\nFusing personas...")
    view_stock(player)  # Show stock to help the user choose
    try:
        persona_num_1 = int(input("Enter the number of the first persona: ").strip())
        persona_num_2 = int(input("Enter the number of the second persona: ").strip())
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    # Get personas by the entered numbers
    persona_1 = player.get_persona_by_number(persona_num_1)
    persona_2 = player.get_persona_by_number(persona_num_2)

    if not persona_1 or not persona_2:
        print("Invalid selection. Please try again.")
        return

    # Perform fusion
    success = player.fuse_personas(persona_1.id, persona_2.id)
    if success:
        print("Fusion successful!")
    else:
        print("Fusion failed. Ensure the conditions are met.")
def view_all_arcanas():
    """List all arcanas and allow the user to view associated personas."""
    conn = sqlite3.connect('velvetRoom.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name FROM arcanas")
        arcanas = cursor.fetchall()

        if not arcanas:
            print("No arcanas available.")
            return

        print("\n--- All Arcanas ---")
        for arcana in arcanas:
            print(f"{arcana[0]}. {arcana[1]}")

        try:
            arcana_id = int(input("Enter the number of an arcana to see its personas: ").strip())
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        cursor.execute("SELECT name, level FROM personas WHERE arcana_id = ?", (arcana_id,))
        personas = cursor.fetchall()

        if personas:
            print(f"\n--- Personas of Arcana {arcana_id} ---")
            for persona in personas:
                print(f"- {persona[0]} (Level: {persona[1]})")
        else:
            print("No personas available for the selected arcana.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
