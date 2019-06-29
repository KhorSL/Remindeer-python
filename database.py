import os
import psycopg2

class Database:
    
    """Deployment"""
    DATABASE_URL = DATABASE_URL = os.environ['DATABASE_URL']

    def __init__(self, user="postgres", dbname="todo", port="5432", host="127.0.0.1", password=""):
        self.dbname = dbname

        """Development"""
        # self.conn = psycopg2.connect(user = user, password = password, host = host, port = port, database = dbname)
        
        """Deployment"""
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        self.cursor = self.conn.cursor()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS reminders (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL, reminder_text TEXT, reminder_time TIME)"
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_reminder(self, input_text, chat_id):
        stmt = "INSERT INTO reminders (reminder_text, chat_id) VALUES (%s, %s)"
        args = (input_text, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def delete_reminder(self, reminder_text):
        stmt = "DELETE FROM reminders WHERE reminder_text = (%s)"
        args = (reminder_text, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_reminders(self, chat_id):
        stmt = "SELECT reminder_text FROM reminders WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return [x[0] for x in self.cursor.fetchall()]
