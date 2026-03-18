Фінальний проєкт модуля 1 JavaRush-університету
Telegram bot
підтримує настуний функціонал:
/random - дізнатись випадковий факт
/gpt 	- Задати питання ChatGPT
/talk 	- поговорити з відомою особистістю
/quiz 	- перевірити свої знання
/translate - перекладач
/resume - допомога з резюме

## Встановлення

1. Клонуйте репозиторій:
   ```bash
   git clone 
   cd telegram_bot_gpt
2. Створіть та активуйте віртуальне середовище:

	python -m venv venv
	source venv/bin/activate   # Linux / macOS
	venv\Scripts\activate      # Windows
3. Встановіть залежності:
	pip install -r requirements.txt
4. Створіть файл .env і додайте ваші ключі:
	BOT_TOKEN=ваш_токен
	ChatGPT_TOKEN=ваш_api_ключ
	
5.Запустіть бота:
	python bot.py

