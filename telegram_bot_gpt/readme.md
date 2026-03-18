# Фінальний проєкт модуля 1 JavaRush-університету

Telegram‑бот підтримує наступний функціонал:
- `/random` — дізнатись випадковий факт  
- `/gpt` — задати питання ChatGPT  
- `/talk` — поговорити з відомою особистістю  
- `/quiz` — перевірити свої знання  
- `/translate` — перекладач  
- `/resume` — допомога з резюме  

## 📦 Встановлення

1. Клонуйте репозиторій:
   ```bash
   # Клонуй репозиторій
    git clone https://github.com/Bigoook/JavaRushStudy.git
    cd JavaRushStudy

    # Увімкни sparse-checkout
    git sparse-checkout init --cone

    # Вкажи потрібну папку
    git sparse-checkout set telegram_bot_gpt
    cd telegram_bot_gpt
   ```
або завантажте папку https://github.com/Bigoook/JavaRushStudy/tree/main/telegram_bot_gpt

2. Створіть та активуйте віртуальне середовище:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate      # Windows
   ```

3. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```

4. Створіть файл `.env` і додайте ваші ключі:
   ```
   BOT_TOKEN=ваш_токен
   ChatGPT_TOKEN=ваш_api_ключ
   ```

5. Запустіть бота:
   ```bash
   python bot.py
   ```
```
