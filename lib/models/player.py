import sqlite3
from models.stock import Stock


class Player:
    def __init__(self, db_name='game.db', player_id=None, name=None):
        """
        Initialize a Player object.

        :param db_name: Name of the database file (default 'game.db').
        :param player_id: Unique identifier for the player (int).
        :param name: Name of the player (str).
        """
        self.db_name = db_name
        self.player_id = player_id
        self.name = name
        self.stock_limit = self.get_stock_limit()
    def _connect(self):
        return sqlite3.connect(self.db_name)

    @staticmethod
    def create_player(name, db_name='game.db'):
        """
        Create a new player in the database.

        :param name: Name of the player (str).
        :param db_name: Name of the database file (default 'game.db').
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
    def get_player_by_id(player_id, db_name='game.db'):
        """
        Retrieve a player by their ID.

        :param player_id: Unique identifier for the player (int).
        :param db_name: Name of the database file (default 'game.db').
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
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT stock_limit FROM players WHERE id = ?", (self.player_id,))
        stock_limit = cursor.fetchone()[0]
        conn.close()
        return stock_limit