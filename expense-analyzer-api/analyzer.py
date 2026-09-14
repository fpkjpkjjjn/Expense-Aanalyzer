import pandas as pd
from categorizer import categorize


def analyze_dataframe(df: pd.DataFrame) -> dict:
    df["category"] = df["description"].apply(categorize)
    df["date"] = pd.to_datetime(df["date"])

    by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_transactions = df.sort_values("amount", ascending=False).head(5)

    df["week"] = df["date"].dt.isocalendar().week
    by_week = df.groupby("week")["amount"].sum()

    total = df["amount"].sum()

    return {
        "df": df,
        "total": total,
        "by_category": by_category,
        "top_transactions": top_transactions,
        "by_week": by_week,
    }


def load_and_analyze(file_path: str) -> dict:
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    return analyze_dataframe(df)


def analyze_transactions(transactions: list) -> dict:
    """
    Анализирует список трат, введённых вручную в приложении.
    transactions: [{"date": "2026-09-01", "description": "...", "amount": 123.45}, ...]
    """
    df = pd.DataFrame(transactions)
    return analyze_dataframe(df)


if __name__ == "__main__":
    result = load_and_analyze("data/sample_statement.csv")

    print(f"Total spent: {result['total']:.2f}")
    print("\nBy category:")
    print(result["by_category"])
    print("\nTop 5 transactions:")
    print(result["top_transactions"][["date", "description", "amount"]])