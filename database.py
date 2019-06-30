import os
import psycopg2

class Database:

    def __init__(self, user="postgres", dbname="todo", port="5432", host="127.0.0.1", password=""):
        self.dbname = dbname

        """Development"""
        # self.conn = psycopg2.connect(user = user, password = password, host = host, port = port, database = dbname)
        
        """Deployment"""
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        self.cursor = self.conn.cursor()

    def setup(self):
        table_reminders = "CREATE TABLE IF NOT EXISTS reminders (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL NOT NULL, reminder_text TEXT, reminder_time TIMESTAMP WITH TIME ZONE)"
        table_intermediate = "CREATE TABLE IF NOT EXISTS intermediate (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL NOT NULL, reminder_text TEXT, stored_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)"
        self.cursor.execute(table_reminders)
        self.cursor.execute(table_intermediate)
        self.conn.commit()

    def add_reminder(self, input_text, chat_id, reminder_time):
        stmt = "INSERT INTO reminders (reminder_text, chat_id, reminder_time) VALUES (%s, %s, %s)"
        args = (input_text, chat_id, reminder_time, )
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

    def add_intermediate(self, input_text, chat_id):
        stmt = "INSERT INTO intermediate (reminder_text, chat_id) VALUES (%s, %s)"
        args = (input_text, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_intermediate(self, chat_id):
        stmt = "SELECT reminder_text FROM intermediate WHERE chat_id = (%s) ORDER BY stored_time ASC LIMIT 1"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return [x[0] for x in self.cursor.fetchall()]

    def delete_intermediate(self, chat_id):
        stmt = "DELETE FROM intermediate WHERE id = (SELECT id FROM intermediate WHERE chat_id = (%s) ORDER BY stored_time ASC LIMIT 1);"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()
