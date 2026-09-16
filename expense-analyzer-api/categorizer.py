from rapidfuzz import fuzz

CATEGORY_KEYWORDS = {
    "Groceries": ["pyaterochka", "magnit", "supermarket"],
    "Transport": ["taxi", "uber", "gas station", "lukoil"],
    "Subscriptions": ["spotify", "netflix", "subscription"],
    "Dining": ["cafe", "restaurant", "bar"],
    "Shopping": ["ozon", "wildberries", "purchase"],
    "Health": ["pharmacy", "apteka", "gym"],
    "Entertainment": ["cinema", "tickets"],
}

FUZZY_THRESHOLD = 80

def categorize(description: str) -> str:
    description_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    best_category = "Other"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            score = fuzz.partial_ratio(keyword, description_lower)
            if score > best_score:
                best_score = score
                best_category = category

    if best_score >= FUZZY_THRESHOLD:
        return best_category

    return "Other"


if __name__ == "__main__":
    test_cases = [
        "Pyaterochka Moscow",
        "Pyaterochka #4521",
        "Yandex Taxi",
        "Uber4 Trip", 
        "Something Random",
    ]

    for case in test_cases:
        print(f"{case} -> {categorize(case)}")