import sqlite3
from models.player import Player
from models.stock import Stock
import sys
sys.path.insert(0, 'lib')

def main():
    print("Welcome to The Velvet Room!")
    print("---------------------------")
    
    # Load or create player
    player = initialize_player()

    while True:
        # Display player level at the top
        display_player_level(player)

        print("\nMain Menu:")
        print("1. View Player Stats")
        print("2. View Stock")
        print("3. Summon a Persona")
        print("4. Release a Persona")
        print("5. Fuse Personas")
        print("6. Exit Game")

        choice = input("Choose an option (1-6): ")
        
        if choice == "1":
            view_player_stats(player)
        elif choice == "2":
            view_stock(player)
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
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM players WHERE name = ?", (player_name,))
    player_data = cursor.fetchone()

    if player_data:
        player_id = player_data[0]
        player = Player(player_id=player_id)  # Fetch existing player data from the database
    else:
        cursor.execute("INSERT INTO players (name, level, stock_limit) VALUES (?, ?, ?)", 
                       (player_name, 1, 8))  # Default level 1 and stock limit 8
        player_id = cursor.lastrowid
        player = Player(player_id=player_id, name=player_name)  # New player
        conn.commit()

    conn.close()
    return player

def view_player_stats(player):
    """Display the player's stats."""
    # Assuming 'player' is a Player object
    print(f"Name: {player.name}")
    print(f"Level: {player.get_player_level()}")  # You can call the method if you need the level
    print(f"Stock Limit: {player.stock_limit}")

def view_stock(player):
    """View the player's stock of personas."""
    stock = Stock(player_id=player.player_id)
    stock_list = stock.list_stock()

    if stock_list:
        print("Your Stock:")
        for persona in stock_list:
            print(f"Name: {persona[0]}, Level: {persona[1]}, Arcana: {persona[2]}")
    else:
        print("Your stock is empty.")
def summon_persona(player):
    """Summon a random persona."""
    print("\nSummoning a persona...")
    player.summon_persona()

def release_persona(player):
    """Release a persona from the player's stock."""
    print("\nReleasing a persona...")
    view_stock(player)  # Show stock to help the user choose
    persona_id = input("Enter the ID of the persona to release: ").strip()
    if persona_id.isdigit():
        player.release_persona(int(persona_id))
    else:
        print("Invalid ID. Please try again.")

def fuse_personas(player):
    """Fuse two personas in the player's stock."""
    print("\nFusing personas...")
    view_stock(player)  # Show stock to help the user choose
    persona_id_1 = input("Enter the ID of the first persona: ").strip()
    persona_id_2 = input("Enter the ID of the second persona: ").strip()

    if persona_id_1.isdigit() and persona_id_2.isdigit():
        success = player.fuse_personas(int(persona_id_1), int(persona_id_2))
        if success:
            print("Fusion successful!")
        else:
            print("Fusion failed. Ensure the conditions are met.")
    else:
        print("Invalid IDs. Please try again.")

if __name__ == "__main__":
    main()
