import sqlite3
import random
from models.stock import Stock
from models.persona import Persona

class Player:
    def __init__(self, db_name='velvetRoom.db', level=1, player_id=None, name=None, stock_limit=None):
        """
        Initialize a Player object.

      :param db_name: Name of the database file (default 'velvetRoom.db').
        :param player_id: Unique identifier for the player (int).
        :param name: Name of the player (str).
        :param stock_limit: The stock limit for the player (int). If not provided, it will be fetched from the database.
        """
        self.db_name = db_name
        self.player_id = player_id
        self.name = name
        self.level = level
        self.in_memory_stock = []
        # If stock_limit is not provided, fetch it from the database
        if stock_limit is not None:
            self.stock_limit = stock_limit
        else:
            self.stock_limit = self.get_stock_limit()
    def _connect(self):
        return sqlite3.connect(self.db_name)

    @staticmethod
    def create_player(name, db_name='velvetRoom.db'):
        """
        Create a new player in the database.

        :param name: Name of the player (str).
        :param db_name: Name of the database file (default 'velvetRoom.db').
        :return: A Player object.
        """
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name, level) VALUES (?, ?)", (name, 1))
        player_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return Player(db_name=db_name, player_id=player_id, name=name)

    def get_player_level(self):
        """Get the current level of the player."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM players WHERE id = ?", (self.player_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def summon_persona(self):
        """Summon a random persona and increase the player's level by 1."""
        stock = Stock(player_id=self.player_id)

        # Perform the summoning
        stock.summon_persona()

        # Increase the player's level by 1 after summoning
        self.increase_player_level(1)

        print(f"Your level has increased by 1 to {self.get_player_level()}.")

    def increase_player_level(self, increment=1):
        """Increase the player's level."""
        new_level = self.get_player_level() + increment
        if new_level > 99:
            new_level = 99  # Enforce level cap of 99
        self.update_player_level(new_level)

    def update_player_level(self, new_level):
        """Update the player's level in the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET level = ? WHERE id = ?", (new_level, self.player_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_player_by_id(player_id, db_name='velvetRoom.db'):
        """
        Retrieve a player by their ID.

        :param player_id: Unique identifier for the player (int).
        :param db_name: Name of the database file (default 'velvetRoom.db').
        :return: A Player object or None if not found.
        """
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level FROM players WHERE id = ?", (player_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return Player(db_name=db_name, player_id=result[0], name=result[1])
        return None
    
    def _fetch_player_data(self):
        """Fetch player data (including name, level, and stock limit) from the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, level, stock_limit FROM players WHERE id = ?", (self.player_id,))
        player_data = cursor.fetchone()
        if player_data:
            self.name, self.level, self.stock_limit = player_data
        conn.close()
    def get_stock_limit(self):
        """Fetch the player's stock limit from the database."""
        conn = sqlite3.connect("velvetRoom.db")
        cursor = conn.cursor()
        cursor.execute("SELECT stock_limit FROM players WHERE id = ?", (self.player_id,))
        stock_limit = cursor.fetchone()
        conn.close()

        if stock_limit:
            return stock_limit[0]
        return 8  # Default if no stock_limit is found
    
    def release_persona(self):
        """Release a persona from the player's stock."""
        self.stock.list_stock()  # Call the list_stock method from the Stock class
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
    def remove_persona_from_stock(self, persona):
        """Remove a persona from the player's stock."""
        conn = self._connect()
        cursor = conn.cursor()
        try:
           cursor.execute("UPDATE personas SET player_id = NULL WHERE id = ?", (persona.id,))
           conn.commit()
        #    self.increase_player_level(2)
        #    print(f"Your level has increased by 2 to {self.get_player_level()}.")
           print(f"Persona {persona.name} has been removed from your stock.")
        except sqlite3.Error as e:
           print(f"An error occurred while removing the persona: {e}")
        finally:
          conn.close()
    
    def add_persona_to_stock(self, name, level, arcana_id):
        """Add a new persona to the player's in-memory stock (not persisted in database)."""
        try:
        # Create a new Persona object and add it to the in-memory stock (list)
            new_persona = Persona(name=name, level=level, arcana_id=arcana_id, player_id=self.player_id)
            self.in_memory_stock.append(new_persona)  # Assuming you have an in-memory stock like a list or set
            print(f"New persona {name} (Level:{level}, Arcana: {arcana_id}) has been added to your in-memory stock.")
        except Exception as e:
            print(f"An error occurred while adding the persona: {e}")
    
    def fuse_personas(self, persona_id_1, persona_id_2):
        """Fuse two personas and return success."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Fetch the first persona details
            cursor.execute("SELECT id, name, level, arcana_id FROM personas WHERE id = ? AND player_id = ?", (persona_id_1, self.player_id))
            persona_1_data = cursor.fetchone()

            # Fetch the second persona details
            cursor.execute("SELECT id, name, level, arcana_id FROM personas WHERE id = ? AND player_id = ?", (persona_id_2, self.player_id))
            persona_2_data = cursor.fetchone()

            if not persona_1_data or not persona_2_data:
                print("One or both of the personas do not exist in your stock.")
                return False
            
            # Convert data to Persona objects
            persona_1 = Persona(*persona_1_data)
            persona_2 = Persona(*persona_2_data)

            # Ensure the personas have different arcanas
            if persona_1.arcana_id == persona_2.arcana_id:
                print("The personas have the same arcana. Fusion failed.")
                return False

            # Select a new persona in-memory, generated based on the fusion logic
            new_persona = self.get_random_fused_persona(persona_1.arcana_id, persona_2.arcana_id)

            if not new_persona:
                print("No valid persona found to fuse.")
                return False

            # Create the new persona details
            new_persona_id, new_persona_name, new_persona_level, new_persona_arcana = new_persona

            new_persona_object = Persona(new_persona_id, new_persona_name, new_persona_level, new_persona_arcana)
            # Add the new persona to the player's in-memory stock
            self.in_memory_stock.append(new_persona_object) 
            print(self.in_memory_stock)

            # Remove the fused personas from the stock
            self.remove_persona_from_stock(persona_1)
            self.remove_persona_from_stock(persona_2)

            self.increase_player_level(3)
            print(f"Your level has increased by 3 to {self.get_player_level()}.")

            print(f"Fusion successful! {new_persona_name} (Level: {new_persona_level}, Arcana: {new_persona_arcana}) has been added to your stock.")
            return True

        except sqlite3.Error as e:
                print(f"An error occurred: {e}")
                return False
        finally:
         conn.close()
    def get_random_fused_persona(self, arcana_id_1, arcana_id_2):
        """Get a random persona from the database with:
           - A different arcana from persona_1 and persona_2.
           - A level ~3 higher than the player's level."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Find all personas with a different arcana from both persona_1 and persona_2
            cursor.execute("""
                SELECT id, name, level, arcana_id 
                FROM personas 
                WHERE arcana_id NOT IN (?, ?) 
                AND level BETWEEN ? AND ?
                ORDER BY RANDOM()
                 LIMIT 1
            """, (arcana_id_1, arcana_id_2,self.level - 3, self.level + 3))

            new_persona = cursor.fetchone()
            new_persona_obj = Persona(*new_persona)
            new_persona_obj.player_id = self.player_id
            
            cursor.execute("""
            UPDATE personas 
            SET player_id =? 
            WHERE id =?
            """, (new_persona_obj.player_id, new_persona_obj.id)             
                           )
            conn.commit()
            
            return new_persona  # Returns a tuple: (id, name, level, arcana_id)
        
        except sqlite3.Error as e:
            print(f"An error occurred while fetching a new persona: {e}")
            return None
        finally:
            conn.close()
    
   
    
    
   

                          