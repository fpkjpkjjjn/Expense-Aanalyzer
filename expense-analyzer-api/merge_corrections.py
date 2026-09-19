"""
Переносит накопленные исправления (corrections.csv, создаётся автоматически
через /api/feedback) в твою основную базу — после чего можно переобучить
модель командой:

    python train.py sample_data_sk model.joblib

Использование:
    python merge_corrections.py sample_data_sk corrections.csv

После успешного переноса corrections.csv очищается (остаётся только
заголовок), чтобы одни и те же исправления не добавились дважды при
повторном запуске.
"""

import csv
import sys


def merge(database_path: str, corrections_path: str) -> None:
    try:
        with open(corrections_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            corrections = [(row["text"], row["category"]) for row in reader]
    except FileNotFoundError:
        print(f"Файл {corrections_path} не найден — нет исправлений для переноса.")
        return

    if not corrections:
        print("В corrections.csv нет новых исправлений.")
        return

    # sample_data_sk — обычный CSV с колонками text,category (без заголовка
    # или с ним — определяем автоматически по первой строке).
    with open(database_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip().lower()
    has_header = first_line.startswith("text") or first_line.startswith("описание")

    with open(database_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for text, category in corrections:
            # amount всегда 0.0 — колонка в обучении не используется (см. train.py),
            # но нужна для совпадения числа колонок с основным датасетом
            # (text,amount,category), иначе pandas сдвигает category в NaN
            # и dropna() в train.py молча теряет всю строку при обучении.
            writer.writerow([text, "0.0", category])

    # Очищаем corrections.csv, оставляя только заголовок
    with open(corrections_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category", "corrected_at"])

    print(f"Добавлено в {database_path}: {len(corrections)} строк.")
    print(f"Теперь переобучи модель: python train.py {database_path} model.joblib")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python merge_corrections.py sample_data_sk corrections.csv")
        sys.exit(1)

    merge(sys.argv[1], sys.argv[2])
