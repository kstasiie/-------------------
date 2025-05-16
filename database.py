import sqlite3

DATABASE_FILE = "music_catalog.db"

def create_database(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT,
                file_path TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER,
                song_id INTEGER,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id),
                FOREIGN KEY (song_id) REFERENCES songs(id),
                PRIMARY KEY (playlist_id, song_id)
            )
        ''')

        conn.commit()
        print("Файл базы данных и таблицы созданы успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка при создании базы данных или таблиц: {e}")
    finally:
        if conn:
            conn.close()

