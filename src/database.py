import sqlite3

class Storage: 
    def __init__(self):
        self.conn = sqlite3.connect('activities.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS activities (id TEXT UNIQUE)')

    def add(self, id):
        self.cursor.execute('INSERT INTO activities (id) VALUES (?)', (id,))
        self.conn.commit()

    def contains(self, id):
        self.cursor.execute('SELECT * FROM activities WHERE id = ?', (id,))
        return self.cursor.fetchone() is not None
