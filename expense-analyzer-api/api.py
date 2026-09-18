"""
JSON API для мобильного приложения (React Native).

Отличия от старого app.py:
- Не рендерит HTML — только JSON.
- CORS включён, чтобы к серверу можно было стучаться с телефона/эмулятора.
- Файл анализируется прямо в памяти, ничего не сохраняется на диск
  (для мобильного клиента постоянное хранилище на сервере не нужно).

Запуск:
    pip install -r requirements.txt
    python api.py

По умолчанию слушает на 0.0.0.0:5000, чтобы телефон в той же Wi-Fi сети
мог достучаться до сервера по IP компьютера (например http://192.168.1.23:5000).
"""

import csv
import os
import tempfile
import traceback
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from analyzer import load_and_analyze, analyze_transactions
from skynet_categorizer import known_categories
from ai_assistant import parse_expense

app = Flask(__name__)
CORS(app)  # разрешаем запросы с любого origin — упрощает разработку RN-приложения

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}
CORRECTIONS_PATH = os.path.join(os.path.dirname(__file__), "corrections.csv")


def get_all_categories():
    """Список категорий, которые знает твоя обученная модель."""
    return known_categories()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def format_result(result: dict) -> dict:
    by_category = [
        {"category": category, "amount": round(float(amount), 2)}
        for category, amount in result["by_category"].items()
    ]

    by_week = [
        {"week": int(week), "amount": round(float(amount), 2)}
        for week, amount in result["by_week"].items()
    ]

    top_transactions = [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "description": row["description"],
            "amount": round(float(row["amount"]), 2),
            "category": row["category"],
            "category_source": row["category_source"],
            "category_confidence": round(float(row["category_confidence"]), 2),
        }
        for _, row in result["top_transactions"].iterrows()
    ]

    return {
        "total": round(float(result["total"]), 2),
        "by_category": by_category,
        "by_week": by_week,
        "top_transactions": top_transactions,
    }


@app.route("/api/health", methods=["GET"])
def health():
    """Простой пинг, чтобы приложение могло проверить, что сервер доступен."""
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Принимает файл (multipart/form-data, поле "statement"),
    возвращает JSON с результатами анализа.

    Пример ответа:
    {
      "total": 12345.67,
      "by_category": [{"category": "Groceries", "amount": 4500.0}, ...],
      "by_week": [{"week": 35, "amount": 2300.5}, ...],
      "top_transactions": [
        {"date": "2026-09-01", "description": "Pyaterochka Moscow", "amount": 1250.5, "category": "Groceries"},
        ...
      ]
    }
    """
    file = request.files.get("statement")

    if not file or file.filename == "":
        return jsonify({"error": "Файл не найден. Ожидается поле 'statement'."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Поддерживаются только CSV и Excel файлы."}), 400

    file_ext = file.filename.rsplit(".", 1)[1].lower()

    # analyzer.load_and_analyze определяет тип файла по расширению пути,
    # поэтому сохраняем во временный файл с правильным расширением, а не держим в памяти.
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=f".{file_ext}")
    try:
        with os.fdopen(tmp_fd, "wb") as tmp_file:
            file.save(tmp_file)
        result = load_and_analyze(tmp_path)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Не удалось обработать файл. Проверьте названия колонок (date, description, amount)."}), 422
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return jsonify(format_result(result))


@app.route("/api/analyze-transactions", methods=["POST"])
def analyze_transactions_endpoint():
    """
    Принимает JSON со списком трат, введённых вручную в приложении,
    возвращает тот же формат ответа, что и /api/analyze.

    Ожидаемое тело запроса:
    {
      "transactions": [
        {"date": "2026-09-01", "description": "Pyaterochka", "amount": 1250.5},
        ...
      ]
    }
    """
    body = request.get_json(silent=True) or {}
    transactions = body.get("transactions")

    if not transactions or not isinstance(transactions, list):
        return jsonify({"error": "Ожидается непустой список 'transactions'."}), 400

    for tx in transactions:
        if not all(key in tx for key in ("date", "description", "amount")):
            return jsonify({"error": "Каждая трата должна содержать date, description и amount."}), 400

    try:
        result = analyze_transactions(transactions)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Не удалось проанализировать траты. Проверьте формат данных."}), 422

    return jsonify(format_result(result))


@app.route("/api/parse-expense", methods=["POST"])
def parse_expense_endpoint():
    """
    АИ-ассистент: принимает свободный текст, возвращает разобранную трату.

    Тело запроса:
    {"text": "потратил 20 евро на кофе вчера"}

    Ответ:
    {
      "date": "2026-09-16",
      "description": "кофе",
      "amount": 20.0,
      "currency": "EUR",
      "category": "Dining",
      "category_source": "ml",
      "category_confidence": 0.81
    }
    """
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()

    if not text:
        return jsonify({"error": "Поле 'text' не должно быть пустым."}), 400

    try:
        result = parse_expense(text)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Не удалось разобрать текст."}), 422

    if result["amount"] is None:
        return jsonify({"error": "Не удалось найти сумму в тексте. Укажи число, например «20» или «20.50».", "partial": result}), 422

    return jsonify(result)


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """
    Сохраняет исправление категории от пользователя в corrections.csv.

    ВАЖНО: в отличие от старой встроенной модели, эта модель (обучена твоим
    train.py) не дообучается мгновенно на лету. Исправление просто копится
    в файл рядом с этим — периодически добавляй строки из corrections.csv
    в свою sample_data_sk и переобучай: python train.py sample_data_sk model.joblib

    Тело запроса:
    {"description": "Kaufland Kosice", "category": "Продукты"}
    """
    body = request.get_json(silent=True) or {}
    description = body.get("description")
    category = body.get("category")

    if not description or not category:
        return jsonify({"error": "Нужны оба поля: description и category."}), 400

    try:
        is_new_file = not os.path.exists(CORRECTIONS_PATH)
        with open(CORRECTIONS_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(["text", "category", "corrected_at"])
            writer.writerow([description, category, datetime.now().isoformat(timespec="seconds")])
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Не удалось сохранить исправление."}), 500

    return jsonify({"status": "ok", "note": "Сохранено в corrections.csv. Модель дообучится после следующего запуска train.py."})


@app.route("/api/categories", methods=["GET"])
def categories():
    """Список всех доступных категорий — для выбора в приложении при исправлении."""
    return jsonify({"categories": get_all_categories()})


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    # host="0.0.0.0" — обязательно, иначе с телефона по Wi-Fi не достучаться.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
