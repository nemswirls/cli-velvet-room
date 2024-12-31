import sqlite3
import random
from persona import Persona

class Stock:
    def __init__(self, db_name='game.db', player_id=None):
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
                if self.is_persona_in_stock(persona.persona_id):
                    print(f"You already have {persona.name} in your stock.")
                else:
                    self.add_persona_to_stock(persona)
                    print(f"You have summoned {persona.name}!")
            else:
                print("Your stock is full. Cannot summon more personas.")
        else:
            print("No personas found matching your level range.")

    def get_random_persona_from_db(self, player_level):
        """Get a random persona from the database based on the player's level."""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Calculate level range (±3 of player level)
        min_level = max(1, player_level - 3)  # Ensure level is at least 1
        max_level = min(99, player_level + 3)  # Cap level at 99
        
        cursor.execute("""
            SELECT * FROM personas 
            WHERE level BETWEEN ? AND ?
        """, (min_level, max_level))
        
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
        """, (self.player_id, persona.persona_id))
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