import sqlite3
import os

DB_NAME = "chess_tournament.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Players Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            rating INTEGER DEFAULT 1200,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tournaments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            format TEXT NOT NULL,
            time_control_mins INTEGER NOT NULL,
            increment_secs INTEGER NOT NULL,
            status TEXT DEFAULT 'Setup',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tournament Participants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournament_participants (
            tournament_id INTEGER,
            player_id INTEGER,
            group_name TEXT,
            PRIMARY KEY (tournament_id, player_id),
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        )
    """)
    
    # Matches Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER,
            round_num INTEGER,
            group_name TEXT,
            white_player_id INTEGER,
            black_player_id INTEGER,
            status TEXT DEFAULT 'Upcoming',
            result TEXT,
            white_time_left REAL,
            black_time_left REAL,
            active_clock TEXT,
            clock_running INTEGER DEFAULT 0,
            last_updated REAL,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
            FOREIGN KEY (white_player_id) REFERENCES players(id),
            FOREIGN KEY (black_player_id) REFERENCES players(id)
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()