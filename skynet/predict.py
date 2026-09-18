"""
Использование обученной модели для категоризации новой траты.

Использование как скрипт:
    python3 predict.py model.joblib "такси до аэропорта"

Использование как модуль в вашем приложении:
    from predict import Categorizer
    cat = Categorizer("model.joblib")
    result = cat.predict("такси до аэропорта")
    # {'category': 'Транспорт', 'confidence': 0.87, 'alternatives': [...]}

ВАЖНО: text_normalize.py должен лежать рядом с этим файлом (и с model.joblib).
Модель обучена с preprocessor=normalize_text внутри TfidfVectorizer — эта
функция сохранена как часть пайплайна, и joblib.load() должен суметь её
найти/импортировать при загрузке, иначе упадёт с ModuleNotFoundError.
"""

import sys
import joblib

import text_normalize  # noqa: F401 — не используется напрямую, но нужен для
                        # распаковки model.joblib (см. примечание выше)


class Categorizer:
    def __init__(self, model_path: str):
        self.pipeline = joblib.load(model_path)

    def predict(self, text: str, confidence_threshold: float = 0.4) -> dict:
        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_

        # сортируем категории по вероятности
        ranked = sorted(zip(classes, proba), key=lambda x: -x[1])
        top_category, top_confidence = ranked[0]

        return {
            "category": top_category if top_confidence >= confidence_threshold else "Не уверен / Прочее",
            "confidence": round(float(top_confidence), 3),
            "alternatives": [
                {"category": c, "confidence": round(float(p), 3)}
                for c, p in ranked[1:4]  # ещё 3 варианта на случай, если модель ошиблась
            ],
        }


if __name__ == "__main__":
    model_path = sys.argv[1] if len(sys.argv) > 1 else "model.joblib"
    text = sys.argv[2] if len(sys.argv) > 2 else "кофе с собой"

    cat = Categorizer(model_path)
    result = cat.predict(text)

    print(f"Трата: «{text}»")
    print(f"Категория: {result['category']} (уверенность: {result['confidence']:.0%})")
    print("Другие варианты:")
    for alt in result["alternatives"]:
        print(f"  - {alt['category']}: {alt['confidence']:.0%}")
