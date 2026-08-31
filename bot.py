import os
import time
import logging
from threading import Thread
from typing import Dict, List

from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ForumMonitorBot:
    def __init__(self, bot: Bot, forum_url: str):  # Измененный конструктор
        self.bot = bot
        self.forum_url = forum_url
        self.known_topics: Dict[int, List[str]] = {}
        self.monitoring_threads: Dict[int, Thread] = {}
        self.monitoring_intervals: Dict[int, int] = {}
        self.running = True

    def start(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        if user_id not in self.known_topics:
            self.known_topics[user_id] = []
            self.monitoring_intervals[user_id] = 60

        update.message.reply_text(
            f"🚀 Бот начал мониторинг форума {self.forum_url}\n"
            "🔔 Новые темы будут приходить здесь\n"
            "⏳ Интервал проверки: 60 секунд\n"
            "⚙️ Используйте /setinterval [секунды] для изменения интервала"
        )

        if user_id not in self.monitoring_threads:
            self.start_monitoring_for_user(user_id)

    def set_interval(self, update: Update, context: CallbackContext) -> None:
        user_id = update.effective_user.id
        try:
            interval = int(context.args[0])
            if interval < 10:
                update.message.reply_text("❌ Минимальный интервал - 10 секунд!")
                return

            self.monitoring_intervals[user_id] = interval
            update.message.reply_text(f"🕒 Новый интервал проверки: {interval} секунд")
        except (IndexError, ValueError):
            update.message.reply_text("ℹ️ Использование: /setinterval [секунды]")

    def start_monitoring_for_user(self, user_id: int) -> None:
        if user_id in self.monitoring_threads:
            return

        thread = Thread(target=self.monitor_forum, args=(user_id,))
        thread.daemon = True
        thread.start()
        self.monitoring_threads[user_id] = thread

    def monitor_forum(self, user_id: int) -> None:
        logger.info(f"Начат мониторинг для пользователя {user_id}")
        while self.running and user_id in self.known_topics:
            try:
                self.check_forum(user_id)
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
            
            interval = self.monitoring_intervals.get(user_id, 60)
            time.sleep(interval)

    def check_forum(self, user_id: int) -> None:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(15000)
                
                try:
                    page.goto(self.forum_url)
                    page.wait_for_load_state("networkidle")
                except PlaywrightTimeoutError:
                    logger.warning("Таймаут загрузки страницы")
                
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            topics = self.extract_topics(soup)
            
            new_topics = [
                t for t in topics 
                if t['url'] not in self.known_topics[user_id]
            ]
            
            if new_topics:
                self.known_topics[user_id].extend(t['url'] for t in new_topics)
                self.notify_user(user_id, new_topics)

        except Exception as e:
            logger.error(f"Ошибка проверки форума: {e}")

    def extract_topics(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        topics = []
        # Пример селекторов для форума (требует настройки)
        for topic in soup.select('.topic-list-item'):
            title_elem = topic.select_one('.topic-title a')
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                if url:
                    url = url if url.startswith('http') else f"{self.forum_url}{url}"
                    topics.append({'title': title, 'url': url})
        return topics

    def notify_user(self, user_id: int, topics: List[Dict[str, str]]) -> None:
        for topic in topics:
            try:
                self.bot.send_message(
                    chat_id=user_id,
                    text=f"📌 Новая тема: {topic['title']}\n🔗 {topic['url']}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения: {e}")

    def stop(self) -> None:
        self.running = False
        logger.info("Бот остановлен")

def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN', '')
    FORUM_URL = os.getenv('FORUM_URL', '')
    # Создаем Updater с токеном
    updater = Updater(token=TOKEN, use_context=True)
    
    # Получаем бота из Updater
    bot_instance = updater.bot
    
    # Инициализируем наш класс бота
    forum_bot = ForumMonitorBot(bot_instance, FORUM_URL)
    
    # Регистрируем обработчики
    updater.dispatcher.add_handler(CommandHandler('start', forum_bot.start))
    updater.dispatcher.add_handler(CommandHandler('setinterval', forum_bot.set_interval))
    
    try:
        updater.start_polling()
        logger.info("🤖 Бот запущен")
        updater.idle()
    except KeyboardInterrupt:
        forum_bot.stop()
        updater.stop()

if __name__ == '__main__':
    main()