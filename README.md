# RenaiVPN Bot

Telegram бот для продажи VPN-подписок на базе Remnwave.

## Возможности

- 💳 Автоматизированная продажа VPN-подписок
- 💰 Интеграция с ЮKassa для приема платежей
- 🌐 Интеграция с Remnwave API для управления VPN аккаунтами
- 📊 Управление подписками пользователей
- 📱 Инструкции по настройке для всех платформ
- 💬 Система технической поддержки
- 🔐 Административная панель
- 📈 Статистика и аналитика

## Технологический стек

- **Python 3.11+**
- **python-telegram-bot 20.7** - библиотека для работы с Telegram Bot API
- **PostgreSQL 14+** - основная база данных
- **SQLAlchemy 2.0+** - ORM для работы с БД
- **Alembic** - миграции базы данных
- **YooKassa** - платежный провайдер
- **Docker & Docker Compose** - контейнеризация

## Структура проекта

```
RenaiVPN/
├── bot/
│   ├── handlers/       # Обработчики команд и callback
│   └── keyboards/      # Inline клавиатуры
├── database/
│   ├── models.py       # SQLAlchemy модели
│   ├── crud.py         # CRUD операции
│   └── connection.py   # Подключение к БД
├── services/
│   ├── remnwave.py     # Remnwave API клиент
│   ├── payment.py      # Платежные провайдеры
│   └── subscription.py # Бизнес-логика подписок
├── utils/
│   ├── config.py       # Конфигурация
│   ├── logger.py       # Настройка логирования
│   └── helpers.py      # Вспомогательные функции
├── main.py             # Точка входа
├── requirements.txt    # Зависимости Python
├── docker-compose.yml  # Docker конфигурация
└── Dockerfile
```

## Установка и запуск

### Локальный запуск

1. **Клонируйте репозиторий**

```bash
git clone <repository-url>
cd RenaiVPN
```

2. **Создайте виртуальное окружение**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости**

```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения**

Скопируйте `.env.example` в `.env` и заполните необходимые значения:

```bash
cp .env.example .env
```

Основные параметры:
- `BOT_TOKEN` - токен Telegram бота (получить у [@BotFather](https://t.me/BotFather))
- `DATABASE_URL` - строка подключения к PostgreSQL
- `REMNWAVE_API_KEY` - ключ API Remnwave
- `YUKASSA_SHOP_ID` и `YUKASSA_SECRET_KEY` - данные из ЮKassa

5. **Инициализируйте базу данных**

```bash
# Если используете Alembic
alembic upgrade head

# Или базы данных будут созданы автоматически при первом запуске
```

6. **Запустите бота**

```bash
python main.py
```

### Запуск через Docker

1. **Настройте `.env` файл**

```bash
cp .env.example .env
# Отредактируйте .env
```

2. **Запустите контейнеры**

```bash
docker-compose up -d
```

3. **Проверьте логи**

```bash
docker-compose logs -f bot
```

## Первоначальная настройка

### 1. Создание тарифных планов

Тарифные планы нужно добавить в базу данных вручную:

```sql
INSERT INTO plans (name, slug, description, price, currency, duration_days, devices_count, remnwave_plan_id, is_active)
VALUES 
  ('Месячный', 'monthly', '1 месяц VPN', 299.00, 'RUB', 30, 1, 'monthly_plan', true),
  ('Квартальный', 'quarterly', '3 месяца VPN', 699.00, 'RUB', 90, 2, 'quarterly_plan', true),
  ('Годовой', 'yearly', '12 месяцев VPN', 1999.00, 'RUB', 365, 5, 'yearly_plan', true);
```

### 2. Добавление администраторов

Укажите Telegram ID администраторов в `.env`:

```
ADMIN_USER_IDS=123456789,987654321
```

## Использование

### Основные команды бота

- `/start` - Запуск бота и главное меню
- `/admin` - Админ-панель (только для администраторов)
- `/admin_stats` - Статистика (только для администраторов)

### Пользовательский функционал

1. **Покупка подписки**
   - Просмотр тарифов
   - Выбор способа оплаты
   - Оплата через ЮKassa
   - Автоматическое получение конфигурации VPN

2. **Управление подписками**
   - Просмотр активных подписок
   - Скачивание конфигурационных файлов
   - Получение QR-кодов

3. **Поддержка**
   - FAQ
   - Создание обращений в поддержку

### Административные функции

- Просмотр статистики (пользователи, заказы, доход)
- Управление пользователями
- Просмотр заказов и платежей

## Разработка

### Структура базы данных

Основные таблицы:
- `users` - Пользователи
- `plans` - Тарифные планы
- `orders` - Заказы
- `subscriptions` - Подписки
- `support_tickets` - Тикеты поддержки
- `promo_codes` - Промокоды

### Добавление новых обработчиков

1. Создайте функцию-обработчик в `bot/handlers/`
2. Зарегистрируйте её в `main.py` в функции `setup_handlers()`

### Логирование

Логи сохраняются в директорию `logs/`:
- `logs/bot.log` - основной лог бот