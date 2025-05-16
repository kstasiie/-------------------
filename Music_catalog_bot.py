import telebot
from telebot import types
import sqlite3

# Создаем экземпляр бота (ТОЛЬКО ОДИН РАЗ!)
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
    def __init__(self, bot, db_file):  # Передаем экземпляр telebot.TeleBot в конструктор
        self.bot = bot  # Сохраняем экземпляр bot
        self.db_file = db_file  # Сохраняем имя файла БД
        self.db_connection = None
        self.db_cursor = None
        try:
            self.connect_db()
        except Exception as e:
            print(f"Ошибка при инициализации бота: {e}")
            exit()  # Важно: останавливаем выполнение, если не удалось подключиться к БД
        self.setup_handlers()  # Устанавливаем обработчики

    def connect_db(self):
        """Подключается к базе данных."""
        try:
            self.db_connection = sqlite3.connect(self.db_file, check_same_thread=False)
            self.db_cursor = self.db_connection.cursor()
            print(f"Подключено к базе данных: {self.db_file}")
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise  # Важно: пробрасываем исключение, чтобы сообщить о проблеме

    def setup_handlers(self):
        """Устанавливает обработчики команд."""
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.handle_start_command(message)  # Вызываем метод класса

        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            self.handle_help_command(message)  # Вызываем метод класса

        @self.bot.message_handler(commands=['search'])
        def handle_search(message):
            self.handle_search_command(message)  # Вызываем метод класса

        # Обработчик для нажатия на кнопку "Поиск"
        @self.bot.message_handler(func=lambda message: message.text == "Поиск")
        def handle_search_button(message):
            """Обрабатывает нажатие на кнопку "Поиск"."""
            self.handle_search_command(message)  # Вызываем команду поиска

        @self.bot.message_handler(func=lambda message: message.text == "Редактировать плейлист")
        def handle_playlist_button(message):
            """Обрабатывает нажатие на кнопку "Редактировать плейлист"."""
            # Здесь нужно добавить код для редактирования плейлиста.
            self.send_message(message.chat.id, "Функция редактирования плейлиста пока не реализована.")

        @self.bot.message_handler(func=lambda message: message.text == "Помощь")
        def handle_help_button(message):
            """Обрабатывает нажатие на кнопку "Помощь"."""
            self.handle_help_command(message)  # Вызываем команду help


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

    def send_message(self, chat_id, text, reply_markup=None):
        """Отправляет текстовое сообщение пользователю."""
        try:
            self.bot.send_message(chat_id, text, reply_markup=reply_markup)  # reply_markup - для передачи кнопок
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def handle_search_command(self, message):
        """Обрабатывает команду /search."""
        try:
            if len(message.text.split(' ', 1)) > 1:  # Проверяем, есть ли запрос после /search
                query = message.text.split(' ', 1)[1]
                songs = self.search_songs(query)
                if songs:
                    response = "Найденные песни:\n"
                    for song in songs:
                        response += str(song) + "\n"
                    self.send_message(message.chat.id, response)
                else:
                    self.send_message(message.chat.id, "Ничего не найдено.")
            else:
                self.send_message(message.chat.id, "Введите текст запроса после /search, например: /search Beatles")

        except Exception as e:
            print(f"Ошибка при выполнении /search: {e}")
            self.send_message(message.chat.id, "Произошла ошибка при поиске.")

    def handle_start_command(self, message):
        """Обрабатывает команду /start."""
        help_message = """
        Доступные команды:
        /start - Начать работу с ботом
        /help - Получить справку
        """
        # Создаем клавиатуру
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # resize_keyboard=True - для адаптации размера кнопок
        # Создаем кнопки
        search_button = types.KeyboardButton("Поиск")
        playlist_button = types.KeyboardButton("Редактировать плейлист")
        help_button = types.KeyboardButton("Помощь")

        # Добавляем кнопки в клавиатуру
        markup.row(search_button)  # Кнопки в ряд
        markup.row(playlist_button, help_button)  # Кнопки в ряд

        self.send_message(message.chat.id, help_message, reply_markup=markup)

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


# Создаем экземпляр MusicCatalogBot
music_catalog_bot = MusicCatalogBot(bot, 'music_catalog.db')

# Запускаем бота
music_catalog_bot.run()