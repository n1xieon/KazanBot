# Казань Бот 🚄

Telegram-бот для отсчёта времени до поездки в Казань. 
Простой, уютный, с поддержкой кнопок, FSM и базы данных.

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🧠 Возможности

- Выбор времени отправления из заранее заданных опций
- Поддержка состояний (FSM): выбор, ожидание, отмена
- Отправка уведомлений каждый час
- Кнопки "Отменить" и "Сменить время"
- Сохранение прогресса в SQLite
- Поддержка многопользовательской работы
- Готов к деплою 24/7 на Render.com

---

## 🚀 Быстрый старт

```bash
pip install -r requirements.txt
```

Создай `.env` файл:

```env
BOT_TOKEN=твой_токен_бота
```

Запуск:

```bash
python bot.py
```

---

## ☁️ Деплой на Render.com

1. Зарегистрируйся: https://render.com
2. Подключи репозиторий с этим ботом
3. Создай `Background Worker`
4. Укажи `BOT_TOKEN` в переменных окружения

📄 Файл `render.yaml` уже готов — ничего дописывать не нужно.

---

## 📁 Структура проекта

```
Kazan_bot/
├── bot.py             # Основная логика бота
├── database.py        # Работа с SQLite
├── requirements.txt   # Зависимости
├── render.yaml        # Настройка деплоя на Render
├── .env               # Переменные окружения (в .gitignore)
├── .gitignore
└── README.md
```

---

## 🔮 TODO

- [ ] Отправка напоминания за X минут до события
- [ ] Поддержка пользовательских событий
- [ ] Логирование действий пользователей

---

## 📝 Лицензия

MIT © 2025
