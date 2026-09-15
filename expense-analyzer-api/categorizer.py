import unicodedata

from rapidfuzz import fuzz


# Keywords are grouped by the category already used by the application.
# Slovak names are included together with common no-diacritic variants.
CATEGORY_KEYWORDS = {
    "Groceries": [
        "pyaterochka", "magnit", "supermarket",
        "kaufland", "lidl", "billa", "tesco", "coop jednota",
        "fresh", "terno", "kraj", "koruna", "milk agro", "milk-agro", "teta", "101 drogerie",
        "potraviny", "potravina", "food store",
    ],
    "Dining": [
        "cafe", "café", "restaurant", "bar", "restauracia", "reštaurácia",
        "jedlo", "pizza", "burger", "kebab", "donaska", "donáška",
        "foodora", "wolt", "bolt food", "bistro.sk", "bistro sk",
    ],
    "Transport": [
        "taxi", "uber", "bolt", "dopravny podnik mesta kosice",
        "dopravný podnik mesta košice", "dpmk", "mhd", "kosice mhd",
        "elektricka", "električka", "autobus", "cestovne", "cestovné",
        "listok", "lístok", "public transport",
    ],
    "Fuel": [
        "gas station", "lukoil", "slovnaft", "omv", "shell", "tanker",
        "benzin", "benzín", "nafta", "palivo", "cerpacia stanica",
        "čerpacia stanica",
    ],
    "Subscriptions": ["spotify", "netflix", "subscription", "predplatne", "predplatné"],
    "Shopping": [
        "ozon", "wildberries", "purchase", "oblecenie", "oblečenie",
        "clothing", "electronic", "elektronika", "alza", "mall.sk", "mall sk",
    ],
    "Health": [
        "pharmacy", "apteka", "lekaren", "lekáreň", "dm", "dm drogerie markt", "teta", "101 drogerie", "dr.max", "dr max",
        "benu", "health", "gym", "zdravie", "doktor", "medical",
    ],
    "Entertainment": [
        "cinema", "tickets", "kino", "vstupenka", "vstupenky", "divadlo",
        "koncert", "game", "gaming",
    ],
    "Housing": [
        "rent", "najom", "nájom", "housing", "byt", "hypoteka", "hypotéka",
    ],
    "Utilities": [
        "electricity", "elektrina", "water", "voda", "heating", "kurenie",
        "internet", "telekom", "orange", "o2", "4ka", "vodarne", "vodárne",
        "energie", "utility", "ucet za elektrinu", "účet za elektrinu",
    ],
    "Education": [
        "education", "skola", "škola", "university", "univerzita", "course",
        "kurz", "kniha", "books", "student",
    ],
    "Sports": [
        "sport", "fitness", "fitko", "plavaren", "plaváreň", "stadion", "štadión",
    ],
    "Travel": [
        "hotel", "booking", "airbnb", "flight", "let", "dovolenka", "travel",
        "cestovanie", "letenka", "letenky",
    ],
}

FUZZY_THRESHOLD = 88


def _normalize(text: str) -> str:
    """Lowercase text and remove diacritics for robust Slovak matching."""
    text = str(text or "").lower().strip()
    return "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


NORMALIZED_CATEGORY_KEYWORDS = {
    category: [_normalize(keyword) for keyword in keywords]
    for category, keywords in CATEGORY_KEYWORDS.items()
}


def categorize(description: str) -> str:
    description_normalized = _normalize(description)

    # First use exact substring matching. This is deterministic and avoids
    # false fuzzy matches for common short words such as "bolt".
    for category, keywords in NORMALIZED_CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword and keyword in description_normalized:
                return category

    # Fall back to fuzzy matching for small spelling variations / bank text.
    best_category = "Other"
    best_score = 0

    for category, keywords in NORMALIZED_CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if len(keyword) < 5:
                continue
            score = fuzz.partial_ratio(keyword, description_normalized)
            if score > best_score:
                best_score = score
                best_category = category

    if best_score >= FUZZY_THRESHOLD:
        return best_category

    return "Other"


if __name__ == "__main__":
    test_cases = [
        "Pyaterochka Moscow",
        "Kaufland Košice",
        "Lidl Košice",
        "BILLA",
        "Tesco Stores",
        "COOP Jednota",
        "dm drogerie markt",
        "DPMK a.s.",
        "MHD Košice",
        "Bolt",
        "Bolt Food",
        "Foodora",
        "Wolt",
        "Slovnaft",
        "OMV",
        "Dr.Max",
        "lekáreň",
        "Something Random",
    ]

    for case in test_cases:
        print(f"{case} -> {categorize(case)}")
