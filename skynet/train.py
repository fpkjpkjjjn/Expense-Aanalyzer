"""
Обучение модели категоризации трат.

Подход: TF-IDF (по символьным n-граммам, устойчиво к опечаткам и окончаниям
русского языка) + линейный классификатор (LinearSVC).
Это лёгкая модель — не глубокая нейросеть, но она отлично решает задачу
текстовой классификации на малых и средних объёмах данных (сотни-тысячи
примеров) и обучается за секунды на CPU.

Использование:
    python3 train.py sample_data.csv model.joblib
"""

import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import joblib


def build_pipeline(calibration_cv: int = 3) -> Pipeline:
    """Создаёт пайплайн: векторизация текста + классификатор.

    calibration_cv — число фолдов для калибровки уверенности (predict_proba).
    Должно быть <= числа примеров в самой маленькой категории обучающих данных.
    """
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",     # символьные n-граммы — устойчивы к опечаткам,
        ngram_range=(2, 4),     # разным падежам/окончаниям слов
        min_df=1,
        lowercase=True,
    )
    # CalibratedClassifierCV поверх LinearSVC даёт predict_proba —
    # это нужно, чтобы знать "уверенность" модели в категории.
    base_clf = LinearSVC(class_weight="balanced")
    clf = CalibratedClassifierCV(base_clf, cv=calibration_cv)

    return Pipeline([
        ("tfidf", vectorizer),
        ("clf", clf),
    ])


def train(csv_path: str, model_out: str) -> None:
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["text", "category"])

    X = df["text"].astype(str)
    y = df["category"].astype(str)

    # Жёсткий минимум: модели нужно хотя бы 2 примера в каждой категории,
    # иначе её вообще невозможно ни обучить, ни проверить.
    class_counts = y.value_counts()
    too_rare = class_counts[class_counts < 2]
    if len(too_rare) > 0:
        print(
            "ОШИБКА: у следующих категорий всего 1 пример — этого недостаточно "
            "для обучения (нужно минимум 2, а лучше 10+ на категорию):\n  "
            + ", ".join(f"{name} ({count})" for name, count in too_rare.items())
            + "\n\nДобавьте им ещё строк в CSV и запустите заново."
        )
        return

    use_stratify = y.nunique() > 1

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if use_stratify else None
        )
    except ValueError:
        # На маленьких датасетах стратификация может физически не влезть
        # (например, тестовой выборки не хватает на все категории сразу).
        # В этом случае просто делим случайно, без сохранения пропорций.
        print(
            "Внимание: данных слишком мало для стратифицированного разбиения "
            "train/test, делю случайно (без сохранения пропорций категорий)."
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    # Число фолдов калибровки не может быть больше, чем число примеров
    # в самой маленькой категории обучающей выборки — иначе CalibratedClassifierCV
    # упадёт с ошибкой. Подстраиваем автоматически (минимум 2, максимум 3).
    min_train_class_count = y_train.value_counts().min()
    calibration_cv = max(2, min(3, min_train_class_count))
    if min_train_class_count < 3:
        print(
            f"Внимание: в обучающей выборке есть категории всего с "
            f"{min_train_class_count} примером(ами) после разбиения. "
            f"Оценка уверенности (confidence) для них будет менее надёжной — "
            f"добавьте больше примеров в такие категории, когда сможете."
        )

    pipeline = build_pipeline(calibration_cv=calibration_cv)

    # Кросс-валидация — честная оценка качества на всех данных
    try:
        scores = cross_val_score(pipeline, X, y, cv=3)
        print(f"Кросс-валидация accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")
    except ValueError:
        print(
            "Слишком мало данных для кросс-валидации (нужно минимум 3 примера "
            "в каждой категории), пропускаю этот шаг."
        )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\nОтчёт на отложенной выборке:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Финальное дообучение на всех данных перед сохранением
    pipeline.fit(X, y)
    joblib.dump(pipeline, model_out)
    print(f"\nМодель сохранена в {model_out}")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
    model_out = sys.argv[2] if len(sys.argv) > 2 else "model.joblib"
    train(csv_path, model_out)