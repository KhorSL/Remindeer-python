import os
import psycopg2

class Database:

    def __init__(self, user="postgres", dbname="todo", port="5432", host="127.0.0.1", password=""):
        self.dbname = dbname

        """Development"""
        self.conn = psycopg2.connect(user = user, password = password, host = host, port = port, database = dbname)
        
        """Deployment"""
        # DATABASE_URL = os.environ['DATABASE_URL']
        # self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        self.cursor = self.conn.cursor()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS reminders (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL NOT NULL, reminder_text TEXT, reminder_time TIMESTAMP)"
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_reminder(self, input_text, chat_id):
        stmt = "INSERT INTO reminders (reminder_text, chat_id) VALUES (%s, %s)"
        args = (input_text, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def delete_reminder(self, input_text, chat_id):
        stmt = "DELETE FROM reminders WHERE reminder_text = (%s) AND chat_id = (%s)"
        args = (input_text, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_reminders(self, chat_id):
        stmt = "SELECT reminder_text FROM reminders WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return [x[0] for x in self.cursor.fetchall()]
