"""
АИ-ассистент для ввода трат свободным текстом.

Пользователь пишет как удобно: "потратил 20 евро на кофе",
"minul som 15€ na taxi vcera", "spent $8 on lunch" — ассистент сам достаёт
из этого дату, сумму, валюту, чистое описание и категорию.

Из чего это состоит:
1. Извлечение суммы и валюты — регулярные выражения (числа рядом с символами
   валют или словами типа "евро"/"eur"/"$"). Это детерминированный парсинг,
   не ML — для чисел он и не нужен, регулярка справляется надёжнее и без
   черного ящика.
2. Извлечение даты — распознавание слов "сегодня"/"вчера"/"dnes"/"včera"/
   "today"/"yesterday" и явных дат вида ГГГГ-ММ-ДД. Тоже правила, не ML.
3. Категория — здесь работает настоящая обучаемая ML-модель
   (skynet_categorizer.categorize_smart) — твоя собственная модель,
   обученная на своей базе (train.py + sample_data_sk).
4. Описание — то, что осталось от исходного текста после вычитания суммы,
   валюты, даты и служебных слов ("потратил", "spent", "minul", "на"/"on"/"na").

Вместе эти шаги превращают одну строку текста в готовую к сохранению трату.
"""

import re
from datetime import date, timedelta
from typing import Optional

from skynet_categorizer import categorize_smart

# --- Валюты -----------------------------------------------------------

CURRENCY_PATTERNS = [
    # (regex для валюты, код валюты)
    (r"€|eur\b|евро|euro", "EUR"),
    (r"\$|usd\b|долл(?:ар)?(?:ов|а)?|dollar", "USD"),
    (r"£|gbp\b|фунт", "GBP"),
    (r"kč|czk\b|крон", "CZK"),
    (r"₽|rub\b|руб(?:л(?:ей|я))?", "RUB"),
]

DEFAULT_CURRENCY = "EUR"  # Словакия

# Число: "20", "20.50", "20,50" — с точкой или запятой как разделителем
AMOUNT_PATTERN = re.compile(r"(\d+(?:[.,]\d{1,2})?)")

# --- Даты ---------------------------------------------------------------

DATE_WORDS = {
    "сегодня": 0, "dnes": 0, "today": 0,
    "вчера": -1, "včera": -1, "vcera": -1, "yesterday": -1,
    "позавчера": -2,
    "завтра": 1, "zajtra": 1, "tomorrow": 1,
}

EXPLICIT_DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# --- Служебные слова, которые не несут смысла для описания --------------

FILLER_WORDS = {
    "потратил", "потратила", "потратили", "заплатил", "заплатила", "купил", "купила",
    "minul", "minula", "zaplatil", "zaplatila", "kupil", "kupila",
    "spent", "paid", "bought",
    "на", "за", "na", "za", "on", "for", "v", "в",
    "som", "je", "bol", "bola",  # словацкие вспомогательные глаголы ("minul som" = "я потратил")
}


def _extract_amount_and_currency(text: str) -> tuple[Optional[float], str, str]:
    """
    Находит сумму и валюту в тексте, возвращает (сумма, валюта, текст_без_суммы).
    Если валюта явно не указана — используется DEFAULT_CURRENCY.
    """
    currency = DEFAULT_CURRENCY
    remaining = text

    for pattern, code in CURRENCY_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            currency = code
            remaining = remaining[: match.start()] + " " + remaining[match.end():]
            break

    amount_match = AMOUNT_PATTERN.search(remaining)
    if not amount_match:
        return None, currency, remaining

    amount_str = amount_match.group(1).replace(",", ".")
    amount = float(amount_str)
    remaining = remaining[: amount_match.start()] + " " + remaining[amount_match.end():]

    return amount, currency, remaining


def _extract_date(text: str) -> tuple[str, str]:
    """Возвращает (дата в формате ГГГГ-ММ-ДД, текст без упоминания даты)."""
    explicit = EXPLICIT_DATE_PATTERN.search(text)
    if explicit:
        remaining = text[: explicit.start()] + " " + text[explicit.end():]
        return explicit.group(1), remaining

    lowered = text.lower()
    for word, offset in DATE_WORDS.items():
        idx = lowered.find(word)
        if idx != -1:
            remaining = text[:idx] + " " + text[idx + len(word):]
            target_date = date.today() + timedelta(days=offset)
            return target_date.isoformat(), remaining

    return date.today().isoformat(), text


def _clean_description(text: str) -> str:
    """Убирает служебные слова и лишние пробелы, оставляя суть траты."""
    words = text.split()
    cleaned = [w for w in words if w.lower().strip(".,!?") not in FILLER_WORDS]
    description = " ".join(cleaned).strip(" .,!?-")
    return description if description else "Без описания"


def parse_expense(text: str) -> dict:
    """
    Главная функция ассистента: превращает свободный текст в структурированную трату.

    Пример:
        parse_expense("потратил 20 евро на кофе вчера")
        -> {
             "date": "2026-09-16",
             "description": "кофе",
             "amount": 20.0,
             "currency": "EUR",
             "category": "Dining",
             "category_source": "ml",
             "category_confidence": 0.81,
           }
    """
    text = text.strip()

    amount, currency, text_no_amount = _extract_amount_and_currency(text)
    date_str, text_no_date = _extract_date(text_no_amount)
    description = _clean_description(text_no_date)

    category, source, confidence = categorize_smart(description)

    return {
        "date": date_str,
        "description": description,
        "amount": amount,
        "currency": currency,
        "category": category,
        "category_source": source,
        "category_confidence": round(confidence, 2),
    }


if __name__ == "__main__":
    test_cases = [
        "потратил 20 евро на кофе вчера",
        "minul som 15€ na taxi",
        "spent $8.50 on lunch today",
        "Kaufland 45.30 2026-09-01",
        "заплатил 3.50 за автобус",
    ]
    for case in test_cases:
        print(f"{case!r}\n  -> {parse_expense(case)}\n")
