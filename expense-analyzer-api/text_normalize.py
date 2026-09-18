"""
Нормализация текста для сопоставления названий магазинов на разных языках.

Подключается как preprocessor в TfidfVectorizer (см. train.py) — то есть
применяется автоматически и при обучении, и при предсказании, одним и тем
же способом. Поэтому если в обучающих данных есть "Lidl", а пользователь
написал "ЛИДЛ" — обе строки после нормализации превращаются в "lidl" и
модель видит их как один и тот же текст.

Ничего вызывать вручную не нужно — достаточно один раз передать эту функцию
в TfidfVectorizer(preprocessor=normalize_text), дальше она встроена в
пайплайн и сохраняется вместе с моделью в model.joblib.
"""

import unicodedata

_CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def cyrillic_to_latin(text: str) -> str:
    """Фонетическая транслитерация кириллицы в латиницу: 'Лидл' -> 'Lidl'."""
    result = []
    for ch in text:
        lower = ch.lower()
        if lower in _CYRILLIC_TO_LATIN:
            replacement = _CYRILLIC_TO_LATIN[lower]
            result.append(replacement.upper() if ch.isupper() and replacement else replacement)
        else:
            result.append(ch)
    return "".join(result)


def strip_diacritics(text: str) -> str:
    """Снимает диакритику: 'ČSOB' -> 'CSOB', 'Stredoslovenská' -> 'Stredoslovenska'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    """
    Полная нормализация: транслитерация кириллицы + снятие диакритики +
    нижний регистр. Это и есть та функция, что передаётся в TfidfVectorizer
    как preprocessor.

    normalize_text("ЛИДЛ") == normalize_text("Lidl") == "lidl"
    """
    return strip_diacritics(cyrillic_to_latin(text)).lower()
