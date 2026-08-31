# xenforo
I specialize in building Telegram bots, web scrapers, and automation tools designed to process dynamic data and streamline workflows.

An asynchronous Telegram bot built with Python to monitor and track new forum in real-time.  
The project solves the challenge of scraping dynamic, JavaScript-rendered web pages by leveraging a headless browser engine.  
Tech StackLanguage: Python 3.10+Browser Automation: Playwright (Chromium Headless)  
HTML Parsing: BeautifulSoup4  
Telegram API: python-telegram-bot 
Concurrency: Python threading (Background per-user monitoring loops)  
Environment Management: python-dotenv  
Dynamic JS Rendering: Employs Playwright to bypass client-side rendering hurdles and single-page application (SPA) limitations.  
Multi-Threaded Execution: Runs user monitoring tasks in isolated background threads (Thread) to keep the main bot responsive.  
Instant Notifications: Sends real-time alerts to Telegram whenever new content appears on the forum. 
Customizable Intervals: Users can set custom polling intervals on the fly using the /setinterval command.  
Quick Start1. Clone the repositoryBashgit clone https://github.com/casualmove/forum-monitor-bot.git
cd forum-monitor-bot
2. Install dependenciesBashpip install -r requirements.txt
playwright install chromium
3. Environment SetupCreate a .env file in the root directory:  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
FORUM_URL=https://your_site/forums/...
4. Run the BotBashpython bot.py
Bot Commands:
/start — Start monitoring the target forum section.  
/setinterval [seconds] — Adjust the polling frequency (minimum 10 seconds).  
