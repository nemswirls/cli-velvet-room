import sqlite3
from stock import Stock
from persona import Persona  # Import Persona class

class Player:
    def __init__(self, db_name='game.db', player_id=None):
        self.db_name = db_name
        self.player_id = player_id

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def get_player_level(self):
        """Get the current level of the player."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM players WHERE id = ?", (self.player_id,))
        level = cursor.fetchone()[0]
        conn.close()
        return level

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