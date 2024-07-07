import sqlite3


def initialize_if_not_exists():
    command = """pragma journal_mode='wal';
    create table if not exists jobs(uuid TEXT NOT NULL, request JSONB NOT NULL, response JSONB, status INT DEFAULT 0, notified INT DEFAULT 0);"""
    db = sqlite3.connect("jobs.db")
    cursor = db.cursor()
    cursor.executescript(command)
    db.close()


def create_connection():
    db = sqlite3.connect("jobs.db", check_same_thread=False)
    return db, db.cursor()
