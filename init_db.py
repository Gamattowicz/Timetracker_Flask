import sqlite3

connection = sqlite3.connect('time_tracker.db')

cur = connection.cursor()

cur.execute('''CREATE TABLE projects (
            id integer primary key autoincrement,
            name text not null UNIQUE,
            shortcut text not null UNIQUE
            )''')
cur.execute('''create table hours (
            id integer primary key autoincrement,
            amount integer not null,
            work_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            project_id integer not null,
            FOREIGN KEY (project_id) REFERENCES Projects(id))''')


connection.commit()
connection.close()