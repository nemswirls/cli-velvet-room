import sqlite3
import random
from models.persona import Persona

class Stock:
    def __init__(self, db_name='velvetRoom.db', player_id=None):
        self.db_name = db_name
        self.player_id = player_id

    def _connect(self):
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def get_personas_in_stock(self):
        """Retrieve all personas in the player's stock."""
        if not self.player_id:
            raise ValueError("Player ID is not set. Cannot retrieve stock data.")
        
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE player_id = ?", (self.player_id,))
        personas = cursor.fetchall()  # Fetch all personas in the stock
        conn.close()

        # Return persona objects
        return [Persona(*persona) for persona in personas]
    def get_stock_count(self):
        """Returns the number of personas in the player's stock."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM personas WHERE player_id = ?", (self.player_id,))
        stock_count = cursor.fetchone()[0]
        conn.close()
        return stock_count
    def is_stock_full(self, max_stock=8):
        """Check if the player's stock is full (default is 8)."""
        stock_count = self.get_stock_count()
        return stock_count >= max_stock

    def summon_persona(self):
        """Summon a random persona based on the player's level."""
        player_level = self.get_player_level()

        # Get personas within ±3 levels of the player's level
        persona = self.get_random_persona_from_db(player_level)

        if persona:
            # Check if stock is full before adding
            if not self.is_stock_full():
                if not self.is_persona_in_stock(persona.id):
                    self.add_persona_to_stock(persona)
                    print(f"You have summoned {persona.name}!")
                else:
                    print(f"You already have {persona.name} in your stock.")  
            else:
                print("Your stock is full. Cannot summon more personas.")
        else:
            print("No personas found matching your level range.")

    def get_random_persona_from_db(self, player_level):
        """Get a random persona from the database based on the player's level."""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Get a list of persona IDS already in the player's stock
        cursor.execute("SELECT id FROM personas WHERE player_id = ?", (self.player_id,))
        stock_persona_ids = {row[0] for row in cursor.fetchall()}
        # Reconnect to filter out personas already in stock
        conn = self._connect()
        cursor = conn.cursor()
        #initialize min_level and max_level
        min_level = 1
        max_level = 99  
        
        
        # If the player is level 1, ensure they always get a level 1 persona
        if player_level == 1:
         cursor.execute("""
            SELECT * FROM personas WHERE level = 1
        """)
        else:
        # Calculate level range (±3 of player level) for players above level 1
         min_level = max(1, player_level - 3)  # Ensure level is at least 1
        max_level = min(99, player_level + 3)  # Cap level at 99
        cursor.execute("""
            SELECT * FROM personas 
            WHERE level BETWEEN ? AND ? AND id NOT IN ({})
        """.format(','.join('?' for _ in stock_persona_ids)), [min_level, max_level] + list(stock_persona_ids))
        
        matching_personas = cursor.fetchall()
        conn.close()

        if matching_personas:
            # Randomly select one persona from the matching ones
            random_persona_data = random.choice(matching_personas)
            return Persona(*random_persona_data)
        else:
            return None

    def add_persona_to_stock(self, persona):
        """Add a persona to the player's stock."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE personas SET player_id = ? WHERE id = ?
        """, (self.player_id, persona.id))
        conn.commit()
        conn.close()

    def is_persona_in_stock(self, persona_id):
        """Check if a persona is already in the player's stock."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE player_id = ? AND id = ?", (self.player_id, persona_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_player_level(self):
        """Get the current level of the player."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM players WHERE id = ?", (self.player_id,))
        player_level = cursor.fetchone()[0]
        conn.close()
        return player_level

    def list_stock(self):
        """List all personas in the player's stock with a number next to each name."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT personas.id, personas.name, personas.level, arcanas.name 
            FROM personas 
            JOIN arcanas ON personas.arcana_id = arcanas.id               
            WHERE personas.player_id = ?
            """, (self.player_id,))
            
            
            personas = cursor.fetchall()
            conn.close()

            if personas:
                print("Your personas:")
                for index, persona in enumerate(personas, start=1):
                    persona, name, level, arcana_name = persona
                    print(f"{index}. {name} (Level: {level}, Arcana: {arcana_name})")
            else:
                print("You have no personas in your stock.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            conn.close()

    def get_persona_by_number(self, selection_number):
        """Fetch a persona by its number in the list."""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, level, arcana_id FROM personas WHERE player_id = ?", (self.player_id,))
        personas = cursor.fetchall()
        conn.close()

        if 0 < selection_number <= len(personas):
            persona_data = personas[selection_number - 1]
            return Persona(*persona_data)
        else:
            return None
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
    def remove_persona_from_stock(self, persona):
        """Remove a persona from the player's stock."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE personas SET player_id = NULL WHERE id = ?", (persona.id,))
        conn.commit()
        conn.close()