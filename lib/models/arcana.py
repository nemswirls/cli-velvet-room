import sqlite3

class Arcana:
    def __init__(self, db_name='game.db'):
        """Initialize with the database name (default is 'game.db')."""
        self.db_name = db_name

    def _connect(self):
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def get_all_arcanas(self):
        """Retrieve all arcanas from the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM arcanas")
        arcanas = cursor.fetchall()  # Fetch all rows
        conn.close()
        return arcanas

    def get_arcana_by_id(self, arcana_id):
        """Retrieve an arcana by its ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM arcanas WHERE id = ?", (arcana_id,))
        arcana = cursor.fetchone()  # Fetch the first matching row
        conn.close()
        return arcana

    def update_arcana_name(self, arcana_id, new_name):
        """Update the name of an arcana by its ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE arcanas SET name = ? WHERE id = ?", (new_name, arcana_id))
        conn.commit()  # Commit the transaction
        conn.close()
