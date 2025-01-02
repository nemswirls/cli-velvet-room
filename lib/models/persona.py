import sqlite3

class Persona:
    def __init__(self, id, name, level, arcana_id, player_id=None):
        """
        Initialize a Persona object.

        :param persona_id: Unique identifier for the persona (int).
        :param name: Name of the persona (str).
        :param level: Level of the persona (int).
        :param arcana: Arcana to which the persona belongs (str).
        :param player_id: ID of the player who owns this persona, optional (int).
        """
        self.id = id
        self.name = name
        self.level = level
        self.arcana_id = arcana_id
        self.player_id = player_id
    def _connect(self):
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    @classmethod
    def from_db_row(cls, row):
        """
        Create a Persona object from a row fetched from the database.

        :param row: A tuple containing persona data from the database.
        :return: A Persona object.
        """
        return cls(persona_id=row[0], name=row[1], level=row[2], arcana=row[3], player_id=row[4])

    @staticmethod
    def get_persona_by_id(db_name, persona_id):
        """
        Retrieve a persona by its ID from the database.

        :param db_name: The database name (str).
        :param persona_id: The ID of the persona (int).
        :return: A Persona object or None if not found.
        """
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE id = ?", (persona_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Persona.from_db_row(row)
        return None

    @staticmethod
    def get_personas_by_level_range(db_name, min_level, max_level):
        """
        Retrieve personas by level range from the database.

        :param db_name: The database name (str).
        :param min_level: The minimum level for filtering personas (int).
        :param max_level: The maximum level for filtering personas (int).
        :return: A list of Persona objects.
        """
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM personas 
            WHERE level BETWEEN ? AND ?
        """, (min_level, max_level))
        rows = cursor.fetchall()
        conn.close()

        return [Persona.from_db_row(row) for row in rows]

    def __str__(self):
        """Return a string representation of the persona."""
        return f"{self.name} (Level {self.level}, Arcana: {self.arcana})"