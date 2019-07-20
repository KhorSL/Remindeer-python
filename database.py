import os
import psycopg2
import config

class Database:

    def __init__(self, user="postgres", dbname="todo", port="5432", host="127.0.0.1", password=""):
        self.dbname = dbname

        """Development"""
        # self.conn = psycopg2.connect(user = user, password = password, host = host, port = port, database = dbname)
        
        """Deployment"""
        # DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(config.DATABASE_URL, sslmode='require')

        self.cursor = self.conn.cursor()

    def setup(self):
        table_reminders = "CREATE TABLE IF NOT EXISTS reminders (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL NOT NULL, reminder_text TEXT, reminder_time TIMESTAMP WITH TIME ZONE)"
        table_intermediate = "CREATE TABLE IF NOT EXISTS intermediate (id BIGSERIAL PRIMARY KEY, chat_id BIGSERIAL NOT NULL, reminder_text TEXT, reminder_date DATE, stored_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)"
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

    def delete_reminder_by_id(self, input_id, chat_id):
        stmt = "DELETE FROM reminders WHERE id = (%s) AND chat_id = (%s)"
        args = (input_id, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()    

    def get_reminders_text(self, chat_id):
        stmt = "SELECT reminder_text FROM reminders WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return [x[0] for x in self.cursor.fetchall()]

    def get_reminders_text_and_time(self, chat_id):
        stmt = "SELECT reminder_text, reminder_time FROM reminders WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return self.cursor.fetchall()

    def get_reminders(self, chat_id):
        stmt = "SELECT * FROM reminders WHERE chat_id = (%s)"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return self.cursor.fetchall()

    def get_reminders_to_send(self, input_time):
        stmt = "SELECT * FROM reminders WHERE reminder_time = (%s)"
        input_time = input_time.strftime("%Y-%m-%d, %H:%M") + ":00"
        args = (input_time, )
        self.cursor.execute(stmt, args)
        return self.cursor.fetchall()

    def get_reminders_around_time(self, input_time):
        stmt = "SELECT * FROM reminders WHERE reminder_time BETWEEN TO_TIMESTAMP((%s), \'YYYY/MM/DD HH24:MI:SS\') - INTERVAL \'1 minutes\' AND TO_TIMESTAMP((%s), 'YYYY/MM/DD HH24:MI:SS') + INTERVAL \'1 minutes\';"
        input_time = input_time.strftime("%Y-%m-%d, %H:%M") + ":00"
        print (input_time)
        args = (input_time, input_time, )
        self.cursor.execute(stmt, args)
        return self.cursor.fetchall()

    def get_all_reminders(self, input_time):
        stmt = "SELECT * FROM reminders"
        self.cursor.execute(stmt)
        return self.cursor.fetchall()

    def add_intermediate_reminder(self, input_text, chat_id):
        stmt = "INSERT INTO intermediate (reminder_text, chat_id) VALUES (%s, %s)"
        args = (input_text, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def update_intermediate_reminder_date(self, input_date, chat_id):
        stmt = "UPDATE intermediate SET reminder_date = (%s) WHERE id = (SELECT id FROM intermediate WHERE chat_id = (%s) ORDER BY stored_time ASC LIMIT 1)"
        args = (input_date, chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def get_intermediate(self, chat_id):
        stmt = "SELECT * FROM intermediate WHERE chat_id = (%s) ORDER BY stored_time ASC LIMIT 1"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        return self.cursor.fetchall()[0]

    def delete_intermediate(self, chat_id):
        stmt = "DELETE FROM intermediate WHERE id = (SELECT id FROM intermediate WHERE chat_id = (%s) ORDER BY stored_time ASC LIMIT 1);"
        args = (chat_id, )
        self.cursor.execute(stmt, args)
        self.conn.commit()
