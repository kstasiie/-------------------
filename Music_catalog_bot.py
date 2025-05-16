import telebot
import sqlite3

bot = telebot.TeleBot('7953999675:AAGfdcIFOQ51Li-4ioOvQwjNLgpa_bF-6yg')

# Класс для представления музыкального произведения
class Song:
    def __init__(self, id, title, artist, genre, file_path):
        self.id = id
        self.title = title
        self.artist = artist
        self.genre = genre
        self.file_path = file_path

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.genre})"

# Класс для представления плейлиста
class Playlist:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

# Главный класс бота
class MusicCatalogBot:
    def __init__(self, bot, db_file): 
        self.bot = bot 
        self.db_file = db_file  
        self.db_connection = None
        self.db_cursor = None
        try:
            self.connect_db()
        except Exception as e:
            print(f"Ошибка при инициализации бота: {e}")
            exit() 
        self.setup_handlers() 

    def connect_db(self):
        """Подключается к базе данных."""
        try:
            self.db_connection = sqlite3.connect(self.db_file, check_same_thread=False)
            self.db_cursor = self.db_connection.cursor()
            print(f"Подключено к базе данных: {self.db_file}")
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise  

    def setup_handlers(self):
        """Устанавливает обработчики команд."""
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.handle_start_command(message)

        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            self.handle_help_command(message) 

        @self.bot.message_handler(commands=['search'])
        def handle_search(message):
            self.handle_search_command(message) 

    def add_song(self, title, artist, genre, file_path):
        """Добавляет песню в базу данных."""
        try:
            self.db_cursor.execute('''
                INSERT INTO songs (title, artist, genre, file_path)
                VALUES (?, ?, ?, ?)
            ''', (title, artist, genre, file_path))
            self.db_connection.commit()
            print(f"Песня '{title}' добавлена в базу данных.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении песни: {e}")

    def search_songs(self, query):
        """Ищет песни по названию, исполнителю или жанру."""
        try:
            self.db_cursor.execute('''
                SELECT id, title, artist, genre, file_path
                FROM songs
                WHERE title LIKE ? OR artist LIKE ? OR genre LIKE ?
            ''', ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            songs = []
            for row in self.db_cursor.fetchall():
                song = Song(row[0], row[1], row[2], row[3], row[4])
                songs.append(song)
            return songs
        except sqlite3.Error as e:
            print(f"Ошибка при поиске песен: {e}")
            return []

    def send_message(self, chat_id, text):
        """Отправляет текстовое сообщение пользователю."""
        try:
            self.bot.send_message(chat_id, text) 
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def handle_search_command(self, message):
        """Обрабатывает команду /search."""
        try:
            query = message.text.split(' ', 1)[1]  
            songs = self.search_songs(query)  

            if songs:
                response = "Найденные песни:\n"
                for song in songs:
                    response += str(song) + "\n"  
                self.send_message(message.chat.id, response)
            else:
                self.send_message(message.chat.id, "Ничего не найдено.")

        except IndexError:
            self.send_message(message.chat.id, "Используйте: /search <запрос>")
        except Exception as e:
            print(f"Ошибка при выполнении /search: {e}")
            self.send_message(message.chat.id, "Произошла ошибка при поиске.")

    def handle_start_command(self, message):
        """Обрабатывает команду /start."""
        help_message = """
        Доступные команды:
        /start - Начать работу с ботом
        /help - Получить справку
        /search <запрос> - Поиск музыки по названию, исполнителю или жанру
        """
        self.send_message(message.chat.id, help_message)

    def handle_help_command(self, message):
        """Обрабатывает команду /help."""
        help_message = """ Руководство пользователя:  https://jmp.sh/s/UCkw8kKfGsAG6dggeMhR
        """
        self.send_message(message.chat.id, help_message)

    def run(self):
        """Запускает бота."""
        try:
            self.bot.polling(none_stop=True)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка Telegram API: {e}")
        except Exception as e:
            print(f"Ошибка при запуске polling: {e}")

# Создаем экземпляр бота
music_catalog_bot = MusicCatalogBot(bot, 'music_catalog.db')

# Запускаем бота
music_catalog_bot.run()