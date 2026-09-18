"""
Подключение твоей собственной обученной модели (skynet: train.py + predict.py
+ model.joblib) к бэкенду вместо встроенной ml_categorizer.py.

Как это работает:
1. model.joblib должен лежать рядом с этим файлом (в корне бэкенда).
2. При первом обращении модель загружается один раз (Categorizer из predict.py)
   и переиспользуется для всех последующих запросов — переоткрывать файл
   на каждый запрос не нужно.
3. categorize_smart() — функция с тем же именем и той же сигнатурой, что была
   в ml_categorizer.py, поэтому analyzer.py и api.py подключаются к ней без
   переделок остального кода.

Важное отличие от ml_categorizer.py: эта модель не дообучается на лету через
/api/feedback — она обучена один раз через train.py на твоей базе. Если
захочешь дообучение на исправлениях — это отдельная задача (дописать
исправление в CSV и запустить train.py заново), сейчас не реализовано.
"""

import os
from typing import Tuple

from predict import Categorizer

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")

NOT_SURE_LABEL = "Не уверен / Прочее"  # см. predict.py: Categorizer.predict()

_instance = None


def get_categorizer() -> Categorizer:
    global _instance
    if _instance is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Не найден {MODEL_PATH}. Скопируй сюда свой обученный model.joblib "
                f"из папки skynet (после того, как отработает train.py)."
            )
        _instance = Categorizer(MODEL_PATH)
    return _instance


def categorize_smart(description: str) -> Tuple[str, str, float]:
    """
    Возвращает (категория, источник, уверенность) — тот же формат, что был
    у ml_categorizer.categorize_smart(), чтобы остальной код не менять.

    источник:
    - "ml" — модель уверена (>= порога, заданного в predict.py)
    - "ml_low_confidence" — уверенности не хватило, категория "Не уверен / Прочее"
    """
    result = get_categorizer().predict(description)
    category = result["category"]
    confidence = result["confidence"]
    source = "ml_low_confidence" if category == NOT_SURE_LABEL else "ml"
    return category, source, confidence


def known_categories() -> list:
    """Все категории, которые знает модель (для /api/categories)."""
    return sorted(get_categorizer().pipeline.classes_.tolist())


if __name__ == "__main__":
    test_cases = ["Lidl", "ЛИДЛ", "Slovnaft", "СЛОВНАФТ", "кофе с собой"]
    for case in test_cases:
        cat, source, conf = categorize_smart(case)
        print(f"{case!r:25} -> {cat} (source={source}, confidence={conf:.2f})")
