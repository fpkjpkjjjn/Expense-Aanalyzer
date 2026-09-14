# Expense Analyzer — JSON API (backend для мобильного приложения)

## Запуск

```bash
pip install -r requirements.txt
python api.py
```

Сервер поднимется на `http://0.0.0.0:5000` — доступен и с компьютера
(`127.0.0.1:5000`), и с телефона в той же Wi-Fi сети по IP компьютера.

**Как узнать IP компьютера в локальной сети:**
- Windows: `ipconfig` → строка "IPv4-адрес"
- macOS/Linux: `ifconfig` или `ip addr` → обычно `192.168.х.х`

## Эндпоинты

### `GET /api/health`
Проверка, что сервер жив.
```json
{"status": "ok"}
```

### `POST /api/analyze-transactions`
Основной эндпоинт — принимает список трат, введённых вручную в приложении
(JSON, не файл).

Тело запроса:
```json
{
  "transactions": [
    {"date": "2026-09-01", "description": "Pyaterochka", "amount": 1250.50},
    {"date": "2026-09-05", "description": "Uber", "amount": 340.00}
  ]
}
```

Пример через curl:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "transactions": [
    {"date": "2026-09-01", "description": "Pyaterochka", "amount": 1250.50}
  ]
}' http://127.0.0.1:5000/api/analyze-transactions
```

Ответ (одинаковый формат для обоих эндпоинтов анализа):
```json
{
  "total": 1590.5,
  "by_category": [
    {"category": "Groceries", "amount": 1250.5},
    {"category": "Transport", "amount": 340.0}
  ],
  "by_week": [
    {"week": 36, "amount": 1590.5}
  ],
  "top_transactions": [
    {"date": "2026-09-01", "description": "Pyaterochka", "amount": 1250.5, "category": "Groceries"}
  ]
}
```

### `POST /api/analyze` (оставлен для совместимости)
Старый способ — загрузка CSV/Excel файла (`multipart/form-data`, поле
`statement`). Приложение теперь им не пользуется, но эндпоинт работает,
если понадобится в будущем.

Ошибки возвращаются в JSON с соответствующим HTTP-кодом:
- `400` — некорректные данные (пустой список, не хватает полей)
- `422` — не удалось проанализировать (например, неверный формат даты)

## Структура

```
api.py          — Flask-эндпоинты
analyzer.py     — анализ трат (категоризация, суммы по категориям/неделям)
categorizer.py  — определение категории по описанию траты
```

Категоризация трат (`categorizer.py`) работает по ключевым словам и нечёткому
сравнению — не нужно указывать категорию вручную в приложении, она
определится автоматически по описанию (например «Пятёрочка» → Groceries).
